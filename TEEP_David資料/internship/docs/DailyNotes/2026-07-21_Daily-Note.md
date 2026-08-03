# Daily Note

## Date

**Date:** 2026/07/21

---

## Short-term Goal

Prepare the first low-risk OAI scheduler modification image, validate the Jenkins/Quay build path, and attempt a controlled smoke test in `ming-ns` without changing scheduler behavior.

### Goal 1: Build a logging-only scheduler image

* Milestone 1: Create an OAI branch from the BMW nFAPI baseline, Due 2026/07/21
* Milestone 2: Add a scheduler-path log marker without behavior changes, Due 2026/07/21
* Milestone 3: Build and publish the image through Jenkins/Quay, Due 2026/07/21

### Goal 2: Validate deployment and isolate failures

* Milestone 1: Deploy the custom VNF image into `ming-ns`, Due 2026/07/21
* Milestone 2: Compare custom-image behavior against the old `latest` image, Due 2026/07/21
* Milestone 3: Preserve rollback and smoke-test instructions, Due 2026/07/21

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Create OAI scheduler branch | Goal 1 | Branch and commit pushed to BMW GitHub | | Branch `david/oai-scheduler-logonly-20260721` |
| P1 | Add logging-only scheduler marker | Goal 1 | `[WINLAB_SCHED_LOG]` in scheduler allocation path | | OAI commit hash and changed file |
| P2 | Trigger Jenkins image build | Goal 1 | Quay image tag for deployment | | Jenkins build #88 |
| P2 | Deploy custom VNF image | Goal 2 | VNF pod using custom image in `ming-ns` | | Helm rollout status and pod image |
| P3 | Run custom and baseline smoke tests | Goal 2 | Failure-domain comparison | | rApp job IDs and UE attach status |

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Create OAI scheduler branch | Complete | | `david/oai-scheduler-logonly-20260721` |
| Add logging-only scheduler marker | Complete | | Commit `31c7aa0477586643a7acdae9c316c61c1ba0cdbf` |
| Trigger Jenkins image build | Complete | | Jenkins build #88 succeeded |
| Deploy custom VNF image | Complete | | Image `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-scheduler-logonly-20260721` |
| Run custom and baseline smoke tests | Blocked | | Both images failed before iPerf because UE did not obtain `10.45.x.x` |

### Progress Summary

Created and pushed the first scheduler modification branch:

```text
Repository: https://github.com/bmw-ece-ntust/openairinterface5g
Branch: david/oai-scheduler-logonly-20260721
Commit: 31c7aa0477586643a7acdae9c316c61c1ba0cdbf
Image tag: david-oai-scheduler-logonly-20260721
```

The code change was intentionally low risk. It added a `[WINLAB_SCHED_LOG]` marker in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c` to prove the modified binary is running before changing scheduling policy.

Jenkins build #88 completed successfully and produced the expected image. The custom image deployed into `ming-ns` and the VNF registered with AMF. However, the smoke test failed before iPerf because the Samsung UE did not obtain a `10.45.x.x` address.

The VNF was rolled back to `latest` and the same baseline smoke test was attempted. The old image failed in the same way, which isolated the immediate problem to UE/RF/APN/core attach state rather than the logging-only scheduler image.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Verify custom scheduler log marker during traffic | UE attach failed before iPerf | Restore stable UE `10.45.x.x` attachment |
| Run custom-image throughput/power test | No traffic sample was generated | Re-run after baseline image succeeds |
| Start behavior-changing scheduler patch | Build/deploy path is proven, but traffic validation is not yet stable | Complete one clean smoke run with custom image first |

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Re-check UE/APN/core attach state | Smoke-test blocker | UE obtains `10.45.x.x` reliably |
| P2 | Re-run baseline and custom smoke tests | Scheduler validation | One successful `latest` run and one successful log-only image run |
| P3 | Prepare PRB-cap scheduler patch plan | Next roadmap step | First behavior-changing patch target |
