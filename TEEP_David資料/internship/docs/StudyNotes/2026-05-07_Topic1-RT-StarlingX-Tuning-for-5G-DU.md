# Topic 1: Real-Time StarlingX Tuning for 5G DU (2026-05-07)

Status: Ready
Parent: [Research Continuation Plan](./2026-05-07_Research-Continuation-Plan-RT-Tuning-and-Measurement.md)

## Executive Summary

This note consolidates the concrete technical knowledge needed to configure a StarlingX (or bare-metal Ubuntu RT) platform to run a 5G Distributed Unit (DU) workload with minimal latency jitter and predictable power behavior. It answers the five key questions from the research plan and provides actionable checklists, commands, and configuration snippets sourced from StarlingX documentation, srsRAN/OAI community guides, Linux kernel docs, and O-RAN timing specifications.

---

## 1. O-RAN Fronthaul Timing Requirements

### 1.1 Latency Budget

**Fact (O-RAN WG4):** The O-RAN Alliance targets a maximum one-way fronthaul latency of **~100 µs** between O-DU and O-RU. This budget includes:
- Propagation delay (fiber)
- Switching delay (transport nodes, ideally 1–2 hops)
- Processing delay at both O-DU and O-RU ends

**Fact:** The system uses Transmit Windows and Receive Windows to ensure C-Plane (control) and U-Plane (user data) messages are exchanged within strict time bounds. Reference points T1a, T2a are used to manage these delays.

### 1.2 Synchronization Requirements

| Requirement | Value | Context |
|:---|:---|:---|
| Absolute time error | ±1.5 µs | Standard 5G TDD operations |
| Relative time error | <1 µs | Advanced coordination (CoMP) |
| Sync mechanism | PTP (IEEE 1588v2) + SyncE | LLS-C1 through LLS-C4 configs |

### 1.3 Slot Deadline

**Fact (5G NR):** For SCS=30 kHz (common for n78), slot duration = 0.5 ms. The O-DU must complete L1/L2 processing and deliver fronthaul data within this window. **This is the hard real-time deadline that motivates all tuning below.**

### 1.4 Factors Affecting Timing

- **Numerology:** Higher SCS → shorter slot → tighter deadline.
- **Split 7.2x:** Moves some PHY to O-RU, reducing fronthaul bandwidth but making timing more sensitive.
- **Ethernet PDV:** Time-Sensitive Networking (IEEE 802.1Qbv) may be needed to ensure deterministic fronthaul performance.

---

## 2. CPU Isolation & DPDK/NUMA

### 2.1 CPU Isolation via Kernel Boot Parameters

Add to `/etc/default/grub` → `GRUB_CMDLINE_LINUX_DEFAULT`:

```bash
# Example: isolate cores 2-7 for DU workload, keep 0-1 for OS
isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7
```

| Parameter | Purpose |
|:---|:---|
| `isolcpus=2-7` | Remove cores 2–7 from the general SMP load balancer |
| `nohz_full=2-7` | Suppress scheduling-clock interrupts on these cores (tickless) |
| `rcu_nocbs=2-7` | Offload RCU callback processing to housekeeping cores (0–1) |

**Important:** Core 0 must NOT be isolated — the kernel needs it for system interrupts. After editing, run `sudo update-grub && reboot`.

### 2.2 cgroup v2 vs isolcpus

- `isolcpus` is the simplest and most widely documented approach for bare-metal RT workloads.
- `systemd-nspawn` + cgroup v2 provides finer-grained control in containerized environments but adds complexity.
- **Recommendation for initial setup:** Use `isolcpus` + `nohz_full`. Move to cgroup v2 only if running multiple containerized DU instances.

### 2.3 SR-IOV VF Queue Mapping

1. Enable **Intel VT-d** (IOMMU) in BIOS.
2. Create SR-IOV Virtual Functions:
   ```bash
   echo 1 | sudo tee /sys/class/net/<interface>/device/sriov_numvfs
   ```
