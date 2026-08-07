# WINLAB Scheduler Playback, PNF Compatibility Fix, and 500 Mbps Validation

**Date:** 2026/07/31

## Discovery Goal

Create a defensible visual explanation of the single-UE scheduler experiment, eliminate the PNF crash that blocked attachment, and determine whether the repaired E2E path can sustain a 500 Mbps offered load.

## Result at a Glance

| Question | Result |
|---|---|
| Can the experiment be visualized like the professor's scheduler example? | Yes, at the real scale of one UE. The playback uses measured grants, throughput, and PDU power. |
| Why did PNF crash when the UE attempted to attach? | A valid PUSCH job arrived without a non-negative MU-MIMO group index, triggering `AssertFatal(g >= 0)`. |
| Was the scheduler VNF image the cause? | No direct evidence supports that. The abort occurred in the worker-mounted PNF PHY code after PRACH. |
| What repaired it? | A backward-compatible fallback that assigns only legacy ungrouped PUSCH jobs to unused local groups. |
| Did E2E work after the repair? | Yes. A 200 Mbps, 60-second smoke test completed cleanly. |
| Did 500 Mbps work? | It sustained 500 Mbps offered traffic for 1,115 seconds before the UE client was interrupted. |
| Is the 500 Mbps result a full pass? | No. It is a 92.9%-complete usable window, not a clean 20-minute completion. |

## 1. Scheduler Playback Dashboard

### Purpose

The professor's example explains how a scheduler shares one cell among many users. The WINLAB experiment currently has one physical Samsung UE, so the useful question is different:

> How does one UE's allocation, delivered throughput, and RU power change when the scheduler policy or offered load changes?

The offline playback is located at:

```text
assets/winlab_scheduler_playback/index.html
```

Its dataset builder is:

```text
scripts/build_winlab_scheduler_playback.py
```

The current playback uses the July 30 `oai_prb_cap_27` artifact and includes:

- the connected UE and RNTI;
- current downlink grant size, MCS, TBS, HARQ process, layers, and symbols;
- a time-frequency-style allocation history;
- measured UE throughput;
- measured Raritan PDU Outlet 2 active power;
- run completion and scheduler-cap validation.

### Evidence boundary

The VNF pod log is a rotated log tail, not a scheduler trace beginning at the iPerf start timestamp. It contains a dense scheduler capture followed by sparse control traffic. The dashboard therefore:

1. replays only the first contiguous high-density scheduler interval;
2. shows the complete iPerf and PDU timeline separately;
3. does not claim exact timestamp alignment between scheduler grants and the lower chart.

This separation fixed the misleading early dashboard view that appeared to show mostly 5-PRB grants. In the valid dense traffic capture, 13,725 of 13,726 grants used 27 PRBs and one used 5 PRBs.

## 2. PNF Attach Crash

### Symptom

PNF and VNF could start, synchronize, and advertise the cell. When the UE initiated random access, PNF aborted with:

```text
Assertion (g >= 0) failed!
In group_pusch_jobs() .../phy_procedures_nr_gNB.c
Ungrouped ULSCH_id 0
```

The failure followed PRACH, so it was not an RU visibility, AMF registration, or iPerf problem. It occurred while the PNF PHY converted an accepted PUSCH job into its execution groups.

### Runtime architecture that matters

The PNF Helm chart does not obtain its executable from the VNF scheduler image. It directly runs the worker-mounted binary:

```text
/home/oai72_su/oai_mp_f_ming/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
```

The corresponding source is under:

```text
/home/oai72_su/oai_mp_f_ming/openairinterface5g
```

This means the experiment has two independently changing parts:

| Part | Source |
|---|---|
| VNF scheduler behavior | Quay image selected by the VNF Helm chart |
| PNF PHY/fronthaul behavior | Worker-mounted executable and libraries on Lavoisier |

Replacing only one executable with an older copy was unsafe because the surrounding shared libraries and nFAPI expectations were not from the same build lineage.

## 3. Compatibility Repair

The patch modifies `group_pusch_jobs()` in:

```text
openair1/SCHED_NR/phy_procedures_nr_gNB.c
```

Its behavior is:

1. Scan all PUSCH jobs and reserve every valid existing `mu_group_idx`.
2. Preserve those existing group assignments exactly.
3. For a job with `mu_group_idx < 0`, find the next unused group.
4. Assign the legacy job to that fallback group.
5. Retain bounds checks for invalid or exhausted group indices.

