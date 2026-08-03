# Daily Logs
## 2026/01/12
**Short-term Goals**
1. [Define RU power measurement scope + variables](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_RU-Measurement-Scope.md)
2. [Extract WINLAB baseline: scenarios, metrics, expected plots](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_WINLAB-Baseline.md)

**Daily Logs**:
- 09:00-10:30: Define metrics and units (Goal 1: [Metrics definitions](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_RU-Measurement-Scope.md#metrics-definitions))
	(Status: Drafted primary metrics (W, Wh/J) + measurement-point options; set probation defaults for cadence and run length)
- 10:30-12:00: Identify controllable variables + scenarios (Goal 1: [Variables and scenarios](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_RU-Measurement-Scope.md#variables-and-scenarios))
	(Status: Drafted minimal scenario matrix (idle/active-idle/low/med/high load) + run structure compatible with coarse sampling and steady-state analysis)
- 13:00-14:30: Summarize reported WINLAB experimental conditions (Goal 2: [Experimental conditions reported](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_WINLAB-Baseline.md#experimental-conditions-reported))
	(Status: Extracted POET measurement stack details (PDU ~10s, IPMI slower averaging) and noted RU hardware specifics are not fully specified)
- 14:30-16:00: List target plots/tables to reproduce + assumptions (Goal 2: [Reported results to reproduce](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-12_WINLAB-Baseline.md#reported-results-to-reproduce))
	(Status: Confirmed Fig. 4-7 are measurement-method comparisons; added RU-vs-platform scope check + RU-specific extraction checklist)


## 2026/01/13
**Short-term Goals**
1. [Finalize boundaries (in-scope/out-of-scope, frozen definitions, deliverables)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-13_Boundaries.md)
2. [Set monthly/weekly goals (Step 3: session titles)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Probation-Goals.md)

Quick recap for reviewers: [Day 1–Day 2 scope recap](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Day1-Day2-Recap.md)

**Daily Logs**:
- 09:00-10:30: Freeze definitions (measurement point, load definition, run duration) (Goal 1: [Definitions we will freeze](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-13_Boundaries.md#definitions-we-will-freeze-avoid-endless-rework))
	(Status: Frozen for Week 1: software power on compute host (labelled as platform power), real power (W) + energy (Wh/J) over steady-state windows; throughput as primary load definition; warm-up + 5-min steady-state runs)
	(Note: Software-only environment during probation; RU AC input measurement is deferred until hardware exists.)
- 10:30-12:00: Write explicit in-scope vs out-of-scope + probation deliverables (Goal 1: [In-scope vs out-of-scope](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-13_Boundaries.md#in-scope-vs-out-of-scope))
	(Status: Locked scope and acceptance criteria; added explicit limits for coarse polling and non-claims)
- 13:00-14:30: Draft Month/Week sessions as titles + checklist items (Goal 2: [Week-by-week sessions](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Probation-Goals.md#week-by-week-sessions))
	(Status: Action plan updated with Month/Week session titles and Week 1 checklist marked complete)
- 14:30-16:00: Convert unknowns into tomorrow follow-ups + next-day theory topics (Goal 1: [Open questions](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-13_Boundaries.md#open-questions-decision-needed))
	(Status: Reduced to blockers: instrument availability/logging cadence, how to force RU states, simplest controlled load generation, and PRB telemetry availability)


## 2026/01/14
**Short-term Goals**
1. [Study note: energy/power metrics glossary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Energy-Metrics-Glossary.md)
2. [Tutorial: set up Scaphandre power estimator](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Power-Estimator-Setup-Scaphandre.md)
3. [Create analysis plan: plots + metrics + comparison method](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Analysis-Plan.md)
4. [Write risks list + open questions for next check-in](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Risks-and-Questions.md)

**Daily Logs**:

- 10:00-10:30: Write glossary for metrics and terms (Goal 1: [Core quantities](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Energy-Metrics-Glossary.md#core-quantities-what-we-actually-compute))
	(Status: Completed — glossary expanded into a teaching-style primer with units, pitfalls, and efficiency metrics)

- 10:30-11:00: Write Scaphandre setup tutorial + prerequisites (Goal 2: [Recommended setup on Windows](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Power-Estimator-Setup-Scaphandre.md#recommended-setup-on-windows-wsl2--docker))
	(Status: Completed — documented WSL2 limitations and fallback workflow)

- 13:00-14:00: Decide plots/tables you will recreate first (Goal 3: [Plots and tables to reproduce](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Analysis-Plan.md#plots-and-tables-to-reproduce))
	(Status: Completed — prioritized a pilot-ready output set and defined minimal publishables)

- 14:00-15:00: Define computation steps (power -> energy/efficiency) (Goal 3: [Computation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Analysis-Plan.md#computation))
	(Status: Completed — end-to-end calculation steps and windowing guidance)


- 15:15-15:35: Define comparison/acceptance method vs WINLAB (Goal 3: [Comparison method](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Analysis-Plan.md#comparison-method))
	(Status: Completed — defined “match methodology, label scope” acceptance criteria)

- 15:35-16:00: List risks/unknowns + check-in questions (Goal 4: [Software-only run checklist](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Risks-and-Questions.md#software-only-run-checklist-practical))
	(Status: Completed — practical checklist + WSL2-specific constraints)


## 2026/01/15
**Short-term Goals**
1. [Plan the software-first pilot run](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-15_Day-4_Pilot-Run-Plan.md)
2. [Set up and validate Scaphandre power estimation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Power-Estimator-Setup-Scaphandre.md)
3. [Finalize tooling + data format (Day 4)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-15_Day-4_Tooling-and-Data-Format.md)

**Daily Logs**:
- 09:00-10:00: Finalize assumptions + scenario definition (Goal 1: [Scenario definition](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-15_Day-4_Pilot-Run-Plan.md#scenario-definition-exact))
	(Status: Completed — locked software-first pilot scope and fallback logic)
- 10:00-11:30: Install/verify prerequisites (WSL2/Docker) and check energy counters (Goal 2: [Requirements](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Power-Estimator-Setup-Scaphandre.md#requirements-important))
	(Status: Completed — confirmed `/sys/class/powercap` unavailable in WSL2)
- 13:00-14:00: Run Scaphandre and verify `/metrics` output (Goal 2: [Prometheus exporter](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-14_Power-Estimator-Setup-Scaphandre.md#option-b--prometheus-exporter-recommended-for-logging))
	(Status: Completed — Docker container failed on WSL2 due to sysctl read-only; recorded limitation and switched to fallback)
- 14:00-15:30: Execute pilot step-test (idle → active-idle → load) + save raw logs (Goal 1: [Commands](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-15_Day-4_Pilot-Run-Plan.md#commands-copypaste))
	(Status: Completed — ran `iperf3` UDP Load-M at 50 Mbit/s for 300s; saved `.txt` + `.json` + UTC markers)
- 15:30-16:00: Verify artifacts + acceptance checks (Goal 1: [Acceptance checks](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-15_Day-4_Pilot-Run-Plan.md#acceptance-checks-passfail))
	(Status: Completed — artifacts stored in repo under runs/2026-01-15/pilot-scaphandre-iperf/run-01; throughput target met and 0% loss)


## 2026/01/16
**Short-term Goals**
1. [O-RAN fundamentals (Part 1): architecture + CU/DU/RU](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_O-RAN%20Principles.md)
2. [O-RAN control plane (Part 2): RIC + interfaces](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_O-RAN-Principles_Part-2_RIC-and-Interfaces.md)
3. [Get Scaphandre producing power on Intel laptop](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_Scaphandre-Progress_Intel-Laptop.md)

**Daily Logs**:
- 09:00-10:00: Clean O-RAN note structure (Goal 1: [Why this matters for our project](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_O-RAN%20Principles.md#why-this-matters-for-our-project))
	(Status: Completed — converted raw notes into repo-style study note + removed noise)

- 10:00-10:45: Add RIC/interfaces overview (Goal 2: [Key interfaces](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_O-RAN-Principles_Part-2_RIC-and-Interfaces.md#key-interfaces-a1-e2-o1-o2-open-fh-f1e1))
	(Status: Completed — mapped A1/E2/O1/O2/Open FH/F1/E1 into one mental model)

- 13:00-15:30: Scaphandre troubleshooting on Intel laptop (Goal 3: [Quick decision tree](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_Scaphandre-Progress_Intel-Laptop.md#quick-decision-tree))
	(Status: Closed — WSL2 blocked (no `/sys/class/powercap`); resolved later on Ubuntu dual boot with power-enabled artifacts under `runs/2026-01-20/`)

- 15:30-16:00: Update documentation + daily log for publishability (Goal 3: [Logbook](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-16_Scaphandre-Progress_Intel-Laptop.md#logbook-fill-as-you-test))
	(Status: Completed — captured decision path and reproducible next steps)


## 2026/01/19
**Short-term Goals**
1. [Validate Scaphandre on Ubuntu dual boot (evidence bundle)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-19_Scaphandre-Ubuntu-Dualboot.md)
2. [Run pilot step-test with power logging (idle → active-idle → load)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-19_Day-5_Pilot-Run-with-Power.md)

**Daily Logs**:
- 09:00-10:00: Confirm energy counters + environment details (Goal 1: [Step 1 — Verify energy counters exist](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-19_Scaphandre-Ubuntu-Dualboot.md#step-1--verify-energy-counters-exist))
	(Status: Completed — Scaphandre produced a usable power signal on Ubuntu; run artifacts captured under `runs/2026-01-20/`. Follow-up: add `uname -a`, `lscpu`, and `/sys/class/powercap` listings into `runs/2026-01-20/env.md` for evidence.)

- 10:00-11:00: Start Scaphandre exporter and save a `/metrics` snapshot (Goal 1: [Step 3 — Run Scaphandre Prometheus exporter](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-19_Scaphandre-Ubuntu-Dualboot.md#step-3--run-scaphandre-prometheus-exporter-recommended-for-logging))
	(Status: Completed — power logging succeeded. Follow-up: save one Prometheus snapshot (`curl http://localhost:8080/metrics > scaphandre_metrics_snapshot.prom`) into `runs/2026-01-20/`.)

- 13:00-15:00: Execute step-test with power logging + save artifacts (Goal 2: [Artifacts to bring back to the repo](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-19_Day-5_Pilot-Run-with-Power.md#artifacts-to-bring-back-to-the-repo-minimum))
	(Status: Completed — committed run folder under `runs/2026-01-20/` including `power_uw.txt`, `cleaned_power_uw.md`, `iperf_tcp_loadm_300s.json`, `markers.md`, `summary.md`.)

- 15:00-16:00: Record state markers + quick acceptance checks (Goal 2: [Quick acceptance checks](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-19_Day-5_Pilot-Run-with-Power.md#quick-acceptance-checks))
	(Status: Completed — state means clearly separate (Idle 1.023 W, Active-idle 1.874 W, Load 35.279 W) and TCP load reached 97.464 Gbps for 300 s; markers stored in `runs/2026-01-20/markers.md`.)


## 2026/01/20
**Short-term Goals**
1. [Turn the Jan 19/20 run into publishables (Plot 1 + Table 1)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-20_Day-6_Analysis-and-Today-Plan.md)
2. Close Week 2 by producing at least 1 plot (power vs time) and a per-state table
3. Capture the missing evidence bundle (`env.md` + `scaphandre_metrics_snapshot.prom`)

**Daily Logs**:
- 09:00-10:00: Generate Plot 1 + Table 1 from `runs/2026-01-20/` (Goal 1: [Generate artifacts](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-20_Day-6_Analysis-and-Today-Plan.md#1-generate-plot-1--table-1-from-the-run-folder))
	(Status: Completed — generated `runs/2026-01-20/derived/plot_1_power_vs_time.svg`, `runs/2026-01-20/derived/table_1_per_state.md`, and `runs/2026-01-20/derived/power.csv` via `py .\\scripts\\analyze_power_run.py .\\runs\\2026-01-20`.)

- 10:00-10:30: Sanity-check derived outputs + link them in notes (Goal 1: [Acceptance checks](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-20_Day-6_Analysis-and-Today-Plan.md#1-generate-plot-1--table-1-from-the-run-folder))
	(Status: Completed — confirmed state separation in plot; table rows exist for Active-idle, Load-M, and Pure Idle with plausible efficiency values.)

- 13:00-14:00: Capture evidence bundle on Ubuntu (Goal 3: [Evidence bundle](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-20_Day-6_Analysis-and-Today-Plan.md#2-capture-the-missing-evidence-bundle-ubuntu))
	(Status: Completed — created `runs/2026-01-20/env.md` and `runs/2026-01-20/scaphandre_metrics_snapshot.prom` with required metadata.)

- 14:00-15:00: Decide next run improvement and queue Week 3 matrix (Goal 2: [Next run improvement](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-20_Day-6_Analysis-and-Today-Plan.md#3-decide-the-next-run-improvement-so-week-3-is-straightforward))
	(Status: Completed — Decision: Add Load-L and Load-H points (3x repeats) to map the power curve. See `runs/2026-01-20/derived/notes_next_run.md`.)


## 2026/01/21
**Short-term Goals**
1. [Design Week 3 Load Sweep experiment (L/M/H matrix)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-21_Day-7_Experiment-Setup.md)
2. Create reusable bash script for consistent timing/markers

**Daily Logs**:
- 09:00-10:00: Define Week 3 experiment parameters (Goal 1: [Experiment Design](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-21_Day-7_Experiment-Setup.md#experiment-design-from-decision-log))
	(Status: Defined structure: `Idle -> [Load-L(30%) -> Idle -> Load-M(60%) -> Idle -> Load-H(100%) -> Idle] x 3` to capture linearity and thermal consistency.)

- 10:00-11:00: Write automation script `week3_load_sweep.sh` (Goal 2: [Create execution script](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-21_Day-7_Experiment-Setup.md#2-create-the-execution-script-powershellbash))
	(Status: Created `scripts/week3_load_sweep.sh`. It handles `iperf3` execution with variable bandwidths, logs UTC markers automatically to CVS, and enforces precise cool-down periods.)

- 13:00-14:00: Dry-run validation on Ubuntu (Goal 2: [Test the script](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-21_Day-7_Experiment-Setup.md#3-test-the-script-logic-dry-run))
	(Status: Completed — Executed full logic check. Initial run dumped files to root (fixed in script v2). Artifacts saved to `runs/2026-01-21/bandwidth-test`. Confirmed L/M/H logic works.)

- 14:00-15:00: Study Note: O-RU Architecture & Power (Goal 3: [O-RU Deep Dive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-21_O-RU-Deep-Dive.md))
	(Status: Completed — Created a focused note on RU internal components (PA, Low-PHY) and the power implications of the 7.2x split.)

- 15:00-16:00: Validation of Dry Run Data (Goal: Validate script accuracy)
	(Status: Created `scripts/plot_bandwidth_dry_run.py` and generated [`bandwidth_validation.png`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/2026-01-21/bandwidth-test/bandwidth_validation.png). Confirmed precise bandwidth shaping at 30G, 60G, and Max.)

## 2026/01/22
**Short-term Goals**
1. [Execute Week 3 Power Sweep Experiment](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-22_Week3-Run-Log.md)
2. Process and visualize power linearity data

**Daily Logs**:
- 09:00-10:30: Experiment execution on Ubuntu (Goal 1: [Run Log](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-22_Week3-Run-Log.md))
	(Status: Complete. Executed full sweep (L/M/H) with `scaphandre` and [`week3_load_sweep.sh`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/week3_load_sweep.sh). Captured ~20 minutes of power data.)
- 10:30-12:00: Data extraction and preprocessing (Goal 2)
	(Status: Complete. Transferred `power_uw.txt`, `markers.md`, and server-side `iperf.txt` to [`runs/2026-01-22/`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-22). Updated the [analysis script](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/analyze_week3_data.py) to parse explicit Start/Stop markers and build scoring windows.)
- 13:00-14:30: Visualization and Linearity Analysis (Goal 2)
	(Status: Complete. Generated [Power Timeline](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-22/plots/power_timeline.png) and [Linearity Boxplot](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-22/plots/power_linearity_boxplot.png), and produced reviewer-proof stats using trimmed scoring windows (10s trimmed at start/end of each segment): [Stats Summary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-22/plots/stats_summary.md) and [Repeatability](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-22/plots/repeatability_per_run.md). Result: strong step-function from Idle (~1–2 W) to Active (~50 W), with weak scaling across Load-L/M/H.)
- 14:30-16:00: Documentation of findings (Goal 1)
	(Status: Complete. Updated [Run Log](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-22_Week3-Run-Log.md) with interpretation (hypothesis/evidence/limitations/next experiment) and linked the trimmed outputs. Archived traffic evidence and created a summary mapping iperf tests to segments: [iperf_summary.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/2026-01-22/iperf_summary.md). Noted caveat: because `iperf3 -P 4` was used, the nominal “30G/60G” targets appear multiplied in aggregate throughput.)

## 2026/01/23
**Short-term Goals**
1. [Confirm Load Definitions (Single Stream vs Parallel)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-23_Day-8_Confirm-Load-Definition-and-CPU-Behavior.md)
2. Capture CPU P-state/Governor evidence

**Daily Logs**:
- 09:00-10:00: Validate iperf3 bandwidth flags (Goal 1: [Confirm Load Definition](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-23_Day-8_Confirm-Load-Definition-and-CPU-Behavior.md))
	(Status: Complete. Confirmed via single-stream tests that `iperf3 -P 1 -b 30G` delivers exactly 30Gbps, validating that yesterday's `30G x 4` configuration was effectively saturating total throughput.)
- 10:00-12:00: Re-run Power Sweep with `-P 1` (Goal 1: [Load Definition](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-23_Day-8_Confirm-Load-Definition-and-CPU-Behavior.md))
	(Status: Complete. Executed full sweep on Ubuntu with regulated single-stream loads. Run artifacts saved to [`runs/2026-01-23/`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-23). Analysis revealed that without parallelism, the "step-function" to 48W disappears, and the platform remains efficient (~7-8W) even at 60Gbps.)
- 13:00-14:00: CPU State Analysis (Goal 2: [CPU Behavior](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-23_Day-8_Confirm-Load-Definition-and-CPU-Behavior.md))
	(Status: Complete. Captured `lscpu` and governor data. Identified CPU as Intel Core Ultra 7 (Meteor Lake), confirming that the low power draw under single-stream load is due to efficient P-state/E-core handling of network interrupts.)

## 2026/01/26
**Short-term Goals**
1. [Virtual O-RU model (assumptions + validation plan)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-26_Day-9_Virtual-ORU-Power-Model.md)
2. [Gap analysis (proxy vs estimated O-RU)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-26_Day-9_Gap-Analysis-Proxy-vs-ORU.md)
3. Prepare Week 4 Report Draft

**Daily Logs**:
- 09:00-11:00: Develop "Virtual O-RU" Simulation Notebook (Goal 1)
	(Status: Complete. Created [`notebooks/Week4_Virtual_ORU_Simulation.ipynb`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/notebooks/Week4_Virtual_ORU_Simulation.ipynb) to model standard O-RU power behavior ($P_{static} + \Delta\cdot L$) and parse the sweep marker log to reconstruct load **aligned to timestamps**.)
- 11:00-12:00: Generate Gap Analysis Visualization (Goal 2)
	(Status: Complete. Produced [`gap_analysis_simulation.png`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-26/plots/gap_analysis_simulation.png) overlaying real single-stream data against the 300W O-RU model. Added sensitivity band plot [`gap_analysis_sensitivity.png`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-26/plots/gap_analysis_sensitivity.png) and a trimmed-window summary [`gap_analysis_sensitivity_summary.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-26/plots/gap_analysis_sensitivity_summary.md) to make conclusions robust to RU parameter choices.)
- 13:00-14:00: Document Findings + Week 4 framing (Goal 2 + Goal 3)
	(Status: Complete. Split Day 9 documentation into: [Virtual O-RU model note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-26_Day-9_Virtual-ORU-Power-Model.md) (assumptions + validation plan) and [Gap analysis note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-26_Day-9_Gap-Analysis-Proxy-vs-ORU.md) (interpretation + what we can/cannot claim).)


## 2026/01/27
**Short-term Goals**
1. [Replace placeholder RU parameters with citation-backed anchors](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-27/pdf_scan/ru_anchor_citations.md)
2. [Make Week 4 artifacts consistent + reviewer-ready (plots + summary)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-26/plots/gap_analysis_sensitivity_summary.md)
3. [Improve Day 9 notes for long-term studying](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-26_Day-9_Virtual-ORU-Power-Model.md)

**Daily Logs**:
- 09:00-10:30: Literature anchoring (RU parameters)
	(Status: Complete. Extracted citation-backed RU power anchors from [P12.pdf](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-12/WINLAB%20Baseline/P12.pdf): Macro RU $P_{min}=197$ W, $P_{max}=531$ W; Micro RU $P_{min}=59$ W, $P_{max}=110$ W. Integrated these into the Week 4 model and sensitivity sweep.)

- 10:30-12:00: Notebook hardening + regeneration
	(Status: Complete. Updated [Virtual ORU Simulation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/notebooks/Week4_Virtual_ORU_Simulation.ipynb) to use P12 Macro as the baseline and include Macro+Micro anchors in the sweep; fixed sensitivity plotting to compute the RU band columns even if cells are run out-of-order. Regenerated outputs:
	- [Gap Analysis Sensitivity](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-26/plots/gap_analysis_sensitivity.png)
	- [Gap Analysis Sensitivity Summary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-26/plots/gap_analysis_sensitivity_summary.md) (now includes explicit P12 macro/micro anchors and derived $\Delta$))

- 13:00-14:00: Documentation upgrades (study notes)
	(Status: Complete. Expanded the Day 9 model note with a parameter table, derived model points at $L\in\{0,0.3,0.6,1\}$, and a concrete proxy-vs-RU comparison using trimmed medians. Added a “numbers at a glance” block to the gap analysis note. Finalized citation traceability by recording exact page/section/figure locations for P12 and POET anchors in [ru_anchor_citations.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-27/pdf_scan/ru_anchor_citations.md) and embedding them into the Day 9 notes.)


## 2026/01/28
**Short-term Goals**
1. [Run Week 4 “gap” sweep with real power logging](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-28/sweep-01)
2. Generate publishable Week 4 outputs (plots + summary):
	- [gap_analysis_simulation.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_simulation.png)
	- [gap_analysis_sensitivity.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity.png)
	- [gap_analysis_sensitivity_summary.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md)
3. [Study note: Day 10 recap (Week 4 real-power gap sweep)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-28_Day-10_Week4-Gap-Sweep-Real-Power-Run.md)

**Daily Logs**:
- 10:00-11:00: Execute Week 4 sweep (Idle + Load-L/M/H × 3) with power logging
	(Status: Complete. Captured numeric `power_uw.txt` + real `markers.csv` and generated `power_labeled.csv` in the run folder: [runs/2026-01-28/sweep-01](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-28/sweep-01))

- 11:00-12:00: Regenerate Week 4 publishables (gap plots + trimmed summary)
	(Status: Complete. Outputs written under `assets/2026-01-28/plots/`:
	- [gap_analysis_simulation.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_simulation.png)
	- [gap_analysis_sensitivity.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity.png)
	- [gap_analysis_sensitivity_summary.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md))

- 13:00-18:00: Consolidate “numbers at a glance” for publication
	(Status: Complete. Trimmed-window medians from the [sensitivity summary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md):
	- Proxy idle median: 5.696 W
	- Proxy active median: 24.983 W
	- Proxy high-load median: 26.926 W
	Derived RU/proxy ratios (P12 anchors): micro idle 10.36×; macro idle 34.59×; micro full-load 4.09×; macro full-load 19.72×.)

## 2026/01/29
**Short-term Goals**
1. [Verify Digital Ceiling (Max CPU Power) to close Gap Analysis](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-29/digital-ceiling)
2. [Draft IEEE Methodology Section for Final Report](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/01_Methodology_Reproducible_Measurement.md)
3. [Study Note: Why "Simple" Tools Work (Methodology Background)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-29_Methodology_Background_and_Tools.md)

**Daily Logs**:
- 09:00-10:00: Execute "Digital Ceiling" Stress Test (Goal 1)
	(Status: Complete. Ran `stress-ng` (all cores) + Scaphandre. Measured Peak Power at **~59.05 W** before thermal/battery throttling. Result is stored in [`runs/2026-01-29/digital-ceiling/`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-29/digital-ceiling).)

- 10:00-11:00: Analyze Digital Ceiling vs O-RU Baseline (Goal 1: [Digital Ceiling note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-29_Methodology_Background_and_Tools.md))
	(Status: Complete. Conclusion: Even at 100% thermal load (59W), the proxy hardware is **~140W below** the *minimum idle* power of a Macro O-RU (197W). This definitively proves the "Gap" is due to physical RF hardware, not software efficiency.)

- 13:00-15:00: Documentation: Write IEEE Methodology Chapter (Goal 2)
	(Status: Complete. Created [`docs/FinalReport/01_Methodology_Reproducible_Measurement.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/01_Methodology_Reproducible_Measurement.md) detailing the Measurement Point (RAPL), Metrics (Trimmed Median), and Automation Matrix for the final report.)

- 15:00-16:00: Study Note: Methodology Deep Dive (Goal 3)
	(Status: Complete. Wrote [`docs/StudyNotes/2026-01-29_Methodology_Background_and_Tools.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-29_Methodology_Background_and_Tools.md) explaining why `Scaphandre` + `Bash` is the correct engineering approach compared to complex visualizers, focusing on timestamp precision over UI flashiness.)

## 2026/01/30
**Short-term Goals**
1. [Study Note: WiFi Theory Deep Dive & O-RAN Integration](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-30_WiFi-Theory-DeepDive.md)
2. [Implement srsRAN ZMQ Virtual Radio Stack](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-30_Current-Progres-srsRAN.md)

**Daily Logs**:
- 09:00-11:00: Theory Study - WiFi Architecture vs O-RAN (Goal 1: [WiFi Theory DeepDive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-30_WiFi-Theory-DeepDive.md))
	(Status: Complete. Analyzed protocol stack differences, offloading mechanics, and component mapping (AP vs gNB, RIC vs WLC). Produced deep-dive note.)
- 11:00-13:00: Environment Migration to Official srsRAN Images (Goal 2: [srsRAN Progress](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-30_Current-Progres-srsRAN.md))
	(Status: In Progress. Abandoned unstable generic images for official `srsRAN_Project` (gNB) and `srsRAN_4G` (UE). Established clean Docker Bridge `10.53.1.0/24`.)
- 14:00-16:00: Core & Transport Troubleshooting (Goal 2: [srsRAN Progress](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-30_Current-Progres-srsRAN.md))
	(Status: Complete. Fixed Open5GS AMF binding (`127.0.0.5` -> `0.0.0.0`) to allow container listeners. Enabled host SCTP modules (`sctp`, `nf_conntrack_sctp`) for N2 signaling.)
- 16:00-17:30: Debugging "gNB Deadlock" (Goal 2: [srsRAN Progress](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-01-30_Current-Progres-srsRAN.md))
	(Status: Blocked. Identified "Frozen Clock" issue: gNB waits for I/Q samples from UE to tick. UE failing start due to ZMQ channel mismatch (2-channel default vs 1-channel config). Fix identified for tomorrow: sanitizing `ue_zmq.conf`.)

## 2026/02/02
**Short-term Goals**
1. [Analysis: How Much Energy is Needed to Run a Wireless Network? (Auer et al.)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper1.md)
2. [Analysis: Energy Efficiency Improvements through Micro Sites (Fehske et al.)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper2.md)
3. [Analysis: A Parameterized Base Station Power Model (Holtkamp et al.)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper3.md)
4. [Analysis: Deploying Dense Networks for Maximal Energy Efficiency (Björnson et al.)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper4.md)
5. [Generate Final Report: Results & Comparison Chapter](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/02_Results_and_Comparison.md)

**Daily Logs**:
- 11:00-14:00: Deep Dive Literature Review (Goal 1)
	(Status: Complete. Analyzed 4 seminal papers on Base Station energy efficiency ([Auer](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper1.md), [Fehske](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper2.md), [Holtkamp](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper3.md), [Björnson](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-02/Paper4.md)). Key findings synthesized for final report context:
	- **The Energy Gap:** Confirmed network energy is 80% BS-dominated, and mostly static ($P_{static}$) regardless of load.
	- **The Trap:** Small cells fail if offset power is high.
	- **The Mathematical Justification:** Confirmed why our software measurements (low power, high load sensitivity) align with the papers' definitions of Baseband/Digital processing, while the missing ~200W "Gap" is correctly attributed to the PA/Cooling components we lack.)

- 14:00-17:00: Final Report Production: Results & Comparison (Goal 2)
	(Status: Complete. Created [`docs/FinalReport/02_Results_and_Comparison.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/02_Results_and_Comparison.md).
	- **Visuals:** Embedded the Sensitivity and Gap Analysis plots from [`runs/2026-01-28`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-28).
	- **Data:** Reported the key medians (Idle ~5.7W, Peak ~26.9W) and the massive Proxy-to-Hardware idle ratio (~34x).
	- **Narrative:** Wrote the "Gap Analysis" discussion, explicitly linking our results to the static power overhead of Radio hardware proved in the literature review. This closes the "Comparison vs Baseline" deliverable.)

## 2026/02/03
**Short-term Goals**
1. [srsRAN Scheduler Deep Dive: Architecture & Power Analysis](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-03_srsRAN-Scheduler-Deep-Dive.md)
2. [Final Report: Standard Operating Procedure](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/03_Standard_Operating_Procedure.md)

**Daily Logs**:
- 09:00-11:00: srsRAN Code Analysis (Goal 1: [Scheduler Deep Dive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-03_srsRAN-Scheduler-Deep-Dive.md))
	(Status: Complete. Analyzed the MAC scheduler implementation in `intra_slice_scheduler.cpp`. confirmed that the default resource allocation strategy utilizes Frequency Domain Multiplexing (FDM), which prevents O-RU sleep states. Identified the function `get_max_grants_and_rb_grant_size` as the key target for enabling Time Domain Multiplexing (TDM) bursting.)
- 11:00-12:00: Final Report SOP (Goal 2)
	(Status: Complete. Documented the repeatable procedure for the "Gap Run" in [`docs/FinalReport/03_Standard_Operating_Procedure.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/03_Standard_Operating_Procedure.md). This fulfills the requirement for a clear reproduction guide.)
- 13:00-15:00: Deliverable Organization
	(Status: Complete. Restored directory structure after an accidental move. Verified all links in `Daily-Logs.md`.)

## 2026/02/04
**Short-term Goals**
1. [Virtual O-RU: Simulate FDM vs TDM Power Behavior](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/notebooks/Week4_Virtual_ORU_Simulation.ipynb)
2. [Generate "Potential Savings" visualization for Final Report](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/04_Future_Work_and_Recommendations.md)
3. [Study Note: Burst Experiment Validation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-04_Burst-Experiment-Validation.md)

**Daily Logs**:
- 09:00-10:00: Plan TDM Simulation
	(Status: Complete. Updated the [Virtual O-RU notebook](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/notebooks/Week4_Virtual_ORU_Simulation.ipynb) to model "Burst Mode" (TDM) enabling micro-sleep, contrasting it with the current "Always On" (FDM) baseline. Generated [Simulation Plot](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-04/plots/fdm_vs_tdm_savings.png) showing potentially ~103W savings at 30% load for a Macro RU.)
- 10:00-11:00: Draft Future Work & Recommendations
	(Status: Complete. Created [`docs/FinalReport/04_Future_Work_and_Recommendations.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/04_Future_Work_and_Recommendations.md). Synthesized the simulation results into a concrete roadmap for Stage 2 (Main Internship), focusing on implementing the scheduler clamp and validating it with physical O-RU hardware.)
- 13:00-14:00: Design & Execute Burst Experiment (Goal: Empirical Validation)
	(Status: Complete. Developed a bash script [`scripts/run_burst_experiment.sh`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/run_burst_experiment.sh) to mimic TDM via `iperf3` bursting (30% duty cycle at Max Rate) against a smooth baseline (30% constant rate). Executed on testbed. Documented the full methodology and results in [Study Note: Burst Experiment Validation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-04_Burst-Experiment-Validation.md).)
- 14:00-15:00: Analyze Burst Experiment Results
	(Status: Complete. Processed `power_uw.txt` using markers from [`runs/2026-02-04/burst-experiment/`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-02-04/burst-experiment).
	- **Finding:** "Bursting" (TDM Proxy) consumed **11.25 W** avg, while "Smooth" (FDM Proxy) consumed **21.78 W** avg.
	- **Result:** A **48% power reduction** (~10.5W) was achieved by allowing the CPU to Race-to-Sleep. This provides strong empirical evidence validating the "Future Work" recommendation.)


## 2026/02/05
**Short-term Goals**
1. [Two-host sweep: finalize analysis outputs (plots + trimmed-window statistics)](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-02-05/sweep-120233)
2. [Integrate two-host results into the final report draft + generate shareable exports (HTML/DOCX)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/00_Final_Report_Draft.md)
3. [Fix power-capture script robustness (Prometheus metrics parsing)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/run_week4_gap_run.sh)

**Daily Logs**:
- 09:00-10:00: Repair and validate two-host run artifacts (Goal 1)
	(Status: Complete. Replaced corrupted run power log in the two-host sweep folder with the correct `power_uw.txt`, then reran analysis successfully. Run folder: [`runs/2026-02-05/sweep-120233`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-02-05/sweep-120233))

- 10:00-11:30: Generate reviewer-safe plots + statistics from trimmed scoring windows (Goal 1)
	(Status: Complete. Generated timeline + linearity plots, plus trimmed-window summary tables under:
	- [`assets/2026-02-05/plots`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/assets/2026-02-05/plots)
	- Stats: [`stats_summary.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-05/plots/stats_summary.md)
	- Repeatability: [`repeatability_per_run.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-02-05/plots/repeatability_per_run.md))

- 11:30-12:00: Summarize iperf throughput from per-segment client logs (Goal 1)
	(Status: Complete. Created an [`iperf_client_summary.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/2026-02-05/sweep-120233/iperf_client_summary.md) table for the two-host sweep using the per-segment client outputs.)

- 13:00-14:30: Integrate two-host results into the final report draft (Goal 2)
	(Status: Complete. Added a new "Two-host sweep (Windows sink)" subsection and linked the 2026-02-05 figures: [`00_Final_Report_Draft.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/00_Final_Report_Draft.md))

- 14:30-15:30: Generate shareable report exports (Goal 2)
	(Status: Complete. Produced:
	- HTML: [`00_Final_Report_Draft.html`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/00_Final_Report_Draft.html)
	- DOCX: [`00_Final_Report_Draft.docx`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/00_Final_Report_Draft.docx))

- 15:30-16:00: Fix power-capture robustness in the sweep runner (Goal 3)
	(Status: Complete. Patched the Scaphandre Prometheus scrape parsing to ignore `# HELP/# TYPE` lines and capture the numeric `scaph_host_power_microwatts` sample reliably: [`run_week4_gap_run.sh`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/run_week4_gap_run.sh))

## 2026/02/06
**Short-term Goals**
1. [Compile IEEE LaTeX final report on Overleaf](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/docs/FinalReport/Final%20Report%20PDF.pdf)
2. [Run Week 4 Virtual O-RU simulation notebook and verify all outputs](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/notebooks/Week4_Virtual_ORU_Simulation.ipynb)
3. [Clean up study notes for professional language](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/docs/StudyNotes/) <- General review across all notes

**Daily Logs**:
- 09:00-10:00: Compile LaTeX and verify PDF output (Goal 1)
	(Status: Complete. Compiled `docs/FinalReport/00_Final_Report.tex` with `references.bib` on Overleaf. Verified all sections, tables, and equations render correctly in IEEE conference format. Exported the [final PDF deliverable](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/Final%20Report%20PDF.pdf).)

- 10:00-11:00: Run Virtual O-RU simulation notebook (Goal 2)
	(Status: Complete. Executed all cells in [`notebooks/Week4_Virtual_ORU_Simulation.ipynb`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/notebooks/Week4_Virtual_ORU_Simulation.ipynb). Verified gap analysis plots, sensitivity sweeps, and FDM vs TDM savings visualization all generate correctly. Output plots saved to `assets/`.)

- 11:00-11:30: Update README deliverables checklist (Goal 3)
	(Status: Complete. Updated the [README](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/README.md) with current deliverable status and links.)

- 13:00-16:00: Professional language cleanup across all study notes (Goal 4)
	(Status: Complete. Reviewed and updated all 35 study notes under [`docs/StudyNotes/`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/docs/StudyNotes) to use professional language.)

## 2026/02/10
**Short-term Goals**
1. [Identify post-deliverable improvement opportunities](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Probation-Goals.md)
2. [O-RAN Energy Saving Deep Dive: Standards, Sleep Modes & Project Connection](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md)
3. [Fix remaining report issues + finalize documentation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/00_Final_Report_Draft.md)

**Daily Logs**:
- 09:00-10:00: Workspace analysis for improvement opportunities (Goal 1: [Probation Goals](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Probation-Goals.md))
	(Status: Complete. Identified 4 actionable items: (1) O-RAN ES deep-dive study note, (2) unchecked probation-goals risk item, (3) placeholder references in report, (4) duplicate Section 9 numbering. Prioritized the deep-dive note as primary knowledge-building task.)

- 10:00-13:00: Extract and synthesize O-RAN NES specifications (Goal 2)
	(Status: Complete. Used `pdftotext` and Python DOCX extraction to process 8 source documents (WG1 NESUC, WG7 NES, WG2 A1AP, WG4 MP, SuFG NES Analysis, SuFG White Paper, Liang et al. xApp paper, Wadud & Afraz ns3-oran paper) from [`assets/2026-02-10/`](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/assets/2026-02-10). Extracted key content: NES use cases, SM0–SM3 sleep modes with CUS-plane commands, RIC control loops (A1 Policy → E2 execution), energy KPIs (DEE/DEERU/LEE), Phase 3 features, RU power model equations.)

- 13:00-15:00: Write O-RAN Energy Saving Deep Dive study note (Goal 2: [O-RAN Energy Saving Deep Dive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md))
	(Status: Complete. Created comprehensive 12-section deep-dive note.
	- **Key sections:** 4 NES use cases (UC1–UC4), SM0–SM3 definitions + wake-up times, Non-RT RIC / Near-RT RIC control loops, energy savings estimates (All RF off: 80–99%, RF band off: 40–50%), RU power modelling equations from ns3-oran, xApp-based RC switching algorithms.
	- **Section 10:** "Connection to Our Project" — maps each experiment to its standards basis (Scaphandre/RAPL → PEE.AvgPower, Load sweep → UC1/UC2/UC3 scenarios, Burst → WG1 TDM prioritisation + 3GPP Rel-18 Cell DTX/DRX, srsRAN scheduler deep-dive → E2 control decision point) + identified 5 implementation gaps.)

- 15:00-16:00: Fix report issues and finalize documentation (Goal 3: [Final Report Draft](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/00_Final_Report_Draft.md))
	(Status: Complete. Applied 3 fixes to final report:
	1. Renumbered duplicate Section 9 → Conclusions becomes §10, Future Work §11, References §12.
	2. Replaced placeholder "need full BibTeX later" with proper [S1]–[S6] standards citations (O-RAN specs, 3GPP TS 28.552, ETSI ES 203 228) and [L1]–[L4] literature citations (Liang et al. arXiv 2405.10116v1, Wadud & Afraz arXiv 2509.10978v1).
	3. Checked off the final probation-goals item "List risks + next steps" with reference to §7 Limitations, §11 Future Work: [Probation Goals](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Probation-Goals.md))


## 2026/02/12
**Short-term Goals**
1. [Deep Dive: Intel RAPL & CPU Power Measurement](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-12_RAPL-and-CPU-Power-Measurement-Deep-Dive.md)
2. [Deep Dive: 5G NR Resource Grid & Scheduling Fundamentals](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-12_5G-NR-Resource-Grid-and-Scheduling-Fundamentals.md)
3. [Fix: burst experiment analysis script path bug](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/analyze_burst_experiment.py)

**Daily Logs**:
- 10:00-12:00: Workspace audit for post-deliverable improvements (Goal 1, 2, 3)
	(Status: Complete. Analysed all study notes, scripts, and final report. Identified 3 gaps: (1) no foundational note on RAPL — the measurement tool behind all power data, (2) no 5G NR resource grid primer — assumed knowledge in the scheduler deep-dive, (3) [`analyze_burst_experiment.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/analyze_burst_experiment.py) hardcodes `power_uw.txt` to repo root instead of run directory.)

- 12:00-14:00: Write RAPL & CPU Power Measurement Deep Dive (Goal 1: [RAPL Deep Dive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-12_RAPL-and-CPU-Power-Measurement-Deep-Dive.md))
	(Status: Complete. Created comprehensive 10-section study note covering: RAPL domains (PKG, PP0, PP1, DRAM, PSys) with hierarchy diagram, MSR register addresses, energy counter mechanics + overflow math, measurement vs estimation across CPU generations, Weaver et al. accuracy validation, 3 Linux access methods (powercap/perf/MSR) with code examples, WSL2 limitation explanation, Platypus side-channel security restriction (Linux 5.10+), what RAPL does NOT capture (NIC, RF, PA — explains the "gap"), how Scaphandre wraps RAPL, comparison to PDU/IPMI/power-analyzer alternatives, and Stage 2 measurement architecture diagram.)

- 15:00-17:00: Write 5G NR Resource Grid & Scheduling Fundamentals Deep Dive (Goal 2: [5G NR Resource Grid](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-12_5G-NR-Resource-Grid-and-Scheduling-Fundamentals.md))
	(Status: Complete. Created comprehensive 10-section study note covering: frame/subframe/slot/symbol hierarchy with ASCII diagrams, numerology (µ=0–4) with slot duration and OFDM symbol duration tables, frequency domain (subcarrier → RB → BWP) with RB-count-per-bandwidth table, resource grid visualization (273 RBs × 14 symbols = 45,864 REs per slot), slot formats and TDD patterns (DDDSU), reference signal overhead (SSB/CSI-RS/DMRS) and power implications, FDM vs TDM scheduling with visual comparison diagrams, mini-slots for intra-slot sleep, Cell DTX/DRX (Rel-18) as the standardised version of our burst experiment, and project connection mapping each concept to our experiments.)

- 17:00-18:30: Fix burst experiment analysis script (Goal 3: [Script fix](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/analyze_burst_experiment.py))
	(Status: Complete. Changed `POWER_FILE` from hardcoded `"power_uw.txt"` (repo root) to `os.path.join(RUN_DIR, "power_uw.txt")`. Added CLI argument support (`sys.argv[1]` for custom run directory) and a fallback to repo root with a warning message for backwards compatibility.)


## 2026/02/23
**Short-term Goals**
1. [Deep Dive: EARTH Power Model & Base Station Power Modelling](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md)
2. [Fix: Methodology document typos and language issues](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/01_Methodology_Reproducible_Measurement.md)
3. Workspace audit for post-deliverable improvement opportunities

**Daily Logs**:
- 09:00-10:00: Workspace audit for improvement opportunities (Goal 3)
	(Status: Complete. Reviewed all study notes, final report chapters, scripts, and paper summaries. Identified 2 actionable improvements: (1) the EARTH linear power model $P = P_0 + \Delta_p P_{max} x$ is used implicitly in the Virtual O-RU simulation and gap analysis but was never formally derived in its own study note, (2) the Methodology chapter has 3 typos/capitalization issues — "as an" → "As an", "characterizing" → "characterize", "load Definitions" → "Load Definitions", "work load" → "workload".)

- 10:00-10:30: Fix Methodology document typos (Goal 2)
	(Status: Complete. Applied 3 corrections to [`docs/FinalReport/01_Methodology_Reproducible_Measurement.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/FinalReport/01_Methodology_Reproducible_Measurement.md): capitalised opening sentence, fixed "characterizing" → "characterize" and "load Definitions" → "Load Definitions", and corrected "work load" → "workload".)

- 10:30-15:00: Write EARTH Power Model & BS Power Modelling Deep Dive (Goal 1: [EARTH Power Model](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md))
	(Status: Complete. Created comprehensive 10-section study note covering: the EARTH/E³F core linear equation with full parameter definitions and worked examples, component-level power breakdown (PA/RF/BB/DC-DC/cooling) with weight-by-BS-type table, reference parameter tables from Auer (2011), Holtkamp (2013), and P12 O-RAN anchors, sleep mode extension with piecewise model and duty-cycling average power formula, Holtkamp bandwidth/antenna parameterization, efficiency metrics (EE/APC) mapped to O-RAN WG7 KPIs, synthesis of all 4 literature papers into a unified model evolution timeline, and project connection: (a) derived the Virtual O-RU model as simplified single-chain EARTH, (b) mathematically proved the "gap" as structural PA/RF/cooling absence, (c) validated burst savings against duty-cycling formula (model predicts 9.89 W, measured 11.25 W — 88% accuracy), (d) mapped all measurement terms to EARTH model parameters. Includes a practical equations cheat sheet for quick reference.)


## 2026/02/24
**Short-term Goals**
1. [Study: OAI & srsRAN MAC Scheduler — PRB Scheduling in Frequency and Time Domain](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md)

**Daily Logs**:
- 13:00-20:00: Research and write MAC Scheduler deep dive per professor's directive (Goal 1: [MAC Scheduler PRB Scheduling](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md))
	(Status: Complete. The study note covers: (1) OAI MAC scheduler architecture — `gNB_scheduler.c` top-level slot loop → `gNB_scheduler_dlsch.c` PF algorithm (`pf_dl()`) → `nr_find_nb_rb()` PRB calculation → `rballoc_mask[]` VRB tracking, with annotated code from GitLab source. (2) srsRAN MAC scheduler architecture — `scheduler_impl.cpp` → `cell_scheduler.cpp` → `inter_slice_scheduler.cpp` → `intra_slice_scheduler.cpp` (core FDM/TDM decision point) → `rb_helper::find_empty_interval_of_length()` hole finder, with full module hierarchy and mermaid diagram. (3) Frequency domain scheduling (273 PRBs × 1 slot): how both stacks naturally allocate full BWP to a single UE, DCI RIV encoding math, Resource Allocation Type 1 per TS 38.214. (4) Time domain scheduling (27 PRBs × 10 slots): how to cap `max_rbSize` in OAI or `max_prb` in srsRAN slice config to limit per-slot grants, TBS equivalence verification. (5) Power analysis: EARTH model comparison showing FDM-burst is more energy-efficient (PA sleep in 9/10 slots) vs TDM-spread (PA ON for all 10 slots). (6) Side-by-side OAI/srsRAN module mapping tables, 3GPP standards basis (TS 38.214/213/321/101-1), and practical demonstration plan with verification metrics.)


## 2026/02/26
**Short-term Goals**
1. [Study: DCI Formats & PDCCH — The Scheduler's Air Interface Output](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_DCI-Formats-and-PDCCH-Scheduling-Interface.md)
2. [Study: TBS Determination — Worked Examples for 273 vs 27 PRBs](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Determination-Worked-Examples-273-vs-27-PRBs.md)
3. [Tool: Python TBS Calculator — 273×1 vs 27×10 Equivalence Verification](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/tbs_calculator.py)
4. [Results: TBS Calculator Output — All 57 MCS Configs Verified](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md)

**Daily Logs**:
- 13:00-15:00: DCI Formats & PDCCH study note (Goal 1: [DCI Formats & PDCCH](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_DCI-Formats-and-PDCCH-Scheduling-Interface.md))
	(Status: Complete. Created comprehensive study note covering DCI formats (0_0/0_1/1_0/1_1), key fields (frequency domain assignment, TDRA, MCS), Resource Allocation Type 0 vs Type 1 comparison, RIV encoding worked examples (273 PRBs → RIV=545, 27 PRBs → RIV=7098), CORESET & search space architecture, OAI/srsRAN DCI construction code paths, and scheduling scenario comparison: 273×1 needs 1 DCI vs 27×10 needs 10 DCIs with 10× control overhead.)

- 15:00-17:00: TBS Determination study note (Goal 2: [TBS Worked Examples](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Determination-Worked-Examples-273-vs-27-PRBs.md))
	(Status: Complete. Created study note with full TBS algorithm walkthrough (TS 38.214 §5.1.3.2), MCS Tables 1 & 2, DMRS overhead comparison, and hand-worked examples at MCS 4/15/27 for both 273 and 27 PRBs. Key result: **TBS(273×1) ≈ 10 × TBS(27×1)** within 0.7–1.6%. Includes OAI `nr_compute_tbs()` and srsRAN `tbs_calculator` code paths, sensitivity analysis, and WINLAB throughput back-calculation.)

- 17:00-19:00: Python TBS Calculator implementation and results write-up (Goal 3: [`tbs_calculator.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/tbs_calculator.py), Goal 4: [Calculator Results](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md))
	(Status: Complete. Implemented `scripts/tbs_calculator.py` — a clean Python implementation of the 3GPP TS 38.214 §5.1.3.2 TBS determination algorithm including the TBS lookup table (93 entries for N_info ≤ 3824), formula-based quantisation for N_info > 3824, both MCS Table 1 (64QAM, 29 MCS indices) and Table 2 (256QAM, 28 MCS indices). Ran the script and verified: across all **57 MCS configurations**, TBS(273×1) matches TBS(27×10) within **[−1.09%, +2.66%]** (mean +1.02%). Additional sensitivity tests: layer count (1/2/4) and DMRS addPos (0–3) both preserve the equivalence ratio within ±3%. Created a results study note documenting all output tables, layer/DMRS sensitivity, WINLAB throughput predictions, and the final verdict confirming the professor's equivalence assertion.)


## 2026/02/27
**Short-term Goals**
1. [Study: Cell DTX/DRX (Rel-18) — The Standardized Version of Our Burst Experiment](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md)
2. [For Tomorrow: srsRAN ZMQ Unblock — Step-by-Step Fix for UE Channel Mismatch](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_srsRAN-ZMQ-Unblock-Guide.md)
3. [Study: srsRAN gNB Config Walkthrough — Knobs for 273×1 vs 27×10 Demo](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_srsRAN-Config-Walkthrough-273-vs-27-Demo.md)
4. [Fix: Fill in project-documentation.md placeholder sections](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/project-documentation.md)

**Daily Logs**:
- 14:00-16:00: Cell DTX/DRX study note (Goal 1: [Cell DTX/DRX Rel-18](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md))
	(Status: Complete. Created comprehensive study note connecting 3GPP Rel-18 Cell DTX/DRX to our Feb 4 burst experiment. Key finding: using EARTH model with P12 Macro parameters, Cell DTX at 30% load with SM2 sleep predicts **73% power reduction** (297W → 80W), compared to our empirical 48% on CPU proxy. Mapped all Cell DTX mechanisms to project study notes: burst experiment, TBS equivalence, scheduler intervention points. Documented RRC IE `CellDTX-DRX` configuration and current OAI/srsRAN implementation status (neither stack implements it yet — research opportunity).)

- 16:00-17:30: srsRAN ZMQ Unblock Guide (Goal 2: [ZMQ Unblock Guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_srsRAN-ZMQ-Unblock-Guide.md))
	(Status: Complete. Created step-by-step guide with all 5 configuration files (gnb_zmq.yaml, ue_zmq.conf, Dockerfile.ue, docker-compose.yml, open5gs override). The critical fix: `nof_antennas = 1` in ue_zmq.conf to prevent the 2-channel MIMO panic identified on Jan 30. Includes troubleshooting table, log pattern reference, and MAC PCAP extraction instructions for scheduler analysis.)

- 17:30-19:00: srsRAN Config Walkthrough study note (Goal 3: [Config Walkthrough](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_srsRAN-Config-Walkthrough-273-vs-27-Demo.md))
	(Status: Complete. Documented all srsRAN gNB configuration knobs relevant to the 273×1 vs 27×10 demo. Includes PRB lookup table per bandwidth/SCS, 3 approaches to limiting PRBs (slice config, expert_cfg, code mod), complete YAML examples for both Experiment A (full BW) and Experiment B (27 PRB cap), PCAP analysis instructions with expected RIV values, and a verification checklist.)

- 19:00-20:00: Fill in project-documentation.md (Goal 4: [`project-documentation.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/project-documentation.md))
	(Status: Complete. Filled in all 5 placeholder `<Add component explanation>` sections: Near-RT RIC (platform + ES xApp + HO xApp), CU (CU-CP + CU-UP), DU (with scheduler reference), RU (with gap analysis reference), and UE (Quectel hardware + srsUE software). Removed stray Kubernetes table row.)

## 2026/03/03
**Short-term Goals**
1. [Study: Scheduling Algorithms — Time-Domain vs Frequency-Domain in NR](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-02_Frequencies-in-NR.md)
2. [Source-Code-Verified: srsRAN Scheduler Architecture](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md)

**Daily Logs**:
- 09:00-11:30: Scheduling algorithms study note — two-stage pipeline analysis (Goal 1: [Frequencies in NR](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-02_Frequencies-in-NR.md))
	(Status: Complete with corrections needed. Created comprehensive note covering the two-stage scheduler pipeline in OAI and srsRAN.)

- 11:30-13:00: srsRAN source code deep dive — verified scheduler architecture (Goal 2: [Source-Code-Verified Scheduler](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md))
	(Status: Complete. Read **9 actual source files** across `lib/scheduler/` totalling ~4,000 lines. Key findings: (1) srsRAN has only TWO policies: `scheduler_time_rr` (79 lines, priority = allocation-count-based RR) and `scheduler_time_qos` (418 lines, QoS-aware with internal PF via `compute_pf_metric()` — there is **NO standalone PF policy**). (2) The QoS policy combines 4 sub-weights: PF metric ($R_{inst}/R_{avg}^{\alpha}$), GBR weight, QoS priority weight, and packet delay budget weight. (3) `intra_slice_scheduler::dl_sched()` (937 lines) runs retxs first, then a two-pass newTx allocation: Stage 1 reserves PDCCH/UCI/HARQ, Stage 2 fills VRBs. (4) YAML config uses subcmd sections `qos_sched:` and `rr_sched:` (NOT `policy: time_pf`). (5) Each slice can have its own policy — different algorithms per S-NSSAI.)


## 2026/03/04
**Short-term Goals**
1. [Enabling Time-Frequency Domain Scheduling: Practical Configuration & Code-Path Guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_Enabling-Time-Frequency-Domain-Scheduling.md)
2. [Source-Code-Verified: OAI gNB Scheduler Architecture (Counterpart to srsRAN)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_OAI-Scheduler-Source-Code-Verified.md)

**Daily Logs**:
- **10:30-12:00** — Re-read existing study notes ([02-24 OAI-srsRAN MAC Scheduler](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md), [03-03 srsRAN Verified](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md)) to identify gaps in OAI coverage.
- **12:00-13:00** — Fetched actual OAI source code from GitLab (`develop` branch): `gNB_scheduler_dlsch.c`, `gNB_scheduler.c`, `gNB_scheduler_primitives.c`. Verified `pf_dl()`, `nr_find_nb_rb()`, `nr_dlsch_preprocessor()`, and `gNB_dlsch_ulsch_scheduler()` against prior notes. OAI uses a single-pass PF algorithm (no two-stage pipeline like srsRAN). PF coefficient = `tbs / dl_thr_ue` with EWMA smoothing factor `a = 0.01f`. No scheduler policy factory — PF is hardcoded. Only RA Type 1 (contiguous) is supported [Note: Scheduling Read Results](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_OAI-Scheduler-Source-Code-Verified.md)
- **15:00-15:50** — Wrote [OAI Scheduler Source-Code-Verified Reference](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_OAI-Scheduler-Source-Code-Verified.md): 13 sections covering call chain, PF algorithm, `nr_find_nb_rb()` binary search, FAPI PDU construction, VRB map lifecycle, and FDM/TDM analysis.
- **15:30-16:00** — Wrote [Enabling Time-Frequency Domain Scheduling Guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_Enabling-Time-Frequency-Domain-Scheduling.md): Practical side-by-side OAI/srsRAN configuration guide. srsRAN uses `max_prb_policy_ratio` YAML config; OAI requires source code modification (`max_rbSize` cap in `pf_dl()`).
- **16:00-18:00** — Corrected inaccuracies from 02-24 note: `dl_thr_ue` smoothing factor is `0.01f` not `0.1`; `pre_processor_dl()` indirection was missing; RA Type 0 is not supported (enforced by `AssertFatal`).

## 2026/03/06
**Short-term Goals**
1. [Deep Dive: PRB Enforcement & VRB Selection — Source Code Trace](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-06_PRB-Enforcement-and-VRB-Selection-Deep-Dive.md)

**Daily Logs**:
- 09:00-13:00: PRB enforcement end-to-end trace + VRB selection algorithm + MCS/TBS path (Goal 1)
	(Status: Complete. Read **12 additional source files** building on the 03-03 deep dive. Key new findings: (1) **PRB enforcement traced end-to-end**, (2) **VRB selection is first-fit contiguous**, (3) **MCS determined before PRBs**, and (4) **srsRAN TBS implementation matches 3GPP TS 38.214 §5.1.3.2 exactly**. [Note here](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-06_PRB-Enforcement-and-VRB-Selection-Deep-Dive.md)

## 2026/03/10
**Short-term Goals**
1. [Study: External Lab Repos (rApp, Sideloader Service, K8s Guide) — Architecture Summary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-10_External-Repos-Summary.md)
2. Kubernetes single-node cluster setup on Ubuntu 24.04 (adapted from `External/kubernetes/nino-c-ran-installation/` RHEL guide)
3. Test rApp + Sideloader Helm chart deployments on the local cluster

**Daily Logs**:
- **10:00-12:00** — Read and analyzed 3 external lab repos: rApp (`rapp-cicd-ocloud`), Sideloader Service (`nino-sideloader-service`), and the K8s installation guide (`nino-c-ran-installation`). Note: External repos are gitignored.
  (Status: Complete. Created [`2026-03-10_External-Repos-Summary.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-10_External-Repos-Summary.md) covering rApp architecture flow, Sideloader monitoring capabilities table (25+ REST endpoints), K8s setup architecture, and 5 "Key Observations for TEEP" connecting the repos to thesis work.)

- **12:00-15:00** — Kubernetes single-node cluster setup on Ubuntu 24.04, adapting the lab's RHEL 9.4 guide to use `containerd` instead of CRI-O. Steps: swap disabled, kernel modules (overlay, br_netfilter), sysctl bridge-nf-call-iptables/ip_forward, containerd configured with `SystemdCgroup=true`, kubeadm v1.31.14 + kubelet installed from Kubernetes apt repo, `kubeadm init` with pod CIDR 10.0.0.0/8 + service CIDR 10.43.0.0/16, Cilium v1.16.5 CNI installed.
  (Status: Complete, with two debugging iterations. Issues resolved: (1) missing `conntrack` package on Ubuntu — installed via apt; (2) pod CIDR mismatch (10.42.0.0/16 vs Cilium's default 10.0.0.0/8) moved to CoreDNS i/o timeout; (3) UFW FORWARD chain DROP policy blocking pod→service traffic — fixed via `ufw disable` + `iptables -P FORWARD ACCEPT`. Cluster result: node Ready, all 11 system pods 1/1, `cilium status` OK. All commands documented in the summary note.)

- **15:00-16:30** — Tested the full stack: DNS resolution (CoreDNS → `kubernetes.default.svc.cluster.local`), ClusterIP + pod-to-pod networking, NodePort external access, OpenEBS `openebs-hostpath` StorageClass provisioning, and both Helm chart deployments (rApp with 10Gi PVC bound, Sideloader with `privileged: true` + `SYS_ADMIN`/`SYS_PTRACE`/`PERFMON` capabilities confirmed). All K8s layers functional. Registry auth to `bmw.ece.ntust.edu.tw` (Harbor) needs lab credentials for real image pull.
  (Status: Complete.)

## 2026/03/13
**Short-term Goals**
1. [Deep Dive: Sideloader Service — Collector Architecture, Power Monitoring & Fault Injection](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-13_Sideloader-Service-Deep-Dive.md)
2. [Deep Dive: rApp Test Orchestration Pipeline — Data Flow, Storage & TEIV Integration](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-13_rApp-Test-Orchestration-Pipeline-Deep-Dive.md)

**Daily Logs**:
- **09:00-12:00** — Source code deep read of all external repo modules for study note material (Goal 1 + Goal 2)
	(Status: Complete. Read all collector modules (`base.py`, `cpu.py`, `power.py`, `process.py`, `memory.py`, `network.py`, `ptp.py`), fault injection modules (`network_actions.py`, `ptp_actions.py`, `stress.py`), rApp supporting modules (`db.py`, `sideload_client.py`, `ue_client.py`, `influx_writer.py`, `teiv_client.py`), and all 12 test case YAMLs (monolithic/F1/NFAPI × LiteOn/Pegatron × Joule/Kepler).)

- **12:00-14:00** — Write Sideloader Service Deep Dive study note (Goal 1: [Sideloader Deep Dive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-13_Sideloader-Service-Deep-Dive.md))
	(Status: Complete. Created comprehensive 6-section deep dive covering: BaseCollector 1Hz sampling framework, all 8 collector modules (CPU with per-core breakdown + governor/idle/IRQ affinity, Power with RAPL auto-discovery + iDRAC/Redfish, Process with nr-softmodem thread-level CPU tracking + perf sched_latency, Memory with hugepage multi-size tracking + OOM detection, Network with SR-IOV VF + DPDK device detection), and 3 fault injection modules (VLAN fault with auto-restore, PTP sync disruption via ptp4l stop, stress-ng for CPU/memory/hugepage/OOM). Connected each feature to our TEEP project: PowerCollector is identical data source to Scaphandre, iDRAC fills the "gap" we identified, ThreadCPUCollector is the tool for Stage 2 L1/L2 thread analysis.)

- **14:00-16:00** — Write rApp Test Orchestration Pipeline Deep Dive study note (Goal 2: [rApp Pipeline Deep Dive](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-13_rApp-Test-Orchestration-Pipeline-Deep-Dive.md))
	(Status: Complete. Created comprehensive 6-section deep dive covering: test case YAML structure (12 configs with parameter sweep via itertools.product), UE control via ADB-over-SSH (Samsung SM-G9860 — signal/cell detection/airplane mode/iperf), out-of-band RT validation (kubectl+nsenter for CPU isolation/tuned/IRQ affinity/perf/flamegraph), TEIV topology inventory (ODUFunction + NRCellDU entities with vendor-aware Helm branching), dual storage (8 SQLite tables for operational state + 8 InfluxDB measurements for time-series including TEIV topology snapshots with FHI timing parameters), and end-to-end data flow diagram from YAML → permutation → deploy → parallel collect → aggregate → store.)

## 2026/03/20
**Short-term Goals**
1. [Active test: Sideloader Service local endpoint validation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-20_Sideloader-Testing-Progress.md)
2. Identify missing access/credentials/environment requirements for external repos
3. Produce reproducible start/test/check runbook for next sessions

**Daily Logs**:
- **10:30-11:30** — Executed local Sideloader active testing (Goal 1)
	(Status: Complete. Service started successfully from `External/sideloaderService/nino-sideloader-service/app.py`; generated non-destructive API sweep report at `https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/current_sweep/sideloader_api_test_report_2026-03-20.md` with coverage **32/33** routes. Functional: 10, Expected/env-limited: 19, Needs-review: 2, Defect-likely: 1.)

- **11:30-12:30** — Documented known defect and deferred fix (Goal 1)
	(Status: Complete. Confirmed `POST /power/ipmi` returns HTTP 500 due to missing `IPMIPowerCollector` import target in sideloader code path; fix intentionally deferred for this session per testing scope.)

- **13:00-15:30** — Investigated external repo access blockers (Goal 2)
	(Status: Complete. Identified primary blocker repo as **rApp** (`External/rApp/rapp-cicd-ocloud`). Source evidence shows required lab access and credentials: `KUBECONFIG=/root/l-smo.config` (in `QUICKSTART.md`/`Readme.md`), reachable Rapp Manager/ACM/Kong endpoints (`192.168.8.69:*`), private registry `bmw.ece.ntust.edu.tw/infidel/*` references (test cases/Makefile), and operational env vars (`NFO_BASE_URL`, `INFLUXDB_*`, `ADB_MACHINE_SSH_*`) in `.env`/Helm values. Without these, full orchestration cannot be operated end-to-end locally.)

- **16:30-17:30** — Published testing study note + runbook (Goal 3)
	(Status: Complete. Added `https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-20_Sideloader-Testing-Progress.md` with start/test/check commands and categorized outcomes for reproducible continuation.)

## 2026/03/21
**Short-term Goals**
1. [Overhaul full endpoint test report with updated categorized results](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/current_sweep/sideloader_api_test_report_2026-03-20.md)
2. [Overhaul quick-suite endpoint report for post-fix snapshot](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/current_sweep/sideloader_api_test_report_2026-03-21_after_fixes.md)
3. [Update study note with successful / expected fail / code fail breakdown](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-20_Sideloader-Testing-Progress.md)
4. [Create unpushed external-repo change log + risks note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-21_Sideloader-Local-Compatibility-Changes-and-Risks.md)

**Daily Logs**:
- **09:00-10:00** — Re-ran full non-destructive sideloader endpoint sweep and rewrote report format (Goal 1)
	(Status: Complete. Updated report at [sideloader_api_test_report_2026-03-20.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/current_sweep/sideloader_api_test_report_2026-03-20.md) into clear categories: successful / expected fail / code fail. Current summary: Tested 32 endpoints, Successful 18, Expected fail 13, Code fail 1, Needs review 0.)

- **10:30-11:00** — Re-ran quick verification suite and normalized second report (Goal 2)
	(Status: Complete. Updated [sideloader_api_test_report_2026-03-21_after_fixes.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/current_sweep/sideloader_api_test_report_2026-03-21_after_fixes.md) with same categorized structure. Current summary: Tested 16 endpoints, Successful 13, Expected fail 2, Code fail 1, Needs review 0.)

- **11:00-12:00** — Updated testing study note with final endpoint classification and interpretation (Goal 3)
	(Status: Complete. Revised [2026-03-20_Sideloader-Testing-Progress.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-20_Sideloader-Testing-Progress.md) to reflect overhauled results and explicit endpoint groups: successful, expected fail, and code fail.)

- **13:00-14:00** — Documented external repo local patches and risk review for traceability (Goal 4)
	(Status: Complete. Added [2026-03-21_Sideloader-Local-Compatibility-Changes-and-Risks.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-21_Sideloader-Local-Compatibility-Changes-and-Risks.md), listing code changes in order, rationale, and potential side effects since external repo modifications are not pushed upstream.)


## 2026/03/27
**Short-term Goals**
1. [Consolidate StarlingX AIO-Simplex virtual deployment progress into a reproducible guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-27_StarlingX-AIOSimplexVirtual-Progress-and-Guide.md)
2. [Document Virt-Manager critical path (install flow, CPU topology intercept, and LVM fix)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-27_StarlingX-AIOSimplexVirtual-Progress-and-Guide.md)
3. [Archive failure patterns and recovery playbook for future StarlingX runs](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-27_StarlingX-AIOSimplexVirtual-Progress-and-Guide.md)

**Daily Logs**:
- 09:00-11:00: Deployment architecture decision + baseline setup validation (Goal 1)
	(Status: Complete. Finalized AIO-Simplex Virtual as the target topology, documented host requirements (RAM/storage), and recorded the Debian-era documentation boundary (avoid legacy stx.5.0/CentOS installation references).)

- 11:00-13:00: Host networking preparation and bridge recovery workflow (Goal 1)
	(Status: Complete. Standardized host hypervisor prerequisites, bridge creation flow from `virtual-deployment`, and the ghost-bridge cleanup sequence (`stxbr*` teardown + `libvirtd` restart) to make setup deterministic.)

- 14:00-16:00: VM provisioning and Virt-Manager installation timeline hardening (Goal 2)
	(Status: Complete. Captured the full linear path from `virt-install` to GUI installer actions, including the force-recreate safety valve, pre-boot CPU topology correction (1 socket, 4 cores, 1 thread), and post-login LVM `global_filter` unblindfolding before bootstrap.)

- 16:00-18:00: Bootstrap, unlock, verification, and troubleshooting appendix (Goal 3)
	(Status: Complete. Documented OAM interface assignment, host unlock behavior, post-boot health checks (`system host-list`, `kubectl get nodes`), and added a debug graveyard covering the NoneType/LVM failure chain, 0MB RAM topology failure, and SM deadlock point-of-no-return with recovery guidance.)


## 2026/04/14
**Short-term Goals**
1. [Build first complete draft of the StarlingX + OAI deployment guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-04-23_StarlingX-AIOSimplexVirtual-Full-Guide.md)

**Daily Logs**:
- 10:00-12:00: Documented StarlingX host prep + VM baseline path (Goal 1)
	(Status: Complete. Wrote the host prerequisites, bridge setup flow, `virt-install` baseline, and the Virt-Manager critical path needed to get a stable AIO-Simplex installation.)

- 13:00-16:00: Added OAI 5G Core deployment and first-pass troubleshooting notes (Goal 1)
	(Status: Complete. Captured namespace/chart deployment and initial debug findings for network/CNI and SMF stability issues as part of the draft.)


## 2026/04/21
**Short-term Goals**
1. [Extend and validate the same deployment guide with RAN + data-plane sections](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-04-23_StarlingX-AIOSimplexVirtual-Full-Guide.md)

**Daily Logs**:
- 10:00-12:30: Integrated gNB/NR-UE deployment procedure into the guide (Goal 1)
	(Status: Complete. Added stable image pinning, DNS/FQDN requirements, and explicit Helm command patterns for reproducible RAN bring-up.)

- 13:30-16:00: Documented slice/DNN alignment and E2E data-plane validation flow (Goal 1)
	(Status: Complete. Added `DNN_DENIED` root cause/fix, `oaitun_ue1` verification steps, and ordered restart guidance for AMF/SMF/UPF race-condition recovery.)


## 2026/04/23
**Short-term Goals**
1. [Finalize and publish the single-file full guide deliverable](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-04-23_StarlingX-AIOSimplexVirtual-Full-Guide.md)

**Daily Logs**:
- 09:00-11:30: Consolidated all sections into a single linear document (Goal 1)
	(Status: Complete. Unified StarlingX install, OAI Core, OAI RAN, and verification steps into one end-to-end flow with consistent command order.)

- 13:00-15:00: Finalized troubleshooting appendix and recovery playbook (Goal 1)
	(Status: Complete. Curated the practical failure patterns (CPU topology, LVM filter, CNI auth, SMF parser, DNS/FQDN, restart order) into one reproducible debug reference for future reruns.)

## 2026/04/27 - 2026/04/28
**Short-term Goals**
1. [Clean slate and test Mr. Nino's guide for StarlingX setup](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-04-28_Guided-StarlingX-Deployment-Issues.md)

**Daily Logs**:
- 09:00 - 17:00 (2 days): Fresh host setup and guide execution (Goal 1)
	(Status: Complete. Followed the guide from a clean Debian 11 host with 24GB RAM and 500GB free disk. Encountered 5 major issues and stopped at the Ansible playbook deployment point due to image pull failure & incompatibility)

## 2026/04/31
**Short-term Goals**
1. [Study: NVIDIA cuMAC & cuMAC-CP — GPU-Accelerated MAC Scheduling and Power Scheduling Implications](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-01_NVIDIA-cuMAC-GPU-Accelerated-Scheduling.md)

**Daily Logs**:
- 09:00-13:00: Analysed NVIDIA Aerial cuMAC-CP Integration Guide and Implementation Details (Goal 1: [cuMAC Study Note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-01_NVIDIA-cuMAC-GPU-Accelerated-Scheduling.md))
	(Status: Complete. Reviewed 2 NVIDIA documentation pages (cuMAC-CP architecture + CUDA scheduling algorithms). Created comprehensive study note covering: cuMAC-CP thread model (1 receiver + N workers + MPMC lock-free queue), multi-cell 1:N joint scheduling architecture, 5 CUDA-accelerated algorithms (PF UE selection, PRB allocation with inter-cell interference, layer selection, MCS with OLLA, 64T64R MU-MIMO grouping), and detailed comparison to OAI/srsRAN CPU schedulers. Mapped cuMAC capabilities to our power scheduling research: multi-cell joint optimisation enables coordinated cell sleep (UC1), interference-aware PRB allocation reduces transmit power ($\Delta_p \cdot P_{max} \cdot x$ term), MU-MIMO packing creates longer Cell DTX windows, and GPU execution introduces dual power measurement complexity (RAPL + nvidia-smi). Confirmed that our FDM/TDM analysis, TBS equivalence proof, and EARTH model remain valid under GPU-accelerated scheduling.)

## 2026/05/07
**Short-term Goals**
1. [Topic 1: Real-Time StarlingX Tuning for 5G DU](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-07_Topic1-RT-StarlingX-Tuning-for-5G-DU.md)
2. [Topic 2: WINLAB/POET Measurement Methodology](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-07_Topic2-WINLAB-POET-Measurement-Methodology.md)

**Daily Logs**:
- 09:00-13:00: Research and write Topic 1 study note (Goal 2: [RT StarlingX Tuning](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-07_Topic1-RT-StarlingX-Tuning-for-5G-DU.md))
	(Status: Complete. Fetched and synthesized sources from: Linux PREEMPT_RT docs, StarlingX vRAN configuration (CPU Manager, Topology Manager, vRAN Boost Operator), srsRAN performance tuning (`expert_execution.affinities`, `srsran_performance` script), OAI DPDK/xran configuration, O-RAN WG4 fronthaul timing specs (~100 µs one-way, ±1.5 µs sync), DPDK/SR-IOV setup, and cyclictest/rtla validation tools. Created comprehensive 10-section study note with: O-RAN timing budget, CPU isolation checklist (isolcpus + nohz_full + rcu_nocbs), NUMA alignment verification, PREEMPT_RT vs generic kernel latency/power comparison table, IRQ affinity strategy, hugepage allocation (1GB for DPDK, 2MB for DU buffers), StarlingX K8s settings (static CPU Manager, best-effort Topology Manager), srsRAN gnb.yaml thread pinning config, OAI thread-pool allocation, and a complete end-to-end tuning checklist (BIOS → OS → Network → Application → Validation).)

- 15:00-18:30: Research and write Topic 2 study note (Goal 3: [WINLAB/POET Measurement](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-07_Topic2-WINLAB-POET-Measurement-Methodology.md))
	(Status: Complete. Fetched and synthesized sources from: POET paper (IEEE VTC2024-Fall, DOI: 10.1109/VTC2024-Fall63153.2024.10757537), WINLAB RCR articles, Scaphandre/RAPL documentation, Prometheus/Grafana power monitoring architecture, RAPL accuracy research (TU Dresden, ResearchGate). Created comprehensive 9-section study note with: tool comparison table (PDU vs IPMI vs Scaphandre vs Kepler vs nvidia-smi), expected offsets between tools, timestamp alignment strategy (UTC + NTP + Prometheus as single authority), POET load definitions (1 UE = 70% PRB / 65 Mb/s, 2 UE = 100% PRB / 84 Mb/s), sampling cadence recommendations, KPI alignment architecture diagram, labeled power trace format spec, Prometheus + Grafana deployment configs (scrape configs for scaphandre/ipmi_exporter/snmp_exporter), Scaphandre Docker deployment, RAPL security caveat (CVE-2020-8694/5 PLATYPUS mitigation), 4-phase POET replication plan, data format specification (CSV schema + UTC markers), and statistical rigor checklist.)

## 2026/05/08
**Short-term Goals**
1. [Addendum: QA Review & Obstacles - StarlingX Control Plane Debugging](docs/StudyNotes/2026-05-08_Addendum_%20StarlingX_Control_Plane_Debugging.md)

**Daily Logs**:
- 15:00-16:00: Document control plane debugging addendum (Goal 1)
	(Status: Complete. Consolidated QA review notes on SM enabling loops, HAProxy routing, and service deadlocks in the addendum.)

## 2026/05/20
**Short-term Goals**
1. [StarlingX Duplex (KVM) deployment notes](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-20_Duplex_Deployment_Progress.md)
2. [OKD Hub & Slave Node (SNO) deployment notes](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-20_OKD_Deployment_Notes.md)

**Daily Logs**: (Note: 1.5-week progress)
- StarlingX duplex deployment progress and blockers (Goal 1)
	(Status: Complete. Documented control-plane bootstrap, CPR fixes, interface reassignment, and controller-1 PXE failure causes with the recommended virt-install UEFI path.)
- OKD hub + SNO deployment guide write-up (Goal 2)
	(Status: Complete. Captured the successful local OKD path separately from the later Newton lab attempt: host prep, playbook patches, DNS preflight, successful hub install, ZTP flow for the SNO node, and post-install PTP/SCTP validation steps.)

## 2026/06/17
**Short-term Goals**
1. [OKD Hub Deployment on Newton Verification Attempt](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-17_OKD_Newton_Deployment_Notes.md)

**Daily Logs**: (Note: This installment took >1 day)
- 09:00-17:00 (1 week): Validated the OKD Hub guide directly on BMW Newton (`192.168.8.53`) and documented the blocked Agent-Based Installer path (Goal 1)
	(Status: Complete. Confirmed this was a separate attempt from the successful local OKD guide. Preserved Newton's host OS, removed stale VMs (`master-0-vm`, `worker-0`, `ctr-00`), reused `bridge0`, rebuilt the `pti-rtp` OKD Hub workflow, and reached the `master-0-vm` assisted-service / agent-registration stage. The attempt stopped because the Newton VM path could not reproducibly access required OKD/SCOS payloads and metadata from `quay.io`; Kepler remains unverified until a healthy Hub exists. Documented the required next prerequisite: internal mirror registry, disconnected install assets, or a network exception for registry access.)
	- **Known Blockers/Issues Logged**:
		- **Critical**: Missing registry-access prerequisite for the Newton Hub VM during OKD Agent Registration.
		- **Major**: Kepler slave-node validation is blocked until Newton has a working Hub/ZTP path.
		- **Major**: CoreOS live-ISO resets wipe manual payload patches and SSH state, making ad hoc side-load fixes non-reproducible.
		- **Major**: Host-side NAT / gateway hijack did not provide a clean guide-worthy workaround.

## 2026/06/26
**Short-term Goals**
1. [Validate Phase 1 of the POET measurement stack](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/run_poet_phase1.sh)
2. [Troubleshoot Sideloader service IPMI errors and enhance telemetry collection](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/External/sideloaderService/nino-sideloader-service-main/collectors/power.py)

**Daily Logs**:
- 09:00-12:00: Developed automation scripts and captured live power telemetry (Goal 1)
	(Status: Complete. Created [`run_poet_phase1.sh`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/run_poet_phase1.sh) to capture live power telemetry using a host-based RAPL scraper, successfully bypassing Docker permission/symlink issues. Generated a verified, time-correlated power profile of the system under synthetic load ([`plot_poet_phase1.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/plot_poet_phase1.py) and [`power_validation.png`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/poet_phase1/power_validation.png)) to confirm the measurement pipeline is operational.)
- 12:00-15:00: Went to create a bank account at First Bank (Gongguan branch)
	(Status: Complete. ).
- 15:00-17:00: Extended Sideloader service and measurement infrastructure (Goal 2)
	(Status: Complete. Troubleshot the existing Sideloader service to resolve IPMI-related errors. Expanded [`collectors/power.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/External/sideloaderService/nino-sideloader-service-main/collectors/power.py) to include an `IPMIPowerCollector` utilizing `ipmitool dcmi power reading` to enable whole-system DC monitoring alongside RAPL domains. Configured Prometheus/Grafana [`docker-compose.yml`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/measurement_stack/docker-compose.yml) stack for metrics collection.)

## 2026/06/28
**Short-term Goals**
1. [StarlingX AIO-Duplex Deployment on Archimedes](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-28_StarlingX_AIO_Duplex_Deployment_Notes.md)

**Daily Logs**: (Note: This installment took >1 day)
- 09:00-17:00 (1 week): Deployed and documented StarlingX 10.0 AIO-Duplex on the Archimedes host (Goal 1)
	(Status: Complete. Successfully bootstrapped `controller-0` and resolved initial DNS and service deadlocks. Overcame a critical MAC address mismatch on `controller-1` by executing database surgery on the master node to remap the management and PXE interfaces. Implemented a "Frankenstein patch" involving live-RAM network bypasses, IPsec firewall rules modification, and manual configuration script execution to break a persistent reboot loop caused by poisoned Puppet caches. `controller-1` is now in an `online` state, pending final HA DRBD storage synchronization.)
	- **Remaining Blockers/Issues Logged**:
		- **Critical**: Puppet cache fallback — `controller-1` re-applies incorrect configurations if booted without an active tunnel to `controller-0`.
		- **Major**: `Reboot Failed` ghost state — Maintenance Agent (`mtcAgent`) freezes on stale tickets, requiring a manual `pkill -9`.
		- **Major**: 30-minute PXE timeout delays each reboot cycle before defaulting to HDD boot.

## 2026/06/29
**Short-term Goals**
1. [Finalize OKD Newton handover note and clean up filenames](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-17_OKD_Newton_Deployment_Notes.md)
2. [Refocus project direction on WINLAB / Pegatron O-RU power saving](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-29_WINLAB_ORU_Power_Saving_Direction.md)
3. [Prepare WINLAB O-RU experiment plan, scheduler-mode draft, and data templates](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-29_WINLAB_ORU_Experiment_Plan_and_OAI_Scheduler_Modes.md)

**Daily Logs**:
- 09:00-10:00: Consolidated OKD Newton handover documentation and repository filenames (Goal 1)
	(Status: Complete. Finalized the Newton OKD verification/failure catalogue, separated it from the successful local OKD deployment guide, fixed the duplicate/copy filename state, and preserved the main blocker: Newton Hub VM agent registration remains blocked until registry/mirror/disconnected-install prerequisites are solved.)

- 10:00-11:00: Audited and committed recent infrastructure/measurement artifacts from git history (Goal 1)
	(Status: Complete. Confirmed the newly added June artifacts: Phase 1 POET measurement validation scripts/results, Prometheus/Grafana measurement stack config, OKD Newton handover note, and StarlingX AIO-Duplex Archimedes deployment note. Daily log structure was verified as date sections with short-term goals followed by time-blocked status bullets.)

- 12:00-14:30: Captured professor's WINLAB / Pegatron O-RU power-saving direction (Goal 2)
	(Status: Complete. Created the working direction note for duplicating the E2E throughput-vs-RU-power baseline first, then comparing OAI original scheduler against time-domain and frequency-domain scheduler variants. Identified Ming as the source for Test Automation rApp/E2E workflow and Chynna as the source for CortexDC/PDU power measurement.)

- 14.30 - 16.00: Weekly meeting with the BMW team

- 16:30-17:30: Drafted experiment matrix, scheduler logging fields, and CSV/text templates (Goal 3)
	(Status: Complete. Prepared the baseline plan around Pegatron RU on Joule, existing rApp sweep points (`100, 400, 700 Mbps`), optional POET anchors, longer PDU-quality steady-state windows, and minimum OAI scheduler log fields (`frame`, `slot`, `RNTI`, `rbStart`, `rbSize`, `MCS`, `TBS`, layers, beam index). Added templates for run summary, power timeseries, UTC markers, and scheduler allocations under `templates/`.)

## 2026/06/30
**Short-term Goals**
1. [Prepare WINLAB / Pegatron O-RU experiment workflow documentation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md)
2. [Document HPE Helm deployment and OAI runtime configuration workflow](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md)
3. [Clarify the official WINLAB nFAPI baseline and next learning target](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_WINLAB-nFAPI-Baseline-Clarifications-and-Next-Learning-Target.md)
4. [Initialize the new daily log format](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/New-Daily-Logs.md)

**Daily Logs**:
- 09:00-11:00: Converted rough WINLAB operational notes into professional study notes (Goal 1)
	(Status: Complete. Created the [BMW Jenkins OAI image-build workflow note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md), documenting the BMW Jenkins build/push path, Quay image flow, and how OAI images move toward the HPE deployment.)
- 11:00-12:00: Expanded HPE Helm and OAI configuration theory (Goal 2)
	(Status: Complete. Wrote the [HPE OAI Helm and WINLAB config guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md), including Helm values, ConfigMap responsibilities, TDD pattern, ARFCN, Point A, and why these settings matter for throughput/power experiments.)
- 13:00-14:00: Started the new daily-log structure from the template (Goal 4)
	(Status: Complete. Read [`Log_Template.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/Log_Template.md) and initialized [`New-Daily-Logs.md`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/New-Daily-Logs.md) as the new evidence-linked daily index.)
- 14:00-15:30: Clarified the first official nFAPI baseline direction after Ming's E2E walkthrough (Goal 3)
	(Status: Complete. Documented that the first baseline should be the original OAI scheduler on the nFAPI/Pegatron path, and separated what Ming owns in the E2E flow from what can be standardized independently in [the baseline clarification note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_WINLAB-nFAPI-Baseline-Clarifications-and-Next-Learning-Target.md).)
- 15:30-17:00: Identified CortexDC/PDU power export as the next required learning target (Goal 3)
	(Status: Complete. Confirmed that the next blocker was no longer the high-level E2E line, but learning Ms. Chynna's CortexDC/PDU export path so throughput windows can be matched to Pegatron O-RU power data.)

## 2026/07/01
**Short-term Goals**
1. [Follow Open Research Playbook conventions and produce an evidence-linked daily plan](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-01_Daily-Note.md)
2. [Prepare the first `nfapi_pegatron_original_oai` smoke-test run sheet](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-01_nfapi_pegatron_original_oai_Smoke-Test-Run-Sheet.md)
3. [Capture CortexDC/Pegatron O-RU power-mapping discussion structure](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/MeetingNotes/2026-07-01_CortexDC-Pegatron-ORU-Power-Mapping.md)
4. Build and validate the first HPE rApp wrapper for repeatable E2E triggering

**Daily Logs**:
- 09:00-10:30: Converted the research plan into measurable daily and 8-week milestones (Goal 1)
	(Status: Complete. Updated the [2026-07-01 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-01_Daily-Note.md) with weekly milestone targets, action items, owners, evidence expectations, and blocker tracking.)
- 10:30-12:00: Prepared CortexDC/PDU and mentor discussion structure (Goal 3)
	(Status: Complete. Created the [CortexDC/Pegatron O-RU power-mapping meeting note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/MeetingNotes/2026-07-01_CortexDC-Pegatron-ORU-Power-Mapping.md), identifying Chynna/Peter for PDU/CortexDC mapping and Ming for the nFAPI E2E workflow.)
- 13:00-14:30: Drafted the first reproducible smoke-test run sheet (Goal 2)
	(Status: Complete. Wrote the [`nfapi_pegatron_original_oai` smoke-test run sheet](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-01_nfapi_pegatron_original_oai_Smoke-Test-Run-Sheet.md), covering prerequisites, command/output capture, UTC markers, deployment metadata, and power export fields.)
- 14:30-16:00: Built the initial HPE rApp wrapper and unified gNB API path (Goal 4)
	(Status: Complete. Created the first request-driven rApp prototype under the WINLAB rApp path, wrapping HPE-side Bare Metal and OCloud scripts through a unified `POST /gnb/run` API while preserving credential boundaries.)
- 16:00-17:00: Validated the Bare Metal path and prepared OCloud parity work (Goal 4)
	(Status: Complete. Ran the Bare Metal path through the API, brought the Samsung UE online with IP `10.45.0.2`, captured iPerf/log output under `/home/hpe/ming-logs/Exp_Bandwidth/0701-1628-100x`, and prepared an OCloud parity patch so `cloud_e2e.py` can accept `bandwidth`, `period`, `gap_time`, `uplink`, `ue_model`, and `iperf_bind`.)

## 2026/07/02
**Short-term Goals**
1. [Attend scheduled meeting / workshop and keep research context aligned](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-02_Daily-Note.md)

**Daily Logs**:
- 09:00-12:00: Attended scheduled meeting / workshop activities (Goal 1)
	(Status: Complete. Used the meeting/workshop time to keep the WINLAB direction aligned and avoided making unsupported throughput-power claims while no new lab run or PDU export was recorded.)
- 13:00-15:00: Reviewed active technical direction after the meeting / workshop (Goal 1)
	(Status: Complete. Preserved the current working direction in the [2026-07-02 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-02_Daily-Note.md): test OCloud with parameterized iPerf controls, confirm pod readiness, and keep Pegatron O-RU power mapping as a required baseline condition.)
- 15:00-17:00: Prepared the next working-day OCloud test focus (Goal 1)
	(Status: Complete. Set the next task as testing `mode:"ocloud"` through `/gnb/run` using configurable `bandwidth`, `period`, and `gap_time`, with the result classified as smoke/parity evidence unless power mapping becomes confirmed.)

## 2026/07/03
**Short-term Goals**
1. [Validate the OCloud parameterized run path](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-03_Daily-Note.md)
2. [Preserve evidence quality for later baseline use](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-03_Daily-Note.md)
3. [Document HPE helper scripts for repeatable WINLAB E2E evidence collection](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-03_WINLAB-HPE-Helper-Scripts-Guide.md)

**Daily Logs**:
- 09:00-10:30: Planned OCloud pod-readiness and parameterized-run checks (Goal 1)
	(Status: Complete. Prepared the OCloud validation sequence in the [2026-07-03 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-03_Daily-Note.md), including `kubectl get pods -n ming-ns -o wide`, `cloud_e2e.py --help`, and `POST /gnb/run` with `mode:"ocloud"`.)
- 10:30-12:00: Verified the OCloud script expectations and evidence boundaries (Goal 1)
	(Status: Complete. Treated OCloud execution as parity/smoke validation first, not final throughput-power evidence, and documented that Pegatron O-RU power mapping remained a required condition before baseline claims.)
- 13:00-15:00: Documented helper scripts and repeatable evidence workflow (Goal 3)
	(Status: Complete. Created the [WINLAB HPE helper scripts guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-03_WINLAB-HPE-Helper-Scripts-Guide.md), covering status snapshots, OCloud power probes, outlet summaries, evidence-report generation, and the dry/live workflow split.)
- 15:00-17:00: Updated run-sheet expectations and blocker list for OCloud testing (Goal 2)
	(Status: Complete. Clarified that OCloud runs depend on ready `oai-vnf` and `oai-pnf` pods, that `cloud_e2e.py` must expose the same traffic knobs as Bare Metal, and that PDU/CortexDC outlet mapping remained the main power-baseline blocker.)

## 2026/07/06
**Short-term Goals**
1. [Resolve the active RU path and power-source candidate](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-06_Daily-Note.md)
2. [Verify OCloud E2E execution with controlled traffic parameters](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-06_Daily-Note.md)
3. [Record Pegatron O-RU PDU outlet clarification context](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-06_Pegatron_RU_CortexDC_Power_Mapping.md)

**Daily Logs**:
- 09:00-10:30: Reconciled Ming, Ravi, and Chynna responsibilities (Goal 1)
	(Status: Complete. Clarified that Ming owns the E2E flow, Ravi owns PDU schedule/wiring context, and Chynna remains the CortexDC/InfluxDB export-path contact. Captured the corrected power-mapping context in the [Pegatron RU CortexDC/PDU mapping note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-06_Pegatron_RU_CortexDC_Power_Mapping.md).)
- 10:30-12:00: Confirmed active E2E path and mapped it to the PDU schedule (Goal 1)
	(Status: Complete. Ming confirmed that both Bare Metal and OCloud E2E tests use the Pegatron RU `[O]` path. Ravi's schedule maps Pegatron RU `[O]` / OCloud testing to Outlet 2, making `Outlet 2 active_power` the correct power-source candidate.)
- 13:00-14:30: Verified OCloud script traffic controls and pod-readiness path (Goal 2)
	(Status: Complete. Confirmed that `cloud_e2e.py --help` exposes `--bandwidth`, `--period`, `--gap-time`, `--ue-model`, `--uplink`, `--iperf-bind`, `--settle-time`, and `--attach-timeout`, and recovered the OCloud pod path until VNF/PNF could become Running and Ready.)
- 14:30-16:00: Ran a controlled OCloud 100 Mbps smoke test (Goal 2)
	(Status: Complete. Triggered job `f75e676a-a8b5-4661-8940-7204052eab3f`; it succeeded with UE IP `10.45.0.2`, PNF/VNF Running & Ready, 100 Mbps downlink reverse-mode iPerf, 716 MBytes transferred, and 0% packet loss.)
- 16:00-17:00: Recorded remaining power-export blocker and next artifact needs (Goal 3)
	(Status: Complete. Documented that `Outlet 2 active_power` is the candidate, but final throughput-vs-power evidence still requires timestamped export rows, sampling interval, and timestamp basis from CortexDC/InfluxDB.)

## 2026/07/07
**Short-term Goals**
1. [Integrate E2E artifact generation into the rApp endpoint](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-07_Daily-Note.md)
2. [Confirm the power-data path for the Pegatron RU `[O]` experiment](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-07_Daily-Note.md)
3. [Preserve HPE helper-script workflow context](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-03_WINLAB-HPE-Helper-Scripts-Guide.md)

**Daily Logs**:
- 09:00-10:30: Inspected rApp endpoint, Ming scripts, and OCloud log/plot sources (Goal 1)
	(Status: Complete. Reviewed `/home/hpe/winlab_e2e_rapp`, `/home/hpe/ming-logs`, and `/home/hpe/CRAN/ocloud-helm-templates/cloud_e2e.py` to map how `/gnb/run`, Bare Metal, OCloud, UE iPerf, log gathering, and plotting should connect.)
- 10:30-12:00: Integrated the artifact wrapper into both Bare Metal and OCloud modes (Goal 1)
	(Status: Complete. Updated the endpoint path so `/gnb/run` calls `run_e2e_with_artifacts.py` for both `mode=baremetal` and `mode=ocloud`, producing a single evidence directory with request metadata, command logs, stdout, summary, throughput CSV, plots, and pod logs.)
- 13:00-14:30: Validated OCloud artifact generation through the endpoint (Goal 1)
	(Status: Complete. Job `16d9967f-1bb5-4305-aadd-ccb15bc7d6de` succeeded on the Pegatron RU `[O]` path with UE IP `10.45.0.4`, 100 Mbps downlink reverse-mode iPerf for 150 seconds, 1.75 GBytes transferred, and 0% packet loss. Artifact directory: `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260707-071638`.)
- 14:30-15:45: Confirmed Outlet 2 active_power availability in InfluxDB (Goal 2)
	(Status: Complete. Chynna confirmed that Outlet 2 `active_power` exists in InfluxDB, proving the expected RU power source is visible. Her account still lacked export/save permission, so the screenshot was treated as availability proof rather than final data.)
- 15:45-17:00: Defined the remaining power-export request and analysis bridge (Goal 2)
	(Status: Complete. Prepared the Ravi/export-permission follow-up and documented that the next analysis step is to match `iperf_timeseries.csv` and `offered_load_throughput.csv` with timestamped Outlet 2 `active_power` rows over the same UTC/GMT+8 window.)

## 2026/07/08
**Short-term Goals**
1. [Validate OCloud throughput sweep behavior at higher offered loads](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-08_Daily-Note.md)
2. [Prepare side-by-side Docker deployment for the WINLAB E2E rApp](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Deployment/winlab_e2e_rapp_docker/README.md)
3. [Document HPE Docker setup and smoke-test runbook](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Deployment/winlab_e2e_rapp_docker/HPE_Docker_Runbook.md)

**Daily Logs**:
- 09:00-10:30: Ran high-load OCloud offered-load sweep attempt (Goal 1)
	(Status: Partial. Triggered job `62eee274-37a4-4448-8e67-794a1bd46e4e` for 100,200,300,400,500,600,700,800,900,1000 Mbps at 60 seconds per step. The run reached the 900 Mbps step and stalled; stopping the inner `cloud_e2e.py` allowed the wrapper to preserve partial artifacts under `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260708-025454`.)
- 10:30-12:00: Recovered UE/iPerf state and isolated high-load failure behavior (Goal 1)
	(Status: Complete. Cleaned host `iperf3`, force-stopped the Magic iPerf Android package, removed stale UE JSON, and documented that high-load sweeps expose UE/iPerf state issues around the upper offered-load range.)
- 13:00-14:15: Re-ran validation and confirmed clean artifact generation after cleanup (Goal 1)
	(Status: Complete. After one 100-800 Mbps run produced empty UE intervals, a short 100 Mbps sanity run `0845ea8a-e98f-4674-8da0-5eeb313ec74b` succeeded with UE IP `10.45.0.10`, 20 iPerf samples, 0% loss, `iperf_timeseries.csv`, `iperf_throughput.png`, `offered_load_throughput.csv`, and `offered_load_throughput.png`.)
- 14:15-15:30: Clarified the two-server Docker model and configurable identities (Goal 2)
	(Status: Complete. Confirmed Server 1 as the HPE rApp/OCloud runner and Server 2 as the `iapc` UE-control host with Android ADB/Magic iPerf. Preserved the current host rApp on `127.0.0.1:9090` and planned Docker to run side-by-side on `127.0.0.1:19090`.)
- 15:30-17:00: Drafted Docker deployment bundle and HPE runbook (Goal 2 + Goal 3)
	(Status: Complete locally. Prepared the [WINLAB E2E rApp Docker bundle](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Deployment/winlab_e2e_rapp_docker/README.md) and [HPE Docker runbook](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/Deployment/winlab_e2e_rapp_docker/HPE_Docker_Runbook.md), including Docker install checks, `.env` handling, current-rApp preservation, container API port `19090`, and the remaining `iperf_bind` passthrough follow-up.)

## 2026/07/13
**Short-term Goals**
1. [Finish and document Dockerized WINLAB E2E rApp status](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-13_Daily-Note.md)
2. [Explain SMO-driven workload orchestration for report use](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-13_SMO_Workload_Automated_Testing_Architecture.md)
3. Capture Ming's OCloud failed-pod cleanup mechanism from HPE

**Daily Logs**:
- 09:00-10:30: Confirmed Dockerized rApp completion and preserved side-by-side deployment model (Goal 1)
	(Status: Complete. Treated Dockerization as finished while preserving the non-disruptive validation model: the original host rApp remains on `127.0.0.1:9090`, and the Dockerized rApp is tested separately on `127.0.0.1:19090`. Recorded that the next live Docker smoke test still depends on healthy OCloud VNF/PNF pod state.)
- 10:30-12:00: Wrote the SMO/workload architecture explanation for report use (Goal 2)
	(Status: Complete. Created the [SMO and automated workload testing architecture note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-13_SMO_Workload_Automated_Testing_Architecture.md), explaining that SMO/rApp defines the experiment intent, HPE and UE execute traffic workload, Kubernetes/OCloud hosts the network functions, and InfluxDB/PDU monitoring supplies the power data.)
- 13:00-14:30: Diagnosed OCloud PNF pod creation loop and inspected Ming's cleanup script (Goal 3)
	(Status: Complete. Read `/home/hpe/force_cleanup_pods.sh` on HPE. The script scans namespaces for Terminating, Failed, and `OutOf...` pods; force-deletes stuck pods; strips finalizers if needed; detects missing resource names; prints node capacity/allocatable values; and scales the owning Deployment/ReplicaSet/StatefulSet to zero to stop repeated pod creation.)
- 14:30-15:45: Captured the SR-IOV resource blocker and safe recovery rule (Goal 3)
	(Status: Complete. Documented that the observed PNF failure was `OutOfopenshift.io/fh_sriov_up_lao`, meaning the pod requested a resource that `lavoisier` was not advertising with sufficient capacity. The cleanup script is a recovery/control tool; PNF should only be reinstalled or scaled back up after `openshift.io/fh_sriov_up_lao` is visible as nonzero in node capacity/allocatable.)
- 15:45-17:00: Updated daily documentation and next working-day plan (Goal 1 + Goal 3)
	(Status: Complete. Added the [2026-07-13 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-13_Daily-Note.md) and updated the daily-note index. Next steps are to verify SR-IOV capacity, restore clean VNF/PNF pods, run a Dockerized 100 Mbps OCloud smoke test, and then merge throughput artifacts with Outlet 2 power data.)

## 2026/07/15
**Short-term Goals**
1. [Attend Groundhog Taiwan company visit and preserve project-relevant observations](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-15_Groundhog-Taiwan-Company-Visit.md)
2. [Maintain the daily-note record for the visit day](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-15_Daily-Note.md)

**Daily Logs**:
- 09:00-12:00: Attended Groundhog Taiwan company visit activities (Goal 1)
	(Status: Complete. Used the morning company-visit block to observe how production-facing teams present infrastructure, operations, and service monitoring. No WINLAB OCloud E2E run is claimed for this date.)
- 12:00-13:00: Lunch / transition period during company visit (Goal 1)
	(Status: Complete. Continued the visit schedule and kept the day separate from lab execution evidence.)
- 13:00-16:00: Completed afternoon Groundhog Taiwan visit sessions and discussion (Goal 1)
	(Status: Complete. Captured the main project-relevant takeaway: the WINLAB rApp should behave like an operational automation service that triggers tests, preserves artifacts, connects workload output to infrastructure telemetry, and supports reproducible review.)
- 16:00-17:00: Wrote visit-day documentation boundary (Goal 2)
	(Status: Complete. Added the [Groundhog Taiwan company visit note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-15_Groundhog-Taiwan-Company-Visit.md) and [2026-07-15 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-15_Daily-Note.md), explicitly recording this as a company visit day rather than a lab-result day.)

## 2026/07/16
**Short-term Goals**
1. [Consolidate Dockerized WINLAB rApp and OCloud recovery status](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-16_WINLAB_OCloud_Docker_and_Pod_Recovery.md)
2. [Prepare the throughput-power merge validation path](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-16_Daily-Note.md)

**Daily Logs**:
- 09:00-10:30: Rechecked Dockerized rApp side-by-side validation model (Goal 1)
	(Status: Complete. Preserved the working host rApp on `127.0.0.1:9090` and the Dockerized rApp validation path on `127.0.0.1:19090`, avoiding replacement of the known-working service.)
- 10:30-12:00: Clarified the two-server configuration model for the rApp (Goal 1)
	(Status: Complete. Documented that the flow has two configurable identities: the HPE/OCloud runner and the IAPC/UE-control host. Captured the key parameters: `server`, `target_identity`, `ue_serial`, `iapc_host`, and `iapc_port`.)
- 13:00-14:30: Consolidated OCloud PNF/VNF recovery behavior (Goal 1)
	(Status: Complete. Summarized the PNF failure pattern around terminating pods, `UnexpectedAdmissionError`, stale SR-IOV allocation state, and missing/contended `openshift.io/fh_sriov_up_lao` resources.)
- 14:30-15:45: Preserved Ming's cleanup-script logic for later recovery (Goal 1)
	(Status: Complete. Recorded the operational role of `/home/hpe/force_cleanup_pods.sh`: force-delete terminating/failed pods, strip finalizers if needed, detect `OutOf...` resource failures, print node capacity, and scale owners to zero to stop creation loops.)
- 15:45-17:00: Prepared next-day merge validation plan and notes (Goal 2)
	(Status: Complete. Added the [OCloud Docker and pod recovery note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-16_WINLAB_OCloud_Docker_and_Pod_Recovery.md) and [2026-07-16 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-16_Daily-Note.md), setting up the next target: a clean Dockerized OCloud run followed by Outlet 2 power export and merge.)

## 2026/07/17
**Short-term Goals**
1. [Validate a successful Dockerized OCloud E2E run](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-17_Daily-Note.md)
2. [Validate E2E throughput and Outlet 2 active-power merge](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-17_WINLAB_E2E_Power_Merge_Validation.md)
3. [Patch and verify the merge script](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/merge_winlab_e2e_power.py)

**Daily Logs**:
- 09:00-10:30: Recovered OCloud readiness and confirmed the Dockerized rApp execution path (Goal 1)
	(Status: Complete. Restored the test path enough for the Dockerized rApp on `127.0.0.1:19090` to trigger the OCloud flow with ready PNF/VNF pods and the Samsung UE controlled through `sshuser@140.118.162.81:24`.)
- 10:30-12:00: Ran a successful 100 Mbps OCloud E2E test through the Dockerized endpoint (Goal 1)
	(Status: Complete. Job `ce4d30b0-abb6-409e-96b0-74a55c1c7c79` succeeded. The UE attached with IP `10.45.0.3`; the run completed a 100 Mbps downlink/reverse-mode iPerf test for 60 seconds with 0% packet loss. Remote artifact directory: `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260717-083449`.)
- 13:00-14:15: Exported matching Outlet 2 active-power data from InfluxDB/CortexDC (Goal 2)
	(Status: Complete. Exported PDU Outlet 2 `active_power` from bucket `cortexdc_pdu`, measurement `pdu_outlet`, `asset_id=17`, `pdu_ip=192.168.10.72`, `sensor_id=16`, `sensor_name=Outlet 2`. Preserved both the exact-window and padded-window CSV files: [`pdu_data_20260717_083450_083640.csv`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/pdu_data_20260717_083450_083640.csv) and [`pdu_data_20260717_083250_083840.csv`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/pdu_data_20260717_083250_083840.csv).)
- 14:15-15:30: Patched the merge script for InfluxDB timestamp precision (Goal 3)
	(Status: Complete. Updated [`merge_winlab_e2e_power.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/merge_winlab_e2e_power.py) so InfluxDB nanosecond timestamps are truncated to Python-compatible microseconds before parsing.)
- 15:30-16:30: Ran the throughput-power merge and preserved the result (Goal 2 + Goal 3)
	(Status: Complete. Merged the OCloud artifact with the padded PDU CSV and produced [`power_throughput_summary_20260717_083449.csv`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/power_throughput_summary_20260717_083449.csv). The final row shows 100 Mbps offered load, 99.996 Mbps RX throughput, and 40.04 W Outlet 2 active power from one PDU sample inside the iPerf step window.)
- 16:30-17:00: Wrote final progress notes and next-test guidance (Goal 2)
	(Status: Complete. Added the [E2E power merge validation note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-17_WINLAB_E2E_Power_Merge_Validation.md) and [2026-07-17 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-17_Daily-Note.md). The next evidence-improvement step is to run longer traffic windows or repeated runs so each offered-load interval contains multiple PDU samples.)

## 2026/07/20
**Short-term Goals**
1. [Validate long-run Dockerized OCloud E2E execution](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-20_Daily-Note.md)
2. [Document long-run throughput artifacts and power merge validation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-20_WINLAB_Long_Run_E2E_and_Merge_Readiness.md)
3. [Harden the throughput-power merge script for long-run evidence windows](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/merge_winlab_e2e_power.py)

**Daily Logs**:
- 09:00-10:30: Prepared the OCloud E2E environment for long-run testing (Goal 1)
	(Status: Complete. Checked the Dockerized rApp path on `127.0.0.1:19090`, verified the OCloud PNF/VNF path, cleaned stale iPerf state, and confirmed the UE-control path through `sshuser@140.118.162.81:24` with Samsung UE serial `R5CN30TMBYR`.)
- 10:30-12:00: Validated long-run timeout/watchdog behavior before the larger run (Goal 3)
	(Status: Complete. Confirmed the reason earlier long requests appeared stuck: the UE-side Android iPerf process could keep traffic active but fail to return cleanly. Preserved the fix direction in [`merge_winlab_e2e_power.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/merge_winlab_e2e_power.py) by making merge windows prefer actual captured iPerf intervals when available.)
- 13:00-15:00: Ran and analyzed the long 200 Mbps OCloud E2E test (Goal 1 + Goal 2)
	(Status: Complete. Job `3bb047b9-2b21-48b5-bc3b-d66f2a79dcba` succeeded. Remote artifact directory: `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260720-061120`. The run captured 1676 UE samples with average RX throughput `199.892 Mbps` for a `200 Mbps` offered load.)
- 15:00-16:00: Preserved local artifact snapshot and documented the evidence caveat (Goal 2)
	(Status: Complete. Copied the available artifact files under `runs/hpe_artifacts/e2e-ocloud-20260720-061120`, including `summary.json`, `iperf_timeseries.csv`, throughput plots, offered-load CSV/plot, stdout, request/command metadata, and pod logs. Documented that the one-hour request produced about 1676 captured one-second samples, so it is valid long-run stability evidence but not a strict 3600-second sample window.)
- 16:00-17:00: Wrote daily documentation and recorded the final merge blocker (Goal 2)
	(Status: Complete. Exported `pdu_data_20260720_061120_064208.csv`, ran [`merge_winlab_e2e_power.py`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/merge_winlab_e2e_power.py), and produced [`power_throughput_summary_20260720_061120.csv`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/power_throughput_summary_20260720_061120.csv). The merged row reports 200 Mbps offered load, 199.892 Mbps RX throughput, 40.097 W average Outlet 2 active power, 38.03-41.58 W range, and 31 PDU samples. Added the [2026-07-20 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-20_Daily-Note.md) and the [long-run E2E/power merge study note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-20_WINLAB_Long_Run_E2E_and_Merge_Readiness.md).)

## 2026/07/21
**Short-term Goals**
1. [Create a logging-only OAI scheduler branch](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-21_OAI_Scheduler_LogOnly_Branch_and_Build.md)
2. [Build and deploy the custom OAI gNB image through Jenkins/Quay/Helm](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-21_OAI_Scheduler_LogOnly_Branch_and_Build.md)
3. [Run custom-image and baseline-image smoke tests through the Dockerized rApp](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-21_Daily-Note.md)

**Daily Logs**:
- 09:00-10:30: Created the first low-risk OAI scheduler modification branch (Goal 1)
	(Status: Complete. Created branch `david/oai-scheduler-logonly-20260721` from the BMW nFAPI baseline and added a logging-only scheduler marker in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`. The branch produced commit `31c7aa0477586643a7acdae9c316c61c1ba0cdbf` with no intended scheduling-behavior change.)
- 10:30-12:00: Prepared Jenkins/Quay build parameters and verified the build workflow (Goal 2)
	(Status: Complete. Used the Jenkins job parameters for repository `https://github.com/bmw-ece-ntust/openairinterface5g`, branch `david/oai-scheduler-logonly-20260721`, and image tag `david-oai-scheduler-logonly-20260721`. Jenkins build #88 completed successfully and produced the expected OAI gNB image tag.)
- 13:00-14:30: Deployed the custom VNF image into `ming-ns` (Goal 2)
	(Status: Complete. Deployed `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-scheduler-logonly-20260721` through the HPE Helm VNF chart. The custom VNF pod rolled out, registered with AMF, and reached cell-in-service state.)
- 14:30-15:45: Ran custom-image smoke test and isolated the immediate failure domain (Goal 3)
	(Status: Blocked. The custom image failed before iPerf because the Samsung UE did not obtain a `10.45.x.x` address. VNF startup and AMF registration were healthy, so the failure occurred before traffic validation and before scheduler-log evidence could be collected.)
- 15:45-16:30: Rolled back VNF to `latest` and ran the baseline comparison (Goal 3)
	(Status: Complete. Restored the VNF image to `bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest` and repeated the baseline smoke test. The old image failed with the same UE attach symptom, showing that the immediate blocker was UE/RF/APN/core attach state rather than the scheduler-log image.)
- 16:30-17:00: Wrote scheduler build and deployment notes (Goal 1 + Goal 2)
	(Status: Complete. Added the [OAI scheduler log-only branch and build note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-21_OAI_Scheduler_LogOnly_Branch_and_Build.md) and [2026-07-21 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-21_Daily-Note.md). The next target is to restore stable baseline UE attachment before re-testing the custom image.)

## 2026/07/22
**Short-term Goals**
1. [Re-test old-image OCloud E2E behavior after the previous attach failure](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-22_Daily-Note.md)
2. [Diagnose missing iPerf artifacts and unstable UE attachment](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-22_Daily-Note.md)
3. [Prepare weekly progress summary for presentation](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-22_WINLAB_Weekly_Progress_Summary.md)

**Daily Logs**:
- 09:00-10:00: Re-checked current OCloud baseline state (Goal 1)
	(Status: Complete. Verified that PNF/VNF pods in `ming-ns` were Running and Ready using the old `latest` image. The UE initially had `10.45.0.14`, which showed that the old image and current radio/core state could reach attachment at least before the first run.)
- 10:00-11:15: Ran a short baseline rApp smoke test and inspected artifacts (Goal 1 + Goal 2)
	(Status: Partially complete. Job `316a7cb6-6b42-460e-8f30-51b1d282a34f` completed with return code 0 and artifact directory `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260722-024243`. However, the artifact was not valid throughput evidence because `iperf_csv`, `iperf_plot`, and offered-load outputs were empty and `ue_iperf_samples=0`.)
- 11:15-12:00: Cleared stale Android miperf state and retried the smoke test (Goal 2)
	(Status: Blocked. After force-stopping Android miperf and removing `/data/local/tmp/iperf3_log.json`, the UE no longer had a `10.45.x.x` interface. Retry job `79ed2b6f-c51c-4468-baf1-0065900bfb15` failed before iPerf because the UE did not reacquire IP within the attach timeout.)
- 13:00-14:30: Reconciled the previous-day custom-image failure against current baseline behavior (Goal 2)
	(Status: Complete. Confirmed that the scheduler-log image is not yet proven bad. The current evidence shows unstable UE attach and iPerf client behavior: the path can proceed when the UE already has `10.45.x.x`, but airplane-mode cycling or miperf cleanup can leave the UE unable to reacquire the data interface.)
- 14:30-16:00: Prepared presentation-ready weekly progress summary (Goal 3)
	(Status: Complete. Added the [WINLAB weekly progress summary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-22_WINLAB_Weekly_Progress_Summary.md), summarizing the completed Dockerized rApp, InfluxDB power export, merge script, Jenkins/Quay image build, and current UE attach blocker.)
- 16:00-17:00: Updated daily notes and old-format daily log coverage (Goal 3)
	(Status: Complete. Added the [2026-07-22 daily note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-22_Daily-Note.md), updated the daily-note index, and recorded this old daily-log entry. The next practical step is to stabilize UE attachment before continuing scheduler behavior experiments.)


## 2026/07/23
**Short-term Goals**
1. [Restore a reproducible bare-metal OCloud E2E baseline](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-23_Daily-Note.md)
2. [Locate and implement the first OAI scheduler behavior seam](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-23_WINLAB_OAI_NR_Scheduler_Code_Discovery.md)
3. [Learn the active NR downlink scheduling path before comparison testing](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-23_Understanding_OAI_NR_Downlink_Scheduling.md)

**Daily Logs**:
- 09:00-10:15: Recovered HPE network reachability after Docker removal and reboot (Goal 1)
	(Status: Complete. Confirmed the Broadcom NIC driver was present, restored the physical link on `ens1f3`, and obtained DHCP address `192.168.8.26`. This repaired host network reachability; it did not by itself establish the radio path.)
- 10:15-11:30: Compared Nemo Handy broadcast-cell evidence with the active VNF configuration (Goal 1)
	(Status: Complete. The active VNF configuration advertised PLMN `001/01`, PCI `0`, and SSB ARFCN `649920`, while Nemo Handy observed n78 ARFCN `623328` and PCI `27`. Treated this as evidence that the RU had been changed for another use. Recorded that `ssh super` then `pegam` restores the E2E RU configuration when needed, rather than running it before every test.)
- 11:30-13:00: Validated the bare-metal rApp E2E path after RU recovery (Goal 1)
	(Status: Complete. Bare-metal endpoint job `4a7915a3-9378-4afd-ab3e-28467736318b` on `127.0.0.1:9090` succeeded at 200 Mbps for 300 seconds. The server reported 6.99 GBytes transferred at 200 Mbps with 0% loss; the artifact contained 300 UE samples.)
- 13:00-15:00: Traced the OAI NR downlink scheduler and documented the safe modification boundary (Goal 2 + Goal 3)
	(Status: Complete. Identified `nr_dl_proportional_fair()` as the active resource-allocation policy. Its first two phases retain HARQ retransmissions and no-data control scheduling; phase 3 allocates new data from the largest free contiguous PRB block. Added the [scheduler discovery note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-23_WINLAB_OAI_NR_Scheduler_Code_Discovery.md) and [scheduler learning note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-23_Understanding_OAI_NR_Downlink_Scheduling.md).)
- 15:00-16:30: Implemented and published the first scoped scheduler experiment (Goal 2)
	(Status: Complete. Created an isolated HPE worktree and branch `david/oai-prb-cap-27-20260723`. Commit `d7c850098a` caps only phase-3 new-data allocations at 27 PRBs and changes the scheduler marker to `mode=oai_prb_cap_27`; HARQ/control behavior is unchanged. The branch was pushed to the BMW GitHub remote for Jenkins.)
- 16:30-17:00: Built and deployed the PRB-cap VNF image (Goal 2)
	(Status: Complete. Jenkins #89 built commit `d7c850098a` from `david/oai-prb-cap-27-20260723` and published tag `david-oai-prb-cap-27-20260723`. Rolled `oai-vnf` to `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-prb-cap-27-20260723`; its pod became Ready and registered with AMF.)
- 17:00-17:30: Isolated the PNF startup blocker before custom-image E2E validation (Goal 2)
	(Status: Blocked. PNF exited while loading the worker-mounted `libxran.so` with unresolved symbol `MLogSetTaskCoreMap`. The active `phy_k` xRAN library has no declared provider for the symbol and paired `nr-softmodem` does not export it, indicating a worker-side FHI/xRAN build mismatch rather than a VNF scheduler-image failure. Scaled PNF to zero to stop the crash loop; restore the matching FHI runtime before the 5-minute custom-image test.)


## 2026/07/24
**Short-term Goals**
1. [Restore a stable OCloud worker and baseline workloads](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-24_Daily-Note.md)
2. [Identify the immediate UE attach and NR-cell discovery blocker](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-24_Daily-Note.md)
3. [Preserve a valid baseline/custom scheduler-image A/B path](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-24_Daily-Note.md)

**Daily Logs**:
- 09:00-10:00: Recovered Lavoisier scheduling and reconciled OCloud workloads (Goal 1)
	(Status: Complete. Identified that `kubelet` on Lavoisier had been stopped. Starting it with `sudo systemctl start kubelet` restored node scheduling. Reconciled PNF/VNF after stale Pending, Terminating, and `UnexpectedAdmissionError` objects; fresh pods reached `1/1 Running`.)
- 10:00-11:00: Verified VNF target configuration and separated it from observed UE state (Goal 2)
	(Status: Complete. Confirmed the VNF advertises PLMN `001/01`, PCI `0`, n78, SSB ARFCN `649920`, and Point A `646724`; logs showed NG setup, F1 setup, and cell service. This configuration did not match the later UE condition, where Nemo Handy displayed no NR cells.)
- 11:00-12:00: Collected direct UE-control diagnostics (Goal 2)
	(Status: Complete. Confirmed the intended ADB serial `R5CN30TMBYR` identifies `SM_G9860`. The UE had only loopback in `ip -f inet addr show`, with no mobile `rmnet` interface or `10.45.x.x` address. Nemo Handy NR Cell Table was empty, so further E2E attempts could not meaningfully test the image or iPerf path.)
- 13:00-14:00: Evaluated latest-image E2E failure against radio evidence (Goal 2 + Goal 3)
	(Status: Complete. A `latest` baseline attempt also failed to attach while Nemo showed no target cell. Recorded that this is not evidence against the scheduler modification: the current blocker is RU/RF/UE discovery below the rApp and VNF scheduler.)
- 14:00-15:00: Defined the constrained recovery and A/B sequence (Goal 1 + Goal 3)
	(Status: Pending. When the RU has been used for another activity, run `rrr`, wait for recovery, then run `pegam`; verify the n78 target cell in Nemo before submitting E2E. After valid baseline traffic, repeat the same 5-minute 200 Mbps run using `david-oai-prb-cap-27-20260723`.)


## 2026/07/27
**Short-term Goals**
1. [Validate the recovered O-Cloud E2E baseline](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-27_Daily-Note.md)
2. [Document Lavoisier post-reboot fronthaul recovery](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-27_Lavoisier_PostReboot_Fronthaul_Recovery_and_Stable_E2E.md)
3. Return the shared namespace to a clean state before handoff.

**Daily Logs**:
- 09:00-10:00: Validated the bare-metal port `9090` E2E path with a 200 Mbps, five-minute downlink run.
	(Status: Complete. Job `4b44c8e9-a03a-4ed2-b6ea-b67d7397ff83` transferred 6.99 GBytes over 300.06 s at 200 Mbps with zero packet loss and saved E2E artifacts.)
- 10:00-11:30: Documented the Lavoisier recovery sequence needed after BMC reboot.
	(Status: Complete. The required order is fronthaul setup while PNF is down, kubelet start, node `Ready`, then PNF deployment. `rrr` and `pegam` are only for RU recovery after external use or reconfiguration.)
- 11:30-12:30: Reviewed bare-metal rApp behavior and image deployment provenance.
	(Status: Complete. Preserve-UE mode now exits safely when no UE address exists; the mutable `latest` image tag prevents a defensible custom-image A/B claim.)
- 12:30-14:00: Investigated a no-attachment state using UE, VNF, and radio evidence.
	(Status: In progress. Core/pod control-plane setup was healthy, but no target-cell RACH/RRC was observed. UE-visible neighboring n78 cells did not match the OAI cell configuration.)
- 14:00-17:00: Cleaned temporary `gnb` and `nrue` workloads from `ming-ns` and stopped changes when the server was handed to other users.
	(Status: Complete. Further test state is intentionally not assumed after shared use began.)


## 2026/07/28
**Short-term Goals**
1. [Restore a matched PNF runtime and isolate fronthaul startup failures](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-28_PNF_Runtime_Bundle_Rollback_and_PRACH_Investigation.md)
2. [Preserve a controlled VNF scheduler-image E2E path](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-28_Daily-Note.md)

**Daily Logs**:
- 09:00-10:30: Traced the PNF runtime from Helm values to the worker-mounted OAI/FHI artifacts (Goal 1)
	(Status: Complete. Confirmed that PNF runs host-mounted `nr-softmodem` and FHI/xRAN libraries from `/home/oai72_su`, while the VNF scheduler change remains in the Quay image. The active runtime had drifted from the preserved July 24 bundle.)
- 10:30-11:30: Separated the active-runtime ABI crash from the subsequent PRACH failure (Goal 1)
	(Status: Complete. Rebuilding the active softmodem/FHI pair removed the ABI SIGSEGV but exposed the deterministic `PRACH segmentation is not supported` assertion. This is below the VNF scheduler, rApp, and iPerf layers.)
- 11:30-12:30: Applied and validated the PNF-only matched runtime rollback (Goal 1)
	(Status: Complete. Helm release `pnf` revision `3` was configured with the July 24 `oaiBuildRoot` and matching `fhiLibDir`. PNF completed nFAPI P5/P7 setup, logged `XRAN Start! RU0 [1]`, and stayed running without the previous SIGSEGV or PRACH assertion.)
- 12:30-13:00: Restarted VNF to clear its stale nFAPI session after PNF replacement (Goal 2)
	(Status: Complete. VNF returned to `1/1 Running`; PNF and VNF were both healthy. No E2E workload was submitted during this recovery.)
- 13:00-17:00: Deferred the modified-image E2E run for shared-lab coordination (Goal 2)
	(Status: Deferred. The UE had obtained a valid address, but another user began using the shared environment. Leave the PNF rollback in place and resume only after confirming an exclusive window.)

## 2026/07/29
**Short-term Goals**
1. [Read and verify the exact OAI scheduler experiment commits](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-29_OAI_Scheduler_Deep_Dive_Failure_Attribution_and_QC_Plan.md)
2. [Separate scheduler behavior from attachment and lower-layer failures](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-29_Daily-Note.md)
3. [Define the next implementation and QC path](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-29_OAI_Scheduler_Deep_Dive_Failure_Attribution_and_QC_Plan.md)

**Daily Logs**:
- 09:00-10:00: Reconciled the test environment and baseline requirements (Goal 2)
	(Status: Complete. Confirmed that foreign NR cells were visible because the Samsung UE had temporarily been taken outside its RF chamber. Under normal chamber placement it is isolated from unrelated OAI cells. Skipped another `latest` run because successful 5-, 10-, and 20-minute baseline runs already exist and the shared UE was in use.)
- 10:00-11:30: Verified the exact scheduler commit lineage and changed-file scope (Goal 1)
	(Status: Complete. Traced `5bbf48af2d` -> logging commit `31c7aa0477` -> 27-PRB commit `d7c850098a`. The custom history changes only `gNB_scheduler_dlsch.c` and `gNB_scheduler_dlsch_default_policies.c`; no RACH, RRC, nFAPI, NGAP, PNF, or xRAN source was changed.)
- 11:30-13:00: Traced the 27-PRB cap through the active proportional-fair scheduler (Goal 1)
	(Status: Complete. Confirmed that phase 1 keeps exact HARQ retransmission grants, phase 2 keeps five-RB control-only grants, and phase 3 caps only new RLC-data candidates at a maximum of 27 PRBs. `COMMIT_ALLOC()` continues to enforce CCE/PUCCH validation and resource accounting.)
- 13:00-14:30: Identified the RLC logical-channel scope and experiment limitations (Goal 1 + Goal 2)
	(Status: Complete. `update_dlsch_buffer()` aggregates all active LCIDs, so the phase-3 cap includes DRB traffic and can indirectly constrain SRB/RRC payload grants after random access. The patch cannot explain missing-cell, PRACH, xRAN, or PNF failures. It is a maximum grant cap and does not guarantee fixed 27-PRB allocations or a 273x1 versus 27x10 pattern.)
- 14:30-16:00: Defined the next scheduler implementation and QC sequence (Goal 3)
	(Status: Complete. Plan one source base with runtime-selectable baseline/cap modes, decide whether SRBs require exemption, control scheduler telemetry volume, extend `nrdlbench`, then use attach-smoke, short-traffic, and longer power/throughput validation during an exclusive UE window.)

## 2026/07/30
**Short-term Goals**
1. [Validate the custom 27-PRB scheduler in a reserved live E2E window](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/DailyNotes/2026-07-30_Daily-Note.md)
2. [Merge the actual traffic interval with InfluxDB PDU power](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-30_27-PRB_Live_Validation_Power_Merge_and_Run_QC.md)
3. [Prevent incomplete iPerf runs from being reported as successful experiments](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-30_27-PRB_Live_Validation_Power_Merge_and_Run_QC.md)

**Daily Logs**:
- 09:00-10:30: Reserved the shared UE/RU window and preflighted the O-Cloud environment (Goal 1)
	(Status: Complete. Reconciled Lavoisier, RU, PNF, VNF, core, and UE state before testing the custom scheduler image.)
- 10:30-12:00: Recovered stable PNF and VNF operation and separated worker/runtime issues from scheduler behavior (Goal 1)
	(Status: Complete. Resolved stale runtime and resource contention conditions until both pods were healthy and the Samsung UE could attach.)
- 13:00-14:00: Completed custom-image attachment and traffic smoke validation (Goal 1)
	(Status: Complete. Confirmed the 27-PRB VNF could attach the UE, establish the user plane, and generate live downlink scheduler telemetry.)
- 14:00-15:15: Ran and audited the requested 30-minute, 200 Mbps custom-image experiment (Goal 1 + Goal 3)
	(Status: Partial. Job `266b772d-de75-468e-ac56-cfc6ecd464ee` produced 1,120 positive-throughput seconds before a UE iPerf idle timeout. The API reported success, but actual completion was 62.2%; pods remained healthy and the UE stayed attached.)
- 15:15-16:00: Verified the live 27-PRB scheduler behavior (Goal 1)
	(Status: Complete. Parsed 14,072 `[WINLAB_SCHED_LOG]` rows. Both new transmissions and retransmissions had maximum `rbSize=27`, validating the cap independently from the incomplete long-run traffic session.)
- 16:00-16:40: Hardened E2E run acceptance and artifact reporting (Goal 3)
	(Status: Complete. Added expected/observed duration, completion ratio, validation warnings/errors, an 80% minimum-duration rule, and failure when no valid iPerf evidence exists.)
- 16:40-17:00: Exported InfluxDB power data and produced the corrected merged result (Goal 2)
	(Status: Complete. Corrected the merge window to stop at the final positive-throughput interval. The result was 95.910 Mbps mean RX and 40.129 W mean active power across 18 PDU samples; no energy-saving claim is made without a same-day baseline.)
