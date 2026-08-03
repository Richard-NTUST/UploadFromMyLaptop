# Methodology: Reproducible O-RU Power Measurement (Software Proxy)

## 1. Overview
As an initial step toward full O-RU power benchmarking, this methodology utilizes a **Software Proxy** approach. Instead of measuring physical O-RU hardware (which requires specialized RF instruments and smart PDUs), we execute the digital baseband workload on a general-purpose compute host and measure the **Software Power Consumption** using RAPL-based estimators.

This method isolates the "Digital/Compute" component of the O-RU power budget, serving as a lower-bound reference for Full O-RU efficiency. 
Related Note: [Tool Selection](../StudyNotes/2026-01-29_Methodology_Background_and_Tools.md).

## 2. Measurement Point & Metrics

### Measurement Point
- **Target:** General-purpose Compute Host (Laptop/server) running the workload simulation.
- **Instrument:** `Scaphandre` (Software Power Estimator).
- **Sensor Source:** Intel/AMD RAPL (Running Average Power Limit) energy counters via `/sys/class/powercap` on Linux.
- **Scope:** Defines "Platform Power" as the Package (CPU) + DRAM power reported by the kernel.

### Metrics
We adhere to ETSI/O-RAN efficiency definitions adapted for a software context:

| Metric | Unit | Definition |
| :--- | :--- | :--- |
| **Average Power ($P_{avg}$)** | Watts (W) | Mean power consumption over a stable 300s window. |
| **Energy ($E$)** | Joules (J) | Total energy accumulated over a specific scenario segment. |
| **Throughput ($T$)** | Mbps / Gbps | Application-layer payload rate successfully received. |
| **Efficiency ($\eta$)** | J/bit | Energy required to process one bit of payload ($P_{avg} / T$). |

## 3. Scenario Matrix
We defined standard "Step Tests" to characterize the power-load relationship.

### Load Definitions
- **Idle:** OS background processes only; no network traffic.
- **Active-Idle:** Network stack active (link up), but zero payload traffic.
- **Load-L (Low):** 30% of link capacity.
- **Load-M (Medium):** 60% of link capacity.
- **Load-H (High):** 100% of link capacity (saturation).

### Execution Sequence (The "Sweep")
To ensure thermal consistency and repeatability:
1. **Warm-up:** 120s (Discard data).
2. **Idle Baseline:** 300s.
3. **Load Steps:** For each Load Level (L, M, H):
   - **Run:** 300s of traffic.
   - **Cooldown:** 300s of Idle.
   - **Repeat:** 3x iterations per level (to average out OS noise).

## 4. Workload Generation
Since actual 5G NR PHY layer software (e.g., OAI-PHY) is compute-bound, we use `iperf3` to simulate the data-plane stress on the system bus and memory.

- **Tool:** `iperf3` (UDP Mode)
- **Configuration:** Single-stream (`-P 1`) vs Multi-stream (`-P 4`) to test CPU C-state transitions.
- **Validation:** "Digital Ceiling" stress test using `stress-ng` to confirm maximum theoretical component power.

## 5. Automation & alignment
Manual measurement leads to timestamp drift. We utilize a rigid bash script automation:
- **Synchronization:** The script logs a "Marker" to a CSV file (Epoch Timestamp, Label) immediately before triggering the workload.
- **Alignment:** Post-processing Python scripts read the `power_uw.txt` (µW samples) and `markers.csv` to slice the data into precise windows, trimming the first/last 10s to remove transition transients.
