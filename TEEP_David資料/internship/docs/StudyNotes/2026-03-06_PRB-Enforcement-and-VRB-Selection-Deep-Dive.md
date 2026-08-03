# PRB Enforcement & VRB Selection — Source-Code Deep Dive

**Date**: 2026-03-06
**Context**: Continuation of [03-03 Source-Code-Verified note](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md). That note established the scheduler call chain and policy logic but left critical gaps: *how* does `max_prb_policy_ratio` actually enforce PRB caps? *How* are VRBs selected? *How* does srsRAN compute MCS/TBS?
**Method**: Every claim traced through actual source code in `srsRAN_Project/`. New files read today: `du_high_config_translators.cpp`, `rrm.h`, `ran_slice_instance.h/cpp`, `ran_slice_candidate.h`, `grant_params_selector.cpp`, `tbs_calculator.cpp`, `outer_loop_link_adaptation.h`, `mcs_calculator.cpp`, `mcs_tbs_calculator.cpp`, `rb_helper.h`, + config YAML files.
**Prerequisites**: [03-03 Source-Code-Verified Reference](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md), [02-26 TBS Calculator](../../scripts/tbs_calculator.py)

---

## 1. PRB Enforcement: End-to-End Trace

The 03-03 note claimed `max_prb_policy_ratio: 10` caps a 273-PRB cell to 27 PRBs. Today we traced the **exact code path** that makes this happen.

### 1.1 YAML → Absolute RBs

**File**: `apps/.../du_high_config_translators.cpp` line 286

```cpp
unsigned min_rbs = (nof_cell_crbs * cfg.sched_cfg.min_prb_policy_ratio) / 100;
unsigned max_rbs = (nof_cell_crbs * cfg.sched_cfg.max_prb_policy_ratio) / 100;
unsigned ded_rbs = (nof_cell_crbs * cfg.sched_cfg.ded_prb_policy_ratio) / 100;
rrm_policy_cfgs.back().rbs = {ded_rbs, min_rbs, max_rbs};
```

Integer division. With `nof_cell_crbs = 273` and `max_prb_policy_ratio = 10`:

$$\text{max\_rbs} = \lfloor 273 \times 10 / 100 \rfloor = 27$$

### 1.2 The `rrm_policy_ratio_rb_limits` Struct

**File**: `include/srsran/ran/rrm.h` lines 61–88

```cpp
struct rrm_policy_ratio_rb_limits {
  unsigned min()         const { return min_rbs; }        // dedicated + prioritized
  unsigned max()         const { return max_rbs; }        // dedicated + prioritized + shared
  unsigned dedicated()   const { return ded_rbs; }        // reserved exclusively
  unsigned prioritized() const { return min_rbs - ded_rbs; }
  unsigned shared()      const { return max_rbs - min_rbs; }
private:
  unsigned ded_rbs = 0;
  unsigned min_rbs = 0;
  unsigned max_rbs = MAX_NOF_PRBS;  // default = full cell
};
```

The three fields partition the slice's PRB budget:

| Category | Formula | Meaning |
|----------|---------|---------|
| Dedicated | `ded_rbs` | Reserved exclusively, no other slice can use these |
| Prioritized | `min_rbs - ded_rbs` | This slice gets priority but others can borrow |
| Shared | `max_rbs - min_rbs` | Only used if available after other slices served |

For our 27-PRB experiment with defaults (`ded=0, min=0, max=27`): all 27 RBs are "shared" — available but not guaranteed.

### 1.3 Per-Slot Accounting in `ran_slice_instance`

**File**: `lib/scheduler/slicing/ran_slice_instance.h` + `.cpp`

```cpp
class ran_slice_instance {
  unsigned pdsch_rb_count = 0;  // RBs allocated this DL slot

  void store_pdsch_grant(unsigned crbs, slot_point pdsch_slot) {
    pdsch_rb_count += crbs;     // increment running total
  }

  void slot_indication(slot_point slot_tx) {
    avg_pdsch_rbs_per_slot += 0.1f * (pdsch_rb_count - avg_pdsch_rbs_per_slot);
    pdsch_rb_count = 0;         // ← RESET every slot
  }
};
```

Every slot starts at `pdsch_rb_count = 0`. Each grant increments it. The exponential moving average (`0.1` alpha) tracks utilization for inter-slice priority decisions.

### 1.4 Hard Cap via `ran_slice_candidate`

**File**: `lib/scheduler/slicing/ran_slice_candidate.h` lines 36–70

