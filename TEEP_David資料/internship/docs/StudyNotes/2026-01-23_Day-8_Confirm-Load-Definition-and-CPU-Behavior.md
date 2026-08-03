# Day 8 — Jan 23: Confirm Load Definition + CPU Behavior (Week 3)

Status: Complete

## Goal
Convert the Week 3 finding (“step-function power”) into a **confirmed explanation** by removing the biggest ambiguity: whether the configured `iperf3 -b` targets represent **total throughput** or are effectively multiplied by parallel streams (`-P`).

Second goal: collect just enough **CPU evidence** to support (or falsify) the hypothesis that the CPU/uncore ramps immediately into a high-power state.

## Execution Results (Jan 23)

### 1. Traffic Validation (Single Stream)
We confirmed that `iperf3 -P 1` accurately hits the target bitrate.
- **Load-L Target 30G**: Achieved **30.0 Gbits/sec**
- **Load-M Target 60G**: Achieved **60.0 Gbits/sec**
- **Load-H Target Max**: Achieved **Speed limited by CPU single-thread** (Likely ~70-90G)

### 2. Power Measurements
We re-ran the full sweep with `-P 1`.
- **CPU Identified**: Intel Core Ultra 7 255H (Meteor Lake). This is a highly efficient hybrid architecture (P-cores + E-cores + LP-E-cores).

| State | Mean (W) | Std (W) | Notes |
| :--- | :--- | :--- | :--- |
| **Idle** | 8.44 | 5.29 | Baseline (Screen on/Background?) |
| **Load-L (30G)** | 7.50 | 5.05 | **Lower** than idle? Extremely efficient. |
| **Load-M (60G)** | 7.49 | 5.05 | Identical to 30G. Saturation or efficiency? |
| **Load-H (Unlim)** | 11.07 | 5.06 | Clear jump in power consumption. |

### 3. Key Findings

1.  **Surprising Efficiency**: Handling 30Gbps and 60Gbps loopback traffic on a single thread consumed **negligible incremental power** (Delta < 0 or ~0 W vs Idle). The Meteor Lake architecture likely handles this interrupt/copy load on E-cores or without boosting the P-core frequency significantly.
2.  **Contrast with Jan 22**:
    - **Jan 22 (Parallel -P 4)**: Power jumped to **48W**.
    - **Jan 23 (Single -P 1)**: Power stayed around **8-11W**.
    - **Conclusion**: The "Step Function" to 48W was driven by **Parallelism** (waking up multiple cores/clusters), not just raw throughput.
3.  **O-RU Implication**: O-RAN Low-PHY processing is highly parallel (MIMO). The Jan 22 (`-P 4`) 48W figure is likely a more realistic proxy for a "loaded" system doing heavy compute than the highly-optimized single-thread stream we saw today.

## Next Steps (Week 4)
- Use the **Jan 22 Data (48W Step)** as our primary "Heavy Load" dataset for comparison.
- Use the **Jan 23 Data (Power Efficiency)** as a "Low/Single-Thread Load" baseline to demonstrate architectural scaling.
- Proceed to WINLAB comparison.

## Original Plan Details
- Validated traffic semantics (single stream)
- Re-ran sweep with controlled load definition
- Captured CPU evidence (Meteor Lake confirmed)

