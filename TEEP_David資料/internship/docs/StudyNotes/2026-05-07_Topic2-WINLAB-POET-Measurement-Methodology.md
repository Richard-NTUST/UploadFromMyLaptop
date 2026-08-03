# Topic 2: WINLAB/POET Measurement Methodology (2026-05-07)

Status: Ready
Parent: [Research Continuation Plan](./2026-05-07_Research-Continuation-Plan-RT-Tuning-and-Measurement.md)

## Executive Summary

This note maps the POET paper's measurement methodology to our local testbed, answering the five key questions from the research plan. It covers ground-truth selection, tool comparison (PDU vs IPMI vs RAPL/Scaphandre), load definition, sampling cadence, KPI alignment, and validation checks. All sourced from the POET paper (IEEE VTC2024-Fall, DOI: 10.1109/VTC2024-Fall63153.2024.10757537), WINLAB RCR articles, and tool documentation.

---

## 1. Ground Truth & Tool Comparison

### 1.1 Measurement Tools in POET

| Tool | Measurement Point | Scope | Cadence | Accuracy |
|:---|:---|:---|:---|:---|
| **Smart PDU** (Server Tech PRO3X, STV-6521V) | AC outlet | Whole-system (per component) | ~10–15 s query | **Ground truth** ✅ |
| **IPMI** (via BMC) | DC (PSU output) | Whole-server | ~1 s sampling, ~60 s stabilization | Coarse, quantized steps |
| **Scaphandre** (RAPL) | CPU package registers | CPU + DRAM only | ~1 s (configurable) | Model-based estimate |
| **Kepler** (RAPL + cgroups) | CPU + container attribution | Per-pod/container | ~1 s | Model-based, container-aware |
| **nvidia-smi** | GPU power sensor | GPU only | ~1 s | Direct sensor reading |

### 1.2 Which Is Ground Truth?

**Fact (POET paper):** Smart PDU is the primary ground truth for total power consumption. PDU monitors power supplied directly to Physical Network Functions (PNFs) and servers.

**Fact (POET paper):** IPMI tracks similarly to PDU but shows:
- Longer averaging (~60 s to stabilize)
- Lower reported power (~10 W lower on average in one characterization)
- Quantized steps (coarser granularity)

**For our testbed:** Choose the measurement point that matches available hardware:

| If you have... | Ground truth | Complement with |
|:---|:---|:---|
| Smart PDU | PDU (AC) | IPMI + Scaphandre |
| No PDU, IPMI available | IPMI (DC proxy) | Scaphandre for process-level |
| Neither (laptop/VM) | Scaphandre (RAPL) | Calibrate against kill-a-watt or similar |

### 1.3 Expected Offsets Between Tools

| Comparison | Expected Offset | Cause |
|:---|:---|:---|
| PDU vs IPMI | IPMI ~10 W lower | IPMI measures DC post-PSU; PDU measures AC pre-PSU (includes PSU losses) |
| RAPL vs PDU | RAPL much lower | RAPL only covers CPU+DRAM, not fans/disks/NIC/motherboard |
| RAPL vs IPMI | Constant offset | Missing components (fans, chipset, storage) |

### 1.4 Timestamp Alignment Across Sources

**Problem:** PDU, IPMI, and software tools have different clocks and polling intervals.

**Solution (from POET + best practices):**

1. **Standardize to UTC** — all systems must log in UTC (not local time).
2. **NTP sync** — sufficient for ms-level alignment (adequate for 10 s PDU cadence).
3. **PTP sync** — needed only if sub-µs alignment required (fronthaul, not power).
4. **UTC anchor markers** — at start/end of each run, log a marker:
   ```bash
   echo "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) RUN_START run_id=001" >> utc_markers.txt
   ```
5. **Prometheus timestamps** — all exporters should use Prometheus server time (single clock).

---

## 2. Load Definition & Reproducibility

### 2.1 How WINLAB Defines "Load"

**Fact (POET paper):** Load is defined by two coupled metrics:

| Metric | 1 UE Scenario | 2 UE Scenario |
|:---|:---|:---|
| DU PRB Load | **70%** | **100%** |
| Aggregate DU DL Throughput | **65 Mb/s** | **84 Mb/s** (42/UE) |

**Fact:** Test was all-OAI bare-metal (rfsim) with iPerf traffic.

### 2.2 Load Metrics Hierarchy

For reproducibility, define load at multiple levels:

```
Level 1: Traffic generator → iPerf target bitrate (Mb/s)
Level 2: Scheduler output → PRB utilization (%)
Level 3: Radio config → MCS, #layers, bandwidth
Level 4: Observed → Throughput (iperf3 measured)
```

**Minimum for replication:** Report Level 1 (iPerf target) + Level 2 (PRB %) + Level 4 (measured throughput). These three together make a defensible load definition.