```cpp
template <bool IsDl>
class common_ran_slice_candidate {
  unsigned max_rbs;  // set from cfg.rbs.max()

  unsigned remaining_rbs() const {
    if constexpr (IsDl) {
      return max_rbs < inst->pdsch_rb_count ? 0 : max_rbs - inst->pdsch_rb_count;
    }
    // UL: same logic against pusch_rb_count ring buffer
  }

  void store_grant(unsigned nof_rbs) {
    if constexpr (IsDl) inst->store_pdsch_grant(nof_rbs, slot_tx);
    else                inst->store_pusch_grant(nof_rbs, slot_tx);
  }
};
```

### 1.5 Enforcement in `intra_slice_scheduler`

Three checkpoints in `intra_slice_scheduler.cpp`:

| Line | Check | What It Does |
|------|-------|-------------|
| ~284 | `max_nof_rbs = min(bwp_crb_limits.length(), slice.remaining_rbs())` | Caps total RBs available for scheduling round |
| ~327 | `slice.store_grant(alloc_vrbs.length()); if (slice.remaining_rbs() == 0) break;` | After each grant, stop if budget exhausted |
| ~799 | `pdschs_to_alloc = min(pdschs_to_alloc, slice.remaining_rbs())` | Caps scheduled PDSCHs to remaining budget |

### 1.6 Complete Flow Diagram

```
YAML: max_prb_policy_ratio: 10  (percentage)
         │
         ▼  du_high_config_translators.cpp:286
    max_rbs = floor(273 × 10 / 100) = 27  (absolute RBs)
         │
         ▼  stored in slice_rrm_policy_config.rbs  (rrm_policy_ratio_rb_limits)
         │
         ▼  ran_slice_candidate constructor:  max_rbs = cfg.rbs.max() = 27
         │
         ▼  remaining_rbs() = 27 - pdsch_rb_count
         │
         ▼  intra_slice_scheduler clamps every allocation:
            max_nof_rbs = min(bwp_crbs, remaining_rbs())
            after grant: store_grant() → pdsch_rb_count += allocated
            if remaining_rbs() == 0 → stop scheduling this slice
         │
         ▼  slot_indication() → pdsch_rb_count = 0  (reset for next slot)
```

---

## 2. VRB Selection Algorithm: First-Fit Contiguous

The 03-03 note showed Stage 2 calls `recommended_vrbs()` but never read what it does.

### 2.1 Call Chain

```
recommended_vrbs(used_vrbs, max_nof_rbs)
  → compute_newtx_dl_vrbs() / compute_newtx_ul_vrbs()
    → find_available_vrbs()                          (grant_params_selector.cpp)
      → rb_helper::find_empty_interval_of_length()   (rb_helper.h)
```

### 2.2 The Core Algorithm

**File**: `lib/scheduler/support/rb_helper.h` lines 104–130

```cpp
template <typename Tag>
interval<unsigned, false, Tag>
find_empty_interval_of_length(const bounded_bitset<MAX_NOF_PRBS>& used_rb_bitmap,
                              unsigned nof_rbs,
                              interval<unsigned, false, Tag> search_limits = {0, MAX_NOF_PRBS})
{
  interval<unsigned, false, Tag> max_interv;
  do {
    interval<unsigned, false, Tag> interv = find_next_empty_interval(used_rb_bitmap, search_limits);
    if (interv.empty()) break;
    if (interv.length() >= nof_rbs) {
      max_interv.set(interv.start(), interv.start() + nof_rbs);
      break;                       // ← first-fit: return immediately
    }
    if (interv.length() > max_interv.length()) {
      max_interv = interv;         // ← track longest gap as fallback
    }
    search_limits.displace_to(interv.stop() + 1);
  } while (not search_limits.empty());
  return max_interv;
}
```

**Algorithm**: Scan VRB bitmap from lowest index upward. First contiguous gap ≥ `nof_rbs` → return immediately. If no gap is large enough, return the longest gap found.

### 2.3 Key Properties

| Property | Value |
|----------|-------|
| Allocation type | **Always contiguous** — `vrb_interval` is a single `[start, stop)` range |
| Search direction | Low-to-high VRB index |
| Strategy | First-fit (return immediately on exact/larger match) |
| Fragmentation fallback | Returns longest available gap (fewer RBs than requested) |
| Non-contiguous allocation | **Not supported** — data type cannot represent it |
| VRB-to-PRB interleaving | Optional for DL (spreads VRBs across physical PRBs for diversity) |
| UL interleaving | Not supported — `prbs = vrbs` always |
| Retransmission | Must match original grant size exactly, or grant is **rejected** |

### 2.4 Implication for Our Experiment

With `max_prb_policy_ratio: 10` (27 PRBs), a single UE:
1. `remaining_rbs()` = 27
2. `find_available_vrbs()` searches for gap of 27 in an empty bitmap → VRBs 0–26
3. After grant: `remaining_rbs()` = 0 → stop
4. Next slot: reset → same pattern

