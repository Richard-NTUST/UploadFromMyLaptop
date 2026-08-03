# Day 1–Day 2 Recap (2026-01-12 to 2026-01-13)

## One-paragraph summary
I am working toward **RU power consumption measurement replication**, but during probation I am limited to a **software-only setup** (no RU hardware and no external power instrumentation in my possession). So the probation deliverable is a **repeatable measurement + analysis method** and a **software-only pilot result** (platform power under RU-like workload) that proves my logging, timing, metrics, and scenario structure are solid. When hardware becomes available, the same method will be applied to **RU AC input power** (smart PDU/power analyzer) to complete the RU-specific replication.

## What we’re trying to do (goal)
- Build a reproducible way to measure/report energy behavior across state-style scenarios:
  - **Idle** (stack not running / cell not enabled)
  - **Active-idle** (stack running + cell enabled + no user traffic)
  - **Load sweep** (low / medium / high)
- Produce outputs that are easy to compare run-to-run and later compare to a baseline:
  - One **power vs time** plot
  - A small table of **mean power** and **energy** per scenario

## Constraint (important)
- **Software-only during probation**:
  - I can validate the method on the compute host (power estimation + KPIs + timestamps).
  - I do **not** claim RU wall power results yet.

## Decisions we froze (so we don’t keep reworking definitions)
### Measurement point
- **Now (probation):** platform-level power/energy estimate on the compute host running the workload (software tools like Scaphandre/Kepler).
- **Later (target):** RU AC input power measured via smart PDU outlet or power analyzer.

### Metrics
- **Power:** average real power $P$ (W) over a defined steady-state window.
- **Energy:** energy $E$ (Wh/J) computed over the same window (integration/sum over samples).
- Optional later: efficiency metrics such as $J/bit$ once traffic accounting is reliable.

### Load definition
- **Primary:** throughput target (DL Mbps) using `iperf3`.
- **Secondary context (if available):** CPU utilization; PRB utilization is a follow-up improvement if telemetry becomes available.

### Run timing
- **2 min warm-up + 5 min steady-state** per scenario.
- Focus analysis on the steady-state interval; avoid fast-transient claims.

## Baseline we used
- **POET (WINLAB) paper** as methodology/pipeline reference and for the idea of comparing measurement methods.
- I treat POET as primarily a **measurement platform/method** baseline; the RU-specific replication is the longer-term goal.

## What we produced in these 2 days
### Day 1 outputs
- A clear scope note (what power/energy means, where to measure, which metrics matter).
- A baseline extraction note (what POET measures, what plots it shows, what I can reproduce first).

### Day 2 outputs
- A “boundaries lock” note that freezes the probation definitions and explicitly states in-scope vs out-of-scope.
- A probation goals file (Month 1 + Week 1–4 session titles/checklists) that matches the boundaries.

## Where to read the canonical notes
- Day 1 scope: `docs/StudyNotes/2026-01-12_RU-Measurement-Scope.md`
- Day 1 baseline: `docs/StudyNotes/2026-01-12_WINLAB-Baseline.md`
- Day 2 boundaries: `docs/StudyNotes/2026-01-13_Boundaries.md`
- Step 3 (goals/session titles): `docs/Probation-Goals.md`
- Daily progress log: `Daily-Logs.md`

## What “done” looks like for probation
- A frozen definitions doc (measurement point, metrics, load definition, run timing).
- One pilot dataset (software-only) that includes:
  - power time series
  - workload/KPI timestamps
  - scenario start/stop markers
- One plot: power vs time showing at least 3 scenarios (idle / active-idle / one load point).
- One small table: mean power and energy per scenario.

## Sources (quick pointers)
- Local baseline PDF: `assets/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`
- Link scratchpad (Day 2): `assets/13 Jan/Links.md`
- iPerf reference: https://iperf.fr/

## Immediate next step (tomorrow)
- Pick one software-only workload path (e.g., OAI rfsim + `iperf3`) and one power estimator available on my machine.
- Run a single step-test (idle → active-idle → load), log timestamps cleanly, and generate the first power-vs-time plot.
