# Run Metadata — 2026-01-15 pilot-scaphandre-iperf / run-01

## Summary
This is a software-only pilot run in WSL2 to validate the scenario structure and logging artifacts.

## Environment
- Host OS: Windows
- Linux env: WSL2 Ubuntu (kernel: 5.15.167.4-microsoft-standard-WSL2)
- Docker: Docker Desktop WSL integration (expected)

## Power measurement status
- `/sys/class/powercap` in WSL2: not present (RAPL counters not exposed)
- Scaphandre attempt: container start failed due to WSL sysctl read-only (`ip_unprivileged_port_start`), so power estimation is **unavailable** in this environment.

## Workload / KPI
- Tool: `iperf3`
- Mode: UDP
- Target bitrate: 50 Mbit/s
- Duration: 300s

Observed result (from `iperf_load_m.txt`):
- Transfer: 1.75 GBytes
- Achieved bitrate: 50.0 Mbit/s
- Jitter: 0.005 ms (receiver)
- Loss: 0/57221 (0%)

Observed result (from `iperf_load_m.json`):
- Achieved bitrate: 50.000 Mbit/s (`bits_per_second` = 50000425.58)
- Jitter: 0.007 ms (`jitter_ms` = 0.00708)
- Loss: 0/57221 (0%)

## Files in this run folder
Artifacts:
- `iperf_load_m.txt`
- `iperf_load_m.json`
- `utc_markers.txt`
- `notes.md`

## Scenario windows
- Warm-up: 2 min (planned)
- Steady-state: 5 min (this run)

Fill actual UTC start/end markers:
- Start (UTC): Wed Jan 14 16:22:20 UTC 2026
- End (UTC): Wed Jan 14 16:32:15 UTC 2026

Note: the `iperf3` load window is 300s; the markers may include setup/teardown.