3. Bind VF to DPDK-compatible driver:
   ```bash
   sudo dpdk-devbind.py --bind=vfio-pci <VF_PCI_ADDRESS>
   ```
4. Pin VF interrupt queues to isolated cores (same NUMA node):
   ```bash
   # Identify IRQ for VF
   cat /proc/interrupts | grep <VF_interface>
   # Set affinity to isolated cores
   echo <core_mask> > /proc/irq/<IRQ_NUMBER>/smp_affinity
   ```

### 2.4 NUMA Alignment

**Fact:** Cross-NUMA memory access adds 40–100 ns latency penalty. For 5G DU with 0.5 ms slot deadline, this matters.

**Checklist:**
- [ ] Identify NUMA topology: `lscpu | grep NUMA` or `numactl --hardware`
- [ ] Ensure NIC (fronthaul interface) is on same NUMA node as isolated cores: `cat /sys/class/net/<iface>/device/numa_node`
- [ ] Allocate hugepages on the correct NUMA node (see §4)
- [ ] Pin DU threads to cores on the same NUMA node as NIC

---

## 3. Kernel & Scheduler Tuning

### 3.1 PREEMPT_RT Kernel

**Fact:** The PREEMPT_RT patchset (mainline since kernel 6.12+) is the foundation for 5G DU real-time performance. It:
- Converts spinlocks to sleeping locks
- Makes interrupt handlers preemptible (threaded IRQs)
- Enables priority inheritance to solve priority inversion

**Installation (Ubuntu/Debian):**
```bash
sudo apt install linux-image-rt-amd64
# or for specific version:
sudo apt install linux-image-6.8.0-rt-amd64
```

**Verification:**
```bash
cat /sys/kernel/realtime   # Should return: 1
uname -a                   # Should show: PREEMPT_RT
```

### 3.2 RT vs Generic Kernel: Latency & Power

| Metric | Generic Kernel | PREEMPT_RT Kernel |
|:---|:---|:---|
| Worst-case latency (cyclictest) | 50–500+ µs | 5–20 µs |
| Average latency | ~5 µs | ~3 µs |
| Power overhead | Baseline | +2–5% (due to forced `performance` governor, disabled C-states) |
| Throughput | Higher peak | Slightly lower peak, much lower variance |

**Note:** The power cost of RT kernel is primarily from disabling power-saving states (C-states, P-states), not from the kernel itself. This is a conscious trade-off for the 0.5 ms deadline.

### 3.3 Scheduling Classes: CFS vs RT

| Thread Type | Recommended Class | Priority | Rationale |
|:---|:---|:---|:---|
| L1 PHY (timing-critical) | `SCHED_FIFO` | 90–98 | Hard real-time deadline |
| MAC/L2 scheduler | `SCHED_FIFO` | 80–89 | Soft real-time, slot-aligned |
| RLC/PDCP (best-effort) | `SCHED_OTHER` (CFS) | nice 0 | Tolerant of jitter |
| System services | `SCHED_OTHER` (CFS) | nice 10+ | Lowest priority |

Set thread priority with:
```bash
chrt -p -f <priority> <PID>
```

### 3.4 IRQ Affinity Strategy

**Recommendation:** O-RU fronthaul interrupts should live on **separate housekeeping cores**, not on the isolated DU processing cores. This prevents interrupt-induced jitter on the critical path.

```bash
# 1. Disable irqbalance (it conflicts with manual affinity)
sudo systemctl stop irqbalance
sudo systemctl disable irqbalance

# 2. Identify fronthaul NIC IRQs
cat /proc/interrupts | grep <fronthaul_iface>

# 3. Route to housekeeping cores (e.g., core 0-1)
for irq in $(grep <fronthaul_iface> /proc/interrupts | awk '{print $1}' | tr -d ':'); do
    echo 0-1 > /proc/irq/$irq/smp_affinity_list
done
```

**Exception:** If using DPDK for fronthaul (kernel bypass), IRQs are irrelevant for data-plane packets — DPDK polls the NIC directly.

---

## 4. Memory & Huge Pages

