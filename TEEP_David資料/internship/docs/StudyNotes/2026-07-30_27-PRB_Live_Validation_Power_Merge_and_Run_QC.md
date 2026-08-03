# WINLAB 27-PRB Live Validation, Power Merge, and Run QC

**Date:** 2026/07/30

## Discovery Goal

Determine whether the custom 27-PRB scheduler image actually limits live downlink allocations, measure its observed throughput and PDU power, and distinguish scheduler correctness from end-to-end run stability.

## Result at a Glance

| Question | Result |
|---|---|
| Did the UE attach and receive traffic? | Yes; the UE used `10.45.0.4` and produced 1,120 positive-throughput samples. |
| Did the scheduler enforce the cap? | Yes; all observed new-data and retransmission grants had `rbSize <= 27`. |
| Did the requested 30-minute test complete? | No; traffic lasted about 1,120 of 1,800 seconds, or 62.2%. |
| Did the API originally report success? | Yes, but the UE JSON ended with an idle-timeout error. The API status alone was therefore insufficient. |
| Was power data merged successfully? | Yes; 18 PDU samples were aligned to the actual positive-traffic window. |
| Can an energy-saving claim be made? | No. A controlled same-day baseline comparison is still required. |

## Test Evidence

- Job ID: `266b772d-de75-468e-ac56-cfc6ecd464ee`
- Artifact directory: `runs/hpe_artifacts/e2e-ocloud-20260730-064034`
- Requested load and duration: 200 Mbps for 1,800 seconds
- Actual positive-traffic window: `2026-07-30T06:41:17Z` to `2026-07-30T06:59:57.001073Z`
- Observed mean UE throughput: 95.910 Mbps
- UE JSON termination: `idle timeout for receiving data`
- Final pod condition: PNF and VNF healthy with zero restarts
- Scheduler marker: `mode=oai_prb_cap_27`

The UE remained attached and the radio logs continued after application traffic stopped. This means a retained `10.45.x.x` address does not prove that the iPerf user-plane session is still active.

## Scheduler Validation

The VNF log contained 14,072 `[WINLAB_SCHED_LOG]` records. The observed mode was exclusively `oai_prb_cap_27`.

| Allocation type | Samples | Maximum observed `rbSize` |
|---|---:|---:|
| New transmission | 13,952 | 27 PRBs |
| Retransmission | 120 | 27 PRBs |

No live allocation exceeded the configured cap. This validates the scheduler mechanism itself, even though the long E2E session was incomplete. The change remains a maximum grant size, not a promise that every grant will use exactly 27 PRBs.

## Power and Throughput Merge

InfluxDB active-power data for Raritan PDU Outlet 2 was exported to `pdu_data_20260730_063800_070400.csv`.

The corrected merged output is `power_throughput_summary_20260730_064034.csv`.

| Metric | Value |
|---|---:|
| Offered load | 200 Mbps |
| Mean received throughput | 95.910 Mbps |
| Mean active power | 40.129 W |
| Minimum active power | 39.690 W |
| Maximum active power | 40.800 W |
| PDU samples in traffic window | 18 |

The merge script originally treated zero-throughput intervals after the idle timeout as part of the experiment. `scripts/merge_winlab_e2e_power.py` was corrected to end the measurement window at the final interval with positive throughput, while retaining a fallback for files that contain no positive samples. This prevents post-failure idle power from contaminating the traffic average.

The earlier July 20 baseline was approximately 199.892 Mbps at 40.097 W, while this capped run was approximately 95.910 Mbps at 40.129 W. These runs occurred on different days and under different conditions, so the comparison is diagnostic only. It does not demonstrate an energy benefit.

## Run Acceptance Hardening

The rApp previously marked the job successful because the outer command returned zero even though iPerf ended early. The runner was hardened with these checks:

1. Parse the observed iPerf duration rather than trusting only the process return code.
2. Require at least 80% of the requested traffic duration.
3. Treat a UE JSON idle timeout below 80% completion as a failure.
4. Fail when no valid iPerf evidence is present.
5. Store expected duration, observed duration, completion ratio, validation errors, and warnings in the artifact summary.

Under the new rule, this 1,120/1,800-second result correctly fails the stability criterion while remaining valid evidence that the scheduler cap operated correctly.

## What We Learned

1. Scheduler correctness, UE attachment, application traffic, and long-run stability are separate acceptance layers.
2. A healthy pod and retained UE address cannot substitute for validated iPerf duration.
3. Power data must be aligned to actual positive traffic, not merely the API job lifetime.
4. The 27-PRB cap is ready for repeatable A/B evaluation, but its energy effect is not established.
5. The reservation system materially improves experiment control by reducing shared-UE and shared-RU interference.

## Next Experiment

1. Reserve an exclusive UE/RU window and complete the normal worker, RU, pod, and attachment preflight.
2. Run same-day baseline and 27-PRB tests with identical duration and offered load.
3. Require the hardened runner to report at least 80% completion; prefer 100% for final data.
4. Repeat each condition and compare delivered throughput, power, and energy per delivered bit.
5. After stable A/B validation, move to runtime-selectable or more substantial scheduler policies.