The 27 PRBs are always **contiguous starting from VRB 0** (first-fit on empty bitmap).

---

## 3. MCS/TBS Computation Path

### 3.1 MCS Selection: CQI → OLLA → Final MCS

The MCS is determined **before** PRBs are allocated:

```
UE CQI report → map_cqi_to_mcs() lookup table (mcs_calculator.cpp)
  → base MCS (0–28)
    → OLLA offset (outer_loop_link_adaptation.h)
      → final MCS
```

**OLLA mechanism** (`outer_loop_link_adaptation.h`):

```cpp
class olla_algorithm {
  float update(bool ack, sch_mcs_index used_mcs, interval<sch_mcs_index> mcs_bounds) {
    float eff_delta_down = (used_mcs >= mcs_bounds.stop()) ? 0 : delta_down;
    float eff_delta_up   = (used_mcs <= mcs_bounds.start()) ? 0 : delta_up;
    current_offset += ack ? eff_delta_down : -eff_delta_up;
    current_offset = clamp(current_offset, -max_snr_offset, max_snr_offset);
    return current_offset;
  }
};
```

- On ACK: increase offset by `delta_down` (MCS goes up slowly)
- On NACK: decrease offset by `delta_up` (MCS goes down faster)
- `delta_up = (1 - target_bler) × snr_inc_step / target_bler` — asymmetric to converge to target BLER
- Saturates at MCS boundaries to prevent unbounded drift

**Key insight**: MCS and PRBs are **not jointly optimized**. MCS is fixed from CQI+OLLA, then PRBs are derived to fit pending bytes at that MCS.

### 3.2 PRB Computation

**File**: `grant_params_selector.cpp` lines 48–80

```cpp
auto mcs_prbs_sel = compute_newtx_required_mcs_and_prbs(pdsch_cfg, ue_cc, pending_bytes, nof_rb_lims);
// 1) Get MCS from OLLA
const sch_mcs_index mcs = ue_cc.link_adaptation_controller().calculate_dl_mcs(...);
const sch_mcs_description mcs_config = pdsch_mcs_get_config(pdsch_cfg.mcs_table, mcs);

// 2) Compute PRBs needed for pending_bytes at this MCS
sch_prbs_tbs prbs_tbs = get_nof_prbs(prbs_calculator_sch_config{
    pending_bytes, symbols.length(), dmrs_per_rb, nof_oh_prb, mcs_config, nof_layers
}, nof_rb_lims.stop());

// 3) Enforce minimum 2 PRBs for partial-slot allocations
if (prbs_tbs.nof_prbs == 1 && symbols.length() < 14)
    prbs_tbs.nof_prbs = 2;
```

This feeds `expected_nof_rbs` into the VRB search (§2).

### 3.3 TBS Calculator — Matches 3GPP TS 38.214 §5.1.3.2 Exactly

**File**: `lib/ran/sch/tbs_calculator.cpp` lines 124–149

```cpp
unsigned tbs_calculator_calculate(const tbs_calculator_configuration& config)
{
  // Step 1: N_RE' = 12 × N_symb_sh − N_DMRS_PRB − N_oh_PRB
  //         N_RE  = min(N_RE', 156) × n_PRB
  unsigned nof_re_prime = 12 * config.nof_symb_sh - config.nof_dmrs_prb - config.nof_oh_prb;
  unsigned nof_re       = min(nof_re_prime, 156) * config.n_prb;

  // Step 2: N_info = S × N_RE × R × Q_m × v  (with tb_scaling_field)
}
```

Step 3 (N_info ≤ 3824): quantize → lookup in TS 38.214 Table 5.1.3.2-1
Step 4 (N_info > 3824): formula-based with CBS segmentation

**Verification**: Our Python `tbs_calculator.py` implements the same procedure. The srsRAN C++ version is functionally identical.

### 3.4 Post-Allocation MCS/TBS Finalization

After VRBs are assigned (may be fewer than requested), final MCS/TBS is recomputed on actual VRBs:

```cpp
// In set_pusch_params() (ue_cell_grid_allocator.cpp ~L616)
mcs_tbs_info = compute_ul_mcs_tbs(pusch_cfg, ue_cc.active_bwp(),
                                   grant.cfg.recommended_mcs,
                                   vrbs.length(), contains_dc);
```

If effective code rate exceeds 0.95, MCS is reduced iteratively (`mcs_tbs_calculator.cpp`).

---

## 4. Corrections & Improvements to Previous Notes

### 4.1 Config YAML Structure

