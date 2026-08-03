# Day 9 (Week 4): Gap Analysis — Proxy Platform vs. Estimated O-RU

## Objective
Summarize what the Week 3/Day 8 **software-first** measurement means in real RU terms by comparing:
- **Measured proxy platform power** (laptop/mini-PC running traffic sink), vs.
- **Estimated O-RU power** produced by the Virtual O-RU model.

This provides the Week 4 deliverables: interpretation, assumptions, limitations, and a clear “what can/cannot be claimed”.

## Result (main visualization)
![Gap Analysis Plot](../../assets/2026-01-28/plots/gap_analysis_simulation.png)

## Numbers at a glance (Jan 28 update)
Citation-backed RU anchors (P12 highway digital twin):
- Micro RU: $P_{min}=59$ W, $P_{max}=110$ W
- Macro RU: $P_{min}=197$ W, $P_{max}=531$ W

Exact location in source PDF: `assets/2026-01-12/WINLAB Baseline/P12.pdf`, page 1, Section "Equations" ("Basic RU Power Model").

From the trimmed-window summary for our Jan 28 proxy trace (UDP LMH sweep):
- Proxy idle median (trimmed): $\approx 5.696$ W
- Proxy active median (trimmed): $\approx 24.983$ W
- Proxy high-load (100%) median (trimmed): $\approx 26.926$ W

Implications (RU / proxy):
- Micro RU idle vs proxy idle: $59/5.696 \approx 10.36\times$
- Macro RU idle vs proxy idle: $197/5.696 \approx 34.59\times$
- Micro RU full-load vs proxy high-load: $110/26.926 \approx 4.09\times$
- Macro RU full-load vs proxy high-load: $531/26.926 \approx 19.72\times$

## Sensitivity (robustness check)
Because $P_{max}$ and the static power ratio vary across RU classes, we also generate a parameter sweep and plot a **sensitivity band**:

Update (Jan 28): the sweep now includes **citation-backed anchor parameters** for Macro and Micro RU classes from `P12.pdf` (highway scenario digital twin), in addition to generic placeholder scenarios.

- Plot: `assets/2026-01-28/plots/gap_analysis_sensitivity.png`
   ![Gap Analysis Sensitivity Plot](../../assets/2026-01-28/plots/gap_analysis_sensitivity.png)
- Trimmed-window summary (marker-aligned, boundary-trimmed): `assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md`

Interpretation: even under the lowest sweep static power, the modeled RU baseline remains an order-of-magnitude above the proxy platform.

## Key observations
1. **Static power penalty dominates RU energy**
   - Proxy platform idle is on the order of a few watts.
   - A macro O-RU model typically has a **large non-zero baseline** ($P_{static}$), often tens to hundreds of watts.

2. **Different scaling mechanisms**
   - Proxy platform: power is mostly governed by CPU package states (P-states/C-states) and NIC/interrupt handling.
   - O-RU: RF chain dominates; PA efficiency is load-dependent, and the curve can be non-linear in real hardware.

3. **Interpretation of the “step-function” vs “flat” behavior**
   - The Week 3 artifact under `iperf3 -P 4` looked like a step increase; Day 8/Jan 23 results indicate that was largely a **load-definition + parallelism artifact**.
   - Under single-stream load (`-P 1`), the proxy platform can stay near a low plateau even at high throughput, which is plausible for an efficient CPU/NIC path.

## What we can claim (reviewer-safe)
- We measured **platform power under RU-like traffic timing** (not RU AC input power).
- Marker-based segmentation gives reproducible timing and consistent windowing.
- The Virtual O-RU model provides an explicit way to estimate the “missing” RF energy and to avoid over-claiming efficiency.
- We now have **citation-backed RU power anchors** (macro/micro $P_{min}$/$P_{max}$) to parameterize the model for Week 4 interpretation.

## What we cannot claim (yet)
- RU absolute power for *our specific run* as if it were a measured RU, because our load proxy (throughput segments) is not the same as the cited paper’s load proxy (`ru_load` from traffic bytes/hour).
- RU power outside the cited scenario/hardware definitions unless we add more sources (ETSI/EARTH/vendor datasheets) and reconcile measurement points (RU-only vs RU+DU+CU, AC vs DC).
- Energy-per-bit of an RU without mapping throughput → RF output power and accounting for PA efficiency.

## Week 4 checklist mapping
- **Data consistency / outliers:** verify marker overlap and scan for background-task spikes.
- **Idle vs active ratios:** proxy vs modeled RU ratios are explicitly compared.
- **Assumptions + limitations:** called out above; model note contains the validation plan.

## Supporting note
Model definition + assumptions live here:
- [Virtual O-RU Power Model](2026-01-26_Day-9_Virtual-ORU-Power-Model.md)

## Jan 28 run (publishable artifacts)
Run folder:
- `runs/2026-01-28/sweep-01/`

Publishable outputs:
- `assets/2026-01-28/plots/gap_analysis_simulation.png`
- `assets/2026-01-28/plots/gap_analysis_sensitivity.png`
- `assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md`

Absolute links:
- Run folder: [runs/2026-01-28/sweep-01](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/2026-01-28/sweep-01)
- [gap_analysis_simulation.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_simulation.png)
- [gap_analysis_sensitivity.png](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity.png)
- [gap_analysis_sensitivity_summary.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/2026-01-28/plots/gap_analysis_sensitivity_summary.md)