### 4.1 Why Huge Pages Matter

**Fact:** Standard 4 KB pages cause frequent TLB (Translation Lookaside Buffer) misses during DU processing. Each TLB miss adds ~10–100 ns of latency variance. Huge pages (2 MB or 1 GB) dramatically reduce TLB pressure.

### 4.2 Allocation

**Boot-time allocation (recommended for 1 GB pages):**
Add to GRUB:
```bash
hugepagesz=1G hugepages=4 default_hugepagesz=1G
```

**Runtime allocation (2 MB pages):**
```bash
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

### 4.3 NUMA-Pinned Hugepages

```bash
# Allocate 2 x 1GB hugepages on NUMA node 0
echo 2 > /sys/devices/system/node/node0/hugepages/hugepages-1048576kB/nr_hugepages
```

### 4.4 Mount hugetlbfs

```bash
mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
# Add to /etc/fstab for persistence:
# nodev /mnt/huge hugetlbfs pagesize=1G 0 0
```

### 4.5 Trade-off

| Factor | Small Pages (4 KB) | Huge Pages (2 MB / 1 GB) |
|:---|:---|:---|
| TLB misses | High | Very low |
| Memory fragmentation | Low | Higher (especially 1 GB) |
| Allocation flexibility | Fine-grained | Coarse |
| **Recommendation for DU** | ❌ | ✅ Use 1 GB for DPDK, 2 MB for general DU buffers |

---

## 5. StarlingX-Specific Settings

### 5.1 RT Kernel in StarlingX

**Fact (StarlingX docs):** StarlingX provides a built-in "Low Latency" worker function performance profile with a pre-configured RT kernel.

- Always deploy the **RT kernel variant** for vRAN workloads.
- Verify: `uname -ri` should show `realtime`.
- The StarlingX RT kernel supports deterministic interrupt handling with latencies often **below 20 µs**.

### 5.2 Kubernetes CPU Manager

**Fact:** StarlingX uses Kubernetes CPU Manager in `static` mode to provide exclusive CPU allocation to pods.

```yaml
# In kubelet config (StarlingX manages this):
cpuManagerPolicy: static
```

- Pods requesting integer CPU values (e.g., `cpu: "4"`) get **exclusive, pinned cores**.
- Pods with fractional requests share a "shared pool" of non-isolated cores.

### 5.3 Topology Manager

**Fact (StarlingX docs):** Recommended policy is `best-effort`.

| Policy | Behavior | Risk |
|:---|:---|:---|
| `none` | No alignment enforcement | Poor NUMA performance |
| `best-effort` | **Attempts NUMA alignment, no hard failure** | Best balance ✅ |
| `restricted` | Enforces alignment, fails if impossible | Pod scheduling failures |
| `single-numa-node` | Strictest, all resources on one NUMA | Highest failure rate |

```yaml
# StarlingX topology manager setting:
topologyManagerPolicy: best-effort
```

### 5.4 Intel vRAN Boost (if applicable)

StarlingX provides a **Kubernetes Operator for Intel vRAN Boost** on 4th Gen Xeon:
- Detects and labels worker nodes with accelerators
- Configures Virtual Functions for the accelerator
- Manages VFs as Kubernetes resources

### 5.5 Power Management in StarlingX

- Disable C-states (C3/C4) on isolated cores to prevent latency spikes.
- Set CPU governor to `performance` globally.
- Ensure PTP/GNSS synchronization via `ptp4l` / `phc2sys`.

### 5.6 StarlingX vRAN Tuning Summary

| Component | Setting | Value |
|:---|:---|:---|
| Kernel | RT Kernel | `uname -ri` → `realtime` |
| CPU Manager | Policy | `static` |
| Topology Manager | Policy | `best-effort` |
| CPU Governor | Mode | `performance` |
| C-states | Disabled on isolated cores | via kernel params |
| Sync | PTP | `ptp4l` + `phc2sys` |
| Acceleration | vRAN Boost Operator | If 4th Gen Xeon |

---

## 6. srsRAN-Specific RT Configuration

### 6.1 Performance Script

srsRAN provides a built-in script:
```bash
sudo ./scripts/srsran_performance
```
This handles: CPU governor, DRM KMS polling, network buffer tuning.

### 6.2 Thread Affinity in gnb.yaml

```yaml
expert_execution:
  affinities:
    l1_dl_cpus: 2,3       # L1 downlink on isolated cores
    l1_ul_cpus: 4,5       # L1 uplink on isolated cores
    l2_cell_cpus: 6,7     # MAC/scheduler
    ru_cpus: 10,11,12,13  # Radio Unit interface
  l1_dl_pinning: mask