The `configs/slicing.yml` example shows slice identity (`sst`/`sd`) nested under `cell_cfg:`:

```yaml
cell_cfg:
  slicing:
    - sst: 1
      sd: 1
    - sst: 2
      sd: 42
```

The `max_prb_policy_ratio` / `min_prb_policy_ratio` / `ded_prb_policy_ratio` are set via the `sched_cfg:` sub-block under each slice entry. **No shipped YAML config file demonstrates these knobs** — they're only documented in the C++ config code.

### 4.2 Default gNB Config

The `configs/gnb_rf_b200_tdd_n78_20mhz.yml` uses:
- Band 78 TDD, 20 MHz BW, 30 kHz SCS → **51 PRBs** (not 273)
- No explicit scheduler policy → defaults to `time_qos`
- No slicing config → default SRB slice (full BW, max priority) + default DRB slice (full BW, normal priority)

For a 273-PRB cell, you need 100 MHz BW at 30 kHz SCS.

### 4.3 `pdsch_nof_rbs` vs `max_prb_policy_ratio` — Two Different Knobs

The 03-03 note §6.3 mentioned `pdsch_nof_rbs` but didn't clarify the difference:

| Knob | Scope | What It Limits |
|------|-------|---------------|
| `pdsch_nof_rbs: [1, 273]` | Per-UE | Max PRBs in a **single PDSCH grant** |
| `max_prb_policy_ratio: 10` | Per-slice per-slot | Max PRBs across **all grants in the slice** this slot |
| `pdsch_crb_limits: [0, 26]` | Per-cell | Which CRBs are **allowed at all** (hard boundary) |

For the 273×1 vs 27×10 experiment, `max_prb_policy_ratio` is the correct and cleanest knob.

### 4.4 UL-Specific Details

Not covered in the 03-03 note:
- UL uses a **per-slot ring buffer** for RB accounting (not a single counter like DL)
- UL with transform precoder: VRB count is snapped to valid DFT-s-OFDM sizes via `transform_precoding::get_nof_prbs_lower_bound()`
- UL allocation always uses non-interleaved mapping (`prbs = vrbs`)
- PHR (Power Headroom Report) can further reduce UL PRBs via `adapt_pusch_prbs_to_phr()`

---

## 5. Open Questions for Next Session

1. **Experiment validation**: Run the actual `max_prb_policy_ratio: 10` config in ZMQ and verify DCI shows 27 PRBs in Wireshark
2. **Slice priority interaction**: With `min_prb_policy_ratio: 0`, what happens when two slices compete for the same PRBs? The `inter_slice_scheduler` priority queue should handle this but hasn't been tested
3. **OLLA convergence**: How many slots does OLLA take to converge from `initial_cqi: 3`? This affects early throughput in our experiment
4. **`ded_prb_policy_ratio` isolation**: Does the dedicated PRB mechanism actually prevent other slices from using those PRBs? Needs code trace through `inter_slice_scheduler::get_next_dl_candidate()` → `rb_lims`

---

## 6. File Reference (New Files Read Today)

| File | Lines | Purpose |
|------|-------|---------|
| `apps/.../du_high_config_translators.cpp` | ~286 | Percentage → absolute RBs conversion |
| `include/srsran/ran/rrm.h` | 61–88 | `rrm_policy_ratio_rb_limits` struct: ded/min/max/prioritized/shared |
| `lib/scheduler/slicing/ran_slice_instance.h` | 34–115 | Per-slot RB accounting, `pdsch_rb_count` counter |
| `lib/scheduler/slicing/ran_slice_instance.cpp` | 50–58 | `slot_indication()` resets `pdsch_rb_count` |
| `lib/scheduler/slicing/ran_slice_candidate.h` | 36–70 | `remaining_rbs()` and `store_grant()` — the hard cap |
| `lib/scheduler/ue_scheduling/grant_params_selector.cpp` | 48–510 | MCS/PRB joint computation, `find_available_vrbs()` |
| `lib/ran/sch/tbs_calculator.cpp` | 124–149 | 3GPP TBS algorithm implementation |
| `lib/scheduler/support/outer_loop_link_adaptation.h` | 32–82 | OLLA: CQI → MCS offset tracking |
| `lib/scheduler/support/mcs_tbs_calculator.cpp` | 171–215 | Effective code rate ≤ 0.95 enforcement |
| `lib/scheduler/support/rb_helper.h` | 104–130 | `find_empty_interval_of_length()` — first-fit contiguous |
| `configs/slicing.yml` | full | Slice S-NSSAI example (sst/sd only) |
| `configs/gnb_rf_b200_tdd_n78_20mhz.yml` | full | Default gNB: 20MHz, 51 PRBs, no slicing |
