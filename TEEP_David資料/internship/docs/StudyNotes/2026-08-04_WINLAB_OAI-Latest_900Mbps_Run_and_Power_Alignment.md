# WINLAB Digest-Pinned OAI Latest 900 Mbps Run and Power Alignment

**Date:** 2026-08-04
**Status:** Run succeeded; power aligned; transient RRC/RLC re-establishment event retained in QC

## Condition Identity

| Item | Value |
|---|---|
| VNF image | `bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest@sha256:c227006518795bdb517db0db15be7c12850c9184297e4cb514ea3987a5108edc` |
| Runtime digest | `sha256:c227006518795bdb517db0db15be7c12850c9184297e4cb514ea3987a5108edc` |
| OAI abbreviated source hash | `95223172` |
| Offered load | 900 Mbps downlink |
| Requested duration | 1200 seconds |

The moving `latest` tag was resolved and pinned by digest before deployment. An ordered PNF-then-VNF restart cleared stale nFAPI state. Preflight then showed Lavoisier Ready, SR-IOV CP/UP `1/1`, both pods Ready with zero restarts, continuous P7, zero fronthaul error counters, the expected ARFCN 649920 / PCI 0 / PLMN 001-01 cell, UE attachment, and a healthy rApp.

## Run Result

| Item | Result |
|---|---|
| Job ID | `5554c656-d8af-472c-a49c-66851814a393` |
| Artifact | `runs/hpe_artifacts/e2e-ocloud-20260804-040735` |
| Positive-traffic UTC window | `2026-08-04T04:08:12Z` to `2026-08-04T04:26:48.001097Z` |
| UE samples / observed duration | 1113 / 1116.001097 seconds |
| Completion | 93.0001% |
| Mean delivered throughput | 760.715037 Mbps |
| Minimum / maximum | 7.286479 / 932.097461 Mbps |
| rApp status | Succeeded |
| Validation errors | None |
| Validation warning | `interrupt - the client has terminated` |
| Post-run pods | Both Ready, zero restarts |

This was the first live confirmation of the repaired validator: the expected client shutdown marker was retained as a warning because positive traffic exceeded the configured 80% threshold, while the job remained successful.

## Outlet 2 Alignment

The padded InfluxDB export `pdu_data_20260804_040700_043030.csv` covers `04:07:00Z` to `04:30:30Z`. The established merge script clipped it to the positive UE interval and produced `power_throughput_summary_20260804_040735.csv`.

| Metric | Value |
|---|---:|
| Aligned PDU samples | 18 |
| Mean Outlet 2 active power | 41.987778 W |
| Minimum / maximum | 40.81 / 42.64 W |
| Sample standard deviation | 0.530001 W |
| Coefficient of variation | 1.262% |
| Estimated interval energy | 46.858 kJ / 13.016 Wh |
| Estimated delivered data | 848.959 Gbit / 106.120 GB |
| O-RU energy per delivered bit | 55.195 nJ/bit |

The energy intensity uses delivered UE throughput:

`41.987778 W / (760.715037 × 10^6 bit/s) = 5.51951 × 10^-8 J/bit = 55.195 nJ/bit`.

## RRC/RLC Event

During the traffic interval, the UE initiated RRC re-establishment from RNTI `5c19` to `912a`. The VNF emitted 16 `fatal: SDU sent to unknown RB` RLC messages while replacing the old UE context. Msg4 was acknowledged, RRC re-establishment completed, the PDU session bearer was modified, and traffic continued. Neither pod restarted.

This event is a real run-quality caveat and may explain part of the low-throughput tail. It did not terminate the run, but the interval must not be described as interruption-free. The pinned OAI `latest` image does not contain the custom `WINLAB_SCHED_LOG` telemetry, so scheduler-grant distributions are not available for this condition.

## Interpretation Boundary

This 900 Mbps result must not be directly treated as a scheduler comparison with the 500 Mbps 54- or 104-PRB runs because both offered load and scheduler image changed. It is a separate high-load operating point. Repeat runs would be required for uncertainty estimates or causal power-efficiency claims.

## Follow-on Sweep

The subsequent 27-, 54-, and 104-PRB runs at the same 900 Mbps offered load, their aligned power results, run-quality caveats, and the Ming debug-UI assessment are consolidated in [the 900 Mbps PRB-cap sweep study note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-08-04_WINLAB_900Mbps_PRB-Cap_Sweep_and_Debug-UI_Assessment.md).
