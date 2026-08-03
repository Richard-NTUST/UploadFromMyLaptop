# Understanding OAI NR Downlink Scheduling

## What This Note Is For

This is a learning note for understanding the OAI downlink scheduler currently used
by the WINLAB gNB. It explains the path from queued application data to a radio
allocation, then identifies what a scheduler experiment can change safely.

The key point is simple:

> The scheduler decides who gets radio resources, where those resources are, and how
> large each grant is. It does not create data, attach the UE, or send packets by
> itself.

If the UE cannot attach or the RU is misconfigured, changing scheduler code will not
fix that problem. Scheduler experiments begin only after the regular E2E path works.

## Big Picture

For a downlink iPerf test, data travels like this:

```text
iPerf server
  -> core network / user-plane tunnel
  -> gNB RLC buffers
  -> OAI MAC downlink scheduler
  -> OAI PHY / nFAPI messages
  -> RU radio transmission
  -> UE
```

The MAC scheduler operates once per radio slot. At 30 kHz subcarrier spacing, a slot
is 0.5 ms long, so scheduler decisions must be made quickly and repeatedly.

## The Three Questions a Scheduler Answers

For each slot, the scheduler answers:

1. **Which UE should be served?**
2. **How much time-frequency resource should it receive?**
3. **What transmission settings should be used?**

In OAI, the resulting allocation contains values such as:

```text
rnti       Which UE receives the grant
rbStart    First physical resource block of the grant
rbSize     Number of contiguous physical resource blocks
mcs        Modulation and coding scheme
tbs        Transport-block size in bytes
layers     Number of spatial layers
tda        Time-domain allocation
harq_pid   HARQ process used for reliability
```

These are exactly the fields recorded by `[WINLAB_SCHED_LOG]` in the custom image.

## What Is a PRB?

A physical resource block (PRB) is a small rectangular piece of radio resource:

```text
frequency: 12 subcarriers wide
time:      a selected set of OFDM symbols in a slot
```

With the current 100 MHz, 30 kHz configuration, the gNB has a large PRB budget.
The scheduler gives a UE a contiguous run of PRBs, for example:

```text
rbStart = 0, rbSize = 97
```

means the UE gets PRBs 0 through 96 for the relevant time-domain allocation.

OAI's active NR PDSCH path uses resource-allocation type 1. In practical terms,
that means the PRBs assigned to one UE must be contiguous. The scheduler cannot
freely scatter isolated PRBs around the band as the LTE type-0/RBG design in the Liu
thesis does.

## The Actual OAI Scheduler Path

The deployed source has a pipeline. Each stage adds one part of the decision:

```text
nr_dlsch_preprocessor()
  -> nr_dl_schedule()
       -> collect_dl_candidates()
       -> dl_ri_pmi_select()
       -> dl_beam_select()
       -> dl_tda_select()
       -> dl_mcs_select()
       -> dl_rb_alloc()
       -> post_process_dlsch()
```

The main files are:

```text
gNB_scheduler_dlsch.c                  pipeline and scheduler orchestration
gNB_scheduler_dlsch_default_policies.c default policy decisions
nr_mac_gNB.h                            candidate and policy data structures
gNB_scheduler_primitives.c              RB search and TBS helper functions
main.c                                  connects default policy functions at startup
```

## Step 1: Build Candidates

`collect_dl_candidates()` creates one candidate for every active UE that may need a
downlink grant.

For each candidate, OAI gathers information such as:

- pending bytes in RLC buffers;
- retransmission status;
- UE average throughput;
- BLER and current MCS state;
- CQI, rank indicator, and PMI;
- logical-channel priority and 5QI;
- NSSAI slice identity when available;
- BWP range and beam measurements.

This is useful because a future scheduler policy already receives enough information
to prioritize traffic by throughput, QoS, or slice identity. We do not need to add a
new path through RLC merely to read these values.

## Step 2: Choose Radio Properties

Before deciding PRB size, OAI chooses settings that define what kind of grant is
possible.

### RI/PMI selection

`dl_ri_pmi_select()` chooses the number of spatial layers and precoding information
from CSI feedback. More layers can carry more data, but only when the channel supports
them.

### Beam selection

`dl_beam_select()` assigns a beam for the UE. Candidates that cannot obtain a valid
beam are skipped before the RB allocator runs.

### Time-domain allocation

`dl_tda_select()` selects the OFDM-symbol range used by the PDSCH. This defines the
time part of the resource rectangle.

### MCS selection

`dl_mcs_select()` selects modulation and coding using BLER feedback. A higher MCS
usually gives a larger transport block for the same number of PRBs, but it is less
robust when radio conditions are poor.

## Step 3: Proportional-Fair RB Allocation

The default allocator is:

```text
nr_dl_proportional_fair()
```

It has three phases.

### Phase 1: retransmissions

HARQ retransmissions come first. A failed earlier transmission must be repaired
before new data receives priority. Their resource needs are treated carefully so the
original transport block remains valid.

### Phase 2: control-only grants

