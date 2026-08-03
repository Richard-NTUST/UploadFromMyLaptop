# Notes / anomalies — run-01

## What went well
- `iperf3` UDP run achieved target throughput (50 Mbit/s) with 0% loss.

## Issues encountered
- WSL2 does not expose `/sys/class/powercap` (no RAPL counters).
- Scaphandre container failed to start on WSL2 due to read-only sysctl (`ip_unprivileged_port_start`).

## Decisions
- Proceed in fallback mode for Day 4: publish scenario structure + throughput (and CPU/NIC if available), and explicitly mark power/energy as unavailable in this environment.

## Next attempts
- Done: captured `iperf_load_m.txt`, `iperf_load_m.json`, and `utc_markers.txt`.
- Optional next: capture CPU (`mpstat 1 600`) during the next load window.
- Next publish step: keep this run as “pipeline validation (no power)” evidence, and use a full Linux environment (Ubuntu) for power-enabled plots/tables.
