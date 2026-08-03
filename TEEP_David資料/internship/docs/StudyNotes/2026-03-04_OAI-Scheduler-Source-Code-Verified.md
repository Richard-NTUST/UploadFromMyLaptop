# OAI gNB Scheduler Architecture — Source-Code-Verified Reference

**Date**: 2026-03-04
**Method**: Every claim in this note is backed by actual source code reads from the OAI GitLab `develop` branch (`openair2/LAYER2/NR_MAC_gNB/`). This serves as the OAI counterpart to the [03-03 srsRAN Scheduler Source-Code-Verified note](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md).
**Prerequisites**: [02-24 MAC Scheduler Modules](./2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md), [03-03 srsRAN Reference](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md)

---

## 0. Key Architectural Difference from srsRAN

> **OAI uses a single-pass algorithm, NOT a two-stage pipeline.**

| Aspect | srsRAN | OAI |
|--------|--------|-----|
| Architecture | Two-stage: Policy → Grid Allocator | Single-pass: PF sorts UEs, then greedy contiguous allocation |
| Policy abstraction | `scheduler_policy` interface with factory | No policy abstraction — PF is hardcoded in `pf_dl()` |
| Slicing | `inter_slice_scheduler` + per-slice policies | No slicing framework in MAC scheduler |
| FD allocator | VRB bitmap with `recommended_vrbs()` | `rballoc_mask[]` bitmap with `nr_find_nb_rb()` |
| Scheduling algorithm choice | `rr_sched:` or `qos_sched:` YAML | Only Proportional Fair (hardcoded) |

---

## 1. Complete Call Chain (Verified from Source)

```
gNB_dlsch_ulsch_scheduler()                          ← gNB_scheduler.c : top-level per-slot entry
  ├─ memset(vrb_map, 0)                              ← clear VRB maps for all beams
  ├─ schedule_nr_mib()                               ← MIB/BCH scheduling
  ├─ schedule_nr_sib1()                              ← SIB1 scheduling
  ├─ schedule_nr_prach()                             ← PRACH occasions
  ├─ nr_csirs_scheduling()                           ← CSI-RS (marks VRBs)
  ├─ nr_csi_meas_reporting()                         ← CSI measurement
  ├─ nr_schedule_srs()                               ← SRS scheduling
  ├─ nr_schedule_RA()                                ← Random Access response
  ├─ nr_schedule_ulsch()                             ← UL scheduling
  └─ nr_schedule_ue_spec()                           ← DL user-specific scheduling
       └─ gNB_mac->pre_processor_dl()                ← function pointer → nr_dlsch_preprocessor()
            └─ nr_dlsch_preprocessor()               ← gNB_scheduler_dlsch.c
                 ├─ n_rb_sched[beam] = bw            ← sets available RBs = carrier bandwidth
                 ├─ max_sched_ues = bw / (avg_agg × 6) ← max UEs limited by PDCCH capacity
                 └─ pf_dl()                          ← the PF scheduling algorithm
                      ├─ update_dlsch_buffer()       ← compute num_total_bytes from LC queues
                      ├─ PF coefficient = tbs / dl_thr_ue  ← proportional fair metric
                      ├─ qsort(UE_sched, comparator) ← sort UEs by descending PF coefficient
                      └─ for each UE (sorted):
                           ├─ scan rballoc_mask[]    ← find first free contiguous RBs
                           ├─ nr_find_nb_rb()        ← binary search for optimal RB count
                           ├─ mark rballoc_mask[]    ← reserve allocated RBs
                           └─ populate sched_pdsch   ← rbStart, rbSize, MCS, TBS
```

**Source files**:
- `gNB_scheduler.c` — top-level slot loop
- `gNB_scheduler_dlsch.c` — `nr_dlsch_preprocessor()`, `pf_dl()`, `nr_schedule_ue_spec()`, `prepare_pdsch_pdu()`
- `gNB_scheduler_primitives.c` — `nr_find_nb_rb()`, `set_pdcch_structure()`

---

## 2. Top-Level Scheduler — `gNB_dlsch_ulsch_scheduler()`

