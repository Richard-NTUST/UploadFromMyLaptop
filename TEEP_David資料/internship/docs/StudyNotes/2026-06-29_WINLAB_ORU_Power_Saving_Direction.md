---
title: WINLAB / O-RU Power Saving Direction - Professor Context and Execution Plan
---

# WINLAB / O-RU Power Saving Direction

**Date:** June 29, 2026  
**Main topic:** Duplicate WINLAB / POET-style RU power consumption measurements, then compare OAI scheduler variants for Pegatron RU power saving.  
**Current priority:** OAI scheduler + CN-gNB-RU-UE E2E test automation + CortexDC/PDU power measurement.

---

## 1. Professor's Latest Direction

Prof. Ray's latest instruction, from the June 27 group chat, is that David will build the digital twin model for the Pegatron RU and is currently studying the OAI scheduler.

The end goal is:

1. Inject different data rates into the gNB.
2. Measure the power consumption of the Pegatron RU using PDU / CortexDC.
3. Plot E2E throughput against RU power consumption.
4. Extend the test from the original OAI scheduler to OAI scheduler variants for time-domain and frequency-domain scheduling.

Prof. Ray listed three required knowledge/work areas:

| Area | Owner / Source | Purpose |
|---|---|---|
| OAI scheduler | David | Implement time- and frequency-domain scheduling behavior |
| CN-gNB-RU-UE E2E automatic testing environment | Learn from Ming | Run reproducible E2E throughput tests with Test Automation rApp |
| Power measurement using CortexDC | Learn from Chynna | Collect Pegatron RU power consumption through the lab measurement path |

---

## 2. Required Milestones

### Milestone 1 - Duplicate Existing E2E Test Result

Duplicate the E2E test results from Ming's MS thesis and produce a 2D plot:

| Plot Element | Required Value |
|---|---|
| X-axis | E2E Throughput |
| Y-axis | Power consumption of the Pegatron RU |
| Curve | OAI original scheduler |

This is the baseline replication step. It should be completed before modifying the OAI scheduler, because it verifies that the test automation and power measurement pipeline work.

### Milestone 2 - Implement OAI Scheduler Variants

Implement time-domain and frequency-domain scheduler behavior on OAI and produce a 2D comparison plot:

| Plot Element | Required Value |
|---|---|
| X-axis | E2E Throughput |
| Y-axis | Power consumption of the Pegatron RU |
| Curves | OAI original scheduler, OAI time-domain scheduler, OAI frequency-domain scheduler |

This is the main research comparison.

---

## 3. Current State

### Completed Background Work

The following technical background is already documented:

| Topic | Status | Reference |
|---|---|---|
| WINLAB / POET baseline extraction | Complete | `docs/StudyNotes/2026-01-12_WINLAB-Baseline.md` |
| RU measurement scope and metrics | Complete | `docs/StudyNotes/2026-01-12_RU-Measurement-Scope.md` |
| EARTH / RU power model | Complete | `docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md` |
| OAI + srsRAN MAC scheduler PRB study | Complete | `docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md` |
| TBS equivalence proof, 273x1 vs 27x10 | Complete | `docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md` |
| OAI scheduler source-code verification | Complete | `docs/StudyNotes/2026-03-04_OAI-Scheduler-Source-Code-Verified.md` |
| rApp orchestration pipeline study | Complete | `docs/StudyNotes/2026-03-13_rApp-Test-Orchestration-Pipeline-Deep-Dive.md` |
| Sideloader / monitoring service study | Complete | `docs/StudyNotes/2026-03-13_Sideloader-Service-Deep-Dive.md` |
| WINLAB / POET measurement methodology | Complete | `docs/StudyNotes/2026-05-07_Topic2-WINLAB-POET-Measurement-Methodology.md` |
| Phase 1 POET measurement validation | Complete | `scripts/run_poet_phase1.sh`, `assets/poet_phase1/power_validation.png` |

### Current Infrastructure Context

Most of the previous week was spent finishing handover and setup notes for the OKD / StarlingX infrastructure track:

