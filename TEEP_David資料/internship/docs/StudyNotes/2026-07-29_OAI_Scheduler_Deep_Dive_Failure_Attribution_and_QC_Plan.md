# OAI Scheduler Deep Dive: Failure Attribution and QC Plan

Date: 2026-07-29

## Purpose

This note answers four practical questions:

1. Did our custom OAI image cause the earlier UE attachment failures?
2. Which OAI code actually controls downlink PRB allocation in the BMW nFAPI fork?
3. What should we change to reproduce the WINLAB scheduler experiments?
4. How do we prove a change works without breaking attachment, HARQ, nFAPI, or the radio path?

## Short Answer

- The logging-only custom VNF image is proven to work end to end.
- The 27-PRB-cap image was never tested in a clean, stable radio environment, so it is unvalidated, not proven defective.
- The recurring attachment failures also occurred with the baseline `latest` image and coincided with lower-layer failures such as:
  - stopped or unstable Lavoisier `kubelet`;
  - missing post-reboot fronthaul setup;
  - changed or moved Pegatron RU state;
  - PNF host runtime ABI mismatch;
  - xRAN timing faults;
  - PRACH segmentation assertions;
  - another gNB broadcasting and competing for the same UE while the phone had been taken outside its normal RF chamber.
- The first PRB-cap patch changed only the new-data allocation phase of the DL proportional-fair policy. It did not modify RACH, RRC, nFAPI transport, AMF registration, or UE attachment code.
- However, OAI aggregates buffered bytes from every active RLC logical channel before phase 3. The cap can therefore constrain downlink SRB/RRC payload grants after random access, even though it does not change the RACH or RRC implementation itself.
- Future experiments should use one binary with runtime-selectable scheduler modes. This makes baseline and experimental runs differ only by configuration.

## Evidence from the Previous Custom Image

### Logging-only image

Branch:

```text
david/oai-scheduler-logonly-20260721
```

Commit:

```text
31c7aa0477586643a7acdae9c316c61c1ba0cdbf
```

Image:

```text
bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-scheduler-logonly-20260721
```

The image added one scheduler allocation log statement to:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c
```

It produced a successful five-minute E2E artifact:

```text
/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260723-053441
```

Verified results:

| Evidence | Result |
|---|---:|
| E2E return code | 0 |
| UE iPerf samples | 300 |
| Throughput CSV rows including header | 301 |
| Scheduler log records | 13,092 |
| New transmissions | 12,647 |
| Retransmissions | 445 |
| Observed RB size | 5 to 243 |
| Traffic | approximately 200 Mbps for the full run |

This directly disproves the claim that all custom images fail attachment or traffic.

### 27-PRB-cap image

Branch:

```text
david/oai-prb-cap-27-20260723
```

Commit:

```text
d7c850098ac96f89a04695e6342ceca8ec757555
```

This commit is based on the logging-only commit. Its behavioral change was:

```c
const int max_new_data_rbSize = 27;
...
max_rbSize = min(max_rbSize, max_new_data_rbSize);
```

The cap was inserted only in phase 3, which schedules new DL RLC data. It did not directly alter:

- HARQ retransmission allocation;
- control-only grants;
- RACH or PRACH;
- RRC implementation;
- nFAPI messages;
- NGAP or AMF registration;
- PNF xRAN timing.

There is one important scope detail. `update_dlsch_buffer()` loops over all
activated logical channels and adds every non-empty RLC buffer to
`num_total_bytes`. `collect_dl_candidates()` copies that total into
`candidate.pending_bytes`, and the phase-3 policy applies the 27-PRB maximum
to that candidate. The default LCID allocation policy then copies all
`pending_bytes_per_lcid` values into the transport block allocation.

Therefore, the cap includes both user-plane DRB data and downlink signaling
carried through RLC, such as SRB/RRC payloads. It cannot explain a missing
cell, failed PRACH reception, xRAN crash, or pre-RRC attachment failure.
Nevertheless, a short attachment smoke test remains necessary because it can
change the resources available to post-RACH downlink signaling.

No collected artifact contains:

```text
mode=oai_prb_cap_27
```

Therefore, the 27-PRB image never reached a valid traffic experiment. Its result is "not validated", not "failed because of scheduler code".

## Why the Earlier Comparison Was Not Clean

The known working `latest` image and the custom branches did not use exactly the same source base.

- A known working baseline image came from commit `9522317237`.
- The custom branches were based on commit `5bbf48af2d`.
- These commits diverged from a common ancestor instead of having a direct baseline-to-experiment relationship.

The difference included nFAPI timing-related code. It did not prove that nFAPI caused the failure, but it invalidated a strict one-variable A/B comparison.

Rule for the next build:

> Freeze one exact known-good source commit, build it as baseline, and create all experiment commits directly on top of it.

Use immutable image tags and record the image digest. Do not compare against a moving `latest` tag.

## VNF Image Versus PNF Runtime

The lab has two distinct code paths:

### VNF

The VNF executes OAI code from the Jenkins-built container image. The DL MAC scheduler runs here.

### PNF

The PNF chart mounts host directories from Lavoisier and starts:

```text
<host OAI build root>/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
```

It also loads host FHI/xRAN and DPDK libraries.

This means a VNF image can be correct while the PNF crashes because its host binary and host libraries do not match.

The known-good PNF runtime rollback is:

```text
/home/oai72_su/oai_mp_f_ming/experiments/k-pristine-20260724
```

with FHI libraries under:

```text
/home/oai72_su/oai_mp_f_ming/experiments/k-pristine-20260724/xran-package-shim/fhi_lib/lib/build
```

Examples of PNF-side failures that cannot be attributed to the DL scheduler image:

- unresolved `MLogSetTaskCoreMap`;
- `SIGSEGV` in host `nr-softmodem`;
- `xran_timingsource_poll_next_tick too long`;
- nFAPI request timing hundreds of milliseconds outside the valid window;
- `PRACH segmentation is not supported`;
- RU reachability or M-plane configuration failure.

## Actual OAI DL Scheduler Pipeline

The deployed BMW fork does not perform all scheduling inside one old `pf_dl()` function.

The active path is:

```text
nr_dlsch_preprocessor()
  -> collect UE candidates
  -> select RI/PMI
  -> select beam
  -> select TDA
  -> select MCS
  -> mac->dl_rb_alloc()
  -> post_process_dlsch()
