# Research Continuation Plan: RT StarlingX Tuning & WINLAB Measurement Methodology (2026-05-07)

Status: Planning
Deadline: 2026-05-07

## Executive Summary

After reviewing the NVIDIA cuMAC scheduler note (2026-05-01) and WINLAB baseline (2026-01-12), we identified that the most productive next steps for **replicating WINLAB's energy-efficiency results** are not GPU-focused, but rather **platform tuning** and **measurement rigor**. This note outlines two critical study topics and explains why they are the right continuation path.

---

## Context: Why Not cuMAC First?

**The NVIDIA cuMAC study (2026-05-01) was valuable for understanding the state-of-the-art in GPU-accelerated scheduling, but**:
- cuMAC is a vendor-proprietary SDK requiring explicit integration into the O-DU (cuMAC-CP + nvIPC).
- It does not modify StarlingX itself — only requires StarlingX to *host* GPU-enabled containers.
- The scheduling algorithms (PF, PRB allocation, MCS) are already understood from our srsRAN and OAI deep-dives (Feb–Mar 2026 notes).
- Deploying cuMAC is a *future optimization*, not a blocker for replicating WINLAB.

**Instead, we should focus on the immediate blockers:**
1. **We don't yet know how to configure StarlingX for real-time 5G workloads** (CPU isolation, hugepages, kernel tuning, SR-IOV, IRQ affinity, NUMA alignment).
2. **We don't yet have a rigorous measurement methodology** — the WINLAB/POET baseline describes PDU/IPMI/software estimators, but we haven't mapped it to our local setup.

---

## Topic 1: Real-Time StarlingX Tuning for 5G Stack

### Scope & Objectives

Configure a StarlingX instance (or bare-metal Ubuntu with RT kernel) to run a 5G DU workload (OAI or srsRAN) with **minimal latency jitter** and **predictable power behavior**.

### Key Questions to Answer

1. **CPU Isolation & DPDK/NUMA**
   - How to isolate CPU cores for the DU workload?
   - Is `isolcpus` + `nohz_full` enough, or do we need full `systemd-nspawn` + cgroup v2?
   - How do we map vNIC/SR-IOV VF queues to isolated cores?
   - Does NUMA affect the O-RU fronthaul latency?

2. **Kernel & Scheduler Tuning**
   - Real-time kernel (PREEMPT_RT) vs generic: latency comparison and power cost.
   - CFS vs RT scheduling class: which is best for a mixed workload (L1 timing-critical + L2/MAC best-effort)?
   - IRQ affinity: should O-RU fronthaul interrupts live on isolated cores or separate cores?

3. **Memory & Huge Pages**
   - Why huge pages matter for DU (fewer TLB misses → lower latency variance).
   - How to allocate and pin hugepages to specific NUMA nodes.
   - Trade-off: memory fragmentation vs latency.

4. **StarlingX-Specific Settings**
   - How to enable RT tuning in StarlingX's Kubernetes layer (vs bare-metal).
   - CPU manager (static) + topology manager (best-effort NUMA) settings.
   - NVIDIA device-plugin (if using GPU) + resource requests/limits for low-latency.

5. **Benchmarking & Validation**
   - Latency metrics: DU processing cycle jitter, MAC slot deadline miss rate, RU fronthaul round-trip delay.
   - Power impact: does RT kernel cost extra power? (RAPL comparison).
   - Throughput stability: does tuning improve consistency (reduce variance in iPerf/iperf3)?

### Why This Topic First

- **Blocker**: Current StarlingX is not tuned for RAN; we don't know if our deployment can meet the ~0.5 ms slot deadline.
- **Enables WINLAB replication**: WINLAB's measurement baseline (POET paper) assumes a well-tuned platform; we need to match that baseline first.
- **References available**: O-RAN specs (O-RU WG), srsRAN docs, and OAI community guides all discuss RT tuning.

### Sub-Topics to Study

1. O-RAN Fronthaul timing requirements and latency budgets.
2. DPDK + SR-IOV for O-RU vNIC: setup and performance impact.
3. Linux RT kernel tuning checklist (isolcpus, IRQ affinity, memory locking, preemption settings).
4. Kubernetes CPU manager and topology manager configuration.
5. Latency profiling tools: `cyclictest`, `LatencyTOP`, perf, tracepoints for DU validation.

---

