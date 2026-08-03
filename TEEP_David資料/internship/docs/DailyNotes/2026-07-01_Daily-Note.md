# Daily Note

## Date

**Date:** 2026/07/01

---

## Short-term Goal

Follow the Open Research Playbook for daily planning, mentor discussions, and evidence-linked research progress.

### 8-Week Expected Milestones

| Week | Expected Milestone | Measurable Deliverable |
| ---- | ------------------ | ---------------------- |
| Week 1 | Align research plan with mentors and senior students | Meeting notes, confirmed 8-week milestone plan, and open-question list for CortexDC/PDU and E2E access |
| Week 2 | Prepare reproducible nFAPI baseline workflow | `nfapi_pegatron_original_oai` smoke-test run sheet, evidence checklist, and known-good deployment/access checklist |
| Week 3 | Reproduce original WINLAB nFAPI E2E smoke path if lab access is ready | One smoke-test evidence bundle with iPerf output, UTC markers, and deployment metadata; if blocked, documented blocker report |
| Week 4 | Build the original-OAI measurement pipeline | Confirmed CortexDC/PDU export procedure and one matched throughput-power data row; if RU mapping is still blocked, use server/PDU sample export as a dry run |
| Week 5 | Complete original-OAI baseline sweep | 100/400/700 Mbps baseline sweep with repeated runs and timestamp-aligned RU power data |
| Week 6 | Buffer / validation week | Resolve lab-access, PDU-mapping, UE, Helm, or data-quality blockers; otherwise repeat baseline runs for confidence |
| Week 7 | Add scheduler allocation logging evidence | OAI scheduler log fields captured for original mode: frame, slot, RNTI, rbStart, rbSize, MCS, and TBS |
| Week 8 | Buffer / interim research package | Study note, runbook, dataset summary, plots, blockers, next-step recommendation, and emergency catch-up if earlier lab work slipped |

### Goal 1: Follow Open Research Playbook conventions

* Milestone 1: Read and summarize the Open Research Playbook conventions, Due 2026/07/01
* Milestone 2: Convert today's work into measurable action items and planned evidence, Due 2026/07/01
* Milestone 3: Post the morning daily plan before noon, Due 2026/07/01

### Goal 2: Sync WINLAB / Pegatron O-RU plan with mentors and senior students

* Milestone 1: Ask Chynna/Peter/Ming for CortexDC/PDU and Pegatron O-RU outlet mapping, Due 2026/07/01
* Milestone 2: Prepare meeting-note structure for any mentor/senior discussion, Due 2026/07/01
* Milestone 3: Convert discussion outcomes into concrete action items, Due 2026/07/01

### Goal 3: Prepare first reproducible E2E baseline step

* Milestone 1: Confirm whether E2E smoke test should wait for RU power-source confirmation, Due 2026/07/01
* Milestone 2: Draft the first `nfapi_pegatron_original_oai` smoke-test run sheet, Due 2026/07/01
* Milestone 3: Define required evidence bundle for E2E + power alignment, Due 2026/07/01

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Read `External/Playbook` and extract research conventions | Professor Ray's request to read Open Research Playbook | Short summary of daily planning, meeting-note, evidence, and reproducibility rules | | |
| P2 | Prepare and post today's daily plan with 8-week milestones | Professor Ray's request for daily plan and 8-week milestone plan | Morning post containing short-term goals, 8-week milestones, today's action items, and expected evidence | | |
| P3 | Ask CortexDC/PDU clarification questions to Chynna/senior students | WINLAB baseline blocker: Pegatron O-RU power source unknown | Sent questions confirming O-RU PDU outlet, CortexDC/InfluxDB representation, `active_power` export, and outlet-label mapping; if no reply today, record it as a blocker and prepare a dry-run export plan | | |
| P4 | Prepare meeting-note structure for any mentor/senior discussion today | Playbook rule: every discussion should produce consensus and action items | Meeting note structure with agenda, discussion topics, consensus, action items, owner, due date, and evidence | | |
| P5 | Draft `nfapi_pegatron_original_oai` smoke-test run sheet | First reproducible E2E baseline step | Run sheet listing prerequisites, commands/outputs to capture, UTC markers, deployment metadata, and power export fields | | [Smoke-test run sheet](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-01_nfapi_pegatron_original_oai_Smoke-Test-Run-Sheet.md) |