```

The default callback is wired in:

```text
openair2/LAYER2/NR_MAC_gNB/main.c
```

as:

```c
RC.nrmac[i]->dl_rb_alloc = nr_dl_proportional_fair;
```

The active PRB policy is:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch_default_policies.c
```

The default policy has three phases:

1. HARQ retransmissions receive highest priority and reuse their required RB count.
2. UEs with only control work receive the minimum grant.
3. New-data UEs receive PRBs according to PF priority and available contiguous RBs.

The scheduler must continue to allocate through:

```c
COMMIT_ALLOC(...)
```

That path performs the existing CCE/PUCCH checks, records the allocation, and reserves the VRB map. A new policy must not directly edit the VRB map or bypass this macro.

## Correct Interpretation of the Experiment Modes

The earlier notes used "time-domain" and "frequency-domain" loosely. Those names can hide what the scheduler actually does.

Use observable policy names instead:

### `baseline`

Unmodified OAI proportional-fair scheduling.

### `prb_cap_spread`

Limit each new-data grant to at most a configured number of PRBs, such as 27.

Expected behavior:

- traffic is spread across more slots;
- each new-data grant uses no more than the cap;
- low-buffer grants may use fewer than the cap;
- retransmissions may exceed the cap because they preserve the original HARQ allocation.

This mode does not guarantee exactly 27 PRBs for exactly ten slots.

### `wide_burst`

Permit new-data scheduling only during configured active slots in a repeating cycle. During active slots, the scheduler may use the normal wide allocation.

Example:

```text
cycle_slots = 10
active_slots = 1
```

Expected behavior:

- buffered new data is concentrated into the active slot;
- inactive slots do not schedule new application data;
- HARQ retransmissions and necessary control traffic remain allowed;
- the offered load must be low enough for the active slots to drain the accumulated buffer.

This is the mode that can create observable idle-slot opportunities. It still does not prove that the RU enters a lower-power state. That must be measured at the PDU.

### Multi-UE TDM/FDM

True UE multiplexing comparisons require at least two UEs. A single Samsung UE cannot prove whether multiple UEs are separated in time or frequency.

## Exact Code Changes