## Topic 2: WINLAB/POET Measurement Methodology

### Scope & Objectives

Establish a **repeatable, reviewer-safe measurement pipeline** compatible with the WINLAB baseline (POET paper) that can distinguish:
- Measurement tool artifacts (PDU vs IPMI vs software estimators).
- Load-dependent vs load-independent power.
- Scheduler-driven variations (FDM vs TDM, slot utilization, sleep windows).

### Key Questions to Answer

1. **Ground Truth & Tool Comparison**
   - Which measurement point (AC vs DC) is "ground truth" for your testbed?
   - How do PDU, IPMI, RAPL (Scaphandre), and GPU power (nvidia-smi) compare?
   - What is the expected offset and averaging time for each tool?
   - How to align timestamps across heterogeneous power sources?

2. **Load Definition & Reproducibility**
   - How to define "load" in a 5G context: PRB utilization %? Throughput (Mb/s)? User count? Packet rate?
   - WINLAB uses PRB load (70%, 100%) + DU throughput (65, 84 Mb/s) — can we replicate this?
   - How to ensure the same load is repeatable across runs (warm-up duration, steady-state duration, traffic pattern)?

3. **Sampling & Cadence**
   - WINLAB: PDU ~10 s, IPMI ~60 s stabilization, software tools variable.
   - What cadence do we need to capture RU sleep modes? (milliseconds? seconds?)
   - How to handle clock skew and out-of-order measurements?

4. **KPI Alignment & Timestamps**
   - How to synchronize DU KPIs (throughput, latency, PRB allocation) with power measurements?
   - What are the "events" that matter? (slot boundaries, HARQ retransmissions, RU state transitions).
   - How to create a "labeled" power trace (e.g., `power_labeled.csv` with state/load annotations)?

5. **Validation & Plausibility Checks**
   - Is the measured power plausible against the RU model? (P_idle + ΔP × load).
   - Does throughput match TBS expectations? (we have TBS equivalence proof from Feb 26 note).
   - Do PDU and IPMI agree within acceptable tolerance (e.g., ±10 W)?

### Why This Topic Second

- **Critical for WINLAB replication**: WINLAB's figures show PDU/IPMI/software comparisons (Fig. 4–7). We must understand and reproduce these first.
- **Dependencies**: Once RT tuning is in place (Topic 1), we can run repeatable workloads and collect clean power data.
- **Unblocks later topics**: Once measurement is solid, we can study scheduler effects (Topic 3), RU power models (Topic 4), etc.

### Sub-Topics to Study

1. Smart PDU specifications and querying (Server Technology PRO3X, STV-6521V from POET).
2. IPMI power domain mapping and stabilization delays.
3. RAPL (Intel Running Average Power Limit) and Scaphandre setup for CPU/package power.
4. nvidia-smi for GPU power telemetry (if using GPU).
5. Prometheus + Grafana setup for heterogeneous power source integration.
6. Timestamp synchronization and data alignment tools (e.g., UTC markers, NTP, PTP).
7. POET paper's specific measurement methodology (load steps, warm-up durations, KPI export).
8. Statistical rigor: mean/median, variance, confidence intervals, and outlier handling.

---

## Dependency & Sequencing

```
Topic 1: RT StarlingX Tuning
    ↓
    (Enables: stable, repeatable DU workload)
    ↓
Topic 2: WINLAB Measurement Methodology
    ↓
    (Enables: clean power + KPI data)
    ↓
Topic 3: Scheduler Behavior & Load Shaping [Future]
    ↓
Topic 4: RU Power Modeling & Anchors [Future]
    ↓
Topic 5: cuMAC Integration (if needed) [Future]
```

**Why sequential?**
- Cannot measure reliably without a tuned platform (T1 → T2).
- Cannot study scheduler effects without clean measurement (T2 → T3).
- Cannot build power models without scheduler understanding (T3 → T4).
- GPU acceleration is an optimization, not a prerequisite (T5 after all others).

---

## References & Existing Work

### From Our Study Notes (Already Complete)

