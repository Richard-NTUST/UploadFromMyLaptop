# Day 4 - Pilot Run Plan (2026-01-15)

## Goal (1 paragraph)
Status: Done
Deadline: 2026-01-15

This was a **software-first pipeline validation run** in WSL2: prove we can execute a controlled throughput workload (iperf3), record UTC markers for the window, and store artifacts in a consistent `runs/` folder structure. Power estimation (Scaphandre) was attempted, but **power is unavailable in WSL2** due to missing `/sys/class/powercap` and a Docker/sysctl limitation, so the focus is KPI correctness and timing. The output of Day 4 is a reproducible run folder containing iperf logs + UTC markers + metadata. We do **not** claim RU wall/input power, and we do **not** claim platform power for Day 4.

## Assumptions (lock these)
Status: Done
Deadline: 2026-01-15

- Measurement point: **throughput/KPI only** (power unavailable in this environment)
- Power source/tool: Scaphandre (attempted) → **blocked in WSL2** (iperf-only fallback)
- Time sync: UTC via `date -u` (markers saved)
- Load definition: throughput via `iperf3`

## Scenario definition (exact)
Status: Done
Deadline: 2026-01-15

Use the frozen window structure:
- Warm-up: 2 min
- Steady-state: 5 min

States (fill exact order):
1) Load-M (UDP)
- How you enforce it: run iperf3 UDP at fixed target bitrate
- Load target(s): Load-M = 50 Mbit/s for 300 s
- Start time (UTC): 2026-01-14 16:22:20Z (marker)
- End time (UTC): 2026-01-14 16:32:15Z (marker)

Note: this Day-4 run did not include a scored idle/active-idle window because power was unavailable; the step-test with power is captured on Day 5.

## Commands (copy/paste)
Status: Done
Deadline: 2026-01-15

iperf3 server:
- `iperf3 -s` (host: 127.0.0.1)

iperf3 client:
- Load-M (UDP, 50 Mbit/s, 300 s):
	- `iperf3 -c 127.0.0.1 -u -b 50M -t 300 --json | tee iperf_load_m.json`
	- (optional) also save text output: `iperf3 -c 127.0.0.1 -u -b 50M -t 300 | tee iperf_load_m.txt`

Telemetry:
- Power exporter start: attempted Scaphandre in Docker (blocked on WSL2)
- Power exporter stop: n/a
- System stats capture (optional): CPU and NIC counters (not required for Day 4 acceptance)

## Data artifacts (what files must exist)
Status: Done
Deadline: 2026-01-15

Run folder:
- `runs/2026-01-15/pilot-scaphandre-iperf/run-01/`

Must include:
- `iperf_load_m.json`
- `iperf_load_m.txt`
- `utc_markers.txt`
- `run.md` (metadata)
- `notes.md` (anomalies, deviations)

## Acceptance checks (pass/fail)
Status: Done
Deadline: 2026-01-15

- Throughput target met (50 Mbit/s) with 0% loss (or explain why not)
- UTC markers recorded and consistent with the iperf run window
- Run folder contains the required artifacts and metadata

## What you will publish (end-of-day)
Status: Done
Deadline: 2026-01-15

- One paragraph in this note summarizing what was validated (scenario + artifacts) and what was blocked (power)
- Run folder evidence under `runs/2026-01-15/pilot-scaphandre-iperf/run-01/`

Note: Plot/table requiring power were produced later once Ubuntu Scaphandre worked (see Day 5 run artifacts).
