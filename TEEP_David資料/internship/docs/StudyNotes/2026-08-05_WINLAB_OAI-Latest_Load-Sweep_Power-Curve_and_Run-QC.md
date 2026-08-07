# WINLAB OAI Latest Load Sweep, Power Curve, and Run QC

**Date:** 2026-08-05  
**Status:** 100–600 Mbps aligned and plotted; 700–900 Mbps pending; 300 and 600 Mbps retained as incomplete diagnostic points

## Objective and Controls

The immediate objective was to build the OAI `latest` baseline throughput-versus-power curve requested by the professor. The requested downlink sequence was 100–900 Mbps in 100 Mbps increments, with one ten-minute iPerf step per offered load. The UE was already attached, so the rApp requests used `preserve_ue_state=true` and `keep_ue_online_on_failure=true`; bandwidth transitions did not deliberately cycle airplane mode.

The controlled path remained the Samsung UE `R5CN30TMBYR`, Nemo target cell ARFCN 649920 / PCI 0 / PLMN 001-01, Pegatron O-RU, Raritan PDU Outlet 2, O-Cloud core and namespace, PNF worker runtime, digest-pinned VNF baseline, downlink direction, 30-second inter-step gap, and the established positive-traffic power-alignment method.

## Runtime and OAI Version Identity

| Layer | Identity | Relationship to OAI `2026.w28` |
|---|---|---|
| VNF image | `bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest@sha256:c227006518795bdb517db0db15be7c12850c9184297e4cb514ea3987a5108edc` | Source `9522317237738e3c4d1f4e006dc3b27faf5904b5`; 13 commits ahead |
| OAI `2026.w28` tag | `70508ebaf52f2aae420566d380c6537f2efb9f0c` | Reference requested by the professor |
| PNF worker runtime | Host-mounted source `b045eb399b3435ea174333232a5e76a90875c2ef` | 153 commits ahead; includes local PRACH/FHI compatibility repairs |

The VNF therefore satisfies “2026 w28 or newer”; it is not an obsolete pre-w28 image. The PNF is not supplied by the VNF image. It executes worker-mounted binaries and libraries from a distinct, later custom lineage, so both identities must remain in provenance.

The active VNF configuration allows `maxMIMO_layers = 4` with four configured PUSCH antenna ports, but preserved VNF logs repeatedly report UE `RI 2`. The defensible description of the measured single-UE link is therefore **configured for up to four layers, observed at rank two**, rather than simply claiming measured 4x4 MIMO. This helps explain why the previous 900 Mbps offered-load run delivered 760.715 Mbps rather than treating the offered rate as guaranteed radio throughput.

## Run Chronology and Selection

| Artifact | Requested step(s) | Outcome | Selection |
|---|---|---|---|
| `e2e-ocloud-20260805-051900` | 100–900 Mbps | 100 completed; first 200 was partial; the workflow was stopped when progression stalled at 300 | Use only the complete 100 Mbps point |
| `e2e-ocloud-20260805-060051` | continuation from 200 Mbps | 200 completed; 300 ran partially; workflow was stopped before a valid 400 result | Use complete 200 and diagnostic 300 |
| `e2e-ocloud-20260805-062935` | 400 Mbps | 600-second step completed successfully | Use |
| `e2e-ocloud-20260805-064253` | 500 Mbps | 600-second step completed successfully | Use |
| `e2e-ocloud-20260805-065806` | 600 Mbps | Manually stopped after traffic/radio degradation; no finalized throughput CSV | Exclude |
| `e2e-ocloud-20260805-070558` | 600 Mbps retry | 392.001-second positive-traffic window; server terminated below the 80% threshold | Diagnostic only |

The first multi-band workflow demonstrated that sequential rApp execution can preserve UE state, but it is not yet reliable enough to babysit an entire 90-minute sweep. When iPerf flattened and the VNF/radio path stopped progressing, the run was killed rather than silently waiting. Attachment was recovered and the sweep continued one bandwidth at a time. This avoided unnecessary airplane-mode transitions and made the 400 and 500 Mbps steps cleanly repeatable.

## Power Alignment and Consolidated Results

Outlet 2 `active_power` was exported once for the padded UTC interval `2026-08-05T05:18:00Z`–`2026-08-05T07:14:00Z`. The established merge script clipped that export separately to every selected iPerf positive-traffic window.