| Date | Topic | Link |
|---|---|---|
| May 20 | OKD local Hub + SNO deployment | `docs/StudyNotes/2026-05-20_OKD_Deployment_Notes.md` |
| June 17 | OKD Newton verification attempt | `docs/StudyNotes/2026-06-17_OKD_Newton_Deployment_Notes.md` |
| June 28 | StarlingX AIO-Duplex on Archimedes | `docs/StudyNotes/2026-06-28_StarlingX_AIO_Duplex_Deployment_Notes.md` |

These are adjacent infrastructure tasks, but the WINLAB / O-RU Power Saving direction now needs to return to the foreground.

---

## 4. Technical Understanding So Far

### WINLAB / POET Measurement Target

The POET paper and related notes establish the measurement style:

- Smart PDU is the ground-truth power measurement source.
- IPMI / BMC power can be used as a whole-system DC proxy.
- Scaphandre / Kepler / RAPL are useful for CPU or container-level attribution, but they do not measure full RU hardware power.
- Power and performance metrics must be timestamp-aligned.
- POET examples use iPerf traffic and report both throughput and PRB utilization.

Important POET numeric targets already extracted:

| Scenario | DU PRB Load | Aggregate DL Throughput |
|---|---:|---:|
| 1 UE | 70% | 65 Mb/s |
| 2 UEs | 100% | 84 Mb/s total, about 42 Mb/s per UE |

These should be treated as reference targets, not guaranteed exact values for the Pegatron RU setup unless the radio configuration matches.

### OAI Scheduler Understanding

OAI uses a hardcoded proportional-fair DL scheduler in `pf_dl()` inside `gNB_scheduler_dlsch.c`.

Key facts from the verified OAI scheduler note:

- OAI does not have a scheduler policy factory like srsRAN.
- OAI does not expose a clean config switch for time-domain vs frequency-domain scheduling.
- DL scheduling is effectively:
  1. Build UE list.
  2. Compute PF coefficient.
  3. Sort UEs.
  4. Scan `rballoc_mask[]` for contiguous free RBs.
  5. Call `nr_find_nb_rb()` to choose RB count.
  6. Populate PDSCH PDU with `rbStart`, `rbSize`, MCS, and TBS.
- OAI supports Resource Allocation Type 1, meaning contiguous RB allocation.

Likely intervention points:

| Scheduler Variant | Possible Implementation |
|---|---|
| Original OAI scheduler | No source modification; baseline PF behavior |
| Time-domain scheduler | Limit scheduled UEs per slot, e.g. force `max_sched_ues = 1`, or rotate UE selection across slots |
| Frequency-domain scheduler | Keep multiple UEs in the same slot and allocate PRBs across frequency; original OAI may already behave this way under multiple active UEs |
| Narrow-band / 27-PRB mode | Cap `max_rbSize` inside `pf_dl()` after contiguous-block scan |

The exact definitions of "time-domain scheduler" and "frequency-domain scheduler" must be aligned with Prof. Ray / Ming before implementation, because OAI's default PF scheduler already mixes time fairness and frequency-domain RB allocation.

### 273x1 vs 27x10 Equivalence

The TBS calculator result proves that:

```text
TBS(273 PRBs x 1 slot) ~= 10 x TBS(27 PRBs x 1 slot)
```

Across all tested MCS configurations, the difference stayed within about -1.09% to +2.66%.

This supports the professor's scheduling question: the same approximate data volume can be delivered either as a full-bandwidth burst or as smaller allocations spread across time.

---

## 5. Collaborators and What to Ask

### Ming - Test Automation rApp / E2E Testing

Ming is the key person for the CN-gNB-RU-UE E2E automatic testing environment and the existing thesis test flow.

Need from Ming:

- Which Test Automation rApp test case was used for the Pegatron RU E2E throughput result.
- How to run the test from the lab environment.
- Required access, credentials, cluster context, and test input files.
- Expected outputs and where they are stored.
- How E2E throughput is calculated.
- Whether the test already supports traffic/data-rate sweep parameters.
- Whether the OAI scheduler variant can be selected through image tag, Helm value, config parameter, or deployment branch.

Initial DM already prepared:

```text
Hello Mr. Ming, sorry to bother you.

Prof. Ray said my next goal is to duplicate the WINLAB / Pegatron RU power consumption test, starting from the CN-gNB-RU-UE E2E automatic testing environment using the Test Automation rApp.

My current understanding is:
- First, I need to reproduce the existing E2E throughput test result from your MS thesis.
- Then I need to run throughput sweeps using the original OAI scheduler.
- After that, I will compare original OAI scheduler vs time-domain scheduler vs frequency-domain scheduler.

Could you please guide me on what I should study or run first from your side?
If possible, I would also like to know which test case / rApp flow was used for the Pegatron RU E2E throughput test, and what inputs I need to prepare before running it.

Thank you!
```

### Chynna - CortexDC / PDU Power Measurement

Chynna is the key person for the CortexDC / PDU measurement side.

Need from Chynna:

- How CortexDC collects Pegatron RU power.
- Whether the measurement source is PDU, DC power, BMC/IPMI, or another sensor path.
- Power data export method.
- Units, fields, and timestamp format.
- Sampling interval and averaging behavior.
- How to align power data with rApp test runs.
- Whether existing Pegatron RU power data can be used as a reference later.
- Whether CortexDC already tags runs by test ID, RU, gNB deployment, or timestamp.

Initial DM already prepared:

```text
Hello Ms. Chynna, sorry to bother you.

Prof. Ray said my next goal is to duplicate the WINLAB / Pegatron RU power consumption test, and I should learn the power measurement part using CortexDC from you.

My current understanding is:
- The experiment should inject different data rates into the gNB.
- For each run, I need to collect E2E throughput and Pegatron RU power consumption.
- The final plot should use E2E throughput as the X-axis and RU power consumption as the Y-axis.

Could you please guide me on what I should study or check first for the CortexDC / PDU power measurement flow?
If possible, I would also like to know how the RU power data is exported, what timestamp format it uses, and whether there is existing Pegatron RU power data I can use as a reference while setting up my experiments.

Thank you!
```

### Recommended Ask Order

Ask for workflow and direction first. Ask for actual power usage datasets after they respond.

Reason:

- It is better to understand the measurement path before requesting data.
- The data may only make sense after knowing test IDs, timestamps, averaging windows, and units.
- The professor asked for learning the workflows from Ming and Chynna, so the first message should ask for guidance rather than only files.

---

## 6. Concrete Execution Plan

### Step 1 - Reproduce Original E2E Test

Goal: reproduce Ming's original E2E throughput result using the existing OAI scheduler.

Inputs needed:

- rApp test case for Pegatron RU.
- OAI gNB deployment image/config used in thesis.
- UE setup and traffic generator details.
- CortexDC/PDU power source.

Outputs:

- E2E throughput.
- RU power consumption.
- Timestamp-aligned run log.
- One baseline curve: OAI original scheduler.

### Step 2 - Build Data-Rate Sweep

Goal: inject different data rates into gNB and measure throughput/power response.

Suggested sweep:

| Sweep Point | Purpose |
|---|---|
| Idle / active-idle | RU baseline power |
| Low data rate | Low load behavior |
| Medium data rate | Linearity / slope |
| High data rate | Saturation / full-load behavior |
| POET anchor points | 65 Mb/s and 84 Mb/s if compatible with setup |

Each point should run long enough for PDU/CortexDC averaging to stabilize. If PDU cadence is about 10 seconds, use multi-minute steady-state windows.

### Step 3 - Define OAI Scheduler Variants

Before implementation, confirm exact definitions with the team.

Candidate definitions:

| Variant | Meaning | OAI Implementation Idea |
|---|---|---|
| Original | Existing OAI PF behavior | No code change |
| Frequency-domain | Multiple UEs share one slot across different RB ranges | Existing PF may already serve as baseline FDM under multi-UE load |
| Time-domain | Reduce or avoid multi-UE frequency sharing; schedule users across different slots | Force `max_sched_ues = 1` or add UE rotation |
| Narrow-band spread | Deliver similar data volume over more slots with fewer RBs per slot | Cap `max_rbSize`, e.g. 27 RBs |

Important: "time-domain scheduler" might mean different things:

- Strict TDM: one UE per slot, full bandwidth.
- Narrow-band time-spread: one or more UEs use limited PRBs across many slots.
- Burst scheduling for sleep opportunity: concentrate traffic into fewer slots and leave empty slots.

