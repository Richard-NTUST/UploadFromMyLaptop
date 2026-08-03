# Day 6 — Jan 20: Analysis + Evidence Bundle + Next Run (2026-01-20)

Status: In Progress
Deadline: 2026-01-20

## Goal
Now that the power-enabled pilot artifacts exist, today is about converting them into **publishable outputs** and closing Week 2 items:
- Plot 1 (power vs time + state annotations)
- Table 1 (per-state mean power + energy + throughput)
- Evidence bundle (env snapshot + one Prometheus `/metrics` snapshot)

Scope note (keep this wording): results are **platform power under RU-like workload** until RU input power is measured with hardware.

## What to do today (checklist)
### 1) Generate Plot 1 + Table 1 from the run folder
This repo now includes a dependency-free script that produces derived outputs from the Jan 19/20 run artifacts.

Run (Windows / PowerShell):
- `py .\scripts\analyze_power_run.py .\runs\2026-01-20`

Expected outputs:
- `runs/2026-01-20/derived/power.csv`
- `runs/2026-01-20/derived/plot_1_power_vs_time.svg`
- `runs/2026-01-20/derived/table_1_per_state.md`

Acceptance checks:
- The plot shows clear state separation.
- Table rows exist for Active-idle, Load-M, and Pure Idle.
- The load row includes throughput and efficiency.

### 2) Capture the missing evidence bundle (Ubuntu)
These are not needed to compute Plot/Table, but they are needed for record.

Boot into Ubuntu (dual boot) and run from the same host used for the power run:

Create file:
- `runs/2026-01-20/env.md`

Paste outputs:
- `uname -a`
- `lscpu | head`
- `ls -la /sys/class/powercap/`
- `docker version`
- `docker image inspect hubblo/scaphandre --format '{{.Id}}'` (or record the exact tag used)

Save a Prometheus snapshot (while exporter is running):
- `curl -s http://localhost:8080/metrics > runs/2026-01-20/scaphandre_metrics_snapshot.prom`

### 3) Decide the next run improvement (so Week 3 is straightforward)
Pick one improvement (do not over-scope):
- Add Load-L and Load-H points (same structure, repeat 3x each)
- Move from loopback to a real client/server pair (if you have two machines)
- Add CPU/NIC counters during each stage

Write the decision + reason in:
- `runs/2026-01-20/derived/notes_next_run.md` (or in the daily log)

## Quick interpretation (what we can say today)
- The pilot run produces a stable, state-dependent power signal on Ubuntu.
- We can now ship Plot 1 + Table 1 as a “method works” proof.
- We still label this as platform power under RU-like workload.
