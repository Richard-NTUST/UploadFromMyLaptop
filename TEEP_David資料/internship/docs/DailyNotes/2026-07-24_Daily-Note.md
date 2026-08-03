# Daily Note

## Date

**Date:** 2026/07/24

---

## Short-term Goal

Stabilize the OCloud test environment sufficiently to separate Kubernetes, VNF image, RU/RF, UE-attachment, and user-plane failures before continuing the scheduler experiment.

### Goal 1: Restore a reliable OCloud test baseline

* Milestone 1: Restore worker scheduling after kubelet was found stopped, Due 2026/07/24
* Milestone 2: Confirm PNF and VNF reach Ready state without stale admission-failure pod storms, Due 2026/07/24
* Milestone 3: Identify whether the UE currently observes the intended NR cell, Due 2026/07/24

### Goal 2: Preserve a valid scheduler-image A/B test path

* Milestone 1: Keep `latest` as the baseline image and retain the Jenkins-built PRB-cap tag for comparison, Due 2026/07/24
* Milestone 2: Run E2E only after RF and UE preflight checks pass, Due 2026/07/24

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | ---------------- |
| P1 | Restore Lavoisier kubelet and reconcile workloads | Goal 1 | Schedulable worker with stable PNF/VNF pods | Node Ready condition and pod readiness |
| P1 | Capture UE radio and data-interface state | Goal 1 | Clear attachment-state boundary | ADB device listing, UE IP state, Nemo Handy cell table |
| P1 | Reapply RU E2E profile when the RU was used elsewhere | Goal 1 | Intended n78 target cell becomes visible | `rrr`, then `pegam`, followed by Nemo validation |
| P2 | Resume baseline/custom-image comparison | Goal 2 | Comparable 5-minute E2E artifact | Valid iPerf session and scheduler marker |

---

## Review

| Task | Status | Evidence |
| ---- | ------ | -------- |
| Restore Lavoisier kubelet and reconcile workloads | Complete | The worker had stopped `kubelet`; `sudo systemctl start kubelet` restored node scheduling. Fresh PNF and VNF pods subsequently reached `1/1 Running`. |
| Remove stale PNF admission-failure churn | Complete | Scaled the PNF deployment down before deleting failed admission objects, then restored it after the worker recovered. This stopped the uncontrolled pod creation loop. |
| Verify active baseline VNF configuration | Complete | The running VNF configuration advertises PLMN `001/01`, PCI `0`, band n78, SSB ARFCN `649920`, and Point A `646724`. VNF logs confirm NG setup, F1 setup, and the cell in service. |
| Diagnose the UE attach boundary | Complete | The control host sees the expected Samsung UE `R5CN30TMBYR` as `SM_G9860`, but `ip -f inet addr show` reported only loopback. Nemo Handy later showed an empty NR Cell Table. The UE is not currently seeing a usable NR cell or establishing a 10.45 data interface. |
| Establish whether the modified VNF image is the current blocker | Complete | Not supported by current evidence. A `latest` baseline run also failed attachment while Nemo showed no cell, so the immediate blocker is below the rApp and scheduler image: RU/RF state and UE radio discovery. |
| Validate the PRB-cap image by E2E | Blocked | The scheduler experiment remains unvalidated until Nemo shows the intended cell and the UE first obtains a working `10.45.x.x` address. |

### Progress Summary

The main recovery issue was not Helm itself. Lavoisier had a stopped kubelet, which produced Pending, Terminating, and `UnexpectedAdmissionError` symptoms despite valid Helm release state. Starting kubelet restored scheduling. This should be included in the normal preflight check before deleting pods or reinstalling charts.

The subsequent attachment failures are not explained by the rApp. The E2E runner can only observe and react to attachment state; during its attach timeout it intentionally cycles airplane mode. Direct ADB inspection confirmed that the expected UE is present, but it had no mobile data interface. Nemo Handy then showed an empty NR Cell Table, which is decisive evidence that the UE cannot attach to the intended cell at that time.

The desired VNF configuration and the UE-visible radio state must match before E2E is run:

```text
VNF target: PLMN 001/01, PCI 0, band n78, SSB ARFCN 649920
UE state:   target cell must appear in Nemo, then UE must obtain 10.45.x.x
```

When the RU has been used or reconfigured by another activity, the recovery procedure is to run `rrr` through `ssh super`, wait for the RU to return, then run `pegam` to apply the Pegatron E2E M-plane profile. `pegam` is not a routine per-test command; it is an RU-state recovery action. The next test should wait for Nemo confirmation rather than repeatedly submitting E2E jobs while the cell table is empty.

The custom PRB-cap image remains a valid candidate for A/B testing. Its change limits only phase-3 new-data downlink allocations and does not explain an absent UE-visible cell. Use `latest` first after RF recovery, then deploy `david-oai-prb-cap-27-20260723` with the identical values file and repeat the same 5-minute test.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Restore target NR cell visibility | UE currently reports no NR cells and no mobile interface | Run `rrr`, wait for RU reachability, then run `pegam`; verify the target cell in Nemo before further E2E calls |
| Verify usable UE bearer | A 10.45 address alone does not prove the user-plane path | Check the UE interface and then confirm traffic to `10.45.0.1:5201` during the next short run |
| Run baseline/custom A/B | Current radio state invalidates any result | Run matching 5-minute, 200 Mbps tests after RF preflight succeeds |
| Reduce recovery uncertainty | Shared infrastructure changes can affect RU and node state | Adopt a written preflight: kubelet active, node Ready, pods Ready, zero restarts, target Nemo cell visible, then submit E2E |

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Recover and verify the Pegatron RU target profile | Radio preflight | Nemo displays the configured n78 target cell |
| P1 | Run one baseline `latest` 5-minute E2E test | Baseline validation | Valid 200 Mbps iPerf evidence and UE artifact |
| P2 | Roll out the PRB-cap image and repeat the matched test | Scheduler A/B | Comparable custom-image artifact and scheduler marker |
| P2 | Export and merge PDU power only for valid traffic sessions | Measurement validation | Throughput-power comparison CSV |
