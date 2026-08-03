# Measurement Methodology (Reproducible Method)

## 1. Measurement Point & Instrumentation
For this "Software Proxy" phase (prior to physical RU hardware availability), power consumption is measured at the **Operating System / CPU package level** of the compute host running the RU load simulation.

- **Measurement Point:** CPU Package / Platform Energy Counters (RAPL).
- **Instrument:** [Scaphandre](https://github.com/hubblo-org/scaphandre) (Kepler-based estimator).
- **Interface:** `/sys/class/powercap/intel-rapl` on Linux (Ubuntu Dual-boot).
- **Sampling Cadence:** 1.0 seconds.
- **Why this method:** Provides a high-resolution "Digital Lower Bound" of the O-RU's processing energy, excluding RF amplifier inefficiencies.

## 2. Metrics & Units
To ensure consistency with O-RAN alliance goals and the POET baseline, we define:

- **Primary Metric:** **Power (Watts)**.
    - Measured as instantaneous power samples ($P_{inst}$).
    - Reported as **Trimmed Median Power** ($P_{med}$) over steady-state windows to reject startup/teardown transients.
- **Secondary Metric:** **Throughput (Gbps)**.
    - Measured at the Transport Layer (UDP/TCP) via `iperf3`.
    - Used to define the "Load" percentage relative to link capacity.
- **Derived Metric:** **Energy Efficiency (J/bit)** for digital processing.
    - $\text{EE} = P_{med} / \text{Throughput}$.

## 3. Scenario Matrix
The standard Weekly Test Cycle consists of the following states, executed via the `week3_load_sweep.sh` automation script:

| State | Duration | Load Definition | Criteria |
| :--- | :--- | :--- | :--- |
| **Idle** | 60s | No user traffic | OS background tasks only. |
| **Load-Low (L)** | 120s | 30% Link Capacity | `iperf3 -u -b 30M/30G`. Thermal warming phase. |
| **Cool-down** | 30s | Idle | Return to baseline temp. |
| **Load-Med (M)** | 120s | 60% Link Capacity | `iperf3 -u -b 60M/60G`. Linearity check. |
| **Load-High (H)** | 120s | 100% Link Capacity | Saturation test (Max throughput). |
| **Digital Ceiling** | 300s | 100% CPU on all cores | `stress-ng`. Theoretical max digital power. |

## 4. Reproducibility
- **Scripted Execution:** All runs are triggered by `scripts/week3_load_sweep.sh` which logs UTC timestamps for every state transition to `markers.csv`.
- **Analysis Pipeline:** Raw data (`power_uw.txt`) is processed by `scripts/analyze_power_run.py`, which aligns timestamps with markers and automatically trims unstable transition periods (first/last 10s of each window).
