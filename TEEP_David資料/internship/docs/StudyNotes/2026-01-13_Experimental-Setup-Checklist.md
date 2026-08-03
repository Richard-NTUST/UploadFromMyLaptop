# Experimental Setup Checklist (2026-01-13)

## Equipment list
Status: Done (software-first)
Deadline: 2026-01-13

- Compute host to run workload + logging (Linux preferred)
- Software power estimator/exporter on the host (e.g., Scaphandre or Kepler) OR at minimum OS telemetry (CPU %, NIC bytes)
- Traffic generator: `iperf3` client/server (local LAN)
- Time sync: NTP (or at least consistent UTC timestamps in logs)

Hardware-grade upgrades (when available):
- RU + power source
- Smart PDU outlet / power analyzer to measure RU AC input (or DC rail tools if accessible)
- UE / emulator / RF setup if required by scenario

## Measurement points
Status: Done
Deadline: 2026-01-13

- Primary (software-first): compute host power/energy estimate (platform power under RU-like workload)
- Target (hardware-grade): RU AC input at a single feed (smart PDU/power analyzer)

Signals to log alongside power:
- Throughput (iperf3 Mbps) and bytes transferred (for data volume)
- CPU utilization (%), memory, and NIC counters (bytes/packets)
- Scenario state label (idle / active-idle / load-L/M/H) with start/end timestamps
- Configuration snapshot: bandwidth, numerology, any key “cell on/off” toggles (as applicable)

## Environment + configuration
Status: Done
Deadline: 2026-01-13

- Record versions: OS + kernel, estimator tool version, iperf3 version, and any container/runtime versions
- Clock/time sync: NTP enabled; log timestamps in UTC everywhere
- Calibration notes:
	- Software-first: no meter calibration; instead document estimator limitations and validate via repeats
	- Hardware-grade: record meter model + last calibration date and sampling cadence

Pilot evidence (Day 4):
- iperf3 version observed in artifacts: `iperf 3.16` (from `iperf_load_m.json`)
- WSL2 kernel observed in artifacts: `5.15.167.4-microsoft-standard-WSL2`