Some UEs need a small downlink grant for MAC control, such as timing advance or a
beam-switch command, even when there is no user data. OAI gives these the minimum
five-PRB grant.

### Phase 3: new data

For normal downlink traffic, OAI ranks UEs using a proportional-fair weight:

```text
estimated short-term rate / historical average throughput
```

This tries to balance two goals:

- serve a UE when its channel can carry data efficiently;
- avoid continually favoring a UE that has already received more throughput.

The historical throughput is an exponentially weighted moving average. It changes
gradually, rather than jumping after every single grant.

After sorting candidates, OAI finds the largest contiguous currently-free PRB block.
`nr_find_nb_rb()` then chooses the smallest number of PRBs that can hold the queued
bytes. The final number may be smaller than the largest free block.

## Why `COMMIT_ALLOC` Matters

The RB allocator does not merely write `rbStart` and `rbSize`. It must call the
`COMMIT_ALLOC` macro.

That macro:

1. writes the candidate's PRB and MCS decision;
2. validates that a PDCCH control grant can be created;
3. validates the required PUCCH feedback resource;
4. reserves the selected PDCCH and PRBs so later UEs cannot reuse them;
5. marks the candidate as scheduled.

An experiment that bypasses this step may appear to allocate PRBs in logs but produce
an invalid radio schedule. A safe policy changes the decision inputs and still uses
`COMMIT_ALLOC`.

## Where a Safe Experiment Belongs

The default policy implementation is in:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch_default_policies.c
```

This is the right place to change allocation behavior. The policy callback is named
`dl_rb_alloc`, and the standard implementation is `nr_dl_proportional_fair()`.

Avoid making the first behavior experiment in `gNB_scheduler_dlsch.c`. That file
coordinates candidate collection, beams, time allocation, MCS, and final processing.
Changing it increases the chance of disturbing several unrelated parts of the radio
path at once.

## A Good First Change: PRB Cap

The first meaningful experiment for the current single Samsung UE is a cap on the
maximum new-data grant:

```text
actual maximum for a new-data grant
  = min(largest free contiguous block, chosen PRB cap)
```

This should be applied in phase 3, before `nr_find_nb_rb()` decides the final grant.

Keep these behaviors unchanged in the first patch:

- HARQ retransmissions;
- control-only grants;
- beam selection;
- time-domain allocation;
- MCS selection;
- CCE/PUCCH validation;
- FAPI dispatch.

Why this is a useful experiment:

- the log will show a smaller `rbSize` under traffic;
- the offered load and achieved throughput can be compared;
- the radio and deployment stack remains otherwise unchanged;
- it works with one UE.

Why `max_num_ue = 1` is not useful now:

- only one Samsung UE is active, so the default scheduler is already effectively
  serving at most that one data UE in the test.

## What the Liu Thesis Contributes

The thesis presents a useful long-term design:

```text
inter-slice scheduler -> allocates each slice a resource budget
intra-slice scheduler -> chooses UEs within each slice
final scheduler       -> builds control and data messages
```

The current OAI pipeline has a natural place for this idea. A future custom
`dl_rb_alloc()` policy could:

1. group candidates by `nssai` or `fiveQI`;
2. calculate a PRB budget for each group;
3. order UEs inside each group by PF, round robin, or priority;
4. call `COMMIT_ALLOC` for each accepted allocation.

That is a multi-UE or multi-traffic-class project. It cannot be evaluated properly
with one UE carrying one iPerf flow, because there is no competing traffic to isolate
or share.

## What the Telemetry Findings Change

The professor's findings show an important experimental lesson: in a stable O-DU
testbed, the large energy cost came from gNB operation and maintaining an attached
UE. Moving moderate user traffic added much less power. CPU occupancy also did not
reliably represent energy use.

For our experiment, this means:

- compare scheduler variants with the same RU configuration and UE state;
- use the same offered load and test duration;
- collect real Outlet 2 active power, not CPU utilization as a substitute;
- use the scheduler log to prove the policy actually changed allocation behavior;
- repeat baseline and variant runs before claiming an energy effect.

It is possible for a scheduler change to visibly alter PRB allocations and throughput
but produce no measurable power difference. That is still a useful result.

## Before You Modify Code

Use this checklist:

1. Confirm the RU has the intended E2E configuration. Run `pegam` only after the RU
   was used or reconfigured for another purpose; it is not a per-run requirement.
2. Confirm PNF and VNF are Ready.
3. Confirm the UE can attach and receive a `10.45.x.x` address.
4. Run a baseline E2E test and verify nonzero iPerf samples.
5. Confirm `[WINLAB_SCHED_LOG]` appears in the VNF artifact log.
6. Build the policy variant with a unique tag.
7. Run a 300-second E2E smoke test before a longer comparison.
8. Export the matching PDU power window and merge it with the run artifact.

## Takeaway

The scheduler code is already structured to support a clean policy experiment. The
next change should be small and observable: alter only new-data PRB budgeting, keep
the control and reliability path intact, and prove the effect with scheduler logs,
iPerf, and PDU power data.