### 2.3 Reproducing WINLAB Scenarios Locally

```bash
# Scenario 1: 1 UE, target 70% PRB load
iperf3 -c <DU_IP> -b 65M -t 300 -i 1 --json > run_1ue_70pct.json

# Scenario 2: 2 UEs, target 100% PRB load
# Terminal 1:
iperf3 -c <DU_IP> -b 42M -t 300 -i 1 --json > run_2ue_a.json
# Terminal 2:
iperf3 -c <DU_IP> -b 42M -t 300 -i 1 --json > run_2ue_b.json
```

### 2.4 Ensuring Repeatability

| Parameter | Frozen Value | Rationale |
|:---|:---|:---|
| Warm-up duration | **2 min** | From our Boundaries.md (2026-01-13) |
| Steady-state duration | **5 min** | From our Boundaries.md |
| Traffic pattern | Constant bitrate (CBR) | Simplest to reproduce |
| Number of runs | ≥3 per scenario | For mean/variance calculation |
| Ambient conditions | Log room temp | Fans/cooling affect power |

---

## 3. Sampling & Cadence

### 3.1 POET Cadences

| Source | Polling Interval | Stabilization Time | Notes |
|:---|:---|:---|:---|
| PDU (SNMP) | ~10–15 s | Near-instant | Ground truth cadence |
| IPMI | ~1 s raw | ~60 s to stabilize | Longer averaging window in BMC |
| Scaphandre | 1–10 s (configurable) | <1 s | Reads RAPL MSRs |
| Kepler | ~15 s (Prometheus default) | <1 s | Kubernetes-native |

### 3.2 What Cadence Do We Need?

| Phenomenon | Required Cadence | Tool |
|:---|:---|:---|
| Steady-state power (Fig. 4–7 replication) | 10–15 s | PDU or IPMI |
| Transient power (load step response) | 1 s | Scaphandre / RAPL direct |
| RU sleep mode transitions | **100 ms – 1 s** | Custom RAPL reader or hardware power analyzer |
| Slot-level power variation | ~0.5 ms | **Not feasible with PDU/IPMI** — need oscilloscope |

**For initial replication:** 10 s PDU + 1 s Scaphandre is sufficient to reproduce POET Fig. 4–7.

### 3.3 Clock Skew Handling

- Use a single Prometheus server as the timestamp authority.
- If multiple machines: ensure NTP offset < 50 ms (check with `ntpq -p`).
- For post-hoc alignment: use cross-correlation of load-step edges in power traces.

---

## 4. KPI Alignment & Timestamps

### 4.1 Synchronizing DU KPIs with Power

**Problem:** DU metrics (throughput, PRB, latency) come from the application; power comes from external instruments. They must be time-aligned.

**Architecture:**

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  DU (srsRAN/ │    │  Scaphandre  │    │   PDU/IPMI   │
│  OAI) KPIs   │    │  (RAPL)      │    │  (SNMP)      │
│  → JSON/CSV  │    │  → Prometheus│    │  → Prometheus│
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └──────────┬────────┘───────────────────┘
                  ▼
           ┌──────────────┐
           │  Prometheus   │  ← single timestamp authority
           │  (scrape all) │
           └──────┬───────┘
                  ▼
           ┌──────────────┐
           │   Grafana     │  ← visualization + correlation
           └──────────────┘
```

### 4.2 Key "Events" to Label

| Event | How to Detect | Label |
|:---|:---|:---|
| Run start/end | UTC marker file | `state=idle→active` |
| Load step change | iPerf start/stop | `load=0%→70%→100%` |
| UE attach/detach | DU log / RRC event | `ues=0→1→2` |
| HARQ retransmissions | MAC metrics | `harq_retx_rate` |
| RU state transition | RU telemetry (if available) | `ru_state=active→sleep` |

### 4.3 Creating a Labeled Power Trace

```python
# Post-processing script (conceptual)
import pandas as pd

power = pd.read_csv("prometheus_power_export.csv", parse_dates=["timestamp"])
events = pd.read_csv("utc_markers.txt", parse_dates=["timestamp"])

# Merge events into power trace
labeled = pd.merge_asof(power.sort_values("timestamp"),
                         events.sort_values("timestamp"),
                         on="timestamp", direction="backward")

labeled.to_csv("power_labeled.csv", index=False)
# Columns: timestamp, power_w, state, load_pct, ue_count, notes
```

### 4.4 srsRAN JSON Metrics for KPI Export

srsRAN exports real-time metrics via JSON:
- **MAC metrics:** UE throughput, HARQ stats
- **Scheduler cell metrics:** PRB utilization, MCS distribution
- **OFH metrics:** Open Fronthaul latency (if applicable)

Configure in `gnb.yaml`:
```yaml
metrics:
  enable_json_metrics: true
  addr: 0.0.0.0
  port: 55555
