# Day 9 (Week 4): Virtual O-RU Power Model (Assumptions + Validation Plan)

## Objective
Define a **transparent, reviewer-safe** way to map our Week 3/Day 8 traffic sweep timeline onto an **estimated O-RU power curve**, so we can quantify the “gap” between:
- **Measured platform power** (laptop/mini-PC running traffic sink), and
- **Estimated O-RU power** (static + load-dependent RF chain cost).

This is not claiming “we measured RU power” — it is explicitly a **model-based transformation** used for Week 4 interpretation.

## Inputs (current repo artifacts)
- Power trace (proxy): `runs/2026-01-28/sweep-01/power_uw.txt` (Scaphandre-based, uW → W)
- Sweep markers (timing + segment labels): `runs/2026-01-28/sweep-01/markers.csv` (real CSV)
- Labeled power table (derived, W + state + round): `runs/2026-01-28/sweep-01/power_labeled.csv`

Absolute links (publish-ready):
- Run folder: [runs/2026-01-28/sweep-01](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-28/sweep-01)
- Plots + summary: [assets/2026-01-28/plots](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/assets/2026-01-28/plots)

## Jan 28 run note (data integrity)
Earlier in the Jan 28 work, the power logger could write non-numeric lines into `power_uw.txt` because Prometheus exporters include `# HELP` / `# TYPE` metadata lines. That made the trace too short/unusable.

Fix: the logger now extracts only the numeric sample line for `scaph_host_power_microwatts`, and tolerates transient `curl` failures without exiting the loop.

## Load definition used by the model
We map experiment segments to a normalized load value $L\in[0,1]$:
- `Load_L_*` → $L=0.3$
- `Load_M_*` → $L=0.6$
- `Load_H_*` → $L=1.0$
- Everything else (idle/cooldown) → $L=0$

Important limitation: **throughput load is not identical to RF output power load**. We treat it as a practical proxy for “RU operating point” during probation.

## Power model
We use a standard linear macro-RU approximation:

$$ P_{RU}(L) = P_{static} + (P_{max}-P_{static})\cdot L $$

Where:
- $P_{static}$ is the non-zero baseline (FPGA/ASIC leakage, RF biasing, always-on circuitry)
- $P_{max}$ is nameplate/max draw at full load

### Default parameters (now citation-backed)
We now have a **direct Watts-vs-load mapping** for two RU classes from a local paper:

- **Macro RU (highway scenario anchor):** $P_{min}=197\,\text{W}$, $P_{max}=531\,\text{W}$ (static ratio $\approx 197/531 \approx 0.371$)
- **Micro RU (highway scenario anchor):** $P_{min}=59\,\text{W}$, $P_{max}=110\,\text{W}$ (static ratio $\approx 59/110 \approx 0.536$)

Source: *Digital Twin for Network Energy Consumption* (local PDF: `assets/2026-01-12/WINLAB Baseline/P12.pdf`).

Exact citation locations (for reviewer-proof traceability):
- Page 1, Section "Equations" ("Basic RU Power Model"): Macro RU $P_{min}=197$ W, $P_{max}=531$ W; Micro RU $P_{min}=59$ W, $P_{max}=110$ W; `ru_load` used as load scaling factor
- Page 1, Section "Highway Traffic Dataset": `ru_load` derived from traffic volume measured as bytes/hour (7-day dataset)
- Page 1, Section "O-RAN Architecture": RU power measurement point is the RU individual component (Watts)
- Page 1, Sections "Highway Scenario" and "Data Collected/Plots": 30-mile highway NJ↔NYC; Macro tower range 1000 m; Tx power 45 dBm; max user capacity 6000

The Week 4 notebook uses the **Macro RU anchor** as the baseline for the gap plot, and includes both macro/micro anchors in the sensitivity sweep.

Important limitation: their load proxy is `ru_load` derived from hourly traffic volume (bytes/hour). Our experiment load proxy is segment-based ($L \in \{0.3, 0.6, 1.0\}$). We use the cited values to bound plausible RU power, not to claim a precise physical mapping.

## Parameter table (for citation + reuse)
These are the concrete values we can cite and reuse in the Week 4 notebook.

| Class | $P_{min}$ (W) | $P_{max}$ (W) | Static ratio $P_{min}/P_{max}$ | $\Delta = P_{max}-P_{min}$ (W) |
|---|---:|---:|---:|---:|
| Macro RU (P12 anchor) | 197 | 531 | 0.371 | 334 |
| Micro RU (P12 anchor) | 59 | 110 | 0.536 | 51 |

### Derived model points at our experiment load levels
We use $P(L) = P_{min} + (P_{max}-P_{min})\cdot L$.

Macro RU (P12):
- $P(0.0)=197.0$ W
- $P(0.3)=197 + 334\cdot 0.3 = 297.2$ W
- $P(0.6)=197 + 334\cdot 0.6 = 397.4$ W
- $P(1.0)=531.0$ W