This must be clarified before coding.

### Step 4 - Implement Minimal OAI Patch

Possible implementation strategy:

1. Add compile-time or runtime scheduler mode flag.
2. Keep original PF as mode 0.
3. Add `max_rbSize` cap mode.
4. Add `max_sched_ues = 1` mode.
5. Log mode, `rbStart`, `rbSize`, UE RNTI, MCS, TBS, frame, and slot.

The logging is important because the plot alone cannot prove the scheduler changed behavior.

### Step 5 - Run Full Comparison

For each scheduler mode:

1. Deploy OAI gNB.
2. Attach UE / run E2E test through rApp.
3. Sweep data rate.
4. Collect E2E throughput.
5. Collect Pegatron RU power through CortexDC/PDU.
6. Export aligned CSV.
7. Plot throughput vs power.

Final plot:

```text
X-axis: E2E Throughput
Y-axis: Pegatron RU Power Consumption
Curves:
  - OAI original scheduler
  - OAI time-domain scheduler
  - OAI frequency-domain scheduler
```

---

## 7. Data Needed for Final Analysis

Minimum dataset per run:

| Field | Source | Notes |
|---|---|---|
| run_id | rApp / manual marker | Must connect throughput and power |
| scheduler_mode | OAI config / image tag / log | original, time-domain, frequency-domain |
| offered_rate_mbps | traffic generator | Input data rate |
| measured_e2e_throughput_mbps | rApp / UE / iperf | X-axis |
| ru_power_w | CortexDC / PDU | Y-axis |
| timestamp_start_utc | rApp / marker | Alignment |
| timestamp_end_utc | rApp / marker | Alignment |
| ue_count | rApp / OAI log | Needed for POET-style comparison |
| prb_utilization_pct | OAI / DU metrics if available | Important validation metric |
| mcs / rbSize / rbStart | OAI scheduler log if available | Confirms scheduler behavior |

Preferred analysis format:

```csv
run_id,timestamp_start_utc,timestamp_end_utc,scheduler_mode,offered_rate_mbps,measured_e2e_throughput_mbps,ru_power_w,ue_count,prb_utilization_pct,notes
```

---

## 8. Risks and Open Questions

| Risk / Question | Why It Matters | Owner / Next Action |
|---|---|---|
| Exact meaning of "time-domain scheduler" and "frequency-domain scheduler" | Prevents implementing the wrong comparison | Clarify with Prof. Ray / Ming |
| How to run Ming's rApp test case | Needed for Milestone 1 | Ask Ming |
| How CortexDC exports RU power | Needed for aligned plot | Ask Chynna |
| Whether PDU cadence is slow | Determines run duration and averaging window | Ask Chynna |
| Whether OAI image can be modified/redeployed easily | Determines implementation path | Ask Ming / lab repo owner |
| How to log PRB allocation from OAI | Needed to prove scheduler mode | Inspect active OAI source and enable MAC logs |
| Whether Pegatron RU supports visible sleep/power states | Affects expected savings | Ask team after baseline works |
| Whether existing historical data exists | Useful for sanity checks, not first dependency | Ask after initial workflow response |

---

## 9. Immediate Next Actions

1. Send DM to Ming asking for rApp / E2E test direction.
2. Send DM to Chynna asking for CortexDC / PDU direction.
3. Send group update to WINLAB Replication team with:
   - POET experiment summary.
   - Current scheduler/measurement progress.
   - Infrastructure notes briefly at the bottom.
4. Locate active OAI source tree used by the lab.
5. Identify exact `gNB_scheduler_dlsch.c` version and confirm `pf_dl()` structure.
6. Prepare a minimal OAI scheduler logging patch before implementing behavior changes.
7. Once Ming and Chynna respond, define the first baseline run:
   - original OAI scheduler,
   - one Pegatron RU setup,
   - one data-rate sweep,
   - CortexDC/PDU export,
   - final throughput-power CSV.

---

## 10. One-Sentence Summary

The current thesis direction is to reproduce the existing Pegatron RU E2E throughput-power experiment using OAI and CortexDC/PDU first, then modify the OAI scheduler to compare original, time-domain, and frequency-domain scheduling curves against RU power consumption.
