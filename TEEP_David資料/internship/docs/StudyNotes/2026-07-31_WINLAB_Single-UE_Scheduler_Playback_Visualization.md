# WINLAB Single-UE Scheduler Playback Visualization

**Date:** 2026/07/31

## Goal

Present the real WINLAB scheduling experiment in a visual form while staying accurate to the laboratory setup: one physical Samsung UE, one OAI cell, and measured RU power.

## Visualization

Open `assets/winlab_scheduler_playback/index.html` directly in a browser. It uses the July 30 `oai_prb_cap_27` run in `runs/hpe_artifacts/e2e-ocloud-20260730-064034`.

## Measured Inputs

| Input | Defensible coverage | Use |
|---|---:|---|
| VNF `[WINLAB_SCHED_LOG]` | 13,726 dense grants over about 8.6 seconds | PRB allocation, MCS, TBS, layers, HARQ, frame, and slot |
| UE iPerf CSV | 1,120 seconds | Received throughput |
| Raritan PDU Outlet 2 | Approximately one sample per minute | Active power |
| Run request and summary | Whole job | Offered load, requested duration, UE, target, and mode |

## Important Discovery

The copied VNF log is a rotated pod-log tail, not a scheduler trace beginning exactly when iPerf began. It contains a dense traffic interval followed by sparse idle/control grants. The scheduler timestamps are process-relative and there is no shared run-start marker that aligns them precisely with iPerf wall-clock time.

Therefore, the page now separates the evidence:

1. The allocation playback uses only the initial contiguous high-density scheduler capture.
2. The lower chart shows the complete throughput and PDU-power run.
3. It does not claim that a scheduler grant at playback second X occurred at throughput second X.

## What the Capture Shows

- 13,725 of 13,726 dense-window grants used 27 PRBs.
- One dense-window record used 5 PRBs.
- No captured allocation exceeded the configured 27-PRB cap.
- The complete traffic record lasted 18 minutes 40 seconds and averaged about 95.9 Mbps.

The earlier 5-PRB-heavy display came from replaying the sparse post-traffic/control tail as though it were continuous traffic scheduling. That interpretation was incorrect.

## Screen Structure

1. **Connected device:** the single UE, RNTI, direction, scheduler, and MIMO layers.
2. **Current grant:** one captured allocation with MCS, TBS, HARQ process, and symbol range.
3. **Allocation history:** rolling mean and maximum grant size on a 0-27 PRB scale.
4. **Scheduler capture:** grant density, mean grant size, and retransmission rate. Throughput and power are explicitly run-level means.
5. **Full timeline:** the independent 18:40 throughput and PDU active-power record.

## Accuracy Boundaries

- This is one real UE, not a simulation of 100 users.
- The scheduler capture and full-run timeline are measured but not precisely time-aligned.
- PDU power is sampled approximately once per minute.
- The run validates the 27-PRB allocation ceiling but does not establish energy savings without a controlled same-day baseline.

## Presentation Message

> This is a measured single-UE experiment. The scheduler receives a 200 Mbps offered load and caps each new downlink allocation at 27 PRBs. The upper playback shows a dense captured scheduling interval on a cap-relative scale. The lower chart separately shows the complete measured throughput and RU power. We do not claim exact timestamp alignment between those two sources for this run.

For future experiments, insert a unique run marker into the VNF log or collect scheduler records into a dedicated timestamped file. That will support exact scheduler-throughput-power alignment and a stronger animation.