Conceptually:

```c
if (g < 0) {
  while (fallback_group is already reserved)
    fallback_group++;
  assert(a fallback group is available);
  g = fallback_group++;
}
```

This is a compatibility fallback, not a scheduler policy change. It does not alter PRB allocation, proportional fairness, HARQ decisions, or the 27-PRB VNF cap.

The repaired `nr-softmodem` was rebuilt from the active worker source. After deployment, the UE completed PRACH, remained in sync, and no new `Ungrouped ULSCH`, PRACH-segmentation, or fatal PNF assertion appeared.

## 4. Post-Fix Smoke Test

| Field | Value |
|---|---|
| Job | `ab0ad307-3b9c-4697-abbc-cd2b69c4483e` |
| Artifact directory | `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260731-061156` |
| UE address | `10.45.0.3` |
| Offered load | 200 Mbps downlink |
| Requested duration | 60 seconds |
| Observed duration | 60.001 seconds |
| UE samples | 60 |
| Transfer | 1.40 GBytes |
| Sender-reported packet loss | 0% |
| Final status | Succeeded |

This validates all required layers for proceeding:

1. pods Ready;
2. cell and UE attach;
3. user-plane path to `10.45.0.1:5201`;
4. sustained iPerf traffic;
5. artifact collection;
6. no additional PNF/VNF restart during the test.

## 5. 500 Mbps, 20-Minute Run

| Field | Value |
|---|---|
| Job | `f3b50b65-34ae-4ad8-8a74-23fadc1ee7ef` |
| Artifact directory | `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260731-062515` |
| Offered load | 500 Mbps downlink |
| Requested duration | 1,200 seconds |
| Positive UE samples | 1,115 |
| Positive-traffic duration | 1,115.001 seconds |
| Completion | 92.9% |
| Server transfer | 64.9 GBytes |
| Final status | Failed validation |
| Failure reason | `UE iPerf error: interrupt - the client has terminated` |

The per-second server output remained at the requested 500 Mbps through the positive-traffic interval. The server's final 432 Mbps average includes a later zero-traffic tail and must not be interpreted as the average during the valid 1,115-second window.

The current 80% rule correctly distinguishes two conclusions:

- **Measurement usability:** passed; 92.9% is a substantial high-load window.
- **Full-run stability:** failed; the UE client did not complete the requested 1,200 seconds.

This result should be retained for diagnosis and preliminary analysis, but a clean repeat is preferable for the final same-day scheduler/power comparison.

## 6. What We Are Testing Now

The current experiment is no longer just "does the UE attach?" The measurement question is:

> Under the same radio configuration and offered load, how do scheduler allocation limits change delivered throughput, RU active power, and energy per delivered bit?

The immediate comparison matrix should hold the physical environment constant and vary scheduler allocation:

| Condition | Purpose |
|---|---|
| Baseline/273-PRB behavior | Control condition |
| 27-PRB cap | Validated strong restriction |
| 54-PRB cap | Intermediate allocation point |
| 106-PRB cap | Higher intermediate allocation point |

Using 500 Mbps makes the intermediate caps more informative than another low-load run because it creates enough buffered demand for allocation limits to become active. Each condition should use the same UE, RU configuration, offered load, duration, PDU outlet, and acceptance criteria.

## 7. Next Improvements

1. Add a unique run-start marker to the scheduler log or write scheduler telemetry to a dedicated timestamped file.
2. Repeat 500 Mbps until a clean 100%-duration result is obtained.
3. Export InfluxDB data for the exact positive-traffic window and run the power merge.
4. Perform same-day baseline, 27-, 54-, and 106-PRB runs.
5. Compare mean throughput, mean power, energy per delivered bit, grant-size distribution, MCS, TBS, and retransmission rate.
6. Keep the PNF compatibility patch separate from VNF scheduler commits so infrastructure and policy changes remain independently auditable.

## Key Lesson

A useful scheduler experiment requires three independent validations:

1. **Infrastructure compatibility:** PNF, VNF, nFAPI, xRAN, and worker libraries remain alive.
2. **Policy evidence:** scheduler logs prove the intended PRB behavior.
3. **Measurement completeness:** iPerf and PDU data cover the required interval.

Today established the first two and produced a strong but incomplete 500 Mbps measurement window. The next reserved session should focus on clean completion and controlled same-day comparisons rather than further infrastructure changes.

