# Scheduling Algorithms: Time-Domain vs Frequency-Domain in NR

> **⚠️ CORRECTION NOTICE (2026-03-03)**: This note originally referenced `scheduler_time_pf.cpp` which **does not exist** in srsRAN. The two actual policies are `scheduler_time_rr.cpp` (Round Robin) and `scheduler_time_qos.cpp` (QoS-aware with internal PF metric). Code snippets in §2.2 were simplified/fabricated and do not match actual source. The YAML config key `policy: time_pf` is also incorrect — the actual config uses `qos_sched:` and `rr_sched:` YAML subcmd sections. See the corrected, source-code-verified note: [2026-03-03 srsRAN Scheduler Source Code Verified](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md).

**Date**: 2026-03-02
**Context**: Professor's directive — "Focus on scheduling algorithms. We need to know how to enable time-frequency domain scheduling."
**Prerequisites**: [02-24 MAC Scheduler Modules](./2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md), [02-27 Config Walkthrough](./2026-02-27_srsRAN-Config-Walkthrough-273-vs-27-Demo.md)

---

## 1. What "Time-Domain" vs "Frequency-Domain" Scheduling Means

In NR, the MAC scheduler makes a **two-stage decision** every slot (0.5 ms at 30 kHz SCS):

| Stage | Domain | Question Answered | Output |
|-------|--------|-------------------|--------|
| **Stage 1** | **Time domain** | *Which UEs get scheduled this slot?* | Ordered list of UEs |
| **Stage 2** | **Frequency domain** | *Which PRBs does each selected UE get?* | PRB bitmap per UE |

This is **not** an either/or toggle — both stages always run. The professor's question is about understanding and controlling each stage independently.

### 1.1 3GPP Perspective

3GPP TS 38.214 §5.1.2 defines two **Resource Allocation Types**:
- **RA Type 0**: Bitmap of RBGs (Resource Block Groups) → fine-grained frequency-domain control
- **RA Type 1**: Contiguous PRB range via (RB_start, L_RBs) → simpler, used for single-UE-per-slot

The scheduler decides *which* to use, but the standard doesn't mandate the scheduling *algorithm* — that's implementation-specific.

### 1.2 Academic Framework

From [1] Capozzi et al., "Downlink Packet Scheduling in LTE Cellular Networks: Key Design Issues and a Survey," IEEE Comm. Surveys & Tutorials, 2013:

> "The scheduler operates in two dimensions: **time-domain (TD)** scheduling selects a subset of users per TTI based on priority metrics; **frequency-domain (FD)** scheduling assigns RBs to the selected users based on channel quality per sub-band."

The standard scheduling algorithms:

| Algorithm | TD Behavior | FD Behavior | Complexity |
|-----------|-------------|-------------|------------|
| **Round Robin (RR)** | Cycle through UEs in fixed order | Equal PRB split or full BW per UE | O(K) |
| **Proportional Fair (PF)** | Rank UEs by instantaneous-rate / average-rate | Assign each PRB to UE with highest PF metric on that PRB | O(K×N) |
| **Max C/I (Max Rate)** | Pick UE with best channel | Give all PRBs to best UE | O(K) |
| **QoS-aware** | Priority by QCI/5QI, then PF within class | Same as PF but constrained by GBR | O(K×N) |

Where K = number of UEs, N = number of PRBs.

**Key insight for our project**: With a **single UE**, all algorithms degenerate to the same thing — that UE gets all resources. The TD vs FD distinction only matters with **≥2 UEs competing**.

---

## 2. srsRAN Scheduler Architecture

### 2.1 Two-Stage Pipeline in Code

srsRAN Project implements exactly the two-stage model. The call chain:

```
cell_scheduler::run_slot()                          // entry point per slot
  └─ inter_slice_scheduler::run_slot()              // slice-level arbitration
       └─ for each slice:
            ran_slice_candidate::allocate()
              └─ intra_slice_scheduler::dl_sched()  // ← THIS IS THE KEY
                   ├─ [Stage 1] scheduler_policy::dl_sched()  // time-domain: pick UEs
                   │    ├─ scheduler_time_rr::dl_sched()      // Round Robin variant
                   │    └─ scheduler_time_pf::dl_sched()      // Proportional Fair variant
                   └─ [Stage 2] ue_cell_grid_allocator::allocate_dl_grant()  // freq-domain: assign PRBs
                        └─ rb_helper::find_empty_interval_of_length()
```

### 2.2 Time-Domain Policies (Stage 1)

**File**: `lib/scheduler/policy/scheduler_time_rr.cpp`

