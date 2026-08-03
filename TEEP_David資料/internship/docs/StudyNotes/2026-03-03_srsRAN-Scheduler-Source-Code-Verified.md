# srsRAN Scheduler Architecture — Source-Code-Verified Reference

**Date**: 2026-03-03
**Method**: Every claim in this note is backed by actual source code reads from `srsRAN_Project/lib/scheduler/`. This corrects inaccuracies in the [03-02 Frequencies-in-NR note](./2026-03-02_Frequencies-in-NR.md) that referenced a nonexistent `scheduler_time_pf.cpp`.
**Prerequisites**: [02-24 MAC Scheduler Modules](./2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md), [02-27 Config Walkthrough](./2026-02-27_srsRAN-Config-Walkthrough-273-vs-27-Demo.md)

---

## 0. Critical Correction from 03-02 Note

> **There is NO `scheduler_time_pf.cpp` in srsRAN.**

The two scheduler policies are:
| Policy | Source File | Config Trigger |
|--------|-----------|----------------|
| **Round Robin** | `scheduler_time_rr.cpp` (79 lines) | `rr_sched:` YAML subcmd |
| **QoS-aware (with internal PF)** | `scheduler_time_qos.cpp` (418 lines) | `qos_sched:` YAML subcmd (default) |

The "PF" functionality exists **inside** `scheduler_time_qos` via `compute_pf_metric()`, but it is fused with GBR, QoS priority, and packet delay budget weights. There is no standalone PF policy.

---

## 1. Complete Call Chain (Verified)

```
cell_scheduler::run_slot()
  └─ inter_slice_scheduler::slot_indication()         ← builds priority queue of slice candidates
       └─ get_next_dl_candidate() / get_next_ul_candidate()
            └─ intra_slice_scheduler::dl_sched(slice, policy)
                 ├─ schedule_dl_retx_candidates()     ← retransmissions first (always)
                 └─ schedule_dl_newtx_candidates(slice, policy, max_grants)
                      ├─ [STAGE 1] prepare_newtx_dl_candidates(slice, policy)
                      │    ├─ fill_ue_candidate_group()       ← pre-policy RR rotation
                      │    ├─ policy.compute_ue_dl_priorities()  ← TIME-DOMAIN decision
                      │    ├─ std::sort(candidates, by_priority_desc)
                      │    └─ remove candidates with forbid_priority
                      └─ [STAGE 2] for each candidate (highest priority first):
                           ├─ ue_alloc.allocate_dl_grant()   ← PDCCH + UCI + HARQ alloc
                           ├─ grant_builder.recommended_vrbs(used_vrbs, max_rbs)  ← FD decision
                           └─ grant_builder.set_pdsch_params(vrbs, crbs, interleaving)
```

**Source**: `intra_slice_scheduler.cpp` lines 184–588

### Key Insight

Stage 1 (**policy**) only sets `candidate.priority` — a `double` value.
Stage 2 (**grid allocator**) does the actual PRB allocation via VRB bitmap.
The policy never touches PRBs directly.

---

## 2. Scheduler Policies — Actual Source Code

### 2.1 Policy Factory

**File**: `lib/scheduler/policy/scheduler_policy_factory.cpp` (42 lines)

```cpp
std::unique_ptr<scheduler_policy>
create_scheduler_strategy(const scheduler_ue_expert_config& expert_cfg_,
                          du_cell_index_t                   cell_index_)
{
  if (std::holds_alternative<time_rr_scheduler_config>(expert_cfg_.policy_cfg)) {
    return std::make_unique<scheduler_time_rr>(expert_cfg_, cell_index_);
  }
  if (std::holds_alternative<time_qos_scheduler_config>(expert_cfg_.policy_cfg)) {
    return std::make_unique<scheduler_time_qos>(expert_cfg_, cell_index_);
  }
  report_fatal_error("Unknown scheduling policy");
}
```

The policy is selected via `expert_cfg_.policy_cfg`, which is a `std::variant<time_qos_scheduler_config, time_rr_scheduler_config>`. Default is `time_qos_scheduler_config{}`.

### 2.2 Round Robin — `scheduler_time_rr.cpp` (79 lines, complete)

The RR policy tracks a running allocation counter per UE:

```cpp
void scheduler_time_rr::compute_ue_dl_priorities(slot_point               pdcch_slot,
                                                  slot_point               pdsch_slot,
                                                  span<ue_newtx_candidate> ue_candidates)
{
  for (auto& candidate : ue_candidates) {
    // Priority = how many slots since this UE last got a grant.
    // Higher value = waited longer = higher priority.
    candidate.priority = dl_alloc_count - ue_last_dl_alloc_count[candidate.ue->ue_index()];
  }
}

void scheduler_time_rr::save_dl_newtx_grants(span<const dl_msg_alloc> dl_grants)
{
  for (const auto& grant : dl_grants) {
    ++dl_alloc_count;
    ue_last_dl_alloc_count[grant.context.ue_index] = dl_alloc_count;
  }
}
```

**Mechanism**: `priority = dl_alloc_count - ue_last_dl_alloc_count[ue_index]`. The UE that has waited the longest gets the highest priority. With a single UE, that UE always wins trivially.

### 2.3 QoS-Aware with Internal PF — `scheduler_time_qos.cpp` (418 lines)

This is the **default** policy. It computes priority as a product of four sub-weights:

#### PF Metric (lines 27–36)

```cpp
static double compute_pf_metric(double estim_rate, double avg_rate, double fairness_coeff)
{
  if (avg_rate == 0) {
    return max_sched_priority;   // UE with no prior allocation gets max priority
  }
  static constexpr unsigned MAX_PF_COEFF = 10;
  fairness_coeff = std::min(fairness_coeff, static_cast<double>(MAX_PF_COEFF));
  return estim_rate / std::pow(avg_rate, fairness_coeff);
}
```

This is classic Proportional Fair: $\frac{R_{inst}}{R_{avg}^{\alpha}}$ where $\alpha$ = `pf_fairness_coeff` (default 2.0).

#### Combined Weight (lines 123–142)

```cpp
static double combine_qos_metrics(double   pf_weight,
                                   double   gbr_weight,
                                   double   prio_weight,
                                   double   delay_weight,
                                   const time_qos_scheduler_config& policy_params)
{
  if (policy_params.combine_function ==
      time_qos_scheduler_config::combine_function_type::gbr_prioritized
      and gbr_weight > 1.0) {
    // GBR flows that are below their guaranteed rate get absolute priority.
    return max_metric_weight * gbr_weight * pf_weight * prio_weight * delay_weight;
  }
  // Geometric mean: all factors equally weighted.
  return gbr_weight * pf_weight * prio_weight * delay_weight;
}
```

The four sub-weights:

| Sub-Weight | Source | What It Does |
|-----------|--------|-------------|
| `pf_weight` | `compute_pf_metric()` | Proportional fairness: $R_{inst} / R_{avg}^{\alpha}$ |
| `gbr_weight` | Per-LC `GBR_rate / actual_rate` | Boosts UEs below their Guaranteed Bit Rate |
| `prio_weight` | `(max_prio+1 - UE_prio) / (max_prio+1)` | QoS priority level (5QI × ARP) |
| `delay_weight` | `HoL_delay / PDB` | Boosts UEs approaching their Packet Delay Budget |

#### DL Priority Computation (lines 276–315)

```cpp
void scheduler_time_qos::ue_ctxt::compute_dl_prio(const slice_ue& u,
                                                    slot_point pdcch_slot,
                                                    slot_point pdsch_slot,
                                                    unsigned   nof_slots_elapsed)
{
  dl_prio = forbid_prio;
  compute_dl_avg_rate(u, nof_slots_elapsed);  // exponential moving average

  const ue_cell& ue_cc = u.get_cc();
  // Estimate instantaneous rate assuming FULL BWP allocation
  const double estimated_rate = ue_cc.get_estimated_dl_rate(
      pdsch_cfg, mcs.value(), ss_info.dl_crb_lims.length());  // ← full BWP width
  const double current_total_avg_rate = total_dl_avg_rate();

  dl_prio = compute_dl_qos_weights(u, estimated_rate, current_total_avg_rate,
                                    pdcch_slot, parent->params);
}
```

**Key detail**: The estimated rate is computed assuming the entire BWP is allocated (all CRBs). This is only used for the PF metric — the actual grant size is determined later in Stage 2.

#### Exponential Average Rate Tracking (lines 380–418)

