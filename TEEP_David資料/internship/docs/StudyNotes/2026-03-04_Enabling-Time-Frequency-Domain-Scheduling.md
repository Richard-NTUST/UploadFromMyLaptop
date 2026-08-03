# Enabling Time-Frequency Domain Scheduling: Practical Configuration & Code-Path Guide

**Date**: 2026-03-04
**Purpose**: Side-by-side practical guide answering the professor's question for **both** OAI and srsRAN stacks.
**Prerequisites**: [03-04 OAI Verified](./2026-03-04_OAI-Scheduler-Source-Code-Verified.md), [03-03 srsRAN Verified](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md)

---

## 1. Background: What Is Time-Frequency Domain Scheduling?

In 5G NR, the MAC scheduler assigns Physical Resource Blocks (PRBs) across two dimensions:

- **Frequency domain (FD)**: Which PRBs (columns in the resource grid) a UE occupies in a given slot.
- **Time domain (TD)**: Which slots (rows) a UE is scheduled in.

The scheduler's strategy across these two dimensions determines whether UEs are multiplexed via **FDM** or **TDM**:

| Strategy | Description | PRB Usage |
|----------|-------------|-----------|
| **FDM** (Frequency-Division Multiplexing) | Multiple UEs share one slot, each using a subset of PRBs | `UE1:[0–100], UE2:[101–200], UE3:[201–273]` in slot N |
| **TDM** (Time-Division Multiplexing) | Each UE gets the full bandwidth, but in consecutive slots | `UE1: slot N (all 273)`, `UE2: slot N+1 (all 273)` |
| **Hybrid** | UEs share both time and frequency resources | Mix of partial BW and alternating slots |

---

## 2. Quick Answer Table

| Question | srsRAN | OAI |
|----------|--------|-----|
| **How to enable FDM?** | Default behavior. `max_prb_policy_ratio: 100` | Default behavior. No change needed. |
| **How to enable TDM?** | Set `max_prb_policy_ratio: 10` (or lower) in YAML | Requires source code modification (see §4) |
| **Config file?** | `gnb_ru.yml` or `gnb.yml` under `cell_cfg:` | `gnb.conf` (no scheduler tuning knobs) |
| **Scheduler algorithm?** | Choose `rr_sched:` or `qos_sched:` | Proportional Fair only (hardcoded) |
| **Policy change requires?** | YAML edit + restart | Source code edit + recompile |

---

## 3. srsRAN: Configuration-Based Control

### 3.1 The Key Knob: `max_prb_policy_ratio`

**Source**: `lib/scheduler/policy/scheduler_time_qos.cpp` — `compute_dl_prio()`

This parameter (range 1–100) sets the **percentage of carrier bandwidth** each UE can occupy:

```yaml
# In gnb.yml or gnb_ru.yml
cell_cfg:
  qos_sched:                    # or rr_sched: for round robin
    max_prb_policy_ratio: 100   # FDM: each UE gets up to 100% of BW
```

#### FDM Configuration (Default)

```yaml
cell_cfg:
  qos_sched:
    max_prb_policy_ratio: 100   # 273 × 1 UE → full BW per UE
```

Result with 3 UEs in 273-PRB carrier:
```
Slot N: [UE1: 91 PRBs][UE2: 91 PRBs][UE3: 91 PRBs]
Slot N+1: [UE1: 91 PRBs][UE2: 91 PRBs][UE3: 91 PRBs]
```

#### TDM Configuration

```yaml
cell_cfg:
  qos_sched:
    max_prb_policy_ratio: 10    # ~27 PRBs per UE → forces time spreading
```

Result: Each UE gets only ~27 PRBs per slot. With 3 UEs needing 273 PRBs worth of data, UEs "rotate" across slots:
```
Slot N:   [UE1: 27][UE2: 27][UE3: 27][    free    ]
Slot N+1: [UE1: 27][UE2: 27][UE3: 27][    free    ]
```

For strict TDM (1 UE per slot with full BW), set `max_pof_ues: 1`:

```yaml
cell_cfg:
  qos_sched:
    max_pof_ues: 1              # Only 1 UE per slot
    max_prb_policy_ratio: 100   # That UE gets full BW
```

### 3.2 Choosing the Scheduling Policy

