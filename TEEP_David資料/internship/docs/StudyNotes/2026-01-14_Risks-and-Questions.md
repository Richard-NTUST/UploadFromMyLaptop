# Risks and Questions (2026-01-14)

## Risks / unknowns
Status: Done
Deadline: 2026-01-14

- No RU hardware access yet: risk of drifting into “platform power under RU-like workload” only.
	- Mitigation: label results explicitly; keep an upgrade path to RU AC/DC measurement.
	- Quick diagnostic: can you write one sentence describing your measurement point without mentioning RU hardware?

- No power instrumentation yet: software power estimators can be biased depending on CPU model, kernel support, and virtualization.
	- Mitigation: run repeats, record tool versions, and plan a future cross-check against a real meter.
	- Quick diagnostic: if you reboot and re-run the same scenario, do you get the same per-state mean power within ~5–10%?

- Baseline mismatch risk: WINLAB/POET conditions (RU model, bandwidth, UE emulation, orchestration stack) may not be reproducible.
	- Mitigation: compare trends and normalized metrics such as $J/bit$; keep a configuration table.
	- Quick diagnostic: do you have enough metadata to explain why your watts differ from the paper?

- KPI availability risk: PRB utilization may be unavailable; throughput-only load definition may hide scheduler/PHY effects.
	- Mitigation: treat PRB as follow-up; log CPU, memory, NIC counters as context.
	- Quick diagnostic: if throughput is the same across two runs but power differs, what context metric helps explain it?

- Workload stability risk: `iperf3` throughput can fluctuate due to congestion control or routing changes.
	- Mitigation: fixed windows, consistent client/server placement, and discard ramp periods.
	- Quick diagnostic: does throughput time-series look stable during the steady-state window?

- Time alignment risk: power samples and KPI timestamps may be misaligned.
	- Mitigation: NTP sync, record UTC timestamps, and use window-based statistics.
	- Quick diagnostic: do scenario markers appear at the same time in both logs?

## Software-only run checklist (practical)
- Record UTC timestamps everywhere.
- Record scenario markers (idle/active-idle/load) with start/stop times.
- Record estimator/tool version and machine identity (CPU model).
- Save raw logs (don’t rely only on screenshots).
- Produce one “power vs time” plot before computing any fancy metric.

## Questions for tomorrow check-in
Status: Done
Deadline: 2026-01-14

- For the “hardware-grade” phase later, what is the most realistic RU measurement point to access first (AC input via PDU vs DC rails vs PoE), and what instrument is typically available?
- Which baseline should we treat as authoritative for RU energy benchmarking in this project (WINLAB/POET vs a specific O-RAN/WG spec vs the Open RAN Handbook framing)?
- Which scenarios should be prioritized if we only get one good dataset: (A) idle vs active-idle vs 1 load point, or (B) low/med/high load sweep?
- Are TX power / bandwidth sweeps expected in probation, or are they explicitly “after we can measure RU wall power”?
