# 2026-07-23 WINLAB OAI NR Scheduler Code Discovery

## Purpose

Establish the real modification surface for a scheduler experiment before changing
OAI behavior. This note supersedes the parts of older scheduler notes that assume a
single monolithic `pf_dl()` implementation.

The evidence comes from three sources:

1. The HPE checkout used by the build/deployment workflow.
2. The scheduler-log image branch already validated by a 300-second, 200 Mbps E2E
   run.
3. The professor-provided telemetry findings and `External/Liu` thesis.

## Current Code Baseline

HPE source checkout:

```text
/home/hpe/openairinterface5g
branch: nfapi-DelayManagement-BMW
commit: c87d3827f2 chore(config): add BMW Lab gNB/PNF/VNF split run configs
```

The checkout has unrelated local changes under `nfapi/open-nFAPI/vnf/src/` and
local helper files. Do not reset, rebase, or build from this dirty checkout without
first preserving those changes.

The validated logging-only source branch is:

```text
bmw/david/oai-scheduler-logonly-20260721
commit: 31c7aa0477586643a7acdae9c316c61c1ba0cdbf
image: bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-scheduler-logonly-20260721
```

Relative to `bmw/nfapi-DelayManagement-BMW`, that branch changes only
`openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`, adding 17 logging lines.
It does not change allocation behavior.

## Validated Instrumentation

The logging hook is placed immediately before `post_process_dlsch()` after a
candidate has been accepted and the final PDSCH fields are known:

```text
[WINLAB_SCHED_LOG] mode=oai_logging_only
frame slot rnti is_retx rbStart rbSize mcs tbs layers harq_pid beam tda sym
```

The clean deployment completed a 300-second DL run at 200 Mbps with zero packet
loss, 300 UE samples, and VNF restart count `0`. Its VNF artifact log contained
live scheduler records, including new transmissions and retransmissions. This proves
the image, deployment path, scheduler hook, UE traffic path, and artifact collection
work together.

## Actual NR DL Scheduler Pipeline

The active implementation is a pipeline, not a hard-coded single `pf_dl()`
function:

```text
nr_dlsch_preprocessor()                         gNB_scheduler_dlsch.c
  -> nr_dl_schedule()
       1. collect_dl_candidates()
       2. dl_ri_pmi_select()
       3. dl_beam_select()
       4. dl_tda_select()
       5. dl_mcs_select()
       6. dl_rb_alloc()       <- policy seam
       7. post_process_dlsch()
            -> MAC PDU / FAPI dispatch
```

`main.c` wires the default callbacks at MAC initialization:

```text
dl_ri_pmi_select = nr_dl_ri_pmi_select_default
dl_mcs_select    = nr_dl_mcs_select_default
dl_beam_select   = nr_dl_beam_select_default
dl_tda_select    = nr_dl_tda_select_default
dl_rb_alloc      = nr_dl_proportional_fair
dl_lcid_alloc    = nr_dl_lcid_alloc_default
```

