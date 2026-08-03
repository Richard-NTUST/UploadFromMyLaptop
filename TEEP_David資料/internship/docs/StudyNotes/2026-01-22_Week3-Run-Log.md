# Week 3 Experiment: Power vs Load Sweep (Execution Log)

**Date**: 2026-01-22  
**Status**: Completed  
**Objective**: Measure platform power consumption across load levels (Idle, Load-L, Load-M, Load-H) to test whether platform power scales with throughput or behaves as a step function.

## 1. Experiment Setup
- **DUT**: Ubuntu Dual-Boot Partition
- **Tools**: 
  - `iperf3` (Load Generation)
  - `scaphandre` (Power Measurement)
  - `week3_load_sweep.sh` (Orchestration)
- **Variables**:
  - Independent: Network Throughput (Gbps)
  - Dependent: Power (Watts)

## 2. Execution Steps
1.  **Boot Ubuntu**: Ensure clean state, no unnecessary background services.
2.  **Pull Latest Code**: Get the updated `week3_load_sweep.sh` from git.
3.  **Start Scaphandre & Logger**: 
    **Terminal 2 (Scaphandre Service)**:
    ```bash
    docker run --rm --privileged \
      -v /sys/class/powercap:/sys/class/powercap \
      -v /proc:/proc \
      -p 8080:8080 \
      hubblo/scaphandre prometheus --address 0.0.0.0 --port 8080
    ```
    **Terminal 3 (Logger Loop)**:
    (Note: This run’s saved `power_uw.txt` is ~10s cadence; use `sleep 10` to match.)
    ```bash
    while true; do 
      echo -n "$(date -u +"%Y-%m-%dT%H:%M:%SZ"),"; 
      curl -s http://localhost:8080/metrics | grep "^scaph_host_power_microwatts" | awk '{print $2}'; 
      sleep 10; 
    done | tee -a power_uw.txt
    ```
4.  **Run Sweep Script**: 
    ```bash
    chmod +x scripts/week3_load_sweep.sh
    ./scripts/week3_load_sweep.sh
    ```
5.  **Stop & Collect**: Terminate Scaphandre, save files to `runs/2026-01-22/`.

## 3. Run Log
| Time (Local) | Event | Notes |
| :--- | :--- | :--- |
| 10:14 UTC | Start | Initial Idle phase |
| 10:15 UTC | Load-L | First 30G step |
| 10:20+ UTC | Continued | Cycling L -> M -> H |
| 10:37 UTC | End | Experiment concluded |

## 4. Results Location
- Raw Files: `runs/2026-01-22/power_uw.txt`, `markers.md`
- Traffic Evidence: `runs/2026-01-22/iperf.txt` ([summary](../../runs/2026-01-22/iperf_summary.md))
- Plots: `assets/2026-01-22/plots/`
    - [Timeline](assets/2026-01-22/plots/power_timeline.png)
    - [Linearity Boxplot](assets/2026-01-22/plots/power_linearity_boxplot.png)
  - [Stats Summary (trimmed windows)](assets/2026-01-22/plots/stats_summary.md)
  - [Repeatability per run](assets/2026-01-22/plots/repeatability_per_run.md)

## 5. Post-Run Analysis
*(Completed 2026-01-22)*

### Scoring method (important)
The raw power trace contains transition samples at state boundaries (power ramps). For statistics, scoring uses explicit `Start_*`/`Stop_*` marker pairs and trims **10 seconds** from the start and end of each segment before computing mean/std/min/max.

### Power Stats (trimmed windows)
See the full table in: `assets/2026-01-22/plots/stats_summary.md`

High-level result (mean power):
- **Idle:** ~1.49 W
- **Load-L:** ~50.60 W
- **Load-M:** ~50.30 W
- **Load-H:** ~48.84 W

### Key Findings
1. **Step-function behavior (Idle → Active):** Once traffic starts, platform power jumps from ~1–2 W into the ~50 W band and remains there.
2. **Weak scaling inside Active band:** Load-L/Load-M/Load-H means are close compared to the Idle→Active jump, suggesting early saturation (e.g., CPU frequency/uncore clocks ramp quickly).
3. **Repeatability:** Per-run means for each state are consistent (see `assets/2026-01-22/plots/repeatability_per_run.md`). Load-L is especially stable; Load-H shows higher CV than L/M.

## 6. Interpretation

### Hypothesis
Platform power does not scale linearly with throughput in this setup. Instead, it behaves like a step function: Idle power is low, but the first sustained traffic load triggers a high-power operating point (CPU/uncore/NIC activity), and additional load increases throughput more than it increases power.

### Evidence (from this run)
1. **Trimmed power means:** Idle is ~1.49 W while Load-L/Load-M/Load-H cluster around ~49–51 W (see `assets/2026-01-22/plots/stats_summary.md`). The dominant effect is the Idle→Active transition, not L→M→H scaling.
2. **Per-run repeatability:** Each load level repeats 3 times and the per-run means remain close (see `assets/2026-01-22/plots/repeatability_per_run.md`), indicating this is not a single transient artifact.
3. **Traffic evidence exists for each segment:** The server captured 9 iperf tests (L/M/H × 3) and the extracted `[SUM]` throughput is summarized in `runs/2026-01-22/iperf_summary.md`.

### Important caveat (traffic targeting)
The orchestration uses `iperf3 -P 4`. The server log indicates that the "30G" step produced **~120 Gbps** aggregate, and the "60G" step produced **~235–239 Gbps** aggregate (see `runs/2026-01-22/iperf_summary.md`). This implies the configured target may be **per stream** (or otherwise multiplied by parallel streams), so the labels Load-L/Load-M reflect relative steps but are not guaranteed to be 30/60 Gbps total.

### Limitations
- **Workload realism:** The test is `localhost` loopback; it stresses CPU/network stack more than a real NIC + external link path.
- **Power signal scope:** Scaphandre reports platform power estimate (RAPL/host-level), not RU AC/DC input power.
- **Sampling granularity:** Power samples are ~10-second cadence in `power_uw.txt`, which limits resolution of short transients.
- **CPU governor/affinity not controlled:** Without pinning CPU frequency/governor and process placement, power may saturate early due to automatic turbo/boost behavior.

### Next experiment (to confirm root cause)
1. **Fix the traffic definition:** run `-P 1` first (single stream), then explicitly sweep streams (`-P 1/2/4/8`) while recording achieved throughput, so “load” is measured rather than assumed.
2. **Move off loopback:** run server on a second host (or at least over a real NIC) to avoid the loopback path dominating CPU.
3. **Control CPU behavior:** lock governor/frequency (or compare `performance` vs `powersave`) and record CPU freq/utilization alongside power.


