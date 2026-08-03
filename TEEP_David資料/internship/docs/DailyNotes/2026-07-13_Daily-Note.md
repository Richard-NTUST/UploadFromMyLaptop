# Daily Note

## Date

**Date:** 2026/07/13

---

## Short-term Goal

Finish the Dockerized WINLAB E2E rApp validation path, document the SMO/workload architecture answer, and capture the OCloud PNF cleanup mechanism used to recover from failed pod creation loops.

### Goal 1: Confirm Dockerized rApp status

* Milestone 1: Confirm the Dockerized service is running without replacing the host rApp, Due 2026/07/13
* Milestone 2: Preserve the side-by-side port model for testing, Due 2026/07/13
* Milestone 3: Keep the next E2E test blocked on healthy OCloud pod state, Due 2026/07/13

### Goal 2: Document SMO and workload architecture

* Milestone 1: Explain how SMO, rApp, HPE, UE, traffic workload, and monitoring systems relate, Due 2026/07/13
* Milestone 2: Keep the explanation short enough for report use, Due 2026/07/13

### Goal 3: Capture Ming's OCloud pod cleanup mechanism

* Milestone 1: Inspect `/home/hpe/force_cleanup_pods.sh`, Due 2026/07/13
* Milestone 2: Record what the script fixes and why it matters for OCloud testing, Due 2026/07/13

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Confirm Dockerization is finished and preserve side-by-side deployment model | Goal 1 | Docker rApp retained as validated path beside host rApp | | HPE Docker status / health checks |
| P2 | Write SMO/workload architecture answer | Goal 2 | Short report-ready study note | | `docs/StudyNotes/2026-07-13_SMO_Workload_Automated_Testing_Architecture.md` |
| P3 | Inspect Ming's cleanup script | Goal 3 | Summary of cleanup behavior and operational use | | `/home/hpe/force_cleanup_pods.sh` |
| P4 | Update daily note and daily log | Reporting | New daily note plus old-format `Daily-Logs.md` entry | | This file and `Daily-Logs.md` |

Before starting work:

* [x] Keep the existing host rApp untouched.
* [x] Treat Docker as the finished containerized path, but continue using side-by-side validation.
* [x] Do not restart OCloud E2E until the PNF/VNF pod state is healthy.
* [x] Record cleanup logic without hiding the real root cause: missing advertised SR-IOV resource capacity.

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Confirm Dockerized rApp status | Complete | | Dockerization reported finished; previous validation showed container health on `127.0.0.1:19090` while host rApp remained on `127.0.0.1:9090` |
| Write SMO/workload architecture answer | Complete | | `docs/StudyNotes/2026-07-13_SMO_Workload_Automated_Testing_Architecture.md` |
| Inspect Ming's cleanup script | Complete | | `/home/hpe/force_cleanup_pods.sh` inspected over SSH |
| Update daily note and daily log | Complete | | This daily note and appended `Daily-Logs.md` section |

### Progress Summary

The Dockerization task is now considered finished. The validated deployment model remains:

```text
Host rApp:       127.0.0.1:9090
Dockerized rApp: 127.0.0.1:19090
```

This preserves the working host process while allowing the Dockerized service to be tested independently.

The SMO/workload explanation was written as a short report-ready note:

```text
docs/StudyNotes/2026-07-13_SMO_Workload_Automated_Testing_Architecture.md
```

Main point captured:

```text
The SMO/rApp layer decides what experiment should run.
The HPE runner and UE execute the traffic workload.
Kubernetes/OCloud provides the network-function deployment.
InfluxDB/PDU monitoring supplies the power data for throughput-vs-energy evaluation.
```

Ming's cleanup script was inspected on HPE:

```text
/home/hpe/force_cleanup_pods.sh
```

The script:

* uses `/home/hpe/CRAN/kubectl` with `/home/hpe/CRAN/ming-kubeconfig.yaml`;
* scans one namespace by default, or all namespaces if passed `all` / `*`;
* force-deletes pods stuck with a `deletionTimestamp`;
* strips pod finalizers if force deletion does not clear the pod;
* detects pods in `Failed` phase or `OutOf...` resource states;
* for `OutOf...` failures, prints node capacity/allocatable values for the missing resource;
* scales the owning Deployment, ReplicaSet, or StatefulSet to zero to stop the creation loop;
* deletes the failed pods after stopping the owner loop.

This directly matches the OCloud PNF failure mode seen today:

```text
OutOfopenshift.io/fh_sriov_up_lao
```

The immediate symptom was repeated PNF pod creation. The actual root condition was that `lavoisier` did not advertise enough `openshift.io/fh_sriov_up_lao` capacity for the PNF pod request. The cleanup script is a recovery/control tool; the final fix still requires the SR-IOV resource to be correctly advertised before reinstalling or scaling PNF back up.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Re-run Dockerized OCloud smoke test | Needs stable OCloud pod state | Verify SR-IOV capacity first, then install/scale VNF/PNF |
| Confirm PNF resource availability | PNF failed on `fh_sriov_up_lao` capacity | Check `kubectl describe node lavoisier` for `openshift.io/fh_sriov_up_lao: 1` |
| Automate Influx export / merge | Final pipeline still needs power CSV integration | Connect Outlet 2 `active_power` export to run artifacts or keep documented manual export |

### Today's Biggest Lesson

```text
Dockerization is no longer the main blocker. The current fragile point is OCloud pod health,
especially the PNF SR-IOV resource advertisement. Ming's cleanup script is useful because it
stops failed pod creation loops before the namespace becomes unreadable.
```

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Verify `lavoisier` SR-IOV capacity before reinstalling PNF | OCloud recovery | `fh_sriov_up_lao` capacity/allocatable visible as nonzero |
| P2 | Reinstall or scale VNF/PNF only after resources are healthy | OCloud recovery | Clean `oai-vnf` and `oai-pnf-pegatron` Running/Ready pods |
| P3 | Run Dockerized rApp 100 Mbps smoke test | Docker validation | Successful `/gnb/run` job through `127.0.0.1:19090` |
| P4 | Merge throughput artifacts with Outlet 2 power CSV | Final analysis path | `power_throughput_summary.csv` for one validated run |