```cpp
void scheduler_time_qos::ue_ctxt::compute_dl_avg_rate(const slice_ue& u,
                                                        unsigned nof_slots_elapsed)
{
  // Push zeros for slots where no allocation happened
  if (nof_slots_elapsed > 1) {
    total_dl_avg_rate_.push_zeros(nof_slots_elapsed - 1);
  }
  // Push this slot's allocated bytes
  total_dl_avg_rate_.push(dl_sum_alloc_bytes);
  dl_sum_alloc_bytes = 0;
}

void scheduler_time_qos::ue_ctxt::save_dl_alloc(uint32_t total_alloc_bytes,
                                                  const dl_msg_tb_info& tb_info)
{
  dl_sum_alloc_bytes += total_alloc_bytes;
}
```

The average rate uses `exponential_averager` with configurable alpha (smoothing factor). UEs with zero recent allocation automatically get boosted by the PF metric (denominator → 0 → max priority).

---

## 3. Intra-Slice Scheduler — The Core Orchestrator

**File**: `lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp` (937 lines)

### 3.1 `dl_sched()` — Entry Point (lines 184–206)

```cpp
void intra_slice_scheduler::dl_sched(dl_ran_slice_candidate slice,
                                      scheduler_policy& policy)
{
  srsran_sanity_check(slice.remaining_rbs() > 0, "Invalid slice");

  // Determine max number of UE grants for this slot
  unsigned pdschs_to_alloc = max_pdschs_to_alloc(slice);
  if (pdschs_to_alloc == 0) return;

  // Step 1: Schedule retransmissions (always first)
  unsigned nof_retxs_alloc = schedule_dl_retx_candidates(slice, pdschs_to_alloc);
  pdschs_to_alloc -= std::min(pdschs_to_alloc, nof_retxs_alloc);
  if (pdschs_to_alloc == 0) return;

  // Step 2: Schedule new transmissions
  schedule_dl_newtx_candidates(slice, policy, pdschs_to_alloc);
}
```

**Design principle**: Retransmissions always get priority over new data. The policy only affects *new transmission* ordering.

### 3.2 Two-Stage NewTx Allocation (lines 445–588)

```
schedule_dl_newtx_candidates()
  ├─ prepare_newtx_dl_candidates()
  │    ├─ fill_ue_candidate_group()    ← pre-policy RR group rotation
  │    ├─ policy.compute_ue_dl_priorities()  ← STAGE 1: set priorities
  │    ├─ std::sort(by priority desc)
  │    └─ remove forbid_priority candidates
  │
  ├─ get_max_grants_and_rb_grant_size()  ← compute max_rbs_per_grant
  │
  ├─ STAGE 1 LOOP: for each candidate (highest priority first)
  │    └─ ue_alloc.allocate_dl_grant()   ← reserve PDCCH + UCI + HARQ
  │         → creates a "grant builder" (no PRBs assigned yet!)
  │
  └─ STAGE 2 LOOP: for each pending grant builder
       ├─ grant_builder.recommended_vrbs(used_dl_vrbs, max_grant_size)  ← PRB allocation
       ├─ grant_builder.set_pdsch_params(vrbs, crbs, interleaving)
       └─ used_dl_vrbs.fill(alloc_vrbs)  ← mark PRBs as used
```

**Critical detail**: Stage 1 reserves control-plane resources (PDCCH, UCI, HARQ). Stage 2 fills data-plane PRBs. These are separate passes.

### 3.3 Grant Size Heuristic (lines 238–295)

```cpp
// Maximum UE grants per slot — implementation-defined heuristic
static constexpr unsigned MAX_UE_GRANT_PER_SLOT = 8;
ues_to_alloc = std::min({
    ues_to_alloc,
    std::max(static_cast<unsigned>(ue_candidates.size()) / 4U, 1U),
    MAX_UE_GRANT_PER_SLOT
});

// CORESET CCE budget shared 50/50 between DL and UL
unsigned max_nof_candidates = (ss_info->coreset->get_nof_cces() / 2) /
                               to_nof_cces(aggregation_level::n2);

// Minimum 4 RBs per grant
static constexpr unsigned MIN_RB_PER_GRANT = 4;
return std::make_pair(max_nof_rbs, std::max(max_nof_rbs / ues_to_alloc, MIN_RB_PER_GRANT));
```

With 1 UE: `max_nof_rbs / 1` = full slice width ⇒ all PRBs go to that UE.

### 3.4 Pre-Policy RR Group Rotation (lines 84–136)

For large UE populations, the scheduler rotates through groups (default size 32) to limit compute:

```cpp
const unsigned group_size = std::min(nof_ues, parent->expert_cfg.pre_policy_rr_ue_group_size);
auto start_ue_it = slice_ues.lower_bound(to_du_ue_index(group_offset));
// ... iterate from group_offset, wrap around, collect up to group_size candidates
```

This means with >32 UEs, the QoS policy only sees a subset per slot — acting as a hybrid RR+QoS.

---

## 4. Inter-Slice Scheduler — Slice-Level Arbitration

**File**: `lib/scheduler/slicing/inter_slice_scheduler.cpp` (440 lines)

### 4.1 Slice Creation (constructor, lines 31–92)

```cpp
// Default SRB slice — max priority, full bandwidth
slices.emplace_back(SRB_RAN_SLICE_ID, cell_cfg,
    slice_rrm_policy_config{.rbs = {cell_max_rbs, cell_max_rbs},
                            .priority = max_priority}, ...);

// Default DRB slice — normal priority, full bandwidth
slices.emplace_back(DEFAULT_DRB_RAN_SLICE_ID, cell_cfg,
    slice_rrm_policy_config{.rbs = {0, cell_max_rbs}}, ...);

// Additional slices per RRM policy config
for (const slice_rrm_policy_config& rrm : cell_cfg.rrm_policy_members) {
    // Each slice gets its OWN scheduler policy instance
    scheduler_ue_expert_config slice_cfg{cell_cfg.expert_cfg.ue};
    slice_cfg.policy_cfg = rrm.policy_sched_cfg;  // can override per slice!
    slices.emplace_back(id, cell_cfg, rrm_adjusted,
        create_scheduler_strategy(slice_cfg, cell_cfg.cell_index), ues);
}
```

**Key finding**: Each slice can have its **own scheduler policy** (RR or QoS). So you could run RR for one slice and QoS for another — different policies per S-NSSAI/SD.

### 4.2 Slice Priority Queue (lines 93–196)

The inter-slice scheduler builds a priority queue each slot. Priority is a 32-bit integer composed of:

```
| Slot distance (7 bits) | minRB priority (1 bit) | Slice priority (8 bits) | Delay (8 bits) | RR (7 bits) | 1 |
```

1. **Slot distance**: Closer slots > further slots (avoids out-of-order)
2. **minRB achieved**: Slices below their guaranteed minRB get priority
3. **Slice priority**: Configured `priority` value (0–254)
4. **Delay priority**: Slices not scheduled for a long time get boosted
5. **Round-robin**: Slot count for tie-breaking

### 4.3 PRB Limits per Slice

From `slice_rrm_policy_config.h`:

```cpp
struct slice_rrm_policy_config {
  rrm_policy_member rrc_member;
  rrm_policy_ratio_rb_limits rbs;    // {dedicated, min, max} in absolute RBs
  unsigned priority = 0;              // 0–255
  scheduler_policy_config policy_sched_cfg = time_qos_scheduler_config{};
};
```

The `rbs` field has three components:
- **dedicated**: RBs reserved exclusively for this slice
- **min**: Minimum guaranteed RBs (prioritized in scheduling)
- **max**: Maximum RBs this slice can use

These are computed from the YAML percentage ratios applied to `cell_max_rbs`:
- `max_prb_policy_ratio: 10` with 273 CRBs → `max = 27 RBs`

---

## 5. Frequency-Domain Allocator — `ue_cell_grid_allocator.cpp`

**File**: `lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp` (922 lines)

### 5.1 Grant Allocation Flow

```cpp
expected<dl_newtx_grant_builder, dl_alloc_failure_cause>
ue_cell_grid_allocator::allocate_dl_grant(const ue_newtx_dl_grant_request& request)
{
    // 1. Get scheduling context (search space, PDSCH TD resource)
    auto sched_ctxt = sched_helper::get_newtx_dl_sched_context(...);

    // 2. Setup grant builder (PDCCH + UCI + HARQ)
    auto result = setup_dl_grant_builder(request.user, sched_ctxt.value(), ...);

    // 3. Return builder — PRBs NOT yet assigned!
    dl_grants.push_back(*result);
    return dl_newtx_grant_builder{*this, dl_grants.size() - 1};
}
```

### 5.2 PDCCH → UCI → HARQ → PDSCH Pipeline

Inside `setup_dl_grant_builder()` (lines 162–228):

