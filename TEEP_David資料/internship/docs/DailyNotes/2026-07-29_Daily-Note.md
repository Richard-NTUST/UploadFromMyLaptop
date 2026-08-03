# Daily Note

## Date

**Date:** 2026/07/29

---

## Short-term Goal

Understand the exact OAI scheduler changes already built for WINLAB, separate scheduler behavior from unrelated radio failures, and define a controlled next implementation without repeating completed baseline runs.

### Goals and milestones

1. Read the exact source lineage for the baseline, logging-only, and 27-PRB commits.
2. Trace the modified code through candidate collection, proportional-fair allocation, HARQ handling, and transport-block construction.
3. Record the safety boundaries and limitations of the current 27-PRB experiment.
4. Prepare the next scheduler implementation and QC sequence for the next exclusive UE window.

## Plan

| Task | Intended result |
|---|---|
| Inspect commit lineage and changed files | Establish the exact experimental delta |
| Trace scheduler execution | Understand where the cap acts and what it preserves |
| Review failure attribution | Avoid blaming scheduler code for RU, PNF, xRAN, or shared-UE failures |
| Document implementation path | Define runtime modes and focused tests |

## Review

| Item | Result |
|---|---|
| Commit lineage | `5bbf48af2d` -> `31c7aa0477` -> `d7c850098a` |
| Logging-only scope | One 17-line allocation log in `gNB_scheduler_dlsch.c` |
| 27-PRB scope | One mode-label change plus a five-line phase-3 cap in `gNB_scheduler_dlsch_default_policies.c` |
| Directly preserved behavior | HARQ retransmissions, MAC-control-only grants, CCE/PUCCH validation, VRB-map accounting |
| Important indirect effect | Phase-3 pending bytes include every active RLC LCID, so SRB/RRC payload grants may also be capped |
| Live test today | Deferred because the shared Samsung UE was in use; no redundant `latest` baseline was required |

### Progress Summary

The exact source was read from `/home/hpe/openairinterface5g`. The custom history is linear: the logging-only commit is based on `5bbf48af2d`, and the 27-PRB commit is based directly on the logging commit. Across both commits, only two NR MAC scheduler files changed. No RACH, PRACH, RRC, nFAPI, NGAP, AMF, PNF, or xRAN source was modified.

The active allocation callback is `nr_dl_proportional_fair()`. Its three phases prioritize exact-size HARQ retransmissions, then five-RB MAC-control-only grants, then new RLC data. The experiment caps only the third phase by replacing the largest available contiguous block with `min(max_rbSize, 27)`. Allocation still passes through `COMMIT_ALLOC()`, which retains CCE/PUCCH validation and resource-map accounting. `nr_find_nb_rb()` may select fewer than 27 PRBs when the buffered payload is small, so the patch is a maximum, not a fixed allocation.

A source-level nuance was identified: `update_dlsch_buffer()` sums data from all activated RLC logical channels, not only application DRBs. The cap therefore does not modify attachment code, but it may constrain downlink SRB/RRC payload grants after random access. This justifies a short attach smoke test before a traffic run when the UE is available.

The foreign NR-cell observations were also reconciled. They occurred while the Samsung UE had been taken outside its normal RF chamber. Under normal placement, the chamber isolates the UE from unrelated OAI cells on other floors, so that contention is situational rather than part of the intended test architecture.

Detailed source findings and the QC plan are recorded in [OAI Scheduler Deep Dive: Failure Attribution and QC Plan](../StudyNotes/2026-07-29_OAI_Scheduler_Deep_Dive_Failure_Attribution_and_QC_Plan.md).

## Next Working Session

| Priority | Action |
|---:|---|
| 1 | Port the scheduler experiment to one chosen source base with runtime-selectable baseline and capped modes |
| 2 | Decide whether SRB LCIDs should be explicitly exempt from the data cap |
| 3 | Replace high-rate unconditional INFO logging with controlled experiment telemetry |
| 4 | Extend `nrdlbench` to assert baseline, capped-new-data, retransmission, and control-only behavior |
| 5 | During an exclusive UE window, run attach smoke, short traffic validation, then the planned longer power/throughput experiment |