```yaml
# Round Robin (simple fairness, no throughput optimization)
cell_cfg:
  rr_sched:
    max_prb_policy_ratio: 100

# QoS-aware with PF metric (default, recommended for energy research)
cell_cfg:
  qos_sched:
    max_prb_policy_ratio: 100
    pf_fairness_coeff: 2.0      # Higher = more fair, lower = more throughput
```

### 3.3 Call Chain Summary

```
YAML config
  └─ scheduler_ue_expert_config.policy_cfg (std::variant)
       └─ create_scheduler_strategy() → scheduler_time_qos or scheduler_time_rr
            └─ compute_ue_dl_priorities()  ← uses max_prb_policy_ratio to cap grant size
                 └─ grant_builder.recommended_vrbs(used_vrbs, max_rbs)
                      └─ set_pdsch_params(vrbs)  ← actual PRB allocation in VRB bitmap
```

---

## 4. OAI: Source Code Modifications Required

### 4.1 Current Behavior (No Control Knobs)

OAI's `pf_dl()` allocates contiguous RBs greedily. The only implicit FDM/TDM control comes from the PF coefficient: UEs with low throughput history get priority in future slots (implicit TDM via PF fairness).

**There is no config parameter to control FDM/TDM split.**

### 4.2 Approach A — Cap `max_rbSize` in `pf_dl()`

**File**: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`
**Location**: Inside `pf_dl()`, after the contiguous-block scan loop.

#### Original Code

```c
// Find contiguous free block
int max_rbSize = 1;
while (rbStart + max_rbSize <= rbStop
       && !(rballoc_mask[rbStart + max_rbSize + bwp_start] & slbitmap))
  max_rbSize++;
```

#### Modified Code (TDM-like)

```c
// Find contiguous free block
int max_rbSize = 1;
while (rbStart + max_rbSize <= rbStop
       && !(rballoc_mask[rbStart + max_rbSize + bwp_start] & slbitmap))
  max_rbSize++;

// ---- TDM CAP: limit each UE to at most max_rb_per_ue PRBs ----
int max_rb_per_ue = 27;  // ~10% of 273 → TDM-like behavior
if (max_rbSize > max_rb_per_ue)
  max_rbSize = max_rb_per_ue;
// ---- END TDM CAP ----
```

**Effect**: Each UE occupies at most 27 contiguous PRBs. With 273-PRB carrier, up to 10 UEs can be served per slot using 27 PRBs each. If there's only 1 UE, it gets 27 PRBs per slot and spreads its data across multiple slots (TDM behavior).

#### Making It Configurable

To avoid hardcoding, add a config parameter to `gnb.conf`:

```c
// In gNB_scheduler_dlsch.c (pf_dl):
int max_rb_per_ue = mac->max_rb_per_ue;  // read from config
if (max_rb_per_ue > 0 && max_rbSize > max_rb_per_ue)
  max_rbSize = max_rb_per_ue;
```

And in the config parser, add:
```conf
# gnb.conf
mac_scheduler = {
  max_rb_per_ue = 27;   # 0 = no cap (default FDM)
};
```

### 4.3 Approach B — Pre-Mask `rballoc_mask[]`

**File**: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`
**Location**: In `nr_dlsch_preprocessor()`, before calling `pf_dl()`.

```c
// In nr_dlsch_preprocessor(), after n_rb_sched[] initialization:

// ---- TDM pre-mask: block upper portion of BW ----
for (int rb = max_allowed_rb; rb < bwpSize; rb++)
  rballoc_mask[rb + bwp_start] |= slbitmap;  // mark as occupied
// ---- END TDM pre-mask ----

pf_dl(mac, pdsch, UE_list, max_sched_ues, num_beams, n_rb_sched);
```

**Effect**: `pf_dl()` sees only `max_allowed_rb` free PRBs, forcing all UEs into a narrower bandwidth.

### 4.4 Approach C — Limit UEs Per Slot

