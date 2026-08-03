# Standard Operating Procedure (SOP): O-RU Software Power Measurement

## 1. Overview
This document defines the repeatable procedure for measuring the "Platform Power" of an O-RAN software workload. It covers the end-to-end workflow from environment setup to data generation and analysis.

**Target Output:** A set of power logs (`power_uw.txt`) aligned with traffic markers (`markers.csv`), processed into efficiency plots and summary statistics.

---

## 2. Prerequisites

### 2.1 Hardware
*   **Target Machine:** x86-64 Laptop or Server (Intel/AMD) with RAPL support enabled in BIOS.
*   **OS:** Native Linux (Ubuntu 22.04+ recommended).
    *   *Note:* WSL2 is **NOT** supported for power measurement (RAPL counters `/sys/class/powercap` are often inaccessible).
*   **Network:** Loopback interface (`lo`) is sufficient for single-host testing.

### 2.2 Software
*   **Scaphandre:** A power monitoring agent.
    *   Installation: Standard binary or Docker (requires privileged mode).
*   **iperf3:** Traffic generator.
*   **Python 3.10+:** For analysis scripts.
    *   Dependencies: `pandas`, `matplotlib`, `seaborn` (install via `pip install -r requirements.txt` if available, or manually).
*   **curl:** For polling metrics.

---

## 3. Detailed Procedure

### Phase A: Environment Preparation

1.  **Start power estimator (Scaphandre):**
    Run Scaphandre in Prometheus exporter mode. It must be accessible at `http://localhost:8080/metrics`.
    ```bash
    # Option 1: Docker (Preferred)
    docker run -d --privileged -p 8080:8080 -v /sys/class/powercap:/sys/class/powercap hubblo/scaphandre prometheus
    
    # Option 2: Binary
    ./scaphandre prometheus
    ```

2.  **Start traffic sink (iperf3 server):**
    Open a terminal and listen on default port 5201.
    ```bash
    iperf3 -s
    ```

### Phase B: Execution (Data Collection)

We use the automation script `scripts/run_week4_gap_run.sh` to enforce timing consistency.

1.  **Configure Environment Variables (Optional):**
    *   `TARGET_L`, `TARGET_M`, `TARGET_H`: Throughput targets (e.g., "30G", "60G", "90G").
    *   `DURATION`: Seconds per load step (default: 180s).
    *   `IDLE`: Cooldown seconds between steps (default: 60s).

2.  **Run the script:**
    ```bash
    # Example: Run default sweep
    ./scripts/run_week4_gap_run.sh
    
    # Example: Custom output directory
    OUTPUT_DIR=runs/my-test-run ./scripts/run_week4_gap_run.sh
    ```

3.  **Wait for completion:**
    The script will execute the `Idle -> Load -> Idle` sequence automatically. Do not use the machine for other heavy tasks during this time.
    *   *Expected Duration:* ~30 minutes for a standard 3-round sweep.

### Phase C: Analysis (Data Processing)

We use the Python script `scripts/analyze_week3_data.py` to parse logs and generate visualizations.

1.  **Run the analysis script:**
    Point the script to the folder created in Phase B.
    ```bash
    # Syntax: python scripts/analyze_week3_data.py <path_to_run_folder>
    python scripts/analyze_week3_data.py runs/current_sweep
    ```

2.  **Review Outputs:**
    The script will generate artifacts in `assets/<date>/plots/`:
    *   **Time-Series Plot:** Visual confirmation of step function.
    *   **Linearity Boxplot:** Power distribution per load level.
    *   **Stats Summary:** A markdown file with trimmed median power values.

---

## 4. Quality Control (Acceptance Criteria)

Before publishing results, verify them against the reference visual below.

![Reference Sensitivity Plot](../../assets/2026-01-28/plots/gap_analysis_sensitivity.png)
*Figure 1: Example of a successful run. Note the flat plateaus and clear stepping behavior.*

1.  **State Separation:** Is there a clear visual distinction between Idle and Load? (Idle should be <10W, Load >20W).
2.  **Stability:** Are the "plateaus" flat? If they are jagged, check for background system updates or thermal throttling.
3.  **Markers:** Open `markers.csv` and ensure timestamps exist for every "Start_Load" and "Stop_Load" event.
4.  **Sampling Rate:** Check `power_uw.txt`. Samples should be regular (approx. every 1-2 seconds or as configured).

---

## 5. Troubleshooting Reference

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| **No power data in `power_uw.txt`** | Scaphandre not running or RAPL blocked. | Check `curl localhost:8080/metrics`. Verify `/sys/class/powercap` exists. |
| **"Permission Denied"** | Docker running without `--privileged`. | Restart container with `--privileged`. |
| **Throughput lower than target** | CPU bottleneck (single-thread `iperf`). | Use `iperf3 -P 4` (Parallel streams) or check `htop` for core saturation. |
| **Timestamps not aligning** | Timezone mismatch. | Ensure script and python parser both use UTC. (Default behavior in provided scripts). |
