# Measurement Procedure v1 (2026-01-13)

## Procedure v1
Status: Done (software-first)
Deadline: 2026-01-13

This procedure is written to be runnable without RU hardware (software-first). When RU + a power meter exist, replace the “power source” with RU AC input power and keep the rest identical.

1) Prep / sync
- Ensure system time is synced (NTP) and logs use UTC timestamps.
- Create a run folder: `runs/YYYY-MM-DD/{scenario-name}/run-XX/`.

2) Start telemetry capture
- Start power exporter/log capture (software estimator or host telemetry).
- Start a simple system stats capture (CPU/mem/NIC counters) if not already included.

3) Execute scenario states (single run)
- Idle:
	- Stop user traffic.
	- Wait 2 min warm-up.
	- Record 5 min steady-state.
- Active-idle:
	- Start/enable the stack/cell (but keep user traffic off).
	- Wait 2 min warm-up.
	- Record 5 min steady-state.
- Load point(s):
	- Run `iperf3` to hit the target throughput for Load-L/M/H.
	- Wait 2 min warm-up.
	- Record 5 min steady-state.

4) Stop capture and export
- Stop telemetry capture.
- Export logs (raw + machine-readable) into the run folder.
- Save a short metadata file describing the run.

Pilot outcome reference (Day 4):
- Run folder example: `runs/2026-01-15/pilot-scaphandre-iperf/run-01/`
- Power/energy: unavailable on WSL2 (no powercap + Scaphandre container fails)
- KPI/logging: `iperf_load_m.txt`, `iperf_load_m.json`, `utc_markers.txt`

## Data logging schema
Status: Done
Deadline: 2026-01-13

CSV (time-series) minimum columns:
- `timestamp_utc` (ISO-8601)
- `scenario_state` (idle | active-idle | load-L | load-M | load-H)
- `power_w` (if available; software estimate now, RU input later)
- `energy_j` (optional per-sample; otherwise computed in analysis)
- `throughput_mbps` (from iperf3; can be repeated per sample or summarized per window)
- `bytes_total` (monotonic counter if available)
- `cpu_util_pct` (optional)
- `nic_rx_bytes`, `nic_tx_bytes` (optional)

Metadata (sidecar file, e.g., `run.json` or `run.md`):
- Date/time, machine ID, OS/kernel
- Tool versions (iperf3 + power estimator)
- Scenario definition (windows, targets)
- Notes about anomalies

Naming:
- Folder-per-run with a monotonically increasing `run-01`, `run-02`, ...
- Include scenario name in folder (e.g., `idle-active-loadL`)

## Failure modes + checks
Status: Done
Deadline: 2026-01-13

Sanity checks before accepting a run:
- Timestamps monotonic and in UTC; no obvious clock jumps.
- Idle steady-state variance is “small” relative to state changes; if not, increase window or fix background load.
- No missing data for long gaps; if gaps exist, record them and rerun.
- iPerf traffic matches the intended state (idle has ~0 Mbps; load states hit targets within a reasonable tolerance).

Common failure modes:
- Competing background processes causing power/CPU noise.
- Network bottleneck limiting throughput (load targets not reached).
- Estimator not supported on the host CPU/kernel (no power signal). If so, fall back to CPU/NIC counters and treat power as “not measured yet”.