- [2026-01-12_WINLAB-Baseline.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_WINLAB-Baseline.md) — POET platform and metrics overview.
- [2026-02-03_srsRAN-Scheduler-Deep-Dive.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-03_srsRAN-Scheduler-Deep-Dive.md) — Scheduler architecture and FDM/TDM control points.
- [2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md) — RU power model ($P = P_0 + ΔP × L$).
- [2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md) — Throughput validation (TBS equivalence).
- [2026-04-28_Guided-StarlingX-Deployment-Issues.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-04-28_Guided-StarlingX-Deployment-Issues.md) — Current StarlingX deployment blockers and workarounds.
- [2026-05-01_NVIDIA-cuMAC-GPU-Accelerated-Scheduling.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-01_NVIDIA-cuMAC-GPU-Accelerated-Scheduling.md) — GPU scheduler as future optimization.

### Likely Sources for Topic 1 (RT Tuning)

- O-RAN Specifications (WG2/WG4): timing and latency requirements for O-DU/O-RU.
- srsRAN and OAI community docs: RT kernel recommendations.
- Linux kernel docs: isolcpus, nohz_full, DPDK.
- StarlingX documentation: RT kernel integration and CPU manager.

### Likely Sources for Topic 2 (Measurement Methodology)

- POET paper itself (assets/2026-01-12/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf).
- WINLAB NTIA white papers and published RCR articles.
- Server Technology PDU documentation (for instrument-specific caveats).
- RAPL/Scaphandre and nvidia-smi documentation.
- Our own past runs (Daily-Logs.md, 2026-01-26 to 2026-02-05) for what already worked/failed.

---

## Why This Plan Supports WINLAB Replication

**WINLAB's core claims** (from POET and cited papers):
- With proper measurement (PDU/IPMI/software alignment) and platform tuning, O-RAN deployments can achieve measurable energy savings.
- Different scheduler/load patterns (iPerf @ 70% vs 100% PRB load) produce different power curves.
- RU power is the dominant term and is highly dependent on load and transmission pattern.

**Our replication roadmap:**
1. Tune StarlingX to run RAN workloads reliably (T1).
2. Measure that platform rigorously with aligned PDU/IPMI/software tools (T2).
3. Run WINLAB's iPerf scenarios (1 UE @ 70% load, 2 UEs @ 100% load) and compare throughput to their numbers (65 Mb/s, 84 Mb/s).
4. Measure RU power during those scenarios and fit a model.
5. **Result**: We have a defensible, reproducible replication of WINLAB's measurement baseline.

Once that baseline is solid, we can study scheduler interventions (Topic 3), power models (Topic 4), and GPU acceleration (Topic 5).

---

## Next Steps

- **Topic 1 study note ✅**: [2026-05-07_Topic1-RT-StarlingX-Tuning-for-5G-DU.md](./2026-05-07_Topic1-RT-StarlingX-Tuning-for-5G-DU.md) — Complete tuning checklist with commands, configs, and validation targets (cyclictest < 20 µs). Covers PREEMPT_RT, CPU isolation, hugepages, NUMA, StarlingX K8s settings, srsRAN/OAI thread pinning.
- **Topic 2 study note ✅**: [2026-05-07_Topic2-WINLAB-POET-Measurement-Methodology.md](./2026-05-07_Topic2-WINLAB-POET-Measurement-Methodology.md) — Measurement pipeline design with tool comparison table, POET replication plan (4 phases), data format spec, and statistical rigor checklist.
- **Next action**: Apply Topic 1 checklist to our StarlingX deployment (from 2026-04-28 note), validate with cyclictest, then execute Topic 2 Phase 1 (measurement stack validation without RAN).

---

## Notes & Assumptions

**Fact**: We have existing StarlingX deployment (2026-04-28 note) with known blockers (networking, CPU mode, image registry).

**Fact**: We have WINLAB/POET paper baseline with explicit iPerf targets and measurement methodology.

**Assumption**: StarlingX with RT tuning can achieve the latency requirements for a 5G DU.

**Assumption**: PDU + IPMI alignment is feasible with standard tools (Prometheus, custom logging, UTC markers).

**Open question**: What is our RU model/vendor? (Deferred until hardware access; use WINLAB anchors for now.)

---

## References

1. Daily-Logs.md (this repo) — Historical study progress and experiment runs.
2. POET paper (assets/2026-01-12/Workload Definition/) — Primary measurement baseline.
3. O-RAN specifications (O-RU WG, Timing Sync) — Latency and RT requirements.
4. Linux kernel documentation (isolcpus, DPDK) — Platform tuning.
5. RAPL, Scaphandre, nvidia-smi documentation — Measurement tools.
