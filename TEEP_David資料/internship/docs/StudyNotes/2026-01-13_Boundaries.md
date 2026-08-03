# Day 2 - Boundaries Lock (2026-01-13)

## Problem statement (1 paragraph)
Status: Done (frozen for Week 1)
Deadline: 2026-01-13

During probation we are building a **repeatable measurement + analysis method** for O-RAN energy testing, and validating it in a **software-only setup** (no RU hardware and no external power instrumentation in our possession). Practically, this means our Week 1 “pilot” result is **platform power under RU-like workload** (measured/estimated on the compute host) plus clean definitions for metrics, scenario windows, and logging. The long-term goal remains RU power consumption measurement at a clearly defined electrical measurement point (ideally RU AC input via smart PDU/analyzer), but that is explicitly deferred until hardware access exists. This matters because energy costs are a growing part of operator OPEX and O-RAN energy-saving features are only meaningful if we can quantify (and reproduce) their impact in a repeatable way. We will align our definitions with the Open RAN Handbook’s framing: energy consumption (J/kWh), energy efficiency (e.g., data volume per energy), and energy savings as a delta vs a baseline over the same duration. Because coarse sampling can hide fast transients, we scope probation results to steady-state windows and avoid claims about fast dynamics.

## In-scope vs out-of-scope
Status: Done (locked)
Deadline: 2026-01-13

**In-scope (must deliver in probation):**
- Software-only, reproducible test method (definitions + scenario structure + logging)
- Platform power under RU-like workload (compute-host measurement/estimate)
- State-style scenarios: idle vs active-idle vs load sweep (low/med/high)
- A small, reproducible scenario matrix + run duration
- A repeatable data format (power + KPI timestamps)

Concretely, in probation we are aiming for a “first working benchmark slice” that can be repeated on-demand: start from a known RU configuration, run traffic for a fixed window, and produce comparable outputs (power vs time and a small table of averages).

**Out-of-scope (explicitly NOT claiming in probation):**
- Full vendor-to-vendor RU comparison
- Any RU wall-power claims (no RU AC/DC measurement during probation)
- RF output power sweep / PA efficiency (unless explicitly required)
- Transient dynamics claims if polling is coarse (e.g., 10s PDU)

We also treat end-to-end system optimization as out-of-scope for probation: the O-RU’s energy behavior is interdependent with O-DU/O-CU/RIC and cloud platform effects, so we will avoid claims that require isolating all other contributors.

## Definitions we will freeze (avoid endless rework)
Status: Frozen for Week 1 (change only if instrument constraints force it)
Deadline: 2026-01-13

- **Measurement point (Week 1 assumption):** platform-level power/energy estimate on the compute host running the RAN workload, exported via a software tool (e.g., Scaphandre / Kepler) and time-aligned with workload KPIs.
- **Measurement point (target once hardware exists):** AC input to the RU (single feed) measured by a smart PDU outlet (or power analyzer). This remains the end-goal for “RU power measurement replication”, but we are not assuming it is available right now.
- **Power metric:** average power (W) as the mean of samples during a steady-state window (no ramps, no config changes). If using a PDU later, the same definition applies.
- **Energy metric:** energy consumption (EC) over the same window in Wh (or J), computed by integrating the sampled power: $E \approx \sum_i P_i \Delta t$. (This matches the handbook’s EC definition and keeps units consistent.)
- **Load definition (primary):** throughput target (DL Mbps) driven by `iperf3` traffic generation in a software-only setup; we log CPU utilization (if available) as supporting context.
- **Scenario duration:** 2 min warm-up + 5 min steady-state per state, with at least 1 min between states for configuration/traffic stabilization. This is intentionally chosen to be compatible with coarse polling and to support repeatability.

Labeling rule (to avoid over-claiming): until RU AC measurements exist, any plots/tables are reported as “platform power under RU-like workload” and not claimed as RU wall power.

Scenario matrix (minimal):
- Idle (no user traffic)
- Active-idle (stack up, but no user traffic)
- Load-L / Load-M / Load-H defined as ~10% / ~50% / ~90% of the RU’s observed max sustainable DL throughput for the chosen config (so targets scale to the RU and bandwidth)

## Baseline alignment decision
Status: Done (baseline chosen)
Deadline: 2026-01-13


- Primary baseline doc(s):
	- WINLAB/POET paper baseline already summarized on Day 1 (tooling + cadence + workload style)
	- Open RAN Handbook (2nd ed., Feb 2025) for definitions and benchmark framing (EC/EE/energy savings, scenario categories like idle/low/medium load)
	- O-RAN Testing whitepaper (Apr 2025) for KPI/performance testing framing and repeatability warnings
- What we will replicate exactly:
	- A small state-based scenario (idle vs active-idle vs traffic load sweep) with fixed run windows
	- A power-vs-time plot derived from a consistent sampling cadence
	- A throughput-driven load definition (iPerf-style), with KPIs logged alongside power timestamps
- What we cannot match (and how we’ll compare anyway):
	- We cannot guarantee matching RU model, bandwidth, UE emulator, or full POET stack; we will compare trends and normalized efficiency metrics (e.g., $J/bit$) rather than absolute watts alone.
	- If we do not have PRB telemetry, we will still report throughput + configuration parameters and treat PRB as an explicit limitation.

## Deliverables for probation (what “done” looks like)
Status: Done (acceptance criteria)
Deadline: 2026-01-13

Minimum acceptable (pick 3-5 bullets):
- A finalized scope note + action plan (this note + Day-2 plan)
- 1 reproducible RU measurement run (pilot) with the frozen scenario structure and saved raw logs
- A plot: power vs time covering at least 3 state-style scenarios (idle/active-idle/one load point)
- A small table: mean power and energy for each state + throughput achieved
- A short comparison paragraph vs baseline trends + explicit limitations (sampling cadence, missing KPIs, hardware mismatch)

## Open questions (decision-needed)
Status: Reduced to blockers only
Deadline: 2026-01-13

Keep only questions that block progress:
- Do we have access to a smart PDU outlet (or equivalent) that can log per-outlet real power on a fixed cadence (target: 10s) and export timestamps?
- How do we reliably force “active-idle” vs “idle” for the specific RU setup (carrier on/off? DU process running? specific config toggle)?
- What is the simplest way to generate controlled DL load in our lab (iperf client/server placement, traffic path) without needing UE emulation on Day 1 of measurements?
- Can we obtain PRB utilization telemetry from the DU/RU for correlation, or do we treat throughput-only as the primary load proxy for probation?

Resolved defaults (chosen because you have no hardware/materials on hand right now):
- **(1) Instrument availability:** assume no PDU/analyzer yet → proceed with software power export on the compute host; RU AC input measurement becomes a later upgrade.
- **(2) Idle vs active-idle:** define using software state: idle = stack not running / cell not enabled; active-idle = stack running + cell enabled + no user traffic for the full steady-state window.
- **(3) Load + KPIs:** use `iperf3` throughput targets as the primary load proxy; assume PRB telemetry is not available at first and treat PRB as a follow-up improvement.

## Sources used (canonical)
- POET baseline (local PDF): `assets/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`
- Open RAN Handbook (2nd ed., Feb 2025) for EC/EE/energy-savings definitions (local/mentor-provided)
- O-RAN Alliance testing/benchmark framing (Apr 2025) (link/details tracked in `assets/13 Jan/Links.md`)
- iPerf3 (load generation reference): https://iperf.fr/