```

Scrape with Prometheus via a custom exporter or direct JSON parsing.

---

## 5. Validation & Plausibility Checks

### 5.1 Power Plausibility Against RU Model

**From our EARTH power model note (2026-02-23):**

$$P_{total} = P_0 + \Delta_P \times L$$

Where:
- $P_0$ = idle/baseline power (W)
- $\Delta_P$ = load-dependent power slope (W per unit load)
- $L$ = load fraction (0 to 1, where 1 = 100% PRB)

**Check:** After collecting power at 0%, 70%, and 100% load, fit a linear model. If R² < 0.9, investigate measurement artifacts.

**WINLAB anchor:** Medium-power O-RU at ~59 W at active-idle (0% utilization).

### 5.2 Throughput Plausibility Against TBS

**From our TBS equivalence note (2026-02-26):**

For 273 PRBs (100 MHz BW), SCS 30 kHz, 64-QAM, 1 layer:
- Expected max TBS per slot ≈ specific value from calculator
- With 70% PRB load → proportional reduction

**Check:** If measured throughput deviates >10% from TBS expectation, investigate scheduler config or measurement error.

### 5.3 PDU vs IPMI Agreement

**Tolerance:** ±10 W is acceptable based on POET characterization.

**Red flags:**
- IPMI consistently >PDU → impossible (PSU losses mean PDU ≥ IPMI always)
- Offset >30 W → check PSU efficiency, fan power, or instrument calibration
- IPMI oscillating wildly → BMC averaging issue, increase observation window

### 5.4 Statistical Rigor Checklist

| Check | Method | Minimum |
|:---|:---|:---|
| Central tendency | Mean AND median | Report both |
| Variability | Standard deviation + IQR | Must report |
| Confidence | 95% CI on mean | ≥3 runs per scenario |
| Outliers | IQR method (1.5×IQR) | Flag, don't silently remove |
| Steady-state verification | Trim first 2 min (warm-up) | Visual + statistical |

---

## 6. Measurement Pipeline Setup

### 6.1 Prometheus + Grafana Stack

```bash
# Docker-compose for measurement stack
docker compose up -d prometheus grafana

# Prometheus targets (prometheus.yml):
scrape_configs:
  - job_name: 'scaphandre'
    static_configs:
      - targets: ['<DU_HOST>:8080']
    scrape_interval: 5s

  - job_name: 'ipmi'
    static_configs:
      - targets: ['<IPMI_EXPORTER>:9290']
    scrape_interval: 15s

  - job_name: 'snmp_pdu'
    static_configs:
      - targets: ['<PDU_IP>']
    scrape_interval: 15s
    metrics_path: /snmp
    params:
      module: [servertech]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - target_label: __address__
        replacement: <SNMP_EXPORTER>:9116
```

### 6.2 Scaphandre Deployment

```bash
# Bare-metal (DaemonSet or direct)
docker run -d --name scaphandre \
  -v /sys/class/powercap:/sys/class/powercap:ro \
  -v /proc:/proc:ro \
  -p 8080:8080 \
  hubblo/scaphandre prometheus

# Verify RAPL is accessible
ls /sys/class/powercap/intel-rapl:0/energy_uj
```

**Prerequisites:**
- Intel/AMD CPU with RAPL support
- `intel_rapl_common` kernel module loaded: `sudo modprobe intel_rapl_common`
- Access to `/sys/class/powercap` and `/proc`

**Key metrics exported:**
- `scaph_host_power_microwatts` — total host power
- `scaph_process_power_consumption_microwatts` — per-process (container-attributed with `--containers`)

### 6.3 IPMI Exporter

```bash
# Using ipmi_exporter
docker run -d --name ipmi-exporter \
  -p 9290:9290 \
  prometheuscommunity/ipmi-exporter