### 1. Add runtime scheduler configuration

Add parameter names and defaults in:

```text
openair2/GNB_APP/MACRLC_nr_paramdef.h
```

Recommended parameters:

```text
dl_scheduler_mode
dl_scheduler_prb_cap
dl_scheduler_cycle_slots
dl_scheduler_active_slots
dl_scheduler_log_period_slots
```

Recommended defaults:

```text
dl_scheduler_mode = "baseline"
dl_scheduler_prb_cap = 27
dl_scheduler_cycle_slots = 10
dl_scheduler_active_slots = 1
dl_scheduler_log_period_slots = 100
```

Add checks:

- mode is one of `baseline`, `prb_cap_spread`, or `wide_burst`;
- PRB cap is at least the scheduler minimum grant and no larger than the BWP;
- cycle is at least one slot;
- active slots are between one and the cycle length;
- log period is non-negative.

### 2. Store parsed configuration in the MAC instance

Parse the new `MACRLCs` parameters in:

```text
openair2/GNB_APP/gnb_config.c
```

Store them in a typed configuration structure owned by:

```text
gNB_MAC_INST
```

The structure should use an enum for the mode, not repeated string comparisons in the real-time scheduling path.

Suggested shape:

```c
typedef enum {
  NR_DL_SCHED_BASELINE,
  NR_DL_SCHED_PRB_CAP_SPREAD,
  NR_DL_SCHED_WIDE_BURST,
} nr_dl_scheduler_mode_t;

typedef struct {
  nr_dl_scheduler_mode_t mode;
  uint16_t prb_cap;
  uint16_t cycle_slots;
  uint16_t active_slots;
  uint16_t log_period_slots;
} nr_dl_scheduler_experiment_t;
```

The parser should log one startup summary showing the final validated values.

### 3. Apply behavior only to phase-3 new data

Modify:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch_default_policies.c
```

Keep phases 1 and 2 unchanged.

For `prb_cap_spread`:

```c
if (cfg->mode == NR_DL_SCHED_PRB_CAP_SPREAD)
  max_rbSize = min(max_rbSize, cfg->prb_cap);
```

For `wide_burst`, calculate the absolute slot index and skip only phase-3 new-data work outside the active part of the cycle:

```c
const uint64_t absolute_slot =
    (uint64_t)params->frame * slots_per_frame + params->slot;
const bool new_data_slot =
    absolute_slot % cfg->cycle_slots < cfg->active_slots;

if (cfg->mode == NR_DL_SCHED_WIDE_BURST && !new_data_slot)
  continue;