**File**: `gNB_scheduler.c`

This function is called once per slot. It holds the scheduler mutex for the entire duration:

```c
void gNB_dlsch_ulsch_scheduler(gNB_MAC_INST *gNB_mac, frame_t frame, sub_frame_t slot)
{
  NR_SCHED_LOCK(&gNB->sched_lock);    // mutex lock

  // Clear VRB maps for all beams
  for (int i = 0; i < num_beams; i++)
    memset(cc[CC_id].vrb_map[i], 0, sizeof(uint16_t) * MAX_BWP_SIZE);

  // Sequential scheduling stages (order matters — each reserves VRBs)
  schedule_nr_mib(gNB_mac, frame, slot);
  schedule_nr_sib1(gNB_mac, frame, slot);
  schedule_nr_prach(gNB_mac, frame, slot);
  nr_csirs_scheduling(gNB_mac, frame, slot, num_beams);     // CSI-RS reserves VRBs
  nr_csi_meas_reporting(gNB_mac, frame, slot);
  nr_schedule_srs(gNB_mac, frame, slot);
  nr_schedule_RA(gNB_mac, frame, slot);
  nr_schedule_ulsch(gNB_mac, frame, slot, num_beams);        // UL scheduling
  nr_schedule_ue_spec(gNB_mac, frame, slot, num_beams);      // DL user scheduling (LAST)

  NR_SCHED_UNLOCK(&gNB->sched_lock);  // mutex unlock
}
```

### Why Order Matters

DL user scheduling (`nr_schedule_ue_spec`) runs **last**. By this point, the `vrb_map[]` already has bits set by SIB1, CSI-RS, PDCCH CORESETs, etc. The PF allocator sees only the remaining free RBs.

---

## 3. The Preprocessor — `nr_dlsch_preprocessor()`

**File**: `gNB_scheduler_dlsch.c`

This function bridges the entry point `nr_schedule_ue_spec()` and the PF algorithm:

```c
static void nr_dlsch_preprocessor(gNB_MAC_INST *mac, post_process_pdsch_t *pdsch)
{
  // Available bandwidth per beam = full carrier BW
  int n_rb_sched[num_beams];
  for (int i = 0; i < num_beams; i++)
    n_rb_sched[i] = bw;    // e.g., 273 for 100 MHz at SCS 30 kHz

  // Maximum number of UEs we can schedule in this slot
  // Limited by PDCCH CCE capacity
  int max_sched_ues = bw / (average_agg_level * NR_NB_REG_PER_CCE);

  // Build UE list from connected UEs
  NR_UE_info_t *UE_list[MAX_MOBILES_PER_GNB];
  int num_ue = build_ue_list(mac, UE_list);

  // Run PF algorithm
  pf_dl(mac, pdsch, UE_list, max_sched_ues, num_beams, n_rb_sched);
}
```

### Configuration Impact

- `n_rb_sched` starts at the **full carrier bandwidth** (e.g., 273 RBs). There is no config knob to limit this.
- `max_sched_ues` is implicitly limited by PDCCH CCE resources.
- `NR_NB_REG_PER_CCE = 6` (from 3GPP TS 38.211).

---

## 4. The PF Algorithm — `pf_dl()` (Core of OAI Scheduling)

**File**: `gNB_scheduler_dlsch.c`

This is the **only** DL scheduling algorithm in OAI. There is no policy factory or alternative algorithms.

### 4.1 Function Signature

```c
static void pf_dl(gNB_MAC_INST *mac,
                  post_process_pdsch_t *pp_pdsch,
                  NR_UE_info_t **UE_list,
                  int max_num_ue,
                  int num_beams,
                  int n_rb_sched[num_beams])
```

### 4.2 Step 1 — Buffer Update

```c
update_dlsch_buffer(mac, UE);
```

This iterates over all activated Logical Channels and sums their `bytes_in_buffer`:

```c
void update_dlsch_buffer(gNB_MAC_INST *mac, NR_UE_info_t *UE)
{
  NR_UE_sched_ctrl_t *sched_ctrl = &UE->UE_sched_ctrl;
  sched_ctrl->num_total_bytes = 0;
  sched_ctrl->dl_lc_num = 0;

  for (int lcid = 0; lcid < MAX_LC_NUM; lcid++) {
    if (sched_ctrl->dl_lc_bytes[lcid] > 0) {
      sched_ctrl->num_total_bytes += sched_ctrl->dl_lc_bytes[lcid];
      sched_ctrl->dl_lc_ids[sched_ctrl->dl_lc_num++] = lcid;
    }
  }
}
```

### 4.3 Step 2 — PF Coefficient Computation

For each UE with pending data (`num_total_bytes > 0`), OAI computes a hypothetical TBS for 1 RB over 10 slots:

```c
// Hypothetical TBS for 1 RB (to normalize across MCS/layers)
int tbs = nr_compute_tbs(sched_pdsch.Qm,           // modulation order
                         sched_pdsch.R,             // target code rate
                         1,                         // 1 hypothetical RB
                         tda_info.nrOfSymbols,      // symbols in TDA
                         dmrs_parms.N_PRB_DMRS * dmrs_parms.N_DMRS_SLOT,
                         0, 0,                      // overhead
                         sched_pdsch.nrOfLayers)
              * 10;  // × 10 slots normalizer

// PF coefficient
float coeff_ue = (float)tbs / UE->dl_thr_ue;
```

Where `dl_thr_ue` is the exponentially-weighted moving average (EWMA) throughput:

```c
// After each scheduling decision:
float a = 0.01f;   // smoothing factor (hardcoded)
UE->dl_thr_ue = (1 - a) * UE->dl_thr_ue + a * b;
// b = scheduled bytes if UE was served, 0 otherwise
```

**Interpretation**: A UE with high estimated rate (`tbs`) but low historical throughput (`dl_thr_ue`) gets a high PF coefficient → is scheduled first. This is standard Proportional Fair behavior.

### 4.4 Step 3 — UE Sorting

```c
qsort(UE_sched, numUE, sizeof(UEsched_t), comparator);
```

The comparator sorts by **descending PF coefficient**. The UE with the highest `coeff_ue` is served first.

### 4.5 Step 4 — Greedy Contiguous PRB Allocation

For each sorted UE, OAI scans the `rballoc_mask[]` bitmap to find a contiguous block of free RBs:

```c
// Find first free RB
uint16_t rbStart = 0;
while (rbStart < rbStop && (rballoc_mask[rbStart + bwp_start] & slbitmap))
  rbStart++;

// Find contiguous free block size
int max_rbSize = 1;
while (rbStart + max_rbSize <= rbStop
       && !(rballoc_mask[rbStart + max_rbSize + bwp_start] & slbitmap))
  max_rbSize++;
```

Then `nr_find_nb_rb()` performs a binary search within `[min_rbSize, max_rbSize]` to find the optimal number of RBs that fits the UE's buffer:

```c
const int min_rbSize = 5;  // hardcoded minimum

nr_find_nb_rb(sched_pdsch.Qm,           // Qm
              sched_pdsch.R,             // code rate
              1,                         // transform precoding disabled
              sched_pdsch.nrOfLayers,    // layers
              tda_info.nrOfSymbols,      // OFDM symbols
              dmrs_parms.N_PRB_DMRS * dmrs_parms.N_DMRS_SLOT,  // DMRS overhead
              sched_ctrl->num_total_bytes + oh,  // bytes to transport
              min_rbSize,                // min RBs
              max_rbSize,                // max RBs (from contiguous scan)
              &sched_pdsch.tb_size,      // output: TBS
              &sched_pdsch.rbSize);      // output: actual RBs allocated
```

After allocation, the VRB map is marked:

```c
for (int rb = 0; rb < sched_pdsch->rbSize; rb++)
  vrb_map[rb + sched_pdsch->rbStart + bwp_start] |= SL_to_bitmap(...);
```

---

## 5. Binary Search — `nr_find_nb_rb()`

**File**: `gNB_scheduler_primitives.c`