**File**: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`
**Location**: In `nr_dlsch_preprocessor()`.

```c
// Force strict TDM: only 1 UE per slot
int max_sched_ues = 1;  // instead of bw / (avg_agg * 6)
```

**Effect**: Only one UE scheduled per slot. That UE gets all available bandwidth. True TDM.

### 4.5 Recompilation

After any source modification:

```bash
cd ~/openairinterface5g/cmake_targets
./build_oai --gNB -c   # clean build
```

---

## 5. Verification: How to Confirm FDM vs TDM

### 5.1 Wireshark / PCAP Analysis

Capture the FAPI interface or MAC-level traces and inspect DCI Format 1_1 or 1_0:

| Field | FDM Pattern | TDM Pattern |
|-------|-------------|-------------|
| `frequencyDomainAssignment` (RIV) | Different RIV per UE in same slot | Same/full RIV, different slots |
| `rbStart` | UE1=0, UE2=91, UE3=182 | All UEs start at 0 |
| `rbSize` | ~91 each | ~273 each |
| Frame/slot of grants | Same frame+slot | Sequential slots |

### 5.2 OAI MAC-Level Logging

Enable `LOG_D(NR_MAC, ...)` in `pf_dl()` to see allocation decisions:

```bash
# Run gNB with debug logging
sudo ./nr-softmodem --sa -O gnb.conf --log_config.mac_log_level debug
```

Look for lines like:
```
UE RNTI 0x1234: rbStart 0, rbSize 91, MCS 15, TBS 12345
UE RNTI 0x5678: rbStart 91, rbSize 80, MCS 12, TBS 9876
```

### 5.3 srsRAN Console Output

srsRAN prints per-slot allocation summaries in its console:

```
          |----DL----|----DL----|----DL----|
 rnti | prb | mcs | brate | prb | mcs | brate |
 4601 |  91 |  20 | 10.2M |  91 |  18 |  9.1M |
 4602 |  91 |  18 |  9.0M |  91 |  16 |  8.2M |
```

---

## 6. Energy Research Implications

### Why FDM vs TDM Matters for Power Measurement

| Multiplexing | Power Profile | Measurement Impact |
|--------------|---------------|---------------------|
| **FDM** | Constant power envelope across bandwidth; varies with number of UEs | Power ∝ total allocated PRBs. Easy to measure per-slot. |
| **TDM** | Burst pattern: high power in scheduled slots, idle in others | Power ∝ duty cycle. Average over multiple slots. |
| **Hybrid** | Most complex power profile | Requires per-slot, per-PRB attribution |

For our WINLAB energy measurement research:
- **FDM** is simpler to analyze: each slot has a predictable power level based on total PRBs.
- **TDM** produces bursty power traces: Scaphandre/RAPL sees spikes during scheduled slots and valleys during idle slots.
- The `max_prb_policy_ratio` (srsRAN) or `max_rbSize` cap (OAI) directly controls this tradeoff.

---

## 7. Summary Configuration Cheat Sheet

### srsRAN (Config Only)

```yaml
# Full FDM (default)
cell_cfg:
  qos_sched:
    max_prb_policy_ratio: 100

# Partial FDM (50% BW per UE)
cell_cfg:
  qos_sched:
    max_prb_policy_ratio: 50

# Narrow-band TDM-like (10% BW per UE)
cell_cfg:
  qos_sched:
    max_prb_policy_ratio: 10

# Strict TDM (1 UE per slot)
cell_cfg:
  qos_sched:
    max_pof_ues: 1
    max_prb_policy_ratio: 100
```

### OAI (Source Code Mod)

```c
// In pf_dl() — gNB_scheduler_dlsch.c

// Full FDM (default, no change)
// No modification needed

// Narrow-band TDM-like (27 PRBs per UE)
if (max_rbSize > 27) max_rbSize = 27;

// Strict TDM (1 UE per slot)
// In nr_dlsch_preprocessor():
int max_sched_ues = 1;
```

---

## 8. Next Steps for WINLAB Experiments

1. **srsRAN**: Test `max_prb_policy_ratio` sweep (100 → 50 → 25 → 10) and measure power at each point.
2. **OAI**: If OAI experiments are needed, implement Approach A (`max_rbSize` cap) and sweep the cap value.
3. **Both**: Capture PCAP traces alongside Scaphandre power logs. Correlate `rbSize` distributions with power readings.
4. **Document**: Compare FDM vs TDM power profiles in the measurement results section of the final report.

---

*This note is part of the TEEP Probation research project. It directly answers the professor's directive on enabling time-frequency domain scheduling.*
