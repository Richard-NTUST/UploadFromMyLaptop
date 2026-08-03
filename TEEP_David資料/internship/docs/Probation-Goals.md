# Probation Goals

## Month 1 (Probation): RU Power Consumption Measurement Replication

**Deliverable (end of month):**
- A reproducible measurement + analysis method (documented measurement point + metrics + scenario matrix)
- At least 1 software-only pilot dataset and 1 plot (power vs time) for state-style scenarios (idle/active-idle/load)
- A short comparison write-up vs the chosen WINLAB/POET baseline (trend + limitations)

## Week-by-week sessions

### Week 1: Boundaries + Baseline + Definitions Frozen
- [x] Freeze measurement point + instrument assumptions (Week 1: software power on compute host; target later: RU AC via smart PDU/analyzer)
- [x] Freeze primary metrics (W, Wh/J) + averaging window
- [x] Freeze load definition (throughput) + scenario matrix
- [x] Identify baseline figures/results to reproduce first

### Week 2: Setup + Pilot Run
- [x] Confirm what can be run in software-only mode (OAI rfsim / workload generator) and what power estimator is available
- [x] Run 1 pilot measurement (idle -> active-idle -> load)
- [x] Validate timestamp alignment (power vs KPIs)
- [x] Produce 1 plot (power vs time)

### Week 3: Small Experiment Matrix
- [x] Execute low/med/high load sweeps (repeat runs for noise)
- [x] Produce 2–3 plots (power vs load/state)
- [x] Record deviations from baseline assumptions

### Week 4: Analysis + Write-up
- [x] Summarize results vs baseline (what matches, what doesn’t, why)
- [x] List risks + next steps for the internship phase (see §7 Limitations, §11 Future Work in Final Report; `docs/StudyNotes/2026-01-14_Risks-and-Questions.md`)
- [x] Clean up notes, daily logs, and links