Micro RU (P12):
- $P(0.0)=59.0$ W
- $P(0.3)=59 + 51\cdot 0.3 = 74.3$ W
- $P(0.6)=59 + 51\cdot 0.6 = 89.6$ W
- $P(1.0)=110.0$ W

These derived points are especially useful for fast “back of the envelope” checks when reviewing plots.

### Separate reference: virtualized O-RAN (server-side) power
We also have citable **server electrical input power** (not RU hardware power) from:
- *POET: A Platform for O-RAN Energy Efficiency Testing* (local PDF: `assets/2026-01-12/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`)

Exact citation locations (to avoid mixing server vs RU):
- Page 4, Figure 4: PDU as ground-truth server power (vs IPMI and Kepler)
- Page 5, Section "V. RESULTS": Baseline 4.13 W; 1 UE 22.2 W; 2 UE 22.9 W; server saturation 330 W at 32-CPU stress
- Page 2, Section "II. ENERGY EFFICIENCY...": load defined by UE/RRC connections per cell and DL/UL PRB utilization per cell

Use this to contextualize the **software stack power** of CU/DU/Core testbeds vs RU hardware. Do **not** use POET server numbers as $P_{RU}$ parameters.

## Sensitivity (what changes if parameters differ?)
The “gap” story is robust as long as RU static power is large relative to the proxy platform.

Example parameter sweep (for interpretation only):
- If $P_{max}\in\{200,300,400\}\,\text{W}$
- And $P_{static}/P_{max}\in\{0.3,0.4,0.5\}$

Then $P_{static}$ ranges from **60 W → 200 W**, which still dwarfs the measured proxy idle (~2 W) and active (~7–8 W).

## Concrete comparison (using our trimmed medians)
To keep this reviewer-safe, we compare **medians inside marker-aligned, boundary-trimmed windows**.

From the generated summary (Jan 28 run):
- Proxy idle median (trimmed): $\approx 5.696$ W
- Proxy active median (trimmed): $\approx 24.983$ W
- Proxy high-load (100%) median (trimmed): $\approx 26.926$ W

Artifact: `assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md`

Ratios (RU / proxy):
- Micro RU idle vs proxy idle: $59 / 5.696 \approx 10.36\times$
- Macro RU idle vs proxy idle: $197 / 5.696 \approx 34.59\times$
- Micro RU full-load vs proxy high-load: $110 / 26.926 \approx 4.09\times$
- Macro RU full-load vs proxy high-load: $531 / 26.926 \approx 19.72\times$

Interpretation: once you include RU hardware, **static power dominates** (especially macro), and the proxy platform measurements represent only a small portion of a full RU energy budget.

## Validation plan (Week 4 checklist alignment)
To make this model “Week 4 ready”, we'll validate/justify each piece:
1. **Data consistency:** confirm marker timestamps overlap the power trace time span; detect missing start/stop pairs.
2. **Outliers:** flag power spikes unrelated to load markers (background tasks).
3. **Parameter justification:** keep a citation-backed baseline (P12 macro/micro anchors) and optionally add additional cited ranges (ETSI/EARTH/vendor datasheets) to strengthen generality.
4. **Compare scaling:** overlay our modeled curve against a reference curve (WINLAB-style) and confirm shape and static ratio are plausible.

## How to describe this in a report (safe wording)
- We **measured** platform power under a traffic-timed workload (proxy).
- We **modeled** RU power using a cited linear mapping $P(L)$ to estimate the RF-chain baseline and dynamic range.
- The model uses a *load proxy* and is intended for **interpretation and bounding**, not a claim of RU power measurement.

## Glossary (quick study reference)
- $P_{min}$ / $P_{static}$: power at “zero load” (non-zero baseline).
- $P_{max}$: peak power at full load.
- Static ratio: $P_{min}/P_{max}$; indicates how “always-on” the device is.
- $\Delta$: dynamic range, $P_{max}-P_{min}$.
- Load proxy ($L$): a normalized indicator (throughput, PRB utilization, UE count, bytes/hour) used to index the model.

## Self-check questions
1. Why is throughput not necessarily proportional to RF output power?
2. What changes in the narrative if $P_{min}/P_{max}$ is high vs low?
3. What measurement point differences can invalidate a direct comparison (AC plug vs RU-only vs RU+DU+CU)?
4. If we switch from macro to micro RU anchors, how does the baseline gap change and why?

## Deliverable link
Notebook implementing parsing + model + plot:
- `notebooks/Week4_Virtual_ORU_Simulation.ipynb`

Generated artifacts (Day 9):
- `assets/2026-01-28/plots/gap_analysis_simulation.png`
- `assets/2026-01-28/plots/gap_analysis_sensitivity.png`
- `assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md`

Absolute links:
- [gap_analysis_simulation.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_simulation.png)
- [gap_analysis_sensitivity.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity.png)
- [gap_analysis_sensitivity_summary.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md)
