# Analysis Plan (2026-01-14)

## Plots and tables to reproduce
Status: Done
Deadline: 2026-01-14

## Why these outputs (plain-English)
- The goal is not “many plots.” The goal is **one defensible story**:
	- when the system state changes, the workload/KPIs change,
	- and the power signal changes in a stable, repeatable way,
	- and we can summarize it consistently across runs.
- A single good **power vs time** plot plus a small per-state table is enough to prove the method works.

Primary outputs (minimum probation set):
- Plot 1: power vs time for a single run that includes at least 3 states in sequence (idle → active-idle → one load point). Annotate state boundaries on the timeline.
- Table 1: per-state summary for that run (mean power W, energy Wh/J, achieved throughput, and any available CPU/utilization counters).

What Plot 1 teaches you (as an intern):
- whether your workload steps are actually happening,
- whether your power estimator is stable enough to see differences,
- whether timestamps and scenario markers are trustworthy.

Expanded outputs (Week 3–4, if time):
- Plot 2: mean power (W) vs load level (Load-L/M/H), with error bars from repeats.
- Plot 3: energy efficiency vs load using $J/bit$ (or $bit/J$), where $E/bit = E_{window}/DV_{window}$ and $DV$ is data volume transferred.
- Table 2: repeatability summary (mean, stddev, coefficient of variation) for each state.

Baseline alignment plots (trend comparison):
- Plot 4 (optional): power measurement stream comparison if both are available later (software estimator vs PDU/analyzer), shown as two aligned time-series over the same scenario.

## Computation
Status: Done
Deadline: 2026-01-14

## Minimal data you must record (software-only)
Even if you don’t build a full pipeline yet, you need these fields to make the analysis reproducible:
- `timestamp_utc`
- `scenario_id` (idle, active-idle, load-l/m/h)
- `power_w` (from estimator)
- `throughput_mbps` (from `iperf3` summary for the same steady-state window)

Nice-to-have context fields:
- CPU utilization (%), memory, NIC tx/rx
- tool versions (estimator version, kernel, CPU model)

Windowing / filtering:
- Run structure per state: warm-up window (ignored) + steady-state window (analyzed).
- Default: warm-up 2 min, steady-state 5 min.
- Filter rule: drop any samples during transitions (config changes, traffic ramps). Treat those as “unscored” segments.

Power (W):
- Compute per-state mean power $\bar{P} = \frac{1}{N}\sum_i P_i$ over samples in the steady-state window.

Energy consumption (Wh / J):
- Integrate sampled power: $E \approx \sum_i P_i \Delta t$.
- Convert units as needed: $1\,Wh = 3600\,J$.

Data volume (DV):
- Primary DV source (software-first): `iperf3` reported bytes transferred over the steady-state window.
- If packet captures or counters exist later, use them only as cross-checks.

Energy efficiency:
- $E/bit = E_{window} / DV_{window}$ (J/bit) and optionally $bit/J$ as the inverse.

Repeatability:
- For each state/load point, run at least 3 repeats and report mean + stddev, and coefficient of variation $CV = \sigma/\mu$.

## Comparison method
Status: Done
Deadline: 2026-01-14

## Common beginner mistakes (avoid these)
- Mixing windows (energy computed over a different time span than throughput).
- Forgetting warm-up (including ramps/transitions in your averages).
- Comparing absolute watts across different machines or configurations without labeling changes.
- Not recording tool versions (software estimators can change behavior across versions).

What “comparison” means in probation (software-first):
- We compare the shape/trend of curves and the experiment structure rather than absolute RU watts.
- We report clearly that power values are “platform power under RU-like workload” until RU AC/DC/PoE measurements exist.

Qualitative checks:
- Ordering check: $P_{idle} < P_{active-idle} < P_{load}$.
- Monotonicity: mean power increases with load (Load-L < Load-M < Load-H).

Quantitative checks (internal consistency):
- Repeatability threshold: per-state coefficient of variation should be “small enough to see state differences” (target: CV ≤ 5–10% for stable states; if higher, increase window length or fix workload stability).
- Efficiency sanity: $J/bit$ decreases as load rises until saturation/inefficiency effects appear; document deviations.

If later hardware measurement exists:
- Add an alignment run where both PDU/analyzer and software estimator are recorded; quantify agreement using correlation and mean absolute error over steady-state windows.

## Step-by-step workflow (raw logs → results)
1) Run a step-test scenario: idle → active-idle → load.
2) Ensure time sync (UTC) and record scenario markers.
3) Plot raw `power_w` vs time and visually choose steady-state windows.
4) Compute per-state mean power and energy on the steady-state windows.
5) Join in `iperf3` throughput for the same windows.
6) Produce Plot 1 + Table 1.
