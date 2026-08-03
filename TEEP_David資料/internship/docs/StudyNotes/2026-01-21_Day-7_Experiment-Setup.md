# Day 7 — Jan 21: Week 3 Experiment Setup (2026-01-21)

Status: Complete
Deadline: 2026-01-21

## Goal
Prepare the **Load Sweep Experiment** (Week 3 target) to characterize the power-vs-load curve of the platform.
The goal today is to script the logic so the execution (Thu/Fri) is error-free and reproducible.

## Experiment Design (from Decision Log)
Structure: `Idle -> Warmup -> [Load-L -> Idle -> Load-M -> Idle -> Load-H -> Idle] x 3`

### Parameters
- **Load-L (Low):** 30% capacity (~0.3 * Max Throughput).
- **Load-M (Medium):** 60% capacity (~0.6 * Max Throughput).
- **Load-H (High):** 100% capacity (Max Throughput).
- **Duration:** 120s per step (shorter than pilot, but repeated).
- **Idle Gaps:** 60s to let thermal tail dissipate.

## What to do today (Checklist)

### 1) Determine "Max Throughput" baseline
Recall from Pilot (Jan 20):
- TCP Max achieved: ~97.4 Gbps (on loopback?).
- *Limit logic:* If using `iperf3`, we need `-b` (bandwidth) flags for L and M.

Calculated Targets (assuming 100G link or loopback baseline):
- **Load-L:** `-b 30G`
- **Load-M:** `-b 60G`
- **Load-H:** `-b 0` (unlimited)

### 2) Create the execution script (powershell/bash)
We need a script `scripts/week3_load_sweep.sh` (or `.ps1` if running load gen on Windows against Linux) that:
1.  Logs a "Marker: Start" timestamp.
2.  Sleeps 60s (Initial Idle).
3.  Loop x3:
    - Runs Load-L (120s) -> Log Marker "Load-L-RunX"
    - Sleeps 60s -> Log Marker "Idle-Post-L-RunX"
    - Runs Load-M (120s) -> Log Marker "Load-M-RunX"
    - Sleeps 60s -> Log Marker "Idle-Post-M-RunX"
    - Runs Load-H (120s) -> Log Marker "Load-H-RunX"
    - Sleeps 60s -> Log Marker "Idle-Post-H-RunX"

### 3) Test the script logic (Dry Run)
- Run the script with "short timers" (e.g., 5s duration) just to verify it launches iperf and logs markers correctly.
- Do this on **Ubuntu** (or wherever the load generator lives).

## Output for today
- `scripts/week3_load_sweep.sh` committed to repo.
- Confirmation that targets (30G/60G) are achievable on the test setup.