The implementation of the default DL RB policy is in:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch_default_policies.c
```

This is the correct file for an allocation-policy experiment. The orchestration file
`gNB_scheduler_dlsch.c` should remain unchanged except for experiment logging or a
deliberate selector that has been designed and tested.

## Candidate Contract and Existing Control Inputs

`nr_dl_candidate_t` in `nr_mac_gNB.h` already exposes the inputs a policy needs:

```text
RNTI, retransmission state, pending bytes per LCID,
EWMA throughput, BLER/MCS state, BWP range,
5QI, logical-channel priority, NSSAI,
CQI, RI/PMI, beam RSRP/SINR, TDA and symbol bitmap.
```

`nr_dl_sched_params_t` provides the mutable per-beam VRB maps, current frame/slot,
and the `max_num_ue` admission limit. The policy must set `rbStart`, `rbSize`, and
MCS on accepted candidates, call `commit_alloc()`, and mark `scheduled` through the
`COMMIT_ALLOC` macro. `commit_alloc()` validates CCE/PUCCH availability and reserves
both PDCCH and data VRBs. Bypassing it would create invalid grants.

## Default Behavior

`nr_dl_proportional_fair()` has three ordered phases:

1. HARQ retransmissions first, retaining their required RB allocation.
2. Control-only UEs, for timing advance or beam-switch MAC CEs, with the minimum
   five RB allocation.
3. New-data UEs, ordered by PF weight and allocated from the largest contiguous free
   VRB block.

PF priority is `estimated one-RB TBS / EWMA throughput`; retransmissions have
infinite priority. The EWMA is updated per candidate with smoothing factor `0.01`.
New-data allocation uses `find_largest_free_block()` followed by `nr_find_nb_rb()`
to find the smallest contiguous grant satisfying queued bytes. The current PDSCH path
uses resource-allocation type 1, so each grant must remain contiguous.

## Relationship to the Liu Thesis

`External/Liu` is an eight-page-extracted 2020 LTE thesis describing an inter-slice
manager, per-slice intra-schedulers, then final DCI/FAPI-style dispatch. Its useful
design concepts are still relevant:

- fixed versus dynamic spectrum isolation;
- inter-slice resource budgets followed by intra-slice UE scheduling;
- unused-resource sharing using priority, proportional, or round-robin rules;
- preserving a final dispatch stage after policy decisions.

It is not a direct implementation recipe. It targets LTE, assumes resource-allocation
type 0/RBG bitmap allocation, and predates the deployed NR code. The live OAI NR
path only supports contiguous type-1 PDSCH allocation, so non-contiguous RBG masks
from the thesis cannot be copied directly.

The closest modern mapping is:

```text
Liu inter-slice manager  -> policy computes per-NSSAI or per-5QI RB budget
Liu intra-slice scheduler -> orders candidates inside each budget
Liu final scheduler       -> existing post_process_dlsch()/FAPI path
```

## Relationship to the Telemetry Findings

The professor's `finding.md` shows that, in a separate stable TM500 2x2 setup,
the major power steps were gNB startup and UE attachment, while 50-100 Mbps traffic
added comparatively little power. It also shows scheduler-visible CPU occupancy is
not a faithful energy proxy.

For WINLAB, this changes the experimental standard:

1. Do not infer an energy effect from CPU utilization alone.
2. Keep radio configuration, antenna mode, pinning, log level, UE state, and offered
   load fixed across compared scheduler variants.
3. Compare synchronized PDU active-power windows with actual allocation records and
   delivered iPerf throughput.
4. Treat a null power delta as a valid result, especially with one attached UE and
   moderate offered load.

## First Meaningful Policy Experiment

The current Samsung experiment has one active UE. Therefore forcing
`max_num_ue = 1` is not a meaningful test: it reproduces the existing admission
condition.

The first behavior-changing branch should instead add an explicit, named cap to
**phase 3 only** of `nr_dl_proportional_fair()`:

```text
max_rb_size = min(largest_free_block, configured_cap)
```

Use an initial cap that is substantially below the 100 MHz carrier width, but leave:

- retransmissions unchanged;
- control-only grants unchanged;
- CCE/PUCCH validation and `COMMIT_ALLOC` unchanged;
- TDA, beam, RI/PMI, MCS, LCID, and FAPI dispatch unchanged.

The cap must be applied before `nr_find_nb_rb()` in the new-data phase. Add a new
mode tag, for example `oai_prb_cap_27`, to the existing scheduler log. This makes the
behavioral variant auditable in the run artifact.

## Required Experiment Gates

Before calling a scheduler variant valid:

1. Establish an `oai_original` baseline under the same RU configuration.
2. Run a short 300-second E2E proof for the candidate image.
3. Verify scheduler logs show the intended RB cap and contain traffic-era records.
4. Verify 10.45.x.x attachment, nonzero UE iPerf samples, stable VNF/PNF pods, and
   zero unexpected VNF restarts.
5. Export the matching Outlet 2 `active_power` window and merge it with the run
   artifact.
6. Repeat each baseline/variant condition before making an energy claim.

## Next Implementation Decision

Implement a small policy function or a carefully bounded variant of
`nr_dl_proportional_fair()` in `gNB_scheduler_dlsch_default_policies.c`. Do not edit
the old `max_rbSize` location in `gNB_scheduler_dlsch.c`; that is no longer the
default allocation point on the deployed branch.

Before coding, choose the experiment definition:

```text
A. Single-UE allocation-shaping: baseline versus fixed PRB cap.
B. Multi-UE fairness/slicing: NSSAI/5QI budget and per-slice ordering.
```

Option A is the correct next experiment because it changes measurable allocation
behavior with the currently available single Samsung UE. Option B is the research
architecture implied by the Liu thesis, but needs at least two controllable UEs or
traffic classes to validate fairness and isolation.
