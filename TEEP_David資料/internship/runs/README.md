# Runs Folder (Raw Artifacts)

This folder stores **raw experimental artifacts** (power logs, workload logs, markers, and metadata) that back up plots/tables in the study notes.

## Why keep runs from “dysfunctional” periods?
Even when power measurement was unavailable (e.g., WSL2 missing `/sys/class/powercap`), those runs are still useful because they:
- prove the **scenario timing** and **logging pipeline** works,
- provide **throughput/KPI ground truth** for later comparisons,
- document constraints and decisions (so you don’t repeat debugging).

The rule is simple: if a run produced reproducible artifacts and a clear `run.md`, it is worth keeping.

## Folder structure
Recommended:
- `runs/YYYY-MM-DD/{scenario-name}/run-01/`

Each `run-XX/` should include:
- `run.md` (what happened + environment + what you can/can’t claim)
- `notes.md` (anomalies, deviations)
- `markers.txt` or `utc_markers.txt` (UTC timestamps for state boundaries)
- `power_*.txt|csv` (power series; may be missing in early WSL2 runs)
- `iperf_*.json` and/or `iperf_*.txt`

## How to label runs
Use the scenario name to make the measurement mode obvious:
- `pilot-scaphandre-iperf` = pipeline validation (may be “no power”)
- `pilot-scaphandre-ubuntu` = power-enabled (Ubuntu dual boot)

In `run.md`, always state:
- measurement point (software estimator vs RU input meter)
- whether `power_w` is available
- what the run can be used for (pipeline-only vs power+KPI)

## What’s next
As you collect Ubuntu Scaphandre runs, add them under:
- `runs/2026-01-20/` (and so on)

Note: the first power-enabled pilot run was executed around the Jan 19/20 UTC boundary, so the artifacts live under `runs/2026-01-20/` while the narrative notes are dated 2026-01-19.

Those are the runs that will feed Plot 1 + Table 1 in the analysis plan.
