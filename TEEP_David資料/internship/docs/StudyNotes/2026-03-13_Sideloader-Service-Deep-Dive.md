# Sideloader Service Deep Dive — Collector Architecture, Power Monitoring & Fault Injection

**Date:** 2026-03-13  
**Source:** `External/sideloaderService/nino-sideloader-service/`

---

## 1. Overview

The Sideloader Service is a **privileged Flask pod** deployed on each O-RAN worker node. It serves as a **node-level monitoring and fault injection agent** that the rApp calls during automated gNB test runs. What makes it architecturally interesting is its clean separation of concerns: **collectors** handle time-series monitoring via a common `BaseCollector` framework, while **actions** handle destructive fault injection operations. All host access is achieved through `nsenter -t 1 -m -u -n -i` (entering PID 1's namespace).

---

## 2. `BaseCollector` — The 1 Hz Sampling Framework

Every time-series collector inherits from `BaseCollector` (`collectors/base.py`, 50 lines), which enforces:

```python
class BaseCollector(ABC):
    def gather(self, duration: int, include_timeseries=False):
        for _ in range(duration):
            sample = self.collect_sample()    # subclass
            self.timestamps.append(time.time())
            self.samples.append(sample)
            time.sleep(1)                     # ← 1 Hz enforced
        return self.aggregate(include_timeseries)
```

**Key design decisions:**
- **Fixed 1 Hz cadence** — not configurable. Simple and predictable, but means the minimum monitoring window is 1 second.
- **Two-phase pattern** — `collect_sample()` is pure data acquisition; `aggregate()` computes statistics (min/max/avg) and optional timeseries output.
- **Common `get_stats()`** — all collectors share the same min/max/avg calculation, ensuring consistent output format across CPU, memory, power, etc.

---

## 3. Collector Modules

### 3.1 CPU (`collectors/cpu.py`, 302 lines)

| Class | Purpose | Data Source |
|-------|---------|-------------|
| `CPUCollector` | Per-core usage with optional user/system/iowait/irq/softirq breakdown | `/proc/stat` via nsenter |
| `ContextSwitchCollector` | Total + per-CPU context switch rates | `/proc/stat` + `/proc/schedstat` |
| `CPUGovernorCollector` | Static check of scaling governor (performance/powersave) | `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor` |
| `CPUIdleCollector` | Static check of disabled C-states | `/sys/devices/system/cpu/cpu0/cpuidle/state*/disable` |
| `IRQAffinityCollector` | IRQ-to-core pinning for network interfaces | `/proc/irq/*/smp_affinity_list` |

**Delta calculation:** Reads cumulative jiffies from `/proc/stat`, stores `prev_stats`, and computes per-interval deltas. Usage = `(delta_total - delta_idle) / delta_total * 100`.

**Offline CPU detection:** After aggregation, scans `/sys/devices/system/cpu/cpuN/online` to identify offline cores — relevant for RT-isolated worker nodes where housekeeping cores are explicitly separated from signal-processing cores.

### 3.2 Power (`collectors/power.py`, 330 lines)

The most relevant collector for our TEEP work. **Two independent power sources:**

| Source | Method | Cadence | What It Measures |
|--------|--------|---------|------------------|
| **RAPL** | `energy_uj` counters from `/sys/class/powercap/intel-rapl:*` | Every 1s | CPU package, DRAM, Uncore, PSys (software estimate) |
| **iDRAC/Redfish** | HTTPS GET to Dell BMC API | Every 5s (every 5th sample) | Full system power including PSU, fans, storage |

**RAPL domain auto-discovery:**
```python
for socket_id in range(8):          # up to 8 CPU sockets
    for subdomain_id in range(8):   # up to 8 subdomains per socket
        # reads /sys/class/powercap/intel-rapl:{socket}:{sub}/name
        # and /energy_uj counter
```

This is production-grade equivalent of what Scaphandre does — reads the same RAPL `energy_uj` counters. The key difference is the Sideloader calculates **power = delta_energy / 1_000_000** (since interval is 1s, delta_uj directly gives watts).

**iDRAC integration:** Queries `https://{idrac_ip}/redfish/v1/Chassis/System.Embedded.1/Power` for `PowerConsumedWatts` (current, min, max, avg). This gives true AC input power — what we've been calling "the missing gap" between RAPL and actual system power.

**Aggregation:** Computes `total_cpu_dram_watts` (sum of RAPL domains) and, if iDRAC is available, `other_components_watts = system_power - cpu_dram_power` — this "other" category is exactly what would include fans, storage, NIC, and (if it were an O-RU) the PA/RF chain.

### 3.3 Process (`collectors/process.py`, 269 lines)

| Class | Purpose | Tool |
|-------|---------|------|
| `ThreadCPUCollector` | Per-thread CPU + core affinity tracking for `nr-softmodem` | `pidstat -t -p {pid} 1 1` via nsenter |
| `ProcessAffinityCollector` | RT priority + taskset affinity | `taskset -cp`, `chrt -p`, `ps -eLo` |
| `PerfContextSwitchCollector` | Context switch measurement | `perf stat -e context-switches` |
| `SchedLatencyCollector` | Scheduler latency profiling | `perf sched record` + `perf sched latency` |

**Thread discovery:** Auto-discovers the target PID via `pgrep nr-softmodem` (the OAI gNB binary). Tracks per-thread:
- CPU utilisation percentage
- Which core each thread is running on (PSR column from `pidstat`)
- Core distribution histogram after aggregation (how often a thread ran on each core)

This is critical for O-RAN because `nr-softmodem` runs timing-sensitive L1/L2 threads that must stay on isolated RT cores. The `primary_core` field in the output shows which core each thread predominantly runs on.

### 3.4 Memory (`collectors/memory.py`, 245 lines)

| Class | Purpose |
|-------|---------|
| `MemoryCollector` | System RAM: total/free/available/buffers/cached/slab/used |
| `HugepagesCollector` | Per-size hugepage tracking (auto-discovers 2MB and 1G hugepage pools) |
| `OOMCollector` | Static check of `dmesg` for OOM kill events |

**Hugepage discovery:** Enumerates `/sys/kernel/mm/hugepages/hugepages-{size}kB/` and tracks `nr_hugepages`, `free_hugepages`, `resv_hugepages`, `surplus_hugepages` per size. This is critical because OAI/srsRAN require pre-allocated 1G hugepages for DPDK and L1 processing.

### 3.5 Network (`collectors/network.py`, 211 lines)

Monitors all interfaces via `/sys/class/net/{iface}/statistics/` with delta-based rate calculations (bytes→Mbps, packets/s). Key features:
- **SR-IOV VF detection** — scans for `/sys/class/net/{iface}/device/virtfn*` and reads per-VF statistics
- **DPDK device detection** — enumerates VFIO-PCI bound devices via `/sys/bus/pci/drivers/vfio-pci/*`
- Auto-discovers interfaces via `ip link show`

### 3.6 PTP (`collectors/ptp.py`, ~76 lines)

Minimal collector that reads PTP clock offset from a sysfs counter. Full PTP monitoring logic is in `actions/ptp_actions.py` instead (see §4.2).

---

## 4. Fault Injection Modules (`actions/`)

### 4.1 Network Faults (`network_actions.py`, 184 lines)

| Class | Action | Method |
|-------|--------|--------|
| `VLANFaultInjector` | Swap VLAN ID to random value → all traffic drops | `ip link delete` old VLAN + `ip link add` new VLAN |
| `LinkDownInjector` | Bring interface down for N seconds | `ip link set {iface} down && sleep N && ip link set {iface} up` |

**VLAN fault injection flow:**
1. Reads MAC + discovers current VLAN ID
2. Generates random VLAN (100–4094, excluding current)
3. Deletes old VLAN sub-interface, creates new one with wrong ID
4. Waits `duration` seconds
5. Restores original VLAN configuration
6. Has both sync (`inject_vlan_fault`) and async (`inject_vlan_fault_async` via threading) variants

**Purpose:** Tests O-RAN fronthaul resilience — when the O-DU↔O-RU VLAN is disrupted, the gNB should detect the loss and either fail gracefully or recover when the fault clears.

### 4.2 PTP Faults (`ptp_actions.py`, 232 lines)

| Method | Purpose |
|--------|---------|
| `get_time_properties()` | Query IEEE 1588 `TIME_PROPERTIES_DATA_SET` (UTC offset, leap seconds) |
| `get_current_data_set()` | Query `offsetFromMaster` (ns) + mean path delay |
| `get_parent_data_set()` | Query grandmaster identity + clock class + accuracy |
| `monitor_offset(duration)` | Collect PTP offset time-series for analysis |
| `inject_ptp_fault(duration)` | Stop `ptp4l` service → simulate grandmaster loss |
| `comprehensive_check()` | Combined health check with sync quality rating |

All PTP queries use the `pmc` (PTP Management Client) tool via nsenter. The `comprehensive_check()` combines all datasets and rates sync quality:

| |offsetFromMaster|| Quality |
|---|---|
| < 100 ns | EXCELLENT |
| < 1 µs | GOOD |
| < 10 µs | ACCEPTABLE |
| ≥ 10 µs | POOR |

**TEEP relevance:** PTP synchronization is critical for O-RAN FH 7.2 fronthaul timing (T1a/T2a timing windows). The fault injection allows testing what happens to gNB stability when the timing reference is lost — directly relevant to Cell DTX/DRX implementations that require precise slot-level timing.

### 4.3 Stress Tests (`stress.py`, 154 lines)

| Class | Stressors |
|-------|-----------|
| `MemoryStressInjector` | VM allocation stress, page fault flooding, hugepage stress, near-OOM trigger |
| `CPUStressInjector` | CPU core stress (configurable load %), cache stress |

All commands use `stress-ng` via nsenter, running in background (`&`). Includes monitoring (`check_stress_processes`) and cleanup (`kill_all_stress`). The OOM trigger calculates target allocation from `/proc/meminfo` to reliably push the system to a configurable memory pressure percentage.

---

## 5. Architecture Summary

```
┌───────────────────────────────────────────────────────┐
│                 Sideloader Service                     │
│                   (Flask, port 8080)                   │
├─────────────────────┬─────────────────────────────────┤
│  COLLECTORS         │  ACTIONS                        │
│  (time-series)      │  (one-shot / background)        │
│                     │                                 │
│  BaseCollector      │  VLANFaultInjector              │
│    ├── CPU          │  LinkDownInjector               │
│    ├── Power (RAPL) │  PTPTester                      │
│    ├── Memory       │  MemoryStressInjector           │
│    ├── Hugepages    │  CPUStressInjector              │
│    ├── Network      │                                 │
│    ├── Disk         │                                 │
│    ├── PTP          │                                 │
│    └── Process      │                                 │
│       (nr-softmodem │                                 │
│        threads)     │                                 │
├─────────────────────┴─────────────────────────────────┤
│  HOST ACCESS: nsenter -t 1 -m -u -n -i               │
│  PRIVILEGES: hostPID + hostNetwork + privileged       │
│  SELF-REGISTRATION: POST /sideload/register → rApp   │
└───────────────────────────────────────────────────────┘
```

---

## 6. Connection to Our TEEP Work

| Sideloader Feature | Our TEEP Equivalent | Insight |
|---|---|---|
| `PowerCollector` RAPL reading | Scaphandre `/metrics` | Identical data source (`energy_uj`); Sideloader calculates power inline, Scaphandre uses Prometheus export |
| `PowerCollector` iDRAC/Redfish | (not available on our laptop testbed) | This fills the "gap" — system-level power includes PSU/fans/NIC = the "other_components_watts" field |
| `ThreadCPUCollector` for `nr-softmodem` | (not yet deployed) | When we deploy OAI on K8s, this is how we track which L1/L2 threads consume the most CPU |
| VLAN/PTP fault injection | (not yet attempted) | Stage 2 opportunity: test gNB resilience to fronthaul faults and correlate with power behavior |
| `HugepagesCollector` | (not yet monitored) | Critical for Stage 2: hugepage exhaustion directly impacts gNB L1 processing |
| 1 Hz `BaseCollector` cadence | Scaphandre 1s scrape interval | Both systems use 1 Hz — validating that this is the standard monitoring cadence for O-RAN telemetry |