This function determines the minimum number of RBs needed to transport `bytes` worth of data:

```c
bool nr_find_nb_rb(uint16_t Qm, uint16_t R, long transform_precoding,
                   uint8_t nrOfLayers, uint16_t nb_symb_sch,
                   uint16_t nb_dmrs_prb, uint32_t bytes,
                   uint16_t nb_rb_min, uint16_t nb_rb_max,
                   uint32_t *tbs, uint16_t *nb_rb)
{
  // Check if maximum is enough
  *nb_rb = nb_rb_max;
  *tbs = nr_compute_tbs(Qm, R, *nb_rb, nb_symb_sch, nb_dmrs_prb, 0, 0, nrOfLayers) >> 3;
  if (bytes > *tbs)
    return false;     // not enough RBs even at max
  if (bytes == *tbs)
    return true;      // exact fit

  // Check if minimum is enough
  *nb_rb = nb_rb_min;
  *tbs = nr_compute_tbs(Qm, R, *nb_rb, nb_symb_sch, nb_dmrs_prb, 0, 0, nrOfLayers) >> 3;
  if (bytes <= *tbs)
    return true;      // min RBs already sufficient

  // Binary search between [nb_rb_min, nb_rb_max]
  int hi = nb_rb_max;
  int lo = nb_rb_min;
  for (int p = (hi + lo) / 2; lo + 1 < hi; p = (hi + lo) / 2) {
    const uint32_t TBS = nr_compute_tbs(Qm, R, p, nb_symb_sch, nb_dmrs_prb, 0, 0, nrOfLayers) >> 3;
    if (bytes == TBS) { hi = p; break; }
    else if (bytes < TBS) { hi = p; }
    else { lo = p; }
  }

  *nb_rb = hi;
  *tbs = nr_compute_tbs(Qm, R, *nb_rb, nb_symb_sch, nb_dmrs_prb, 0, 0, nrOfLayers) >> 3;
  return *tbs >= bytes && *nb_rb <= nb_rb_max;
}
```

**Key behavioral note**: The function returns `false` if the buffer can't fit in `nb_rb_max` RBs. When this happens, the UE still gets `nb_rb_max` RBs (the maximum contiguous block) — partial transmission with segmentation.

---

## 6. FAPI PDU Construction — `prepare_pdsch_pdu()`

**File**: `gNB_scheduler_dlsch.c`

After `pf_dl()` sets `rbStart` and `rbSize`, the PDU is built for the FAPI interface:

```c
void prepare_pdsch_pdu(/* ... */)
{
  pdsch_pdu->resourceAlloc = 1;       // Resource Allocation Type 1 (contiguous)
  pdsch_pdu->rbStart = sched_pdsch->rbStart;
  pdsch_pdu->rbSize = sched_pdsch->rbSize;
  pdsch_pdu->VRBtoPRBMapping = 0;     // Non-interleaved mapping
  pdsch_pdu->mcsIndex[0] = sched_pdsch->mcs;
  pdsch_pdu->nrOfLayers = sched_pdsch->nrOfLayers;
  // ...
}
```

**Enforced constraint** (assertion in source):

```c
AssertFatal(pdsch_Config == NULL ||
  pdsch_Config->resourceAllocation == NR_PDSCH_Config__resourceAllocation_resourceAllocationType1,
  "Only resource allocation type 1 is supported");
```

This means OAI **only supports RA Type 1** (contiguous RB allocation). RA Type 0 (bitmap-based non-contiguous) is not implemented.

---

## 7. Retransmission Handling — `allocate_dl_retransmission()`

**File**: `gNB_scheduler_dlsch.c`

Retransmissions are handled **before** new transmissions in `nr_schedule_ue_spec()`:

```c
// In nr_schedule_ue_spec():
UE_iterator(mac->UE_info.connected_ue_list, UE) {
  // 1. Handle retransmissions first
  allocate_dl_retransmission(mac, frame, slot, UE, beam_idx);
  // 2. Then new transmissions via pre_processor_dl (→ pf_dl)
}
```

