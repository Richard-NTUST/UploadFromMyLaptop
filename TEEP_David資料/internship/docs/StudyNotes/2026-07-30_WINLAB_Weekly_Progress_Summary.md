# WINLAB Weekly Progress Summary

**Presentation date:** 2026-07-30  
**Coverage:** 2026-07-23 to 2026-07-29  
**Theme:** From unstable shared-lab recovery to a controlled OAI scheduler experiment.

## Presentation Summary

The work has moved beyond basic E2E automation and into controlled OAI NR
scheduler modification.

The main achievements are:

1. Re-established repeatable 200 Mbps O-Cloud E2E traffic through the
   bare-metal rApp on port `9090`.
2. Documented the complete Lavoisier recovery path after BMC reboot, including
   fronthaul setup and kubelet recovery.
3. Separated the VNF scheduler image from the host-mounted PNF OAI/FHI runtime,
   which prevents lower-layer crashes from being blamed on scheduler code.
4. Restored a matched PNF runtime bundle that starts xRAN without the prior ABI
   crash or PRACH segmentation assertion.
5. Built a logging-only scheduler image and proved it works end to end.
6. Built the first behavior-changing scheduler image, which caps phase-3 new
   downlink RLC-data grants at 27 PRBs.
7. Read the exact source lineage and defined the test gates required before the
   larger scheduler redesign.

The remaining immediate gate is a clean validation of the 27-PRB image during
an exclusive UE window. The normal `latest` baseline has already been exercised
repeatedly at 5, 10, and 20 minutes, so another generic baseline run is not the
main task.

A critical architectural lesson is that VNF and PNF provenance are different:

- The **VNF** runs the Jenkins-built Quay image and contains the NR MAC scheduler
  change.
- The **PNF** starts a worker-mounted `nr-softmodem` and worker-mounted
  FHI/xRAN/DPDK libraries from Lavoisier.

A healthy VNF image cannot compensate for an incompatible PNF host runtime.

## Progress Timeline

### Thursday, July 23: baseline recovery and first scheduler experiment

- Restored HPE connectivity after Docker removal and reboot.
- Restored the intended Pegatron configuration after detecting a mismatch
  between the VNF target cell and the cell visible to the UE.
- Completed a five-minute bare-metal E2E run:

```text
Job: 4a7915a3-9378-4afd-ab3e-28467736318b
Offered load: 200 Mbps
Duration: 300 seconds
Transfer: 6.99 GBytes
Reported loss: 0%
UE samples: 300
```

- Located the active downlink proportional-fair scheduler policy.
- Created the 27-PRB branch `david/oai-prb-cap-27-20260723`.
- Jenkins build #89 successfully published commit `d7c850098a`.
- The first custom-image E2E attempt was blocked by a PNF host-library failure,
  not by VNF scheduling logic.

### Friday, July 24: failure-domain separation

- Found that Lavoisier's stopped kubelet caused Pending, Terminating, and
  `UnexpectedAdmissionError` pod symptoms.
- Restored the worker and confirmed fresh PNF/VNF pods could become Ready.
- Verified the intended VNF cell configuration:

```text
PLMN: 001-01
Band: n78
PCI: 0
SSB ARFCN: 649920
```

- Confirmed that an empty Nemo NR Cell Table and missing UE data interface are
  radio-discovery conditions below the rApp and scheduler image.
- Established the rule: do not invoke E2E until node, pods, radio cell, and UE
  bearer preflight checks pass.

### Monday, July 27: repeatable worker and fronthaul recovery

- Completed another valid five-minute, 200 Mbps baseline run:

```text
Job: 4b44c8e9-a03a-4ed2-b6ea-b67d7397ff83
Duration: 300.06 seconds
Transfer: 6.99 GBytes
Reported loss: 0%
```

- Identified the mandatory post-BMC-reboot Lavoisier preparation:

```bash
/home/oai72_su/Script/setup_network.sh enp67s0f1
sudo systemctl start kubelet
```

- Documented that the network script recreates SR-IOV VFs, restores RU-facing
  VLAN/IP state, binds VFIO/DPDK devices, and must run while PNF is stopped.