```

The exact source of `slots_per_frame` should use the existing numerology/frame configuration. Do not hardcode 20 slots per frame.

### 4. Replace per-grant INFO spam with controlled telemetry

The first logging patch used `LOG_I` for every grant. It is useful for discovery but can:

- increase scheduler CPU load;
- produce very large VNF logs;
- add disk and console I/O;
- contaminate the power comparison.

For development, keep detailed records behind a debug level or explicit experiment flag.

For live power runs, emit an aggregate record every configured number of slots:

```text
mode, window_start, slots, active_new_data_slots, new_tx_count,
retx_count, allocated_new_data_prbs, allocated_retx_prbs,
bytes_scheduled, max_scheduler_us
```

The final PDU run should use identical telemetry settings for baseline and experiment modes.

### 5. Expose the parameters in the VNF configuration

Add the selected values to the VNF `gnb.conf` under `MACRLCs`.

Do not rebuild the image merely to change modes. The same image digest should run:

```text
baseline
prb_cap_spread
wide_burst
```

Only the ConfigMap values should differ.

## Software-Only QC Before Jenkins

OAI already contains a useful DL scheduler harness:

```text
tests/nrdlbench/dlbench.c
```

It runs the real `nr_dlsch_preprocessor()`, the real proportional-fair policy, RLC buffers, the DL scheduler, and PHY TX processing.

Extend it to:

- accept the scheduler mode and its numeric parameters;
- use a fixed random seed;
- output allocation rows in addition to timing rows;
- support a controlled pending-buffer size;
- optionally inject BLER to exercise retransmissions.

Recommended allocation CSV:

```text
frame,slot,rnti,is_retx,rb_start,rb_size,mcs,tbs_bytes,layers,
pending_bytes,scheduler_us
```

### Required automated tests

| Test | Required result |
|---|---|
| Baseline compatibility | New binary in `baseline` mode matches the unmodified baseline for a fixed seed |
| Cap bound | Every new transmission has `rb_size <= prb_cap` |
| Cap exercised | Under a saturated buffer, at least one new transmission reaches the cap |
| Small buffer | A small pending buffer may receive fewer PRBs without failure |
| HARQ preservation | Retransmissions preserve the required RB size and are not incorrectly capped |
| Burst gate | New-data grants occur only in active cycle slots |
| Control preservation | Required control-only grants remain possible in inactive burst slots |
| VRB safety | All allocations stay within the BWP and do not overlap |
| Invalid config | Unknown modes and invalid ranges fail at startup |
| Multi-UE fairness | No active UE is permanently starved |
| Timing regression | Scheduler latency remains inside a predeclared slot budget |

The current smoke test checks mainly whether the bench exits. That is insufficient. The new tests must parse allocation output and assert behavior.

## Build and Image Reproducibility

### Baseline decision

There are two valid approaches:

1. Historical comparison:
   - rebuild the exact known-good historical commit;
   - validate it;
   - branch directly from it.
2. Current-code comparison:
   - select the current BMW branch commit;
   - build and validate it unchanged;
   - freeze that digest as the new baseline;
   - branch experiments directly from that commit.

The current-code approach is preferable for continued development because the BMW branch has moved substantially. The historical approach is useful only when reproducing an old result exactly.

### Required build record

For every image, record:

```text
Git URL
Git commit
Git branch
Jenkins build number
E2AP/KPM options
image tag
image digest
build timestamp
changed files
```

Use a unique tag such as:

```text
david-sched-modes-<short-commit>
```

Never overwrite `latest` for an experiment.

## Live-Radio Test Gates

Run the gates in order. Do not proceed to the next gate after a failure.

### Gate 0: exclusive lab ownership

- Confirm nobody else is broadcasting with the same UE/RU path.
- Confirm the Samsung UE is available.
- In Nemo, confirm the intended cell:
  - NR-ARFCN `649920`;
  - PCI `0`;
  - PLMN `001-01`.

### Gate 1: Lavoisier and fronthaul

- Node is `Ready`.
- `kubelet` is active.
- After a Lavoisier reboot, run the fronthaul setup with the PNF stopped:

```bash
/home/oai72_su/Script/setup_network.sh enp67s0f1
```

- Confirm VLANs, routes, and RU management reachability.
- Run `rrr` and `pegam` only when the RU has been moved, reset, or reconfigured for another experiment.

### Gate 2: known-good PNF runtime

- Pin the known-good PNF host binary/FHI bundle.
- Start PNF before VNF.
- Reject the run if logs show:
  - `SIGSEGV`;
  - unresolved shared-library symbols;
  - xRAN timing-source stalls;
  - P7 timing hundreds of milliseconds early/late;
  - PRACH segmentation assertion;
  - repeated pod restart.

### Gate 3: VNF control plane

- VNF reaches Running and Ready with zero restarts.
- nFAPI P5/P7 connects without repeated disconnects.
- gNB receives the AMF setup response.
- The UE completes RACH/RRC and receives a `10.45.x.x` address.

### Gate 4: one-minute smoke

Use:

```text
200 Mbps downlink, 60 seconds, preserve UE state
```

Pass only if:

- iPerf server accepts the UE connection;
- approximately 60 UE samples are collected;
- throughput is non-zero throughout the scored interval;
- both pods remain Ready with zero new restarts;
- no fatal lower-layer log appears;
- the scheduler mode in the artifact matches the requested mode.

### Gate 5: five-minute validation

Use:

```text
200 Mbps downlink, 300 seconds
```

Pass only if:

- approximately 300 throughput samples exist;
- scheduler allocation telemetry exists;
- allocation assertions for the selected mode pass;
- no UE detach occurs;
- no pod restart occurs;
- offered and achieved throughput are reported separately.

### Gate 6: measured experiment

Use the PDU outlet:

```text
PDU [ Raritan ] PX4-5256CR-C8E8A0
Outlet 2
active_power
```

Method:

- two-minute warm-up;
- at least five-minute steady-state scoring window;
- at least three repeats per condition;
- interleave or randomize baseline and experimental runs;
- use the same offered load, radio configuration, telemetry level, and PNF bundle;
- align throughput, scheduler, and PDU timestamps;
- retain the raw files and exact UTC boundaries.

Report:

- offered Mbps;
- achieved Mbps;
- mean and standard deviation of power;
- energy in joules or watt-hours;
- bits per joule or joules per bit;
- mean PRBs per new transmission;
- new-data active-slot ratio;
- retransmission count/rate;
- MCS and layer distribution;
- scheduler latency.

## Experiment Matrix

Start with one UE and a single frozen image digest:

| Mode | Suggested parameters | Purpose |
|---|---|---|
| `baseline` | none | Reproduce normal OAI PF behavior |
| `prb_cap_spread` | cap 27 | Spread new data over more slots |
| `wide_burst` | cycle 10, active 1 | Concentrate new data into fewer slots |

Run offered loads below, near, and above the sustainable capacity of the constrained policy. Suggested initial sweep:

```text
25, 50, 100, 150, 200 Mbps
```

Do not assume 200 Mbps is sustainable with a 27-PRB cap. Measure it.

For each point:

1. Verify achieved throughput.
2. Verify allocation behavior.
3. Verify retransmission rate and MCS/layers.
4. Compare PDU power only when throughput is sufficiently matched.

Primary iso-throughput criterion:

```text
experimental achieved throughput within +/-5% of baseline
```

A deviation larger than 10% is a red flag and should not be presented as an equal-work power comparison.

## Interpreting the 273 x 1 Versus 27 x 10 Calculation

The earlier TBS calculations showed that, across tested MCS and layer settings, the theoretical data volume from one 273-PRB allocation was close to ten 27-PRB allocations.

That result is useful, but it proves only approximate resource-volume equivalence.

It does not prove that:

- the live scheduler will allocate exactly 27 PRBs;
- ten consecutive slots will all be usable;
- MCS and layer count will remain constant;
- HARQ overhead will be equal;
- application throughput will be equal;
- the RU will save power.

Those claims require scheduler telemetry, throughput artifacts, and PDU measurements from the same time window.

## Failure Attribution Table

| Observation | Most likely domain |
|---|---|
| UE cannot see intended PCI/ARFCN/PLMN | RU or competing gNB |
| UE sees cell but no RACH/RRC in VNF | RU/PNF/nFAPI path |
| PNF `SIGSEGV` or unresolved symbol | host PNF binary/library mismatch |
| PRACH segmentation assertion | RU/PNF fronthaul configuration |
| nFAPI disconnect loop | PNF process exit or transport/timing failure |
| UE has `10.45.x.x` but iPerf cannot connect | user plane, UE client, or stale IP |
| Baseline mode passes but experimental mode violates RB assertions | scheduler patch |
| Both baseline and experimental modes fail attachment | environment, not scheduler policy |
| Same binary baseline passes, cap mode attaches but throughput drops | expected policy/capacity effect unless outside acceptance target |
| Pod restarts only in one mode with identical environment | likely software regression; capture core and logs |

## Recommended Development Sequence

1. Choose and freeze an exact baseline commit.
2. Build that commit unchanged with a unique tag.
3. Pass one-minute and five-minute live baseline tests.
4. Add runtime configuration with default `baseline`.
5. Prove the new binary in `baseline` mode is behaviorally equivalent.
6. Add `prb_cap_spread` only.
7. Pass software allocation tests.
8. Build once and test baseline versus cap by ConfigMap only.
9. Run the live one-minute and five-minute gates.
10. Add `wide_burst` only after cap mode is stable.
11. Repeat all QC gates.
12. Begin repeated PDU experiments only after both modes pass.

## Definition of Done

The scheduler work is ready for research comparison when:

- one immutable image supports all modes;
- baseline mode reproduces the known-good E2E path;
- software tests prove each mode's allocation invariants;
- live artifacts prove attachment, traffic, and scheduler behavior;
- PNF runtime and RU configuration are pinned and recorded;
- baseline and experiment use matched throughput windows;
- PDU power data is aligned to those windows;
- each condition has at least three valid repeats;
- failures can be assigned to scheduler, VNF, PNF, RU, UE, or lab contention using recorded evidence.