# Or direct ipmitool query:
ipmitool -I lanplus -H <BMC_IP> -U admin -P <pass> dcmi power reading
```

### 6.4 RAPL Security Caveat

**Warning (CVE-2020-8694/5):** Recent Intel microcode updates add noise to RAPL readings to mitigate power side-channel attacks (PLATYPUS). This can reduce accuracy and increase variance. Check:

```bash
# Verify if mitigation is active
dmesg | grep -i rapl
# If active, RAPL readings may have +/- noise added
```

For lab environments, this mitigation can be disabled, but document the decision.

---

## 7. POET Replication Plan (Step-by-Step)

### Phase 1: Measurement Stack Validation (No RAN, just server)

1. Deploy Prometheus + Grafana + Scaphandre
2. Run CPU stress test (`stress-ng --cpu 4 --timeout 300`)
3. Verify Scaphandre tracks power increase
4. Compare with IPMI reading (if available)
5. **Deliverable:** Plot similar to POET Fig. 4 (power vs time, multiple sources)

### Phase 2: DU Workload with Power Measurement

1. Start srsRAN/OAI in ZMQ mode (from existing setup)
2. Attach UE emulator
3. Run iPerf at target bitrates (65 Mb/s, then 84 Mb/s)
4. Collect: power (Scaphandre), KPIs (srsRAN JSON), throughput (iperf3)
5. Align timestamps and label power trace
6. **Deliverable:** Labeled CSV + time-series plot (power + throughput overlay)

### Phase 3: Fig. 4–7 Replication

1. Reproduce measurement-tool comparison (PDU vs IPMI vs Scaphandre)
2. Show relative offsets and averaging behavior
3. Demonstrate KPI alignment (throughput annotated on power trace)
4. **Deliverable:** 4 plots matching POET Fig. 4–7 structure

### Phase 4: Load-Power Curve

1. Run at 0%, 25%, 50%, 70%, 100% PRB load
2. Record steady-state power at each point (5 min each, 3 runs)
3. Fit linear model: P = P₀ + ΔP × L
4. **Deliverable:** Load-power scatter plot with regression line

---

## 8. Data Format Specification

### 8.1 File Naming Convention

```
<date>_<scenario>_<tool>_<run>.csv
# Examples:
2026-05-15_1ue_70pct_scaphandre_run01.csv
2026-05-15_1ue_70pct_iperf3_run01.json
2026-05-15_1ue_70pct_utc_markers_run01.txt
```

### 8.2 CSV Schema (power_labeled.csv)

```csv
timestamp_utc,power_w,source,state,load_pct,ue_count,throughput_mbps,prb_util_pct,notes
2026-05-15T10:00:00.000Z,145.2,scaphandre,warmup,0,0,0,0,
2026-05-15T10:02:00.000Z,168.7,scaphandre,active,70,1,65.1,70.2,steady-state
```

### 8.3 UTC Markers File

```
2026-05-15T10:00:00.000Z RUN_START run_id=001 scenario=1ue_70pct
2026-05-15T10:02:00.000Z WARMUP_END
2026-05-15T10:07:00.000Z STEADY_END
2026-05-15T10:07:01.000Z RUN_STOP
```

---

## 9. References

### Primary
1. **POET paper:** Shankaranarayanan et al., "POET: A Platform for O-RAN Energy Efficiency Testing," IEEE VTC2024-Fall (RitiRAN), DOI: 10.1109/VTC2024-Fall63153.2024.10757537
2. **WINLAB RCR articles:** [2024-08-28](https://www.rcrwireless.com/20240828/5g/5g-energy-efficiency-metrics-models-and-system-tests-reader-forum), [2024-11-06](https://www.rcrwireless.com/20241106/open_ran/5g-energy-efficiency-o-ran)
3. **Scaphandre docs:** [hubblo-org.github.io/scaphandre](https://hubblo-org.github.io/scaphandre/)
4. **RAPL accuracy research:** TU Dresden, ResearchGate studies on RAPL offset calibration
5. **Prometheus/Grafana:** Community exporters (ipmi_exporter, snmp_exporter)

### From Our Study Notes
- [2026-01-12_WINLAB-Baseline.md](./2026-01-12_WINLAB-Baseline.md) — POET extraction and target plots
- [2026-01-13_Boundaries.md](./2026-01-13_Boundaries.md) — Frozen local decisions (warm-up, steady-state)
- [2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md](./2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md) — P = P₀ + ΔP × L model
- [2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md](./2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md) — Throughput validation
- [2026-01-14_Power-Estimator-Setup-Scaphandre.md](./2026-01-14_Power-Estimator-Setup-Scaphandre.md) — Earlier Scaphandre attempt
- [2026-02-12_RAPL-and-CPU-Power-Measurement-Deep-Dive.md](./2026-02-12_RAPL-and-CPU-Power-Measurement-Deep-Dive.md) — RAPL deep-dive

---

## Notes & Assumptions

**Fact:** POET uses PDU as ground truth, queried at ~10 s intervals via SNMP.

**Fact:** IPMI averages over ~60 s and reads ~10 W lower than PDU.

**Fact:** RAPL is a model-based estimate covering CPU+DRAM only, with a constant offset from system-level power.

**Fact:** POET iPerf targets: 1 UE = 70% PRB / 65 Mb/s; 2 UE = 100% PRB / 84 Mb/s.

**Assumption:** Our initial replication will use Scaphandre (RAPL) as primary tool, calibrated against IPMI if available.

**Assumption:** Prometheus + Grafana stack can be deployed alongside DU without significant power interference (<2 W overhead).

**Open question:** Do we have a smart PDU in the lab? If not, IPMI + Scaphandre is the fallback.

**Open question:** Is the RAPL PLATYPUS mitigation active on our target server? Must check before trusting RAPL variance.