Before starting work:

* [x] Each task supports a milestone or meeting action item.
* [x] Each expected deliverable is measurable.
* [x] The evidence location has been planned.

---

## Escalation / Contact Plan

| Topic | Contact |
| ----- | ------- |
| CortexDC/PDU and Pegatron O-RU outlet mapping | Chynna / Peter |
| nFAPI E2E workflow, UE access, rApp or iPerf flow | Ming |
| HPE Helm release, namespace, OAI image/config | Ming / lab mentor |
| Research scope and milestone approval | Prof. Ray |

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Read `External/Playbook` and extract research conventions | Complete | | Daily plan uses measurable deliverables, owner/action/evidence tables, and explicit blocker tracking |
| Prepare and post today's daily plan with 8-week milestones | Complete | | This daily note now contains the 8-week milestone plan and review |
| Ask CortexDC/PDU clarification questions to Chynna/senior students | In Progress | | CortexDC/PDU mapping remains an explicit blocker before throughput-power baseline claims |
| Prepare meeting-note structure for mentor/senior discussion today | Complete | | [Meeting note](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/MeetingNotes/2026-07-01_CortexDC-Pegatron-ORU-Power-Mapping.md) |
| Draft `nfapi_pegatron_original_oai` smoke-test run sheet | Complete | | [Smoke-test run sheet](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-01_nfapi_pegatron_original_oai_Smoke-Test-Run-Sheet.md) |
| Build HPE E2E rApp wrapper for repeatable lab triggering | Complete | | [`rapps/winlab_e2e_rapp`](../../rapps/winlab_e2e_rapp/README.md) |
| Validate Bare Metal gNB + UE iPerf path through API | Complete | | HPE job output, UE IP `10.45.0.2`, collected log folder `/home/hpe/ming-logs/Exp_Bandwidth/0701-1628-100x` |
| Unify gNB API around Bare Metal and OCloud modes | Complete | | `POST /gnb/run` with `mode: "baremetal"` or `mode: "ocloud"`; old compatibility endpoints removed |
| Prepare OCloud iPerf parity patch | Complete | | [`cloud_e2e_full_iperf.py`](../../rapps/winlab_e2e_rapp/patches/cloud_e2e_full_iperf.py) and patch artifact |

### Progress Summary

Today moved the WINLAB E2E work from a manually described smoke-test plan into a working request-driven rApp prototype.

Main progress:

* Read the operational HPE scripts enough to map responsibilities:
  * `/home/hpe/CRAN/ocloud-helm-templates/cloud_e2e.py`
  * `/home/hpe/ming-logs/e2e_core.py`
  * `/home/hpe/ming-logs/plot_core.py`
  * `/home/hpe/ming-logs/ue_driver.py`
* Created a local rApp package under `rapps/winlab_e2e_rapp/` that wraps the HPE-side scripts without storing lab credentials.
* Added API support for UE actions, job polling, cleanup, dataset generation, plotting, and unified gNB execution.
* Consolidated the gNB API into one endpoint:

```text
POST /gnb/run
```

Supported modes:

```text
mode = baremetal -> /home/hpe/ming-logs/exp_bandwidth.py
mode = ocloud    -> /home/hpe/CRAN/ocloud-helm-templates/cloud_e2e.py
```

* Removed the older compatibility endpoints:

```text
POST /cloud/smoke
POST /experiments/bandwidth
```