- Recorded Lavoisier BMC access at `https://192.168.10.92/`.
- Clarified that `rrr` and `pegam` are conditional RU recovery actions after
  external use, not per-run commands.

### Tuesday, July 28: matched PNF runtime rollback

- Traced PNF startup to host-mounted OAI/FHI artifacts rather than only the pod
  image.
- Separated two lower-layer failures:
  - a softmodem/FHI ABI mismatch and `SIGSEGV`;
  - `PRACH segmentation is not supported` after a partial rebuild.
- Restored the preserved matched runtime:

```text
/home/oai72_su/oai_mp_f_ming/experiments/k-pristine-20260724
```

- PNF reached P5/P7 setup and `XRAN Start! RU0 [1]` without the prior crash or
  assertion.
- Deferred E2E because the shared UE/environment was handed to another user.

### Wednesday, July 29: exact scheduler source audit

Verified commit lineage:

```text
5bbf48af2d  baseline parent
    |
31c7aa0477  logging-only scheduler instrumentation
    |
d7c850098a  27-PRB phase-3 cap
```

Across the two custom commits, only these files changed:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch_default_policies.c
```

No RACH, PRACH, RRC, nFAPI, NGAP, AMF, PNF, or xRAN source was directly
modified.

The foreign NR cells seen during previous troubleshooting were explained by
physical test conditions: the Samsung UE had temporarily been taken outside
its RF chamber. Under normal chamber placement, unrelated cells from other
floors are isolated from this UE.

## Scheduler Modification Findings

The active downlink pipeline is:

```text
nr_dlsch_preprocessor()
  -> collect candidates
  -> select RI/PMI, beam, TDA, and MCS
  -> nr_dl_proportional_fair()
  -> post_process_dlsch()
