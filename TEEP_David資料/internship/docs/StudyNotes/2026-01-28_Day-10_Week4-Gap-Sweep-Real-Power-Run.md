# Day 10 (Week 4): Gap Sweep With Real Power Logging (Jan 28)

**Date**: 2026-01-28  
**Status**: Completed (publishable artifacts generated)  

## Objective
Capture a **real** power trace during the Week 4 timing pattern (Idle + Load-L/M/H × 3), then regenerate the Week 4 deliverables:
- Gap overlay plot (proxy vs modeled RU)
- Sensitivity band plot
- Marker-aligned, trimmed-window summary (reviewer-safe numbers)

This note is designed as a **study/reference** recap: what was done, where the artifacts are, how to reproduce, and what to watch out for.

## Where the data is
### Run artifacts (raw + derived)
- Local path: `runs/2026-01-28/sweep-01/`
- GitHub folder: [runs/2026-01-28/sweep-01](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-28/sweep-01)

Key files in the run folder:
- `power_uw.txt` — power trace (uW) with UTC timestamps
- `markers.csv` — **real CSV** markers (timestamp, event)
- `power_labeled.csv` — labeled power samples (W) with `state` and `round`
- `run_console.log` — execution log / timeline
- `iperf_Load_{L,M,H}_Run{1..3}.txt` — per segment traffic evidence

### Publishable outputs
- Local path: `assets/2026-01-28/plots/`
- GitHub folder: [assets/2026-01-28/plots](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/assets/2026-01-28/plots)

Artifacts:
- [gap_analysis_simulation.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_simulation.png)
- [gap_analysis_sensitivity.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity.png)
- [gap_analysis_sensitivity_summary.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md)

## What the sweep actually did (mental model)
We run a repeated timing pattern:

- Idle baseline
- For each round (Run1..Run3):
  - Load-L (≈30% target)
  - Idle gap
  - Load-M (≈60% target)
  - Idle gap
  - Load-H (≈100% target)
  - Idle gap

Load mapping used downstream (model + labeling):
- Load-L → $L=0.3$
- Load-M → $L=0.6$
- Load-H → $L=1.0$
- Idle/cooldown → $L=0$

## Key results (numbers you can cite)
From the marker-aligned, boundary-trimmed summary:
- Proxy idle median (trimmed): **5.696 W**
- Proxy active median (trimmed): **24.983 W**
- Proxy high-load median (trimmed): **26.926 W**

Citation-backed RU anchors (P12):
- Micro RU: $P_{min}=59$ W, $P_{max}=110$ W
- Macro RU: $P_{min}=197$ W, $P_{max}=531$ W

Derived ratios (RU / proxy), using the trimmed medians:
- Micro RU idle vs proxy idle: $59/5.696 \approx 10.36\times$
- Macro RU idle vs proxy idle: $197/5.696 \approx 34.59\times$
- Micro RU full-load vs proxy high-load: $110/26.926 \approx 4.09\times$
- Macro RU full-load vs proxy high-load: $531/26.926 \approx 19.72\times$

Interpretation to remember:
- The proxy platform is measuring **compute host/platform power**, not RU AC input.
- Once you include RU hardware, **static power dominates** (especially macro), so the gap remains large even if the proxy is “efficient”.

## Study notes: why trimming + markers matter
Raw power samples around state boundaries can include ramps/transients (CPU frequency changes, scheduler jitter, cache warm-up). To keep the stats reviewer-safe:
- We segment by explicit `Start_*` / `Stop_*` markers.
- We compute medians after trimming the start/end of each segment window.

This avoids “boundary contamination” (counting transient samples as steady-state behavior).

## Data formats (so you can parse without guessing)
### `power_uw.txt`
One sample per line:
- `ISO8601Z <microwatts>`

Example:
- `2026-01-28T10:21:09Z 8054281`

### `markers.csv`
Real CSV:
- `timestamp_utc,event`

Example events:
- `Start_Load_L_Run1`, `Stop_Load_L_Run1`, …

### `power_labeled.csv`
Derived table:
- `timestamp_utc,power_w,state,round`

This is convenient for quick plotting and debugging state labeling.

## Common failure mode (and how to avoid it)
### Symptom
`power_uw.txt` contains non-numeric lines or has only a handful of samples.

### Root cause
Prometheus `/metrics` includes metadata lines like:
- `# HELP ...`
- `# TYPE ...`

If a logger script greps too broadly (or the pipeline terminates early on a transient scrape error), it can capture non-numeric content and/or stop too soon.

### Fix (conceptual)
- Extract only the numeric sample line for `scaph_host_power_microwatts`.
- Make the scrape loop resilient to transient `curl` failures.

(Implementation details are in the Week 4 runner script and referenced from Day 9 notes.)

## Data checks performed today
We verified the Jan 28 run is internally consistent and suitable for plotting/statistics:
- The power trace contains numeric samples across the full sweep duration.
- Marker timestamps cover the sweep window and include expected start/stop pairs.
- Labeled data contains the expected states and three rounds.
- Traffic logs show stable plateaus consistent with the L/M/H target rates.

## Key takeaways
- The proxy platform shows a clear idle→active increase, then a relatively narrow active band across L/M/H.
- The trimmed-window medians provide stable, marker-aligned numbers to compare against RU anchor ranges.
- With the P12 macro/micro anchors, the modeled RU baseline remains substantially higher than the proxy platform across idle and load.

## Next steps
1. Integrate the Jan 28 plots/summary into the Week 4 report draft (figures + short interpretation paragraph).
2. Add one additional citation source (ETSI/EARTH/vendor datasheet) to broaden the RU parameter bounds beyond P12.
3. Repeat the same sweep on a second host (if available) to check whether the proxy active-band width is platform-specific.
4. If needed, extend the analysis to report confidence intervals across rounds (in addition to medians) to quantify repeatability.