* Validated that the HPE server must run the rApp on `127.0.0.1:9090`, not `0.0.0.0:9090`, because Open5GS components already bind port `9090` on loopback addresses such as `127.0.0.4`, `127.0.0.5`, and `127.0.0.13`.
* Confirmed that those Open5GS processes should not be killed because they are part of the core network path.
* Ran the Bare Metal path live through the API. The job brought the Samsung UE online, obtained UE IP `10.45.0.2`, ran iPerf, collected logs, generated plots, and committed a log bundle under:

```text
/home/hpe/ming-logs/Exp_Bandwidth/0701-1628-100x
```

* Parsed iPerf output from a 100 Mbps run and confirmed the measured result was approximately target-rate with zero loss in the UE log:

```text
Mbps: approximately 100
lost_percent: 0
```

* Confirmed that OCloud mode currently depends on pre-existing Kubernetes pods in `ming-ns`; the rApp trigger is correct, but `cloud_e2e.py` fails if `oai-vnf` and `oai-pnf` pods are missing or not ready.
* Inspected `cloud_e2e.py` and found that it already imports `ue_driver`, but hard-codes a lite iPerf smoke test: 500 Mbps, 10 seconds, 2 second gap, downlink only.
* Prepared an OCloud parity patch so `cloud_e2e.py` can accept the same iPerf traffic knobs used by Bare Metal:

```text
--bandwidth
--period
--gap-time
--uplink
--ue-model
--iperf-bind
```

This should allow OCloud and Bare Metal runs to use the same UE-side iPerf quality and logging path.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| CortexDC/PDU confirmation | Pegatron O-RU outlet mapping and timestamped `active_power` export are still not confirmed | Follow up with Chynna/Peter; do not claim throughput-power baseline until outlet mapping and export method are confirmed |
| OCloud pod readiness | `cloud_e2e.py` requires `oai-vnf` and `oai-pnf` pods in `ming-ns` to be Running and Ready | Check `kubectl get pods -n ming-ns -o wide` before live OCloud tests |
| OCloud iPerf parity | Current HPE `cloud_e2e.py` uses a hard-coded 500 Mbps / 10 s lite smoke flow | Apply and test the prepared full-iPerf patch after backing up the HPE script |
| Baseline evidence quality | Bare Metal traffic is runnable, but RU power alignment is not yet confirmed | Treat today's successful E2E run as workflow validation, not final throughput-power evidence |

### Today's Biggest Lesson

```text
The first real milestone is not the final power plot; it is making the lab path repeatable.
Today the E2E workflow became controllable through an API: UE attach, gNB mode selection,
iPerf traffic, logs, and job status are now reproducible enough to debug systematically.

Also: bind the rApp to 127.0.0.1 on HPE. Port 9090 is already used by Open5GS on other
loopback addresses, and those processes are part of the experiment path.
```

---

## Next Working Day Plan

Prepare the next working day based on today's review and researcher-reviewed AI feedback.

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Apply and test OCloud `cloud_e2e.py` full-iPerf patch | OCloud/Bare Metal parity | OCloud dry-run and live smoke result using parameterized `bandwidth`, `period`, and `gap_time` |
| P2 | Confirm OCloud pod readiness workflow with Ming | OCloud gNB mode | Clear command sequence for deploying/checking `oai-vnf` and `oai-pnf` pods in `ming-ns` |
| P3 | Follow up on CortexDC/PDU outlet mapping | Power-baseline blocker | Confirmed PDU outlet, CortexDC/InfluxDB export method, timezone, and sampling interval |
| P4 | Run one controlled Bare Metal evidence bundle if power assumptions are explicit | Baseline reproduction milestone | Job ID, log folder, iPerf JSON, ping log, UTC markers, and power export reference |
| P5 | Update smoke-test run sheet with the new rApp commands | E2E baseline preparation | Run sheet reflects `/gnb/run`, Bare Metal/OCloud modes, and known HPE port binding rule |
