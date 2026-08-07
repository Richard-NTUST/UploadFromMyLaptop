# WINLAB 104-PRB 500 Mbps Run, Power Alignment, and rApp Validator Fix

**Date:** 2026-08-04
**Status:** 104-PRB run captured and power-aligned; expected iPerf shutdown classification fixed

## Objective

Run the immutable 104-PRB OAI scheduler condition at a 500 Mbps offered load, validate the live cap, align Raritan Outlet 2 active power to the UE's actual positive-throughput interval, and preserve honest completeness/error metadata before moving to the separate 900 Mbps OAI `latest` condition.

## Immutable 104-PRB Condition

| Item | Value |
|---|---|
| Source branch | `david/oai-prb-cap-104-20260803` |
| Source commit | `d01a1b79ae57def67b8734428f2447f20dafe855` |
| Jenkins build | `#92`, successful |
| Image | `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-prb-cap-104-20260803` |
| Registry/runtime digest | `sha256:1f1ffe2736e8e0ce91e90db586348d3bc8d42cbe669019a4154b8af58e239a8a` |
| Telemetry mode | `oai_prb_cap_104` |

The first Helm command split the repository value at `oai-gnb`, temporarily rendering the invalid VNF image `bmw.ece.ntust.edu.tw/minghong/:latest`. This was caught before measurement and corrected with quoted `--set-string` values. The PNF continued using its intended `latest` image/runtime path; the scheduler-bearing VNF used the exact immutable 104-PRB digest.

Preflight confirmed Lavoisier Ready, SR-IOV CP/UP allocatable `1/1`, both pods Ready with zero restarts, continuous P7 and RU RX timing, no fronthaul error counters, the expected telemetry label, healthy rApp API, and user-confirmed Nemo/UE attachment.

## Run Result and QC

| Item | Result |
|---|---|
| Job ID | `6648012c-8a3e-4e58-840d-38facd224bc7` |
| Remote artifact | `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260804-031316` |
| Local artifact | `runs/hpe_artifacts/e2e-ocloud-20260804-031316` |
| Offered load / requested duration | 500 Mbps / 1200 seconds |
| Positive-traffic UTC window | `2026-08-04T03:13:54Z` to `2026-08-04T03:32:31.001092Z` |
| UE samples / observed duration | 1117 / 1117.001092 seconds |
| Completion | 93.0834% |
| Mean delivered throughput | 362.268829 Mbps |
| Minimum / maximum | 29.322254 / 397.949631 Mbps |
| Post-run pods | Both Ready, zero restarts |
| Original rApp status | Failed due to `interrupt - the client has terminated` |

The captured interval exceeds the configured 80% pragmatic threshold but remains a partial run rather than a complete 20-minute replicate. The client interruption occurred after the usable interval and is retained in the original artifact metadata.

## Scheduler Validation

The copied VNF log contained 7,489 grants, all labeled `oai_prb_cap_104`:

- 6,810 grants with `rbSize=104`
- 148 grants with `rbSize=14`
- 531 grants with `rbSize=5`
- zero new-data grants above 104 PRBs
- zero captured retransmission grants above 104 PRBs

No fatal VNF or PNF signature was found. The 104-PRB scheduler cap is therefore validated for the captured traffic interval.

## Outlet 2 Alignment

The padded InfluxDB export `pdu_data_20260804_031230_033630.csv` covers `03:12:30Z` to `03:36:30Z`. `scripts/merge_winlab_e2e_power.py` clipped it to the positive UE interval and produced `power_throughput_summary_20260804_031316.csv`.

| Metric | Value |
|---|---:|
| Aligned PDU samples | 19 |
| Mean Outlet 2 active power | 41.072105 W |
| Minimum / maximum | 40.48 / 41.97 W |
| Sample standard deviation | 0.410387 W |
| Coefficient of variation | 0.999% |
| Estimated interval energy | 45.878 kJ / 12.744 Wh |
| Estimated delivered data | 404.655 Gbit / 50.582 GB |
| O-RU energy per delivered bit | 113.375 nJ/bit |

The energy intensity uses delivered throughput:

`41.072105 W / (362.268829 × 10^6 bit/s) = 1.13375 × 10^-7 J/bit = 113.375 nJ/bit`.

## Descriptive 54-versus-104 Observation

| Condition | Completion | Throughput | Mean power | Energy per delivered bit |
|---|---:|---:|---:|---:|
| 54 PRBs | 78.33% | 191.297 Mbps | 40.186 W | 210.072 nJ/bit |
| 104 PRBs | 93.08% | 362.269 Mbps | 41.072 W | 113.375 nJ/bit |

Relative to the 54-PRB partial run, the 104-PRB run observed 89.375% higher delivered throughput, 2.204% higher mean power, and 46.031% lower energy per delivered bit. These are descriptive cross-session values from one partial run per condition. They do not establish causality, statistical significance, or a baseline energy-saving claim.

## rApp Validator Fix

The OCloud runner had already accepted the server-side traffic evidence, but the outer artifact validator unconditionally converted the UE JSON shutdown marker into a fatal error. The active HPE validator now treats `interrupt - the client has terminated` and `idle timeout for receiving data` as warnings only when positive UE traffic meets the configured 80% threshold.

Early occurrences below threshold and all unknown iPerf errors remain fatal. Compilation and regression tests passed against this actual artifact plus insufficient-duration and unknown-error cases. The original job record remains unchanged for provenance. The recoverable HPE backup is:

`/home/hpe/winlab_e2e_rapp/scripts/run_e2e_with_artifacts.py.bak-client-interrupt-20260804`

## Follow-on Condition

The digest-pinned OAI `latest` 900 Mbps run was subsequently completed and power-aligned. Its separate condition identity, results, and RRC/RLC caveat are documented in [the 900 Mbps run study note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-08-04_WINLAB_OAI-Latest_900Mbps_Run_and_Power_Alignment.md).
