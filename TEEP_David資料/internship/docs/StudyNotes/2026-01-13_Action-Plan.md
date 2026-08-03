# Day 2 - Action Plan (2026-01-13)

## What step 3 means (monthly/weekly session titles)
Status: Done
Deadline: 2026-01-13

Interpretation for this repo:
- A **session title** is a time-boxed goal header (Month/Week) that makes your progress scannable.
- You implement this as **section headings** (and/or GitHub Project titles) like:
  - "Month 1: RU power measurement replication"
  - "Week 1: Boundaries + baseline extraction"
  - "Week 2: Pilot measurement + logging"

Step 3 is tracked here:
- `docs/Probation-Goals.md`

## Month 1 (Probation) - high-level deliverable
Status: Done
Deadline: 2026-01-13

Session title: **Month 1: RU power consumption measurement replication**

Deliverable statement (1-2 sentences):
- Deliver a reproducible RU power measurement method (defined measurement point + metrics + scenario matrix) and demonstrate it with at least one pilot dataset/plot across RU states. Add a short comparison vs the WINLAB/POET baseline framing (trend + limitations), with all assumptions stated.

## Week-by-week sessions
Status: Updated (actionable)
Deadline: 2026-01-13

Session title: **Week 1: Boundaries + baseline + definitions frozen**
- [x] Pick primary baseline doc(s): WINLAB/POET (Day 1) + Open RAN Handbook (definitions) + O-RAN Testing WP (repeatability framing)
- [x] Freeze measurement point + metrics + load definition (see Boundaries note)
- [x] Define minimal scenario matrix + run durations (idle, active-idle, low/med/high load; warm-up + steady)

Session title: **Week 2: Setup + pilot run**
- [x] Confirm what is available: (A) software power exporter on compute host now, (B) smart PDU/power analyzer later
  - Outcome: WSL2 does not expose `/sys/class/powercap`; Scaphandre could not run; power is unavailable in this environment.
- [x] Run 1 pilot “platform power under RU-like workload” measurement and produce 1 plot (power vs time)
  - Outcome: pilot executed as logging-pipeline validation (throughput + UTC markers + artifacts). Power plot deferred.
- [x] Validate timestamp alignment (power vs KPIs)
  - Outcome: UTC markers collected and iperf JSON includes timestamps; alignment is reproducible from artifacts.

Session title: **Week 3: Small experiment matrix**
- [ ] Execute low/med/high load sweeps
- [ ] Repeat runs for noise estimate
- [ ] Produce 2-3 comparison plots

Session title: **Week 4: Analysis + write-up**
- [ ] Summarize results vs baseline (trend + limitations)
- [ ] List risks/next steps for internship phase
- [ ] Clean up notes and daily logs

## Today’s tasks (Day 2)
Status: Done
Deadline: 2026-01-13

- Fill Boundaries note and freeze Week-1 definitions (measurement point, metrics, load definition, run durations)
- Convert unknowns into tomorrow follow-ups (only blockers that affect instrument choice or workload generation)
- Update `Daily-Logs.md` statuses for Day 2
