# WINLAB Weekly Progress Summary

**Date:** 2026-07-22  
**Scope:** Progress since Dockerized rApp validation, long-run measurement, and first OAI scheduler image build.

## Presentation Summary

This week moved the work from measurement-pipeline validation into the first OAI scheduler modification workflow.

The completed part is the measurement backbone:

1. Dockerized rApp endpoint on HPE can trigger OCloud E2E jobs through `127.0.0.1:19090`.
2. The rApp preserves run artifacts under `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/`.
3. CortexDC/InfluxDB Outlet 2 `active_power` data is accessible and can be exported by time window.
4. The merge script can combine iPerf throughput, offered-load metadata, run summary, and PDU active-power samples.
5. A validated long-run result exists for 200 Mbps offered load:

```text
Run: e2e-ocloud-20260720-061120
Offered load: 200 Mbps
Average RX throughput: 199.892 Mbps
Average Outlet 2 active power: 40.097 W
PDU samples: 31
```

The new part is the OAI scheduler workflow:

1. Created OAI branch `david/oai-scheduler-logonly-20260721`.
2. Added a non-behavior-changing `[WINLAB_SCHED_LOG]` marker in the downlink scheduler allocation path.
3. Jenkins build #88 succeeded and produced image tag `david-oai-scheduler-logonly-20260721`.
4. The custom image deployed into `ming-ns` and the VNF registered with AMF.
5. Baseline and custom-image E2E tests are currently blocked by unstable Samsung UE `10.45.x.x` attachment, not by pod readiness or image deployment.

## Evidence Links

| Topic | Evidence |
|---|---|
| Long-run E2E and power merge | [2026-07-20 long-run note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-20_WINLAB_Long_Run_E2E_and_Merge_Readiness.md) |
| Scheduler modification workflow | [2026-07-20 scheduler workflow note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-20_WINLAB_OAI_Scheduler_Modification_Workflow.md) |
| Scheduler log-only branch and build | [2026-07-21 build note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-21_OAI_Scheduler_LogOnly_Branch_and_Build.md) |
| E2E power merge script | [merge script](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/scripts/merge_winlab_e2e_power.py) |
| Daily notes | [Daily notes folder](https://github.com/bmw-ntust-internship/internship/tree/2026-TEEP-2-JDavid/docs/DailyNotes) |

## Current Architecture Status

```text
User/API
  -> Dockerized rApp on HPE (:19090)
  -> run_e2e_with_artifacts.py
  -> OCloud VNF/PNF pods in ming-ns
  -> Samsung UE via IAPC/ADB
  -> iPerf traffic over ogstun 10.45.0.1 <-> UE 10.45.x.x
  -> Artifact directory
  -> InfluxDB/CortexDC Outlet 2 active_power export
  -> merge_winlab_e2e_power.py
  -> throughput-power summary CSV
```

## What Is Working

| Area | Status |
|---|---|
| Dockerized rApp service | Working |
| HPE OCloud job submission | Working |
| PNF/VNF pod recovery process | Working when SR-IOV resources are healthy |
| CortexDC/InfluxDB PDU export | Working |
| Throughput-power merge script | Working on valid run artifacts |
| Jenkins OAI image build | Working |
| Helm deployment of custom VNF image | Working |

## Current Blocker

The current blocker is not the scheduler image build. It is the UE attach state.

Observed behavior:

- On 2026/07/21, both the custom scheduler-log image and old `latest` image failed because the UE did not obtain `10.45.x.x`.
- On 2026/07/22, the UE initially had `10.45.0.14`, and the baseline job reached the rApp success path, but the artifact contained zero iPerf samples.
- After clearing Android miperf state, the UE lost `10.45.x.x` and failed to reacquire it.

This means scheduler testing should wait until baseline `latest` can reliably produce a complete iPerf artifact after airplane-mode cycling.

## Next Target

1. Stabilize UE attachment after airplane-mode cycling.
2. Produce one valid baseline artifact with:

```text
iperf_timeseries.csv
iperf_throughput.png
offered_load_throughput.csv
offered_load_throughput.png
summary.json with ue_iperf_samples > 0
```

3. Redeploy `david-oai-scheduler-logonly-20260721`.
4. Confirm `[WINLAB_SCHED_LOG]` appears during valid traffic.
5. Only then begin the first behavior-changing scheduler patch, most likely a controlled PRB cap.

The active blocker is UE attachment stability, which must be fixed before scheduler behavior experiments can produce clean evidence.
