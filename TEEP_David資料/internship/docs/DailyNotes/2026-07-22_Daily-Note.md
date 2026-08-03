# Daily Note

## Date

**Date:** 2026/07/22

---

## Short-term Goal

Re-test the OCloud E2E path after the previous day’s UE attach failure, determine whether the old image works again, and preserve the current failure-domain diagnosis before resuming scheduler experiments.

### Goal 1: Re-check baseline OCloud E2E behavior

* Milestone 1: Verify PNF/VNF pod readiness and image tags, Due 2026/07/22
* Milestone 2: Check whether the Samsung UE has `10.45.x.x`, Due 2026/07/22
* Milestone 3: Run a short baseline rApp smoke test, Due 2026/07/22

### Goal 2: Diagnose unstable attach/iPerf artifact state

* Milestone 1: Inspect artifacts when the rApp reports success but no iPerf CSV exists, Due 2026/07/22
* Milestone 2: Clear stale Android miperf state and retry, Due 2026/07/22
* Milestone 3: Record the current blocker before scheduler testing continues, Due 2026/07/22

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Inspect current OCloud state | Goal 1 | Pod/image/gNB readiness snapshot | | `ming-ns` pod and VNF log checks |
| P1 | Run baseline 60 s smoke test | Goal 1 | Job result through Dockerized rApp | | Job `316a7cb6-6b42-460e-8f30-51b1d282a34f` |
| P2 | Inspect missing throughput artifacts | Goal 2 | Reason for absent CSV/plot | | Artifact directory `e2e-ocloud-20260722-024243` |
| P2 | Clear stale miperf state and retry | Goal 2 | Second attach/iPerf result | | Job `79ed2b6f-c51c-4468-baf1-0065900bfb15` |
| P3 | Update daily logs and weekly summary | Reporting | Presentation-ready progress note | | Daily notes and weekly progress note |

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Inspect current OCloud state | Complete | | PNF/VNF both Running/Ready on `latest` |
| Run baseline 60 s smoke test | Partially complete | | Job `316a7cb6-6b42-460e-8f30-51b1d282a34f` reached attach and completed flow |
| Inspect missing throughput artifacts | Complete | | No `iperf_csv`, no `iperf_plot`, `ue_iperf_samples=0` |
| Clear stale miperf state and retry | Complete | | Job `79ed2b6f-c51c-4468-baf1-0065900bfb15` failed to reacquire `10.45.x.x` |
| Update daily logs and weekly summary | Complete | | This file and weekly progress note |

### Progress Summary

The old `latest` image did not work on 2026/07/21, but today the environment initially looked better:

```text
VNF image: bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest
PNF image: bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest
PNF/VNF: Running and Ready
UE IP before first run: 10.45.0.14
```

The first baseline run completed through the rApp job flow:

```text
Job: 316a7cb6-6b42-460e-8f30-51b1d282a34f
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260722-024243
Result: returncode 0
```

However, the artifact was not valid throughput evidence:

```text
iperf_csv: empty
iperf_plot: empty
ue_iperf_samples: 0
```

After clearing stale Android miperf state, the UE no longer had a `10.45.x.x` interface. The retry failed before iPerf:

```text
Job: 79ed2b6f-c51c-4468-baf1-0065900bfb15
Result: failed
Reason: UE failed to get IP within 180 s
```

Current conclusion: the pod/gNB side is generally healthy, but UE attachment is unstable. The path can proceed when the UE already has `10.45.x.x`; after airplane-mode cycling or miperf cleanup, it may fail to reacquire the data interface.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Run valid baseline throughput evidence | First successful flow had no iPerf samples | Re-run after UE attach and miperf behavior are stable |
| Validate custom scheduler image | Requires a clean baseline and custom smoke test | Use the scheduler-log image only after baseline produces CSV/plot |
| Continue scheduler behavior patch | Measurement loop is temporarily unstable | Stabilize UE attach first |

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Stabilize UE `10.45.x.x` attachment | E2E blocker | Repeatable attach after airplane-mode cycling |
| P2 | Produce one valid baseline artifact | Measurement baseline | `iperf_timeseries.csv`, `iperf_throughput.png`, offered-load plot |
| P3 | Redeploy scheduler-log image and re-test | Scheduler roadmap | `[WINLAB_SCHED_LOG]` observed during valid traffic |
