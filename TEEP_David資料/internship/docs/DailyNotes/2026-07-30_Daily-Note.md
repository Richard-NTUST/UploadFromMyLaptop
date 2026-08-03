# Daily Note

## Date

**Date:** 2026/07/30

---

## Short-term Goal

Validate the custom 27-PRB scheduler image in a reserved live E2E window, merge its throughput with InfluxDB PDU power, and harden the rApp so incomplete traffic cannot be reported as a successful experiment.

### Goals and milestones

1. Recover and verify a stable Lavoisier, RU, PNF, VNF, core, and UE path.
2. Confirm from live scheduler logs that the 27-PRB cap is active.
3. Run a longer traffic test and classify scheduler success separately from session stability.
4. Export and merge the matching PDU active-power data.
5. Improve future run acceptance and artifact quality.

## Plan

| Task | Intended result |
|---|---|
| Use the reserved test window and preflight the environment | Remove shared-resource ambiguity |
| Deploy and exercise the custom VNF image | Produce live 27-PRB scheduler evidence |
| Audit iPerf, UE, VNF, and PNF artifacts | Identify the true traffic duration and termination mode |
| Query InfluxDB and run the merge script | Produce aligned throughput and power results |
| Harden rApp validation | Reject incomplete or evidence-free runs |

## Review

| Item | Result |
|---|---|
| UE and user-plane start | Passed; UE attached as `10.45.0.4` and traffic began |
| Scheduler cap | Passed; 14,072 scheduler records and no observed `rbSize` above 27 |
| Requested 30-minute stability | Incomplete; 1,120/1,800 positive-traffic seconds, or 62.2% |
| Failure attribution | UE iPerf JSON ended with an idle timeout while pods remained healthy and the UE stayed attached |
| Power export and merge | Completed; 18 PDU samples aligned to the positive-traffic interval |
| Corrected merged result | 95.910 Mbps mean RX and 40.129 W mean active power |
| Runner QC | Added an 80% minimum-duration rule and explicit artifact validation fields |
| Energy conclusion | Not established; requires a controlled same-day baseline/capped comparison |

### Progress Summary

The reserved test window allowed the custom VNF scheduler image to be exercised without treating unrelated users as the default explanation for every failure. The run attached the Samsung UE, started downlink traffic, and generated 14,072 scheduler records using `mode=oai_prb_cap_27`. New transmissions and retransmissions never exceeded 27 PRBs, providing direct live evidence that the custom cap works.

The requested 1,800-second test did not complete as intended. The UE produced 1,120 positive-throughput samples and then reported an idle timeout, although the API marked the outer job successful. PNF and VNF remained healthy and the UE retained its address, which separates this event from pod crashes or a control-plane detach. The result is therefore a scheduler-cap pass but a long-run stability failure.

InfluxDB Outlet 2 active-power data was exported and merged with the actual traffic interval. The merge script was corrected to exclude zero-throughput idle-tail intervals after a client interruption. The final summary reports 95.910 Mbps mean received throughput and 40.129 W mean active power over 18 PDU samples. This is useful experiment evidence, but it is not yet a controlled energy comparison.

The bare-metal rApp runner was also hardened. Future jobs now record expected and observed durations, completion ratio, warnings, and validation errors; runs below 80% completion or without valid iPerf evidence fail instead of being accepted from the outer return code alone.

Detailed findings are recorded in [WINLAB 27-PRB Live Validation, Power Merge, and Run QC](../StudyNotes/2026-07-30_27-PRB_Live_Validation_Power_Merge_and_Run_QC.md).

## Next Working Session

| Priority | Action |
|---:|---|
| 1 | Reserve an exclusive UE/RU window and rerun under the hardened validator |
| 2 | Collect same-day baseline and 27-PRB runs with identical settings |
| 3 | Repeat both conditions and compare throughput, power, and energy per delivered bit |
| 4 | Investigate the UE/iPerf idle-timeout path if it recurs despite healthy radio and pods |
| 5 | Proceed to runtime-selectable or deeper scheduler policies after stable A/B validation |