```
1. alloc_dl_pdcch()     → reserve PDCCH CCEs for DCI
2. alloc_uci()          → reserve UCI (PUCCH/PUSCH) for HARQ-ACK feedback
3. alloc_dl_harq()      → allocate HARQ process
4. Create dl_msg_alloc  → PDSCH PDU skeleton
```

Then later, `set_pdsch_params()` (lines 230–370) fills the actual VRBs:

```
1. calculate_dl_mcs_tbs()  → MCS + TBS based on allocated CRBs
2. Fill DCI (f1_0 or f1_1)  → frequency domain resource assignment, MCS, RV
3. Fill PDSCH PDU            → codeword, TB size, DMRS config
4. Mark resource grid used   → dl_res_grid.fill(grant_info{scs, symbols, crbs})
```

### 5.3 MCS/TBS Adjustment for CSI-RS

```cpp
// When CSI-RS is present, reduce MCS by 1 to account for overhead
if (not pdsch_alloc.result.dl.csi_rs.empty()) {
    adjusted_mcs = adjusted_mcs == 0 ? adjusted_mcs : adjusted_mcs - 1;
    uint8_t max_mcs_with_csi_rs = 28;
    if (pdsch_cfg.mcs_table == pdsch_mcs_table::qam64) {
        max_mcs_with_csi_rs = 26U;
    } else if (pdsch_cfg.mcs_table == pdsch_mcs_table::qam256) {
        max_mcs_with_csi_rs = 24U;
    }
}
```

---

## 6. Configuration — YAML to Code Mapping (Verified)

### 6.1 Scheduler Policy Selection

**Source**: `du_high_config_cli11_schema.cpp` lines 609–630

The YAML structure uses **subcommands**, not a simple key-value:

```yaml
# Default: QoS-aware (with PF internally) — no config needed
# This is the DEFAULT when you don't specify anything

# To select Round Robin:
cell_cfg:
  scheduler_cfg:
    rr_sched:          # ← this empty section triggers time_rr_scheduler_config

# To configure QoS-aware with custom PF coefficient:
cell_cfg:
  scheduler_cfg:
    qos_sched:
      pf_fairness_coeff: 2.0        # default=2.0, 0=max rate, higher=more fair
      combine_function: gbr_prioritized   # or "geometric_mean"
      prio_enabled: true             # consider QoS/ARP priority
      pdb_enabled: true              # consider Packet Delay Budget
      gbr_enabled: true              # consider Guaranteed Bit Rate
```

**Critical correction**: The [03-02 note](./2026-03-02_Frequencies-in-NR.md) said `policy: time_rr` — this is **wrong**. The actual config uses YAML subcmd sections `rr_sched:` or `qos_sched:`.

### 6.2 Slice PRB Limits

**Source**: `du_high_config_cli11_schema.cpp` lines 1487–1520

```yaml
slicing:
  -
    sst: 1
    sd: 1
    sched_cfg:
      min_prb_policy_ratio: 0      # 0–100%, minimum guaranteed PRBs
      max_prb_policy_ratio: 100    # 1–100%, maximum allowed PRBs
      ded_prb_policy_ratio: 0      # dedicated (reserved) PRBs
      priority: 0                  # 0–254, slice scheduling priority
      policy:                      # per-slice policy override
        qos_sched:                 # or rr_sched:
          pf_fairness_coeff: 2.0
```

For our 273×1 vs 27×10 experiment:

| Experiment | Config | Effect |
|-----------|--------|--------|
| **A: 273×1 (FDM)** | `max_prb_policy_ratio: 100` | Slice can use all 273 PRBs → 1 slot |
| **B: 27×10 (TDM)** | `max_prb_policy_ratio: 10` | Slice capped at 27 PRBs → 10 slots |

### 6.3 Expert UE Config Knobs

**Source**: `scheduler_expert_config.h` lines 147–213

```yaml
expert_cfg:
  dl_mcs: [0, 28]                    # MCS range for DL
  ul_mcs: [0, 28]                    # MCS range for UL
  pdsch_nof_rbs: [1, 273]            # Min/Max PRBs per PDSCH grant
  pusch_nof_rbs: [1, 273]            # Min/Max PRBs per PUSCH grant
  pdsch_crb_limits: [0, 273]         # CRB boundaries for PDSCH
  pusch_crb_limits: [0, 273]         # CRB boundaries for PUSCH
  max_pdschs_per_slot: 16            # MAX_PDSCH_PDUS_PER_SLOT
  max_puschs_per_slot: 16            # MAX_PUSCH_PDUS_PER_SLOT
  max_pucchs_per_slot: 31
  max_nof_dl_harq_retxs: 4
  max_nof_ul_harq_retxs: 4
  initial_cqi: 3                     # Used until UE reports CQI
  olla_cqi_inc: 0.001                # OLLA step size (0=disabled)
  pre_policy_rr_ue_group_size: 32    # UE group rotation size
```

