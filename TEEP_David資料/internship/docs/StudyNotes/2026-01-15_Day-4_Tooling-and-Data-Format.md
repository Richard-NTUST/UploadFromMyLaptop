# Day 4 - Tooling and Data Format (2026-01-15)

## Power source decision
Status: Done
Deadline: 2026-01-15

Pick ONE primary source for the pilot and explain why:
- [ ] Scaphandre (software estimator)
- [ ] Kepler (software estimator)
- [ ] CPU + NIC counters only (no power yet)

Decision:
- Primary source: **CPU + NIC counters + throughput only (no power yet)**
- Why this is acceptable for a software-first pilot: the goal for Day 4 is to validate scenario timing, logging, and artifact structure; throughput correctness is enough to prove the workload control works.
- What it cannot prove (yet): anything about platform/RU power, energy, or energy-efficiency. Those require either a working estimator (Ubuntu) or a real meter.

Notes on Scaphandre attempt:
- WSL2 does not expose `/sys/class/powercap` (no RAPL counters).
- The Scaphandre Docker attempt failed due to WSL2/Docker sysctl constraints.
- Resolution path: move to a real Linux environment (Ubuntu dual boot) where powercap exists (completed on Day 5).

## Log schema (minimum)
Status: Done
Deadline: 2026-01-15

Define the minimum columns you guarantee:

`power.csv`
- `timestamp_utc`
- `scenario_state`
- `power_w` (or blank if not available)

Day 4 outcome:
- `power.csv` is **not produced** for this day because power is unavailable in WSL2.

`kpi.csv` (or `traffic.csv`)
- `timestamp_utc`
- `throughput_mbps`
- `bytes_total` (if available)
- `cpu_util_pct` (optional)
- `nic_rx_bytes`, `nic_tx_bytes` (optional)

Day 4 outcome:
- We store iperf3 outputs directly:
	- `iperf_load_m.json`
	- `iperf_load_m.txt`
- We store UTC markers separately in `utc_markers.txt`.

## Metadata (must be reproducible)
Status: Done
Deadline: 2026-01-15

`run.md` should include:
- Machine info: OS/kernel, CPU
- Tool versions
- Scenario windows + targets
- Notes about noise/anomalies

Day 4 outcome:
- `runs/2026-01-15/pilot-scaphandre-iperf/run-01/run.md` captures WSL2 kernel, iperf mode/target/duration, and why power is unavailable.

## Analysis inputs/outputs
Status: Done
Deadline: 2026-01-15

Inputs:
- power samples + timestamps
- traffic stats for DV (data volume)

Outputs:
- Mean power per state
- Energy per state (Wh/J)
- Energy per bit (J/bit) if DV available

Day 4 outcome:
- Only throughput/KPI validation is possible.
- Power/energy outputs are deferred to Day 5 (Ubuntu) artifacts.

## Publishing language (avoid over-claiming)
Status: Done
Deadline: 2026-01-15

Use this wording pattern:
- “platform power under RU-like workload” (software-first)
- “RU wall/input power” (requires PDU/analyzer)

Write the 2–3 sentences you will put in your report:

"This pilot validates our workload control and artifact logging pipeline using iperf3 and UTC markers. Power and energy are intentionally not reported here because WSL2 does not expose the required powercap/RAPL interfaces for Scaphandre. Power-enabled results are reported separately once the estimator runs on a full Linux environment (Ubuntu)."