```

### 6.3 Additional Kernel Parameters for srsRAN

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="isolcpus=2-13 nohz_full=2-13 rcu_nocbs=2-13 intel_pstate=disable hugepages=4 hugepagesz=1G"
```

### 6.4 USRP-Specific (if using SDR)

- Calibrate USRP timing per srsRAN docs.
- Use `uhd_usrp_probe` to verify device detection.
- Set appropriate `tx_gain` and `rx_gain` in config.

---

## 7. OAI-Specific RT Configuration

### 7.1 Thread Pool Allocation

```bash
sudo ./nr-softmodem --thread-pool 2,3,4,5,6,7,8,9 ...
```
Minimum 8 CPUs recommended for optimal performance.

### 7.2 DPDK for O-RAN 7.2 Fronthaul

OAI uses the `xran` library which requires DPDK:
- Bind NICs to `vfio-pci` driver
- Requires `IPC_LOCK`, `SYS_RESOURCE`, `NET_RAW` capabilities
- Pin `ru_thread`, `L1_rx`/`tx_threads` to isolated cores on same NUMA socket

### 7.3 Ethernet Tuning

```bash
# Increase ring buffers
sudo ethtool -G <ifname> rx 4096 tx 4096

# Increase kernel socket buffers
sudo sysctl -w net.core.wmem_max=62500000
sudo sysctl -w net.core.rmem_max=62500000
sudo sysctl -w net.core.wmem_default=62500000
sudo sysctl -w net.core.rmem_default=62500000
```

---

## 8. Benchmarking & Validation

### 8.1 Latency Validation with cyclictest

```bash
# Install rt-tests
sudo apt install rt-tests

# Run cyclictest on isolated cores under load
sudo cyclictest -t4 -p 98 -m -a 2-5 -D 10m --histogram=100
```

**Target:** Worst-case latency < 20 µs (for 0.5 ms slot deadline, this gives 96% margin).

### 8.2 rtla timerlat (Kernel 5.18+)

```bash
sudo rtla timerlat top -c 2-5 -d 10m
```
Provides per-core latency breakdown and identifies root causes of spikes.

### 8.3 Power Impact of RT Tuning

Use RAPL to compare RT vs generic kernel power:
```bash
# Read package energy counter
cat /sys/class/powercap/intel-rapl:0/energy_uj
# Compare over a fixed workload duration
```

### 8.4 Throughput Stability

```bash
# Run iperf3 for 5 minutes, report every 1 second
iperf3 -c <UE_IP> -t 300 -i 1 --json > iperf_results.json
```

Measure: mean throughput, standard deviation, min/max. RT tuning should **reduce variance** even if it slightly reduces peak.

---

## 9. Complete Tuning Checklist

### BIOS Settings
- [ ] Enable Intel VT-d (IOMMU)
- [ ] Disable Hyper-Threading (SMT)
- [ ] Set high-performance power profile
- [ ] Disable C-states (C3, C6, C7)
- [ ] Disable Intel SpeedStep / P-states
- [ ] Ensure NIC is on correct NUMA node's PCIe slot

### OS / Kernel
- [ ] Install PREEMPT_RT kernel
- [ ] Set GRUB: `isolcpus`, `nohz_full`, `rcu_nocbs`, `intel_pstate=disable`
- [ ] Set GRUB: `hugepagesz=1G hugepages=4`
- [ ] Disable `irqbalance`
- [ ] Set CPU governor to `performance`
- [ ] Mount hugetlbfs
- [ ] Disable security mitigations if lab-only: `mitigations=off` (⚠️ security risk)