| Offered | Delivered | Completion | Mean power | Min–max power | PDU samples | Energy / delivered bit | Classification |
|---:|---:|---:|---:|---:|---:|---:|---|
| 100 Mbps | 100.008 Mbps | 100.0% | 40.594 W | 39.58–41.03 W | 10 | 405.909 nJ/bit | Complete |
| 200 Mbps | 200.007 Mbps | 100.0% | 40.992 W | 40.15–41.50 W | 10 | 204.952 nJ/bit | Complete |
| 300 Mbps | 299.976 Mbps | 76.333% | 41.020 W | 40.15–42.33 W | 8 | 136.744 nJ/bit | Incomplete diagnostic |
| 400 Mbps | 399.498 Mbps | 100.0% | 41.326 W | 40.36–41.95 W | 10 | 103.445 nJ/bit | Complete |
| 500 Mbps | 495.066 Mbps | 100.0% | 42.015 W | 41.41–42.38 W | 10 | 84.867 nJ/bit | Complete |
| 600 Mbps | 549.112 Mbps | 65.333% | 41.953 W | 41.41–42.24 W | 6 | 76.402 nJ/bit | Incomplete diagnostic |

Per-step completeness is the actual positive-traffic window span divided by the requested 600 seconds. The 300 Mbps window spans 458 seconds but contains 429 finalized one-second throughput samples; this distinction is another reason to keep it diagnostic. The excluded first 600 attempt has no finalized offered-load result and does not appear in the curve.

The aligned data, per-run merged CSVs, original PDU export, plot, and concise methodology are collected under [the August 5 analysis directory](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/runs/analysis/20260805_oai_latest_baseline_100_600). The principal outputs are the [four-panel throughput/power/energy/completeness plot](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/analysis/20260805_oai_latest_baseline_100_600/load_sweep_overview.png) and [consolidated CSV](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/runs/analysis/20260805_oai_latest_baseline_100_600/load_sweep_summary.csv).

## Descriptive Power Curve

Across the four complete points at 100, 200, 400, and 500 Mbps, delivered throughput increased by 395.0% while mean Outlet 2 power increased by 3.50%. A descriptive least-squares fit is:

`P(W) = 40.2752 + 0.0032028 × delivered throughput(Mbps)`, with `R² = 0.9246` and `n = 4`.

This is an initial empirical curve, not yet a validated O-RU power-consumption model. There is one run per complete point, no randomization, no confidence intervals, and only roughly one PDU observation per minute. The min–max whiskers in the plot are observed ranges, not statistical uncertainty intervals. The sharp reduction in energy per bit mainly reflects a large load-independent power component being amortized over more delivered traffic.

The partial 600 Mbps point shows radio/user-plane saturation: 600 Mbps was offered but only 549.112 Mbps was delivered. Its mean power is 0.062 W below the complete 500 Mbps point, well inside the observed ranges, so that difference must not be interpreted as a real power reduction.

## Failure and RRC Interpretation

The repeated high-load instability is not explained by the VNF being older than `2026.w28`. Preserved logs show the later VNF commit, rank-two UE reports, `SDU rejected, SDU buffer full`, and RRC re-establishment requests with cause `Other Failure`. During degraded periods the system also exhibited VNF/radio-path stalls and earlier live P7 timing drift. These observations are consistent with overload/backpressure and split-path timing instability leading to loss of UE context, followed by RRC recovery attempts. They do not isolate one root cause or prove that the scheduler alone caused the failure.

Because collected pod logs are cumulative over pod lifetime, repeated copies of the same earlier event must not be counted as independent re-establishments. A future root-cause run should preserve precise per-step pod-log start markers and correlate RLC buffer occupancy, P7 timing, RRC events, UE throughput, and pod state on one clock.

## Scientific Status and Next Work

Scientifically usable complete baseline points now exist at 100, 200, 400, and 500 Mbps. The 300 and 600 Mbps points are diagnostic only. The 700, 800, and 900 Mbps continuation remains pending and should be executed one bandwidth at a time after a clean preflight and attachment check. The existing August 4 900 Mbps result remains a separate 20-minute reference and should not silently substitute for a same-procedure ten-minute sweep point.

After completing 700–900 Mbps, repeat selected loads to estimate variance. Only then fit and compare baseline and custom-scheduler power curves. The next scheduler modification should be implemented on a common current source base with runtime-selectable modes, so image lineage does not confound the scheduler comparison.

The temporary InfluxDB token remains in `/tmp` by user choice and is not recorded here. Documentation and analysis did not mutate the cluster, RU, worker networking, images, UE airplane state, or rApp.