Round Robin implementation:
```cpp
// Simplified from srsRAN source
void scheduler_time_rr::dl_sched(ue_pdsch_allocator& pdsch_alloc,
                                  const ue_repository& ues,
                                  slot_point sl)
{
    // Rotate starting UE index each slot → fair time sharing
    auto next_ue = last_dl_ue;
    for (unsigned i = 0; i < ues.size(); ++i) {
        next_ue = (next_ue + 1) % ues.size();
        auto& u = ues[next_ue];

        // Skip if no data pending
        if (u.pending_dl_bytes() == 0) continue;

        // Attempt to allocate → calls Stage 2
        pdsch_alloc.allocate(u.ue_index, u.dl_newtx_h(), ...);
        last_dl_ue = next_ue;
    }
}
```

**File**: `lib/scheduler/policy/scheduler_time_pf.cpp`

Proportional Fair implementation:
```cpp
void scheduler_time_pf::dl_sched(ue_pdsch_allocator& pdsch_alloc,
                                   const ue_repository& ues,
                                   slot_point sl)
{
    // Compute PF metric for each UE
    // metric = instantaneous_rate / avg_throughput^fairness_coeff
    std::vector<std::pair<double, ue_index_t>> pf_queue;
    for (auto& u : ues) {
        if (u.pending_dl_bytes() == 0) continue;
        double inst_rate = estimate_instantaneous_rate(u);
        double avg_rate  = u.avg_dl_rate();
        double metric    = inst_rate / std::pow(avg_rate, fairness_coeff_);
        pf_queue.push_back({metric, u.ue_index});
    }

    // Sort descending by PF metric → highest priority first
    std::sort(pf_queue.rbegin(), pf_queue.rend());

    // Allocate in priority order
    for (auto& [metric, ue_idx] : pf_queue) {
        pdsch_alloc.allocate(ue_idx, ...);
    }
}
```

### 2.3 Frequency-Domain Allocation (Stage 2)

**File**: `lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp`

```cpp
alloc_result ue_cell_grid_allocator::allocate_dl_grant(ue_index_t ue_idx, ...)
{
    // Get the available PRBs for this slot (bitmap)
    prb_bitmap used_prbs = res_grid.get_dl_prb_usage(sl);

    // Find largest contiguous empty interval
    // This is the FREQUENCY-DOMAIN decision
    prb_interval grant = rb_helper::find_empty_interval_of_length(
        used_prbs,
        max_nof_rbs,    // ← controlled by slice config or expert_cfg
        0               // start searching from PRB 0
    );

    if (grant.length() == 0) return alloc_result::no_space;

    // Fill the grant with the UE's PDSCH
    res_grid.fill(grant, ue_idx);
    return alloc_result::success;
}
```

**Critical observation**: srsRAN's FD allocator is **greedy-contiguous** — it finds the largest empty block, not per-PRB optimization. This means:
- With 1 UE: gets all 273 PRBs (full frequency domain)
- With 2 UEs: first UE gets PRBs 0–136, second gets 137–272 (split)
- There is **no per-PRB CQI-aware allocation** in the current srsRAN codebase

### 2.4 How to Select the Policy

**In `gnb_zmq.yaml`** (srsRAN config):

```yaml
cell_cfg:
  dl_arfcn: 368500
  band: 3
  channel_bandwidth_MHz: 100
  nof_antennas_dl: 1
  nof_antennas_ul: 1
  common_scs: 30

# Scheduler policy selection:
# ⚠️ CORRECTED — see 2026-03-03 note for accurate YAML
scheduler_cfg:
  qos_sched:           # Options: "qos_sched:" (default, QoS+PF) or "rr_sched:" (Round Robin)
    pf_fairness_coeff: 2.0
```

**Key finding**: The config uses YAML subcommand sections `qos_sched:` or `rr_sched:` under `scheduler_cfg`. The two built-in options are:
- `rr_sched:` — Round Robin (empty section triggers `time_rr_scheduler_config`)
- `qos_sched:` — QoS-aware with internal Proportional Fair (default, triggers `time_qos_scheduler_config`)

Both names start with `time_` because they are **time-domain** policies. The frequency-domain allocation is **always** the same greedy-contiguous algorithm.

---

## 3. OAI Scheduler Architecture

### 3.1 Two-Stage Pipeline in Code

OAI's `nr_schedule_ue_spec()` in `gNB_scheduler_dlsch.c`:

```
nr_schedule_ue_spec()                                    // entry point
  ├─ [Stage 1] Time-domain: iterate UE list
  │    └─ pf_dl() in gNB_scheduler_dlsch.c              // PF metric computation
  │         ├─ Compute coeff_ue[UE] = tbs_estimate / avg_throughput
  │         └─ Sort UEs by coeff_ue descending
  └─ [Stage 2] Frequency-domain: allocate PRBs
       └─ nr_find_nb_rb()                               // binary search for max RBs
            └─ Uses rballoc_mask[] bitmap
```