### Network
- [ ] Configure SR-IOV VFs (if applicable)
- [ ] Bind to DPDK driver (`vfio-pci`)
- [ ] Set IRQ affinity for fronthaul NIC
- [ ] Increase ring buffers and socket buffers
- [ ] Configure PTP synchronization (`ptp4l` + `phc2sys`)

### Application (srsRAN / OAI)
- [ ] Pin L1/L2/RU threads to isolated cores
- [ ] Run with `sudo` for RT scheduling privileges
- [ ] Configure thread priorities (`SCHED_FIFO`)
- [ ] Validate with `cyclictest` before DU workload

### StarlingX (if applicable)
- [ ] Deploy RT kernel variant
- [ ] Set CPU Manager to `static`
- [ ] Set Topology Manager to `best-effort`
- [ ] Configure vRAN Boost operator (if 4th Gen Xeon)
- [ ] Disable C-states on worker nodes

### Validation
- [ ] `cyclictest` worst-case < 20 µs
- [ ] `uname -a` shows PREEMPT_RT
- [ ] `/sys/kernel/realtime` returns 1
- [ ] NUMA alignment verified for NIC + cores + hugepages
- [ ] iperf3 throughput variance acceptable
- [ ] RAPL power delta documented (RT vs generic)

---

## 10. References

### Primary Sources (Fetched)
1. **Linux PREEMPT_RT documentation** — [realtime-linux.org](https://wiki.linuxfoundation.org/realtime/start), kernel.org
2. **StarlingX vRAN configuration** — [docs.starlingx.io](https://docs.starlingx.io/), O-RAN SC documentation
3. **srsRAN performance tuning** — [docs.srsran.com/troubleshooting](https://docs.srsran.com/projects/project/en/latest/user_manuals/source/troubleshooting.html)
4. **OAI ORAN_FHI7.2_Tutorial** — [gitlab.eurecom.fr/oai](https://gitlab.eurecom.fr/oai/openairinterface5G)
5. **O-RAN WG4 fronthaul timing** — O-RAN Alliance specifications, Juniper/Telnet Networks summaries
6. **DPDK documentation** — [doc.dpdk.org](https://doc.dpdk.org/)
7. **Intel RAPL** — Intel SDM Volume 3, kernel powercap interface

### From Our Study Notes
- [2026-04-28_Guided-StarlingX-Deployment-Issues.md](./2026-04-28_Guided-StarlingX-Deployment-Issues.md) — Current StarlingX deployment blockers
- [2026-02-03_srsRAN-Scheduler-Deep-Dive.md](./2026-02-03_srsRAN-Scheduler-Deep-Dive.md) — Scheduler architecture
- [2026-02-27_srsRAN-Config-Walkthrough-273-vs-27-Demo.md](./2026-02-27_srsRAN-Config-Walkthrough-273-vs-27-Demo.md) — srsRAN config reference

---

## Notes & Assumptions

**Fact:** PREEMPT_RT is mainline since kernel 6.12+ (Dec 2024).

**Fact:** StarlingX provides built-in "Low Latency" profile with RT kernel support.

**Fact:** srsRAN provides `expert_execution.affinities` YAML config for thread pinning.

**Fact:** O-RAN fronthaul timing budget is ~100 µs one-way; slot deadline for SCS=30 kHz is 0.5 ms.

**Assumption:** Our testbed has Intel CPUs with RAPL support and NICs with SR-IOV capability.

**Assumption:** Initial validation will use ZMQ (no physical radio), so fronthaul timing is relaxed but we still want RT tuning validated via cyclictest.

**Open question:** Exact CPU model and NUMA topology of our target server — needed to finalize core allocation plan.

**Open question:** Whether StarlingX AIO-Simplex supports the "Low Latency" worker profile or if it requires a multi-node deployment.
