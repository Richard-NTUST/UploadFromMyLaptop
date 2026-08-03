# Daily Note

## Date

**Date:** 2026/06/30

---

## Short-term Goal

Define one-month goals and weekly milestones.

* Goal 1: Prepare WINLAB / Pegatron O-RU experiment workflow documentation

  * Milestone 1: Convert rough operational notes into professional study notes, Due 2026/06/30
  * Milestone 2: Document Jenkins image-build workflow for OAI gNB images, Due 2026/06/30
  * Milestone 3: Document HPE Helm deployment and OAI runtime configuration workflow, Due 2026/06/30

* Goal 2: Improve daily research logging structure

  * Milestone 1: Read and understand the new daily log template, Due 2026/06/30
  * Milestone 2: Start a new daily log file using the new template format, Due 2026/06/30
  * Milestone 3: Use evidence-linked plan/review tables for future daily entries, Due 2026/07/01

* Goal 3: Lock the first WINLAB baseline direction

  * Milestone 1: Confirm the first official baseline architecture, Due 2026/06/30
  * Milestone 2: Separate what still needs Ming from what can be standardized independently, Due 2026/06/30
  * Milestone 3: Identify the next required learning target for power measurement, Due 2026/07/01

---

## Plan

Daily tasks should support one of the weekly milestones or action items from the latest meeting notes.

| Priority | Task | Expected Deliverable | Est. Time | Evidence (Hyperlink) |
| -------- | ---- | -------------------- | --------- | -------------------- |
| P1 | Rewrite `RawDualNote.md` into two professional study notes | Two clean study notes under `docs/StudyNotes/` | 2h | [BMW Jenkins workflow](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md), [HPE OAI Helm guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md) |
| P2 | Expand the OAI configuration theory section | Explanation of Helm values, ConfigMap, TDD pattern, ARFCN, Point A, and WINLAB throughput/power implications | 1h | [HPE OAI Helm guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md) |
| P3 | Start the new daily log format | `New-Daily-Logs.md` initialized from `Log_Template.md` structure | 30m | [New-Daily-Logs.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/New-Daily-Logs.md) |
| P4 | Clarify the official baseline after Ming's E2E walkthrough | Confirmed baseline architecture and first run label | 45m | [nFAPI baseline clarifications](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_WINLAB-nFAPI-Baseline-Clarifications-and-Next-Learning-Target.md) |
| P5 | Decide the next learning target | Clear next step for CortexDC / PDU power measurement | 30m | [nFAPI baseline clarifications](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_WINLAB-nFAPI-Baseline-Clarifications-and-Next-Learning-Target.md) |

Guidelines:

* Each task should support a weekly milestone or meeting action item.
* Each deliverable should be measurable.
* Plan where the evidence will be recorded before starting the work.

---

## Review

| Task | Status | Actual Time | Evidence (Hyperlink) |
| ---- | ------ | ----------- | -------------------- |
| Rewrite `RawDualNote.md` into two professional study notes | Done | 2h | [BMW Jenkins workflow](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md), [HPE OAI Helm guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md) |
| Expand the OAI configuration theory section | Done | 1h | [HPE OAI Helm guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md) |
| Start the new daily log format | Done | 30m | [New-Daily-Logs.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/New-Daily-Logs.md) |
| Clarify the official baseline after Ming's E2E walkthrough | Done | 45m | [nFAPI baseline clarifications](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_WINLAB-nFAPI-Baseline-Clarifications-and-Next-Learning-Target.md) |
| Decide the next learning target | Done | 30m | [nFAPI baseline clarifications](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-06-30_WINLAB-nFAPI-Baseline-Clarifications-and-Next-Learning-Target.md) |

If a task is **Pending** or **Blocked**, briefly explain why and update the next working day plan.

**Today's biggest lesson**

```text
The operational path has two separate control planes: Jenkins controls which OAI image is built and pushed, while Helm controls which image and runtime OAI configuration are actually deployed. The first official baseline is now clarified as nFAPI with the original OAI scheduler on the HPE deployment path. Ming is no longer the main blocker for the E2E line; the next required learning target is Ms. Chynna's CortexDC / PDU power export path so throughput can be matched to Pegatron O-RU power.
```

---

## Next Working Day Plan

Prepare the next working day based on today's review.

| Priority | Task | Expected Deliverable |
| -------- | ---- | -------------------- |
| P1 | Learn CortexDC / PDU export workflow from Ms. Chynna | Confirmed Pegatron O-RU power source, export method, fields, units, sampling interval, and timestamp basis |
| P2 | Confirm the exact RU outlet or CortexDC asset for Pegatron O-RU | RU power source mapping that can be linked to iPerf test windows |
| P3 | Prepare the first `nfapi_pegatron_original_oai` smoke-test run sheet | Run metadata template covering iPerf output, UTC markers, and matching CortexDC/PDU power window |