Note: `pdsch_nof_rbs` and `pdsch_crb_limits` are different knobs:
- `pdsch_nof_rbs` limits the **grant size** (how many RBs a single PDSCH can span)
- `pdsch_crb_limits` limits the **CRB range** (which RBs can be used, e.g., PRBs 0–26 only)

---

## 7. Summary: How to Enable Time vs Frequency Domain Scheduling

### 7.1 The Answer to the Professor's Question

**Time-domain scheduling** and **frequency-domain scheduling** are not separate toggles. They are the two stages of a single scheduling pipeline that **always runs both stages**:

1. **Stage 1 (Time-Domain)**: Policy selects which UEs get scheduled this slot and sets priorities. Controlled by `rr_sched:` or `qos_sched:` config.

2. **Stage 2 (Frequency-Domain)**: Allocator assigns PRBs to the selected UEs. Controlled by `max_prb_policy_ratio` and `pdsch_nof_rbs`.

To shift the balance towards **FDM** (frequency-domain multiplexing):
- Use `max_prb_policy_ratio: 100` → UE gets all PRBs in fewer slots

To shift towards **TDM** (time-domain multiplexing):
- Use `max_prb_policy_ratio: 10` → UE gets fewer PRBs but across more slots

### 7.2 Configuration Cheat Sheet

```yaml
# EXPERIMENT A: Full FDM — 273 PRBs × 1 slot
cell_cfg:
  scheduler_cfg:
    qos_sched:                         # default QoS-aware + PF
      pf_fairness_coeff: 2.0

slicing:
  - sst: 1
    sd: 1
    sched_cfg:
      max_prb_policy_ratio: 100        # ← full bandwidth

# EXPERIMENT B: Forced TDM — 27 PRBs × 10 slots
cell_cfg:
  scheduler_cfg:
    qos_sched:
      pf_fairness_coeff: 2.0

slicing:
  - sst: 1
    sd: 1
    sched_cfg:
      max_prb_policy_ratio: 10         # ← cap at 10% of 273 ≈ 27 PRBs
```

### 7.3 Verification in Wireshark

After capturing a MAC PCAP (`--pcap.enable=true`):

1. Filter: `mac-nr.dlsch`
2. Check **Frequency domain resource assignment** in DCI:
   - Exp A: RIV for 273 contiguous PRBs
   - Exp B: RIV for ~27 contiguous PRBs
3. Check **slot allocation pattern**:
   - Exp A: 1 slot with large PDSCH
   - Exp B: ~10 consecutive slots with small PDSCHs
4. Verify throughput ≈ equal (within ~1–2% per [TBS calculator](../../scripts/tbs_calculator.py))

---

## 8. File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `lib/scheduler/policy/scheduler_policy_factory.cpp` | 42 | Creates `time_rr` or `time_qos` based on config variant |
| `lib/scheduler/policy/scheduler_time_rr.cpp` | 79 | Round Robin: priority = `dl_alloc_count - ue_last_dl_alloc_count` |
| `lib/scheduler/policy/scheduler_time_qos.cpp` | 418 | QoS+PF: `pf_weight × gbr_weight × prio_weight × delay_weight` |
| `lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp` | 937 | Core orchestrator: retx → Stage 1 (policy) → Stage 2 (PRBs) |
| `lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp` | 922 | FD allocator: PDCCH → UCI → HARQ → PDSCH → VRB fill |
| `lib/scheduler/slicing/inter_slice_scheduler.cpp` | 440 | Slice priority queue, per-slice policy instances |
| `include/srsran/scheduler/config/scheduler_expert_config.h` | 264 | Config structs: `time_qos_scheduler_config`, `time_rr_scheduler_config` |
| `include/srsran/scheduler/config/slice_rrm_policy_config.h` | 57 | Slice RRM: `rbs`, `priority`, `policy_sched_cfg` |
| `apps/.../du_high_config_cli11_schema.cpp` | 2145 | YAML→config mapping: `qos_sched:`, `rr_sched:`, `max_prb_policy_ratio` |
