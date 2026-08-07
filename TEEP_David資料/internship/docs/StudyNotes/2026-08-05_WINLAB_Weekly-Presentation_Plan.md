# WINLAB Weekly Presentation Plan

**Prepared:** 2026-08-05  
**Presentation constraint:** exactly 10 minutes per presenter  
**Recommended speaking target:** 9 minutes 15 seconds, leaving 45 seconds of safety

## Presentation Requirements

The presentation must include:

- system architecture;
- progress, including a hyperlink to the final checklist and a brief explanation;
- problem;
- plan;
- expected goals.

These slides will also be used for the final presentation. Maintain one master deck and update it weekly rather than producing disposable weekly slides. Detailed evidence, commands, logs, and recovery procedures should be placed in backup slides.

## Recommended Main Deck

| Slide | Topic | Target time |
|---:|---|---:|
| 1 | Research question and scope | 0:30 |
| 2 | System architecture | 1:15 |
| 3 | Weekly progress and final checklist | 1:10 |
| 4 | Custom PRB-allocation playback dashboard | 0:45 |
| 5 | 900 Mbps PRB-cap experiment | 1:30 |
| 6 | OAI-latest baseline throughput/power curve | 1:35 |
| 7 | Problems and technical interpretation | 1:20 |
| 8 | Plan, expected goals, and closing | 1:10 |
|  | **Planned total** | **9:15** |

## Slide 1 — Research Question and Scope

Suggested title:

> OAI Scheduler Allocation vs. O-RU Power Consumption

Show only:

- research question;
- WINLAB/O-Cloud single-UE setup;
- presenter name and date.

Research question:

> How does OAI downlink scheduler resource allocation change delivered UE throughput, Pegatron O-RU active power, and energy per delivered bit?

Suggested opening:

> This week I moved from proving custom scheduler behavior to measuring how throughput and O-RU power change across scheduler caps and offered loads.

## Slide 2 — System Architecture

Use one clean diagram based on this flow:

```text
Git/OAI source → Jenkins → Quay
                         ↓
                 Kubernetes VNF
                 OAI MAC scheduler
                         ↓ nFAPI P5/P7
              PNF worker-side runtime
                         ↓ O-RAN FHI 7.2
                    Pegatron O-RU
                         ↓ RF
                    Samsung UE
                         ↓ iPerf
                     Open5GS core

rApp → orchestration and artifacts
PDU Outlet 2 → InfluxDB → power/throughput merge → plots
```

Visually distinguish three paths:

1. **Build/deployment:** Git, Jenkins, Quay, and the VNF image.
2. **Radio/data path:** VNF, nFAPI, PNF, O-RU, UE, and core.
3. **Measurement path:** rApp, iPerf artifacts, PDU Outlet 2, InfluxDB, merge, and plots.

The slide must make the VNF/PNF split explicit:

- the VNF container image contains the OAI MAC scheduler under test;
- the PNF executes a separate worker-mounted OAI/FHI/DPDK runtime;
- changing the VNF image does not replace or repair the PNF worker runtime.

## Slide 3 — Weekly Progress and Final Checklist

Use no more than five progress rows:

- ✅ Restored Jenkins and Quay; built immutable 54- and 104-PRB images.
- ✅ Validated custom caps with scheduler telemetry, not throughput inference alone.
- ✅ Completed the 900 Mbps 27-/54-/104-PRB and OAI-latest comparison.
- ✅ Built and power-aligned the OAI-latest baseline curve through 600 Mbps.
- ⏳ Complete 700–900 Mbps and repeated trials for uncertainty.

Create and maintain a dedicated `docs/WINLAB-Final-Checklist.md`. The slide should hyperlink to its full GitHub URL:

`https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/WINLAB-Final-Checklist.md`

The checklist should track:

- environment and reproducibility;
- immutable VNF and PNF condition identity;
- baseline offered-load curve;
- scheduler comparisons;
- repetitions and uncertainty;
- final power model;
- final dataset, report, and presentation.

Suggested explanation:

> This checklist separates completed engineering validation from the scientific evidence still required for the final claim.

Until that dedicated checklist is created, link the progress slide to [the August 5 study note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-08-05_WINLAB_OAI-Latest_Load-Sweep_Power-Curve_and_Run-QC.md), especially its “Scientific Status and Next Work” section.

## Slide 4 — Custom PRB-Allocation Playback Dashboard

Include the dashboard in the slides; do not depend on a live demo alone. The deck must preserve the evidence even when the browser or demo environment fails.

Primary assets:

- [Dashboard `index.html`](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/winlab_scheduler_playback/index.html)
- [Dashboard README](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/winlab_scheduler_playback/README.md)
- [QA screenshot](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/assets/winlab_scheduler_playback/qa-desktop.png)

Place one dashboard screenshot on the slide and add three or four callouts:

- UE/RNTI and connected-device identity;
- new transmission versus HARQ retransmission;
- allocated PRB start and size;
- MCS, TBS, and HARQ process.

State clearly that this is an **offline playback of measured scheduler telemetry**, not a live monitoring dashboard.

Suggested narration:

> We did not infer scheduler behavior from iPerf throughput alone. We built this playback from measured OAI scheduler logs. It shows each new transmission and retransmission, including PRB allocation, MCS, TBS, and HARQ state. This independently verified that the custom image actually enforced the intended new-data PRB cap.

### Optional live demo

The live demo is optional and should last only 20–30 seconds:

1. Open and test it before the presentation.
2. Leave it preloaded on the exact view to be shown.
3. Click once to show one representative grant transition.
4. Return immediately to the slides.

Do not type terminal commands, wait for loading, or navigate through several views during the timed presentation. If anything is uncertain, show only the screenshot and keep the demo as backup.

## Slide 5 — 900 Mbps PRB-Cap Experiment

Use a compact chart or this table:

| Condition | Delivered throughput | Mean power | Energy / delivered bit |
|---|---:|---:|---:|
| 27 PRB | 95.601 Mbps | 40.952 W | 428.36 nJ/bit |
| 54 PRB | 191.585 Mbps | 41.258 W | 215.35 nJ/bit |
| 104 PRB | 362.052 Mbps | 41.536 W | 114.72 nJ/bit |
| OAI `latest` | 760.715 Mbps | 41.988 W | 55.20 nJ/bit |

Main takeaway:

> Delivered throughput changed by approximately eight times, while measured O-RU power changed by only about 1 W.

Scientific boundary:

> These are sequential single runs from different image lineages. They provide strong descriptive evidence, but not yet a causal power model.

Full evidence is documented in [the August 4 PRB-cap sweep study note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-08-04_WINLAB_900Mbps_PRB-Cap_Sweep_and_Debug-UI_Assessment.md).

## Slide 6 — OAI-Latest Baseline Power Curve

Use the completed [four-panel throughput/power/energy/completeness plot](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/analysis/20260805_oai_latest_baseline_100_600/load_sweep_overview.png).

Explain only three observations:

1. Delivered throughput follows offered load through approximately 400 Mbps.
2. Saturation begins around 500–600 Mbps.
3. Mean Outlet 2 active power rises only from approximately 40.6 to 42.0 W.

Initial complete-point model:

`P(W) = 40.2752 + 0.0032028 × delivered throughput(Mbps)`, with `R² = 0.9246` and `n = 4`.

Immediately qualify it:

> This is an initial descriptive curve. Repeated runs and the remaining 700–900 Mbps points are required before calling it a validated RU power model.

Keep the incomplete 300 and 600 Mbps points orange and visible. Do not quietly present them as equivalent to the complete points.

## Slide 7 — Problems and Technical Interpretation

Divide the slide into **Observed** and **Interpretation**.

### Observed

- Multi-band automation sometimes stalled between bandwidth steps.
- VNF logs contained `SDU rejected, SDU buffer full`.
- RRC re-establishment requests used cause `Other Failure`.
- The VNF/radio path stopped progressing during some higher-load attempts.
- The 600 Mbps retry delivered 549.112 Mbps and terminated after 65.333% completion.

### Interpretation

- Evidence is consistent with backpressure and split-path timing instability.
- Current evidence does not isolate one root cause.
- The failure cannot be attributed only to the custom scheduler.
- The baseline VNF is not older than the professor-requested OAI version.

Version and MIMO evidence:

- OAI `2026.w28` is commit `70508ebaf52f2aae420566d380c6537f2efb9f0c`.
- VNF commit `9522317237738e3c4d1f4e006dc3b27faf5904b5` is 13 commits newer.
- Configuration permits four MIMO layers, but the UE repeatedly reported `RI 2`.
- The measured single-UE link was therefore effectively operating at rank two.

This rank-two evidence helps contextualize the earlier 760.715 Mbps result under a 900 Mbps offered load.

## Slide 8 — Plan, Expected Goals, and Closing

### Plan

**Phase 1 — Complete the baseline**

- Run 700, 800, and 900 Mbps individually.
- Repeat selected loads.
- Preserve precise per-step pod-log and traffic markers.

**Phase 2 — Validate the model**

- Calculate mean and variance per operating point.
- Add defensible uncertainty ranges.
- Analyze the saturation region separately.

**Phase 3 — Deeper scheduler experiment**

- Use one current OAI source base.
- Implement runtime-selectable baseline and custom modes.
- Avoid image-lineage confounding.
- Compare scheduler telemetry, throughput, power, and energy per bit together.

### Expected final goals

- reproducible throughput-versus-O-RU-power model;
- controlled baseline-versus-custom scheduler comparison;
- scheduler telemetry correlated with throughput and power;
- completeness and energy per delivered bit reported for every condition;
- final checklist, dataset, plots, methodology, and report.

Suggested closing takeaway:

> Current evidence suggests that the Pegatron O-RU has a large load-independent power component. The next step is to determine whether scheduler behavior creates a measurable change beyond normal run-to-run variation.

Finish with:

> Thank you. I choose ___ as the next presenter.

## Presentation Rules

- Use a 16:9 layout.
- Keep body text at 26–28 pt or larger.
- Present one message per slide.
- Use no more than three main speaking points per slide.
- Use the chart or dashboard as evidence rather than reading tables aloud.
- Put GitHub hyperlinks in a consistent footer or hyperlink the relevant image/title.
- Rehearse for 9:00–9:15, never exactly 10:00.
- Keep the live dashboard preloaded, but make the screenshot sufficient on its own.
- Do not expose credentials, internal tokens, or unnecessary terminal output.

## Recommended Backup Slides

1. Exact VNF image digests and OAI commits.
2. VNF-image versus PNF-worker-runtime split.
3. Full run-completeness table.
4. RRC/RLC/P7 failure timeline.
5. Outlet 2 power-alignment methodology.
6. Full experimental/final checklist.
7. Dashboard controls and telemetry-field definitions.

Backup slides are not part of the timed flow unless the professor asks a question.
