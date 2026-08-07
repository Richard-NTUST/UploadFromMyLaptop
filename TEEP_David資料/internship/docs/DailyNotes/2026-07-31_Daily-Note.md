# Daily Note

## Date

**Date:** 2026/07/31

---

## Short-term Goal

Turn the validated single-UE scheduler evidence into a presentation-ready playback, restore PNF/VNF compatibility for reliable UE attachment, and begin higher-load validation at 500 Mbps.

### Goals and milestones

1. Build an honest single-UE scheduler visualization from measured WINLAB artifacts.
2. Diagnose the PNF crash that occurred immediately after UE random access.
3. Repair the PNF without changing the VNF scheduler experiment.
4. Validate attachment and user-plane traffic with a short smoke test.
5. Start testing whether the repaired path remains usable at a 500 Mbps offered load.

## Plan

| Task | Intended result |
|---|---|
| Parse scheduler, iPerf, and PDU artifacts | Produce a measured scheduler playback |
| Trace the PNF exit at UE attachment | Identify the exact failing layer |
| Patch and rebuild the worker-side PNF | Preserve compatibility with the current VNF |
| Run a 60-second smoke test | Verify attach, traffic, artifacts, and pod stability |
| Run 500 Mbps for 20 minutes | Obtain a higher-load measurement window |

## Review

| Item | Result |
|---|---|
| Scheduler playback | Built from the July 30 27-PRB run with scheduler, throughput, and PDU evidence kept within their valid time boundaries |
| PNF failure | Deterministic `Ungrouped ULSCH_id 0` assertion in `group_pusch_jobs()` after PRACH |
| Root cause | Newer PNF grouping logic received legacy/ungrouped PUSCH jobs from the current VNF-side behavior |
| Repair | Added fallback group assignment for only negative `mu_group_idx` values, preserving valid modern group indices |
| 200 Mbps smoke test | Passed for 60.001 seconds with 60 UE samples and 0% sender-reported loss |
| 500 Mbps long run | Produced 1,115 positive-throughput seconds out of 1,200 requested, or 92.9% |
| Long-run classification | Usable measurement window, but job correctly failed because the UE iPerf client was interrupted before full completion |

### Progress Summary

The scheduler playback dashboard was built from the July 30 custom 27-PRB run. It presents one physical Samsung UE, captured downlink grants, throughput, and RU PDU power instead of simulating a 100-user cell. Review of the source artifacts showed that the copied VNF log contains a short dense scheduler interval followed by sparse control traffic. The dashboard therefore replays only the dense allocation capture and presents the full throughput/power timeline separately rather than claiming exact cross-source timestamp alignment.

The main infrastructure blocker was isolated below the VNF scheduler. After the UE initiated random access, the worker-mounted PNF executable aborted in `group_pusch_jobs()` because a PUSCH job had `mu_group_idx < 0`. A complete old runtime could not be substituted safely because its binary and libraries belonged to a different ABI/protocol lineage. The active source was instead patched to reserve valid group IDs and assign each legacy ungrouped job to the next free fallback group. The current behavior for already grouped jobs remains unchanged.

The rebuilt PNF completed PRACH and kept the UE in sync. Job `ab0ad307-3b9c-4697-abbc-cd2b69c4483e` then passed a direct 200 Mbps, 60-second smoke test using UE address `10.45.0.3`. The server accepted the UE connection, observed 60.001 seconds of traffic, transferred 1.40 GBytes, collected 60 UE samples, and reported no packet loss. PNF and VNF remained Ready without additional restarts or fatal assertions.

The follow-up 500 Mbps job `f3b50b65-34ae-4ad8-8a74-23fadc1ee7ef` delivered 1,115 positive-throughput seconds, or 18 minutes 35 seconds of the requested 20 minutes. This exceeds the current 80% minimum-duration threshold and provides a useful high-load window, but the job remains classified as failed because the UE iPerf client was interrupted. The endpoint and artifact validator correctly preserved both facts instead of reporting an unconditional success.

Detailed findings are recorded in [Single-UE Scheduler Playback, PNF Compatibility Fix, and 500 Mbps Validation](../StudyNotes/2026-07-31_WINLAB_Scheduler_Playback_PNF_Compatibility_and_500Mbps_Validation.md).

## Next Working Session

| Priority | Action |
|---:|---|
| 1 | Reserve an exclusive UE/RU window after 16:00 and confirm the repaired PNF remains stable |
| 2 | Repeat the 500 Mbps run and target a clean 100% completion |
| 3 | Export the matching InfluxDB PDU window and merge power with the positive-traffic interval |
| 4 | Capture a same-day baseline and capped run with identical load and duration |
| 5 | Add a shared run marker or dedicated scheduler trace so allocation, throughput, and power can be aligned exactly |