The retransmission allocator scans for free RBs using the same `rballoc_mask[]` mechanism:

```c
static void allocate_dl_retransmission(/* ... */)
{
  // Find free contiguous RBs in rballoc_mask
  uint16_t rbStart = 0;
  while (rbStart < bwpSize && (vrb_map[rbStart + bwpStart] & slbitmap))
    rbStart++;

  // Try to match the original TBS with nr_find_nb_rb()
  nr_find_nb_rb(/* same params as pf_dl, targeting original tb_size */);
}
```

Retransmissions take priority because they run first and consume VRBs before `pf_dl()` sees them.

---

## 8. VRB Map — The Shared Frequency-Domain Resource

The `vrb_map[]` is a `uint16_t` array indexed by PRB position. Each bit in the 16-bit word represents an OFDM symbol (via `SL_to_bitmap()`). This allows symbol-level granularity:

```c
// Mark RBs as used
vrb_map[rb + bwp_start] |= SL_to_bitmap(startSymbol, nrOfSymbols);

// Check if RB is free
if (rballoc_mask[rb + bwp_start] & slbitmap) {
  // RB is occupied
}
```

### VRB Map Lifecycle per Slot

1. **Clear**: `memset(vrb_map, 0, ...)` at start of `gNB_dlsch_ulsch_scheduler()`
2. **Reserve**: SIB1, CSI-RS, PDCCH CORESETs mark their VRBs
3. **Allocate**: `pf_dl()` fills remaining VRBs for user data
4. **Next slot**: Map is cleared again

---

## 9. How Time-Frequency Domain Scheduling Works in OAI

### 9.1 Current Default: Full-Bandwidth FDM

By default, each UE gets as many **contiguous** RBs as it needs (up to the full carrier BW). With multiple UEs, each gets a contiguous block starting from the first free RB:

```
UE1: |###########|              |  ← rbStart=0, rbSize=100
UE2:             |#########|   |  ← rbStart=100, rbSize=80
UE3:                       |###|  ← rbStart=180, rbSize=30
     0          100       180 210  273
                    ← Frequency (PRBs) →
```

This is **Frequency-Division Multiplexing (FDM)**: all UEs share a single slot, each in a different frequency band.

### 9.2 How to Enable TDM-like Behavior

OAI has **no built-in config knob** for TDM scheduling. To achieve TDM (each UE gets the full bandwidth but in separate slots), you would need to:

#### Option A: Cap `max_rbSize` in `pf_dl()` (Source Modification)

In `pf_dl()`, after the contiguous block scan, limit the maximum size:

```c
// After finding max_rbSize from rballoc_mask scan:
max_rbSize = min(max_rbSize, custom_cap);  // e.g., cap at 27 RBs
```

This forces each UE to occupy only a fraction of the bandwidth, effectively creating TDM patterns over time (the first UE in one slot, the next UE in another, etc.).

#### Option B: Pre-mask `rballoc_mask[]` (Source Modification)

Zero out portions of `rballoc_mask[]` before `pf_dl()` runs, restricting available bandwidth per scheduling occasion.

#### Option C: Limit `max_num_ue` to 1

Set `max_sched_ues = 1` in `nr_dlsch_preprocessor()` to allow only one UE per slot. This is true TDM but wastes bandwidth when the UE doesn't need it all.

### 9.3 Contrast with srsRAN

| Feature | srsRAN | OAI |
|---------|--------|-----|
| FDM/TDM switch | `max_prb_policy_ratio` YAML config | No config — source code change required |
| FDM example | `max_prb_policy_ratio: 100` → 273×1 UE | Default behavior (no change) |
| TDM example | `max_prb_policy_ratio: 10` → ~27 RBs per UE | Modify `max_rbSize` cap in `pf_dl()` |
| Intermediate | Any value 1–100 creates spectrum-sharing ratio | Must edit source code |

---

## 10. Configuration Knobs (What CAN Be Changed Without Source Mods)

### 10.1 Carrier Bandwidth

Configured in the OAI config file (e.g., `gnb.conf`) via `dl_carrierBandwidth`:

```conf
servingCellConfigCommon = (
{
    dl_carrierBandwidth = 273;   # 100 MHz at SCS 30 kHz
    # ...
}
);
```

This sets the `bw` variable in `nr_dlsch_preprocessor()`, which becomes `n_rb_sched`.

### 10.2 MCS and BLER

MCS is auto-selected via `get_mcs_from_bler()`, an outer-loop link adaptation. Configurable targets:

```conf
dl_bler_target_upper = 0.15;
dl_bler_target_lower = 0.05;
dl_max_mcs = 28;
```

### 10.3 `phy_test` Mode

Enables a fixed MCS / fixed allocation mode (not PF-scheduled):

```conf
phy_test = 1;
```

In this mode, the scheduler bypasses `pf_dl()` and uses a fixed allocation for testing.

### 10.4 Number of Layers

Determined by CSI reporting (RI) — not directly configurable as a scheduler parameter.

---

## 11. Summary — Answering the Professor's Question

> **"How to enable time-frequency domain scheduling in OAI?"**

### What OAI Does Today

1. **Frequency domain**: PF greedy allocator in `pf_dl()` assigns contiguous RBs from `rballoc_mask[]`. This is FDM by default.
2. **Time domain**: PF coefficient (`tbs / dl_thr_ue`) determines UE priority across slots. UEs with low historical throughput get higher priority in future slots — this is implicit TDM via PF fairness.

### What OAI Does NOT Have

- No explicit TDM/FDM config switch (unlike srsRAN's `max_prb_policy_ratio`)
- No scheduler policy factory (PF is hardcoded)
- No slicing framework
- No RA Type 0 (bitmap) — only RA Type 1 (contiguous)

### To Explicitly Enable TDM

Requires source code modification in `gNB_scheduler_dlsch.c`:
1. Cap `max_rbSize` in `pf_dl()`, OR
2. Pre-mask `rballoc_mask[]` in `nr_dlsch_preprocessor()`, OR
3. Set `max_sched_ues = 1` for strict single-UE-per-slot TDM

---

## 12. Corrections to February 24 Note

The [02-24 note](./2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md) contained simplified/illustrative code snippets. Corrections based on verified source:

| Claim in 02-24 Note | Verified Reality |
|---------------------|------------------|
| `UE->dl_thr_ue` averaging uses `a = 0.1` | Actually `a = 0.01f` (much slower adaptation) |
| `nr_schedule_ue_spec` calls `pf_dl` directly | Actually calls `pre_processor_dl()` → `nr_dlsch_preprocessor()` → `pf_dl()` |
| "OAI supports multiple scheduling algorithms" | Only PF is implemented; function pointer exists but no alternatives |
| `rballoc_mask` described as "1D array" | It's `uint16_t[]` with per-symbol bits (16-bit bitmask per PRB) |
| "RA Type 0 can be configured" | Source has `AssertFatal` enforcing RA Type 1 only |

---

## 13. File Reference

| File | Path (OAI GitLab `develop`) | Key Functions |
|------|----------------------------|---------------|
| `gNB_scheduler.c` | `openair2/LAYER2/NR_MAC_gNB/` | `gNB_dlsch_ulsch_scheduler()` |
| `gNB_scheduler_dlsch.c` | `openair2/LAYER2/NR_MAC_gNB/` | `pf_dl()`, `nr_dlsch_preprocessor()`, `nr_schedule_ue_spec()`, `prepare_pdsch_pdu()`, `allocate_dl_retransmission()`, `update_dlsch_buffer()` |
| `gNB_scheduler_primitives.c` | `openair2/LAYER2/NR_MAC_gNB/` | `nr_find_nb_rb()`, `set_pdcch_structure()`, `get_mcs_from_bler()` |
| `gNB_scheduler_ulsch.c` | `openair2/LAYER2/NR_MAC_gNB/` | `nr_schedule_ulsch()` (UL counterpart, uses `pf_ul()`) |

---

*This note is part of the TEEP Probation research project. All code references are from the OAI `develop` branch as of March 2026.*
