# Day 5 — Pilot Run With Power (Ubuntu) (2026-01-19)

Status: Done
Deadline: 2026-01-19

## Goal
Run the step-test scenario (idle → active-idle → load) **while Scaphandre is producing power**, and save artifacts so that Plot 1 (power vs time with state annotations) becomes feasible.

Outcome: completed. Artifacts are stored under `runs/2026-01-20/` (timestamps are UTC; the run was executed across the Jan 19/20 boundary).

## Scenario (frozen windows)
- Warm-up: 2 min (ignored)
- Steady-state: 5 min (scored)

States:
1) Idle
2) Active-idle
3) Load (start with one point, e.g., Load-M)

## Commands (copy/paste)
### Start Scaphandre exporter
- `sudo docker run --rm --privileged --pid=host -p 8080:8080 -v /proc:/proc:ro -v /sys:/sys:ro hubblo/scaphandre prometheus --address 0.0.0.0 --port 8080`

### Start power logging (10s cadence)
In a second terminal:
- `mkdir -p runs/2026-01-20`
- `cd runs/2026-01-20`
- `while true; do echo -n "$(date -u +\"%Y-%m-%dT%H:%M:%SZ\") "; curl -s http://localhost:8080/metrics | awk '/scaph_host_power_microwatts/{print $2; exit}'; sleep 10; done | tee power_uw.txt`

(We’ll convert `power_uw.txt` to CSV later; this is the quickest reliable capture.)

### Run traffic (iperf3)
This run used localhost loopback (server and client on the same machine).

- Server:
  - `iperf3 -s`

- Client (TCP, 5 minutes):
  - `iperf3 -c 127.0.0.1 -t 300 --json | tee iperf_tcp_loadm_300s.json`

## State markers (must record)
Recorded in `runs/2026-01-20/markers.md`:
- Active-idle: 06:05:14Z → 06:08:15Z
- Load-M: 06:08:55Z → 06:13:47Z
- Pure Idle: 06:30:25Z → 06:32:05Z

Note: the pure-idle baseline was captured after the load stage; this is acceptable for a baseline as long as the system returned to steady state.

## Artifacts to bring back to the repo (minimum)
Saved under `runs/2026-01-20/`:
- `power_uw.txt` (raw)
- `cleaned_power_uw.md` (cleaned subsets)
- `iperf_tcp_loadm_300s.json`
- `markers.md`
- `summary.md`

## Quick acceptance checks
Power signal:
- Non-zero and strongly state-dependent.
- Means from `cleaned_power_uw.md`:
  - Idle: 1.023 W
  - Active-idle: 1.874 W
  - Load-M: 35.279 W

Traffic (iperf3 TCP):
- Duration: 300.001942 s
- Throughput: 97.464 Gbps (received; sender matches)

Derived quick metric:
- Efficiency (throughput / mean power during load): 97.464 / 35.279 = 2.763 Gbps/W

Data quality:
- Raw `power_uw.txt` contains some earlier timestamp-only noise at the very beginning; the usable segments are extracted in `cleaned_power_uw.md`.

## Next (once artifacts exist)
Next actions to turn this into publishable plots:
- Convert the full power series into a clean CSV (timestamp_utc, power_w).
- Produce Plot 1 (power vs time with state annotations) and Table 1 (per-state means + energy + throughput) per the analysis plan.
