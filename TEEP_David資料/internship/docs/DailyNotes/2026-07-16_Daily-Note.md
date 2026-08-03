# Daily Note

## Date

**Date:** 2026/07/16

---

## Short-term Goal

Consolidate the Dockerized WINLAB rApp path, clarify two-server configurability, and prepare OCloud pod recovery so the next successful run can be merged with PDU power data.

### Goal 1: Preserve Dockerized rApp side-by-side validation

* Milestone 1: Keep the host rApp on `127.0.0.1:9090`, Due 2026/07/16
* Milestone 2: Keep the Dockerized rApp on `127.0.0.1:19090`, Due 2026/07/16
* Milestone 3: Confirm HPE and UE-control server identities remain configurable, Due 2026/07/16

### Goal 2: Prepare OCloud recovery path

* Milestone 1: Capture the PNF/VNF pod failure and recovery pattern, Due 2026/07/16
* Milestone 2: Document Ming's cleanup script behavior, Due 2026/07/16

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Review Dockerized rApp deployment model | Goal 1 | Side-by-side validation model retained | | rApp ports and endpoint behavior |
| P2 | Clarify HPE/IAPC configurability | Goal 1 | Configurable runner and UE-control identities | | Request parameters |
| P3 | Capture OCloud pod recovery behavior | Goal 2 | Study note on Docker/pod recovery | | `docs/StudyNotes/2026-07-16_WINLAB_OCloud_Docker_and_Pod_Recovery.md` |
| P4 | Prepare next merge validation | Reporting | Clear next-day run plan | | Daily note and old daily log |

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Review Dockerized rApp deployment model | Complete | | Host service kept on `9090`; Docker service kept on `19090` |
| Clarify HPE/IAPC configurability | Complete | | `server`, `target_identity`, `ue_serial`, `iapc_host`, and `iapc_port` captured |
| Capture OCloud pod recovery behavior | Complete | | `docs/StudyNotes/2026-07-16_WINLAB_OCloud_Docker_and_Pod_Recovery.md` |
| Prepare next merge validation | Complete | | This daily note and `Daily-Logs.md` entry |

### Progress Summary

The rApp validation model was kept non-disruptive: the working host rApp remains on `127.0.0.1:9090`, while the Dockerized service is tested on `127.0.0.1:19090`.

The two-server model was clarified:

```text
Server 1: HPE runner / OCloud host
Server 2: IAPC / UE-control host
```

Both sides must be configurable because the rApp should be reusable across lab hardware.

The OCloud recovery note captured the recurring PNF failure mode around SR-IOV allocation, terminating pods, failed pods, and cleanup through `/home/hpe/force_cleanup_pods.sh`.

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Restore healthy VNF/PNF pod state | OCloud validation | Both pods Running/Ready |
| P2 | Run Dockerized OCloud E2E test | rApp validation | Successful `/gnb/run` job |
| P3 | Export Outlet 2 power data | Power merge | PDU CSV matching run window |
| P4 | Run merge script | Analysis validation | `power_throughput_summary_*.csv` |