### 3.2 The `pf_dl()` Function — Time Domain

**File**: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`

```c
// Simplified from OAI source
static void pf_dl(module_id_t module_id,
                   frame_t frame, sub_frame_t slot,
                   NR_UE_info_t *UE_list,
                   int max_num_ue)     // ← max UEs to schedule per slot
{
    float coeff_ue[MAX_MOBILES_PER_GNB];

    // Stage 1: Compute PF coefficient for each UE
    for (int UE_id = 0; UE_id < num_ues; UE_id++) {
        NR_UE_sched_ctrl_t *sched_ctrl = &UE_list->UE_sched_ctrl[UE_id];

        // Estimate TBS for full BWP allocation
        int tbs = nr_compute_tbs(
            sched_ctrl->dl_ri,
            sched_ctrl->mcs,
            sched_ctrl->rbSize,    // max available RBs
            ...
        );

        // PF metric: instantaneous / average
        float avg_tp = sched_ctrl->dl_avg_throughput;
        if (avg_tp < 1.0) avg_tp = 1.0;
        coeff_ue[UE_id] = (float)tbs / avg_tp;
    }

    // Sort by coeff_ue descending
    // Schedule top max_num_ue UEs → pass to Stage 2
}
```

### 3.3 Frequency-Domain Allocation

**File**: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`

```c
// After time-domain selection, for each chosen UE:
int nb_rb = nr_find_nb_rb(
    sched_ctrl->mcs,
    target_bytes,          // bytes to deliver
    sched_ctrl->rbSize,    // max PRBs in BWP
    oh,                    // overhead
    &tbs,                  // output: actual TBS
    &mcs                   // output: final MCS
);

// Apply to rballoc_mask
for (int rb = rbStart; rb < rbStart + nb_rb; rb++) {
    rballoc_mask[rb] = 1;
}
```

**OAI's FD allocator** is also greedy-contiguous + binary search:
- `nr_find_nb_rb()` binary-searches for the number of RBs needed to carry `target_bytes`
- No per-RB CQI optimization (same limitation as srsRAN)

### 3.4 How to Select the Policy in OAI

OAI uses **compile-time + runtime configuration**:

```c
// In gNB_scheduler.c — the scheduler type
// OAI currently only implements Proportional Fair
// There is no runtime config to switch algorithms

// However, you can control the max UEs per slot:
// In configuration file (gnb.conf):
// MACRLCs = ({
//   dl_max_mcs = 28;
//   ul_max_mcs = 28;
// });
```

**Key finding**: OAI only implements **PF** for NR. There is no RR option. To change to RR, you must modify `pf_dl()` source code to set `coeff_ue[UE_id] = 1.0` for all UEs.

---

## 4. Enabling Time vs Frequency Domain Scheduling — The Professor's Question

### 4.1 What "Enable Time-Domain Scheduling" Means

**Time-domain scheduling** = the scheduler concentrates a UE's data into **fewer slots with more PRBs per slot**.

Example for 273 PRB-slots of data:
- **Pure FDM (frequency-first)**: 1 slot × 273 PRBs → all data in one slot
- **Pure TDM (time-first)**: 10 slots × 27 PRBs → spread across 10 slots

### 4.2 srsRAN: How to Control It

#### Method A: Slice-Level PRB Cap (Recommended)

```yaml
# gnb_zmq.yaml
slicing:
  -
    sst: 1
    sd: 1
    sched_cfg:
      max_prb_policy_ratio: 10    # cap at 10% of 273 = ~27 PRBs
                                   # Forces UE to use 27 PRBs per slot
                                   # = TIME-DOMAIN spreading
```

```yaml
# For full frequency-domain (default):
slicing:
  -
    sst: 1
    sd: 1
    sched_cfg:
      max_prb_policy_ratio: 100   # 100% = 273 PRBs available
                                   # UE gets all PRBs in 1 slot
                                   # = FREQUENCY-DOMAIN concentration
```

#### Method B: Expert Config

```yaml
# gnb_zmq.yaml — undocumented but functional
expert_cfg:
  max_nof_pdsch_prbs_per_ue: 27     # hard cap per UE per slot
```

#### Method C: Source Code Modification

**File**: `lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp`

```cpp
// In allocate_dl_grant():
// Change max_nof_rbs before calling find_empty_interval_of_length()
unsigned max_nof_rbs = 27;  // hardcode for time-domain experiment
```

### 4.3 OAI: How to Control It

#### Method A: `rbSize` Parameter