```

The default proportional-fair allocation has three phases:

| Phase | Purpose | Effect of current 27-PRB patch |
|---|---|---|
| 1 | HARQ retransmissions using the required RB count | Unchanged |
| 2 | Timing advance or beam-switch MAC-control-only grants | Unchanged; retains five-RB minimum |
| 3 | New downlink RLC data | Maximum available block capped at 27 PRBs |

The experiment performs:

```c
max_rbSize = min(max_rbSize, 27);
```

This is a maximum, not a fixed allocation. `nr_find_nb_rb()` may choose fewer
PRBs for a small payload.

Allocation still passes through `COMMIT_ALLOC()`, preserving CCE/PUCCH
validation and VRB-map accounting.

### Important scope detail

`update_dlsch_buffer()` aggregates every active RLC logical channel. Therefore,
the cap applies to application DRB data and can also constrain downlink SRB/RRC
payload grants after random access. It does not change RACH or RRC code, but a
short attachment smoke test remains necessary.

## Proven Results

| Result | Status | Evidence |
|---|---|---|
| Bare-metal rApp can produce valid O-Cloud traffic | Proven | Multiple successful baseline runs, including July 23 and July 27 five-minute runs |
| Logging-only custom VNF works end to end | Proven | Artifact `e2e-ocloud-20260723-053441`, 300 UE samples and 13,092 scheduler records |
| Jenkins/Quay custom-image workflow works | Proven | Jenkins #89 built commit `d7c850098a` with a unique tag |
| Lavoisier post-reboot recovery is understood | Proven | Fronthaul setup plus kubelet sequence documented and used |
| Matched PNF host runtime can start xRAN | Proven | July 24 preserved OAI/FHI bundle starts without prior crash/assertion |
| 27-PRB scheduler behavior works on live radio | Pending | Requires exclusive UE window and valid artifacts |
| Power benefit from scheduler change | Not yet measured | Requires valid repeated iso-throughput runs and InfluxDB merge |

## Current Test Gate

Before larger scheduler work, the 27-PRB image should pass:

1. **One-minute attach/traffic smoke**
   - intended cell visible;
   - UE receives `10.45.x.x`;
   - iPerf connection observed;
   - no pod restart or fatal lower-layer log.
2. **Five-minute scheduler validation**
   - approximately 300 throughput samples;
   - `mode=oai_prb_cap_27` telemetry exists;
   - every new transmission has `rbSize <= 27`;
   - retransmissions remain uncapped and valid.
3. **Twenty-minute stability run**
   - no UE detach or pod restart;
   - sustained achieved throughput is reported separately from offered load;
   - complete artifacts are retained.

If these gates pass, another generic `latest` run is unnecessary. Development
can proceed to the larger scheduler changes, preferably within one binary using
runtime-selectable modes.

## Next Scheduler Phase

The larger change should be implemented incrementally rather than as one opaque
patch:

1. Add runtime scheduler modes with `baseline` as the default.
2. Reimplement the 27-PRB behavior as `prb_cap_spread`.
3. Decide whether SRB logical channels should be exempt from the cap.
4. Add controlled allocation telemetry instead of unconditional per-grant INFO
   logging.
5. Extend `nrdlbench` to assert cap, HARQ, control-grant, overlap, and timing
   behavior.
6. Add `wide_burst`, for example one active new-data slot in a ten-slot cycle.
7. Compare `baseline`, `prb_cap_spread`, and `wide_burst` using the same image
   digest and configuration-only mode changes.
8. Run offered-load sweeps before claiming an energy benefit:

```text
25, 50, 100, 150, 200 Mbps
```

The intended comparison is approximately the same delivered work with a
different time/frequency allocation pattern, such as the conceptual
`273 PRBs x 1 slot` versus `27 PRBs x 10 slots` comparison. The implementation
must measure actual PRBs, MCS, layers, HARQ, throughput, and power rather than
assuming those patterns are equivalent.

## Presentation Takeaways

1. **The E2E measurement stack is working.** Traffic, pod logs, scheduler logs,
   and PDU data can be preserved and merged.
2. **The recovery process is now explicit.** Node, fronthaul, PNF runtime, RU,
   UE, and rApp failures have distinct checks and remedies.
3. **The first custom scheduler image is proven.** Logging-only instrumentation
   completed a valid five-minute traffic run.
4. **The first behavior-changing image is ready for controlled validation.** Its
   source delta is small and understood, but it has not yet passed a clean live
   27-PRB run.
5. **The next research step is scheduler mode design.** After the 27-PRB gate,
   development moves to runtime-selectable spread and burst scheduling followed
   by repeated throughput-power experiments.

## Immediate Next Actions

| Priority | Action | Success condition |
|---:|---|---|
| 1 | Reserve exclusive Samsung UE/RU access | No external user or conflicting radio activity |
| 2 | Preflight Lavoisier, PNF/VNF, RU, and UE | Node Ready, pods stable, intended cell visible, UE attached |
| 3 | Validate the 27-PRB image | One-, five-, and twenty-minute gates pass with allocation evidence |
| 4 | Implement runtime scheduler modes | Same binary supports baseline and experiment modes |
| 5 | Run repeated power experiments | Throughput-matched conditions produce merged power summaries |

## Reference Notes

- [2026-07-23 Daily Note](../DailyNotes/2026-07-23_Daily-Note.md)
- [2026-07-24 Daily Note](../DailyNotes/2026-07-24_Daily-Note.md)
- [2026-07-27 Daily Note](../DailyNotes/2026-07-27_Daily-Note.md)
- [2026-07-28 Daily Note](../DailyNotes/2026-07-28_Daily-Note.md)
- [2026-07-29 Daily Note](../DailyNotes/2026-07-29_Daily-Note.md)
- [Lavoisier Post-Reboot Fronthaul Recovery](2026-07-27_Lavoisier_PostReboot_Fronthaul_Recovery_and_Stable_E2E.md)
- [PNF Runtime Bundle Rollback and PRACH Investigation](2026-07-28_PNF_Runtime_Bundle_Rollback_and_PRACH_Investigation.md)
- [OAI Scheduler Deep Dive and QC Plan](2026-07-29_OAI_Scheduler_Deep_Dive_Failure_Attribution_and_QC_Plan.md)