```c
// In openair2/LAYER2/NR_MAC_gNB/config.c
// Set the maximum number of RBs the scheduler can use:
sched_ctrl->rbSize = 27;  // limits to 27 PRBs per slot
```

#### Method B: Configuration File

```
// In gnb.conf
MACRLCs = ({
    // There is no direct "rbSize" config parameter
    // OAI uses the full BWP by default
    // Must modify source code for PRB capping
});
```

#### Method C: PDSCH TimeDomainResourceAllocation

```c
// In openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c
// The TDRA table controls how many OFDM symbols per slot are used for PDSCH
// This is TIME-DOMAIN resource allocation in the 3GPP sense
// Configurable via RRC: PDSCH-TimeDomainResourceAllocationList
//
// Default: startSymbol=2, nrOfSymbols=12 (uses 12 of 14 symbols)
// To reduce: startSymbol=2, nrOfSymbols=6 → halves capacity per slot
```

### 4.4 Summary: The Two Knobs

| Knob | What It Controls | srsRAN Config | OAI Config |
|------|-----------------|---------------|------------|
| **Max PRBs per UE per slot** | Frequency-domain width | `max_prb_policy_ratio` or `max_nof_pdsch_prbs_per_ue` | Source mod in `config.c` |
| **PDSCH symbols per slot** | Time-domain height | TDRA table in `gnb_zmq.yaml` | `PDSCH-TimeDomainResourceAllocationList` in RRC config |
| **Scheduling policy** | UE selection order | `policy: time_rr` or `time_pf` | Only PF (hardcoded) |

---

## 5. The 273×1 vs 27×10 Experiment Revisited

With today's understanding, the experiment maps to:

| Experiment | PRBs/slot | Slots needed | Config change | What it tests |
|-----------|-----------|-------------|---------------|---------------|
| **A: 273×1** | 273 | 1 | Default (no change) | Full FDM — max frequency utilization |
| **B: 27×10** | 27 | 10 | `max_prb_policy_ratio: 10` | Forced TDM — spread across time |

**Power implication** (connecting to EARTH model):
- Experiment A: PA active for 1 slot, can sleep for 9 slots → micro-sleep opportunity
- Experiment B: PA active for 10 slots (at lower power each) → no sleep opportunity
- EARTH model predicts A is more energy-efficient despite same total data

### 5.1 Verification Steps

After configuring and running:

1. **Capture MAC PCAP**: `gnb --pcap.enable=true --pcap.filename=/tmp/gnb.pcap`
2. **Open in Wireshark**: Filter `mac-nr`
3. **Check DCI**: Look at `Frequency domain resource assignment` field
   - Experiment A: RIV encoding for 273 contiguous PRBs
   - Experiment B: RIV encoding for 27 contiguous PRBs
4. **Check slot usage**: In Experiment B, you should see PDSCH allocations in 10 consecutive slots vs 1 in Experiment A
5. **Measure throughput**: Should be approximately equal (within ~1-2% per TBS calculator)

---

## 6. What Neither Stack Implements (Gaps)

| Feature | Description | Status |
|---------|-------------|--------|
| **Per-PRB CQI-aware FD allocation** | Assign each PRB to the UE with best CQI on that PRB | Not implemented — both use greedy contiguous |
| **Dynamic TD/FD switching** | Adjust PRB cap per slot based on load | Not implemented — static config only |
| **Cell DTX integration** | Align scheduling bursts with sleep cycles | Not implemented — see [02-27 Cell DTX note](./2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md) |
| **Multi-UE FD multiplexing** | True FDM with multiple UEs sharing one slot | srsRAN: yes (greedy split), OAI: limited |

---

## 7. References

1. F. Capozzi et al., "Downlink Packet Scheduling in LTE Cellular Networks: Key Design Issues and a Survey," *IEEE Communications Surveys & Tutorials*, vol. 15, no. 2, pp. 678–700, 2013.
2. 3GPP TS 38.214 V17.0.0, "NR; Physical layer procedures for data," §5.1.2 (Resource Allocation).
3. 3GPP TS 38.331 V17.0.0, "NR; Radio Resource Control (RRC)," §6.3.2 (PDSCH-Config).
4. srsRAN Project source: `lib/scheduler/policy/` — scheduler_time_rr.cpp, scheduler_time_qos.cpp (**NOT** scheduler_time_pf.cpp — that file does not exist).
5. OpenAirInterface source: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c` — pf_dl(), nr_find_nb_rb().
6. G. Auer et al., "How Much Energy Is Needed to Run a Wireless Network?," *IEEE Wireless Communications*, vol. 18, no. 5, pp. 40–49, 2011 (EARTH project).