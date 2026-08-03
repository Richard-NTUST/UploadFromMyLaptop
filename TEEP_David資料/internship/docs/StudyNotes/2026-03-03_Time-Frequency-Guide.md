# Enabling Time-Frequency Domain Scheduling: Practical Guide

**Date**: 2026-03-03
**Context**: Professor's directive — "We need to know how to enable the time-frequency domain scheduling."
**Prerequisites**: [Scheduling Algorithms Study Note](./2026-03-02_Frequencies-in-NR.md), [Source-Code-Verified Reference](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md)

> **Note (2026-03-06)**: YAML config corrected. srsRAN uses `qos_sched:` / `rr_sched:` subcmd sections, **not** `policy: time_rr` / `time_pf`. See the [source-code-verified note](./2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md) §6 for the authoritative YAML mapping.

---

## 1. Quick Answer

**There is no single toggle to "switch between time-domain and frequency-domain scheduling."**

Both always operate together. What we control is the **maximum PRBs per UE per slot**, which shifts the balance:

| Setting | Effect | Scheduling Mode Name |
|---------|--------|---------------------|
| `max_prbs = 273` (100 MHz, SCS 30 kHz) | UE uses full bandwidth in 1 slot | **Frequency-domain first** |
| `max_prbs = 27` | UE uses ~10% bandwidth across ~10 slots | **Time-domain spreading** |
| `max_prbs = 1` | UE uses 1 PRB across ~273 slots | **Extreme TDM** (impractical) |

---

## 2. srsRAN: Step-by-Step

### 2.1 Prerequisites

- srsRAN Project built and working with ZMQ
- UE attached and data session established
- See: [ZMQ Unblock Guide](./2026-02-27_srsRAN-ZMQ-Unblock-Guide.md)

### 2.2 Experiment A: Full Frequency-Domain (273 PRBs × 1 Slot)

**Config file**: `gnb_zmq.yaml`

```yaml
cell_cfg:
  dl_arfcn: 368500
  band: 3
  channel_bandwidth_MHz: 100
  common_scs: 30
  nof_antennas_dl: 1
  nof_antennas_ul: 1
  plmn: "00101"
  tac: 7

scheduler_cfg:
  qos_sched:                        # default QoS-aware + PF
    pf_fairness_coeff: 2.0

# No PRB cap → uses full 273 PRBs
# No slicing config needed for default behavior

pcap:
  mac_enable: true
  mac_filename: /tmp/gnb_273prb.pcap
```

**Expected behavior**:
- DCI shows RIV = 545 (273 contiguous PRBs starting at PRB 0)
- PDSCH fills full bandwidth in 1 slot
- Next slot: no PDSCH if buffer drained

### 2.3 Experiment B: Time-Domain Spreading (27 PRBs × 10 Slots)

```yaml
cell_cfg:
  dl_arfcn: 368500
  band: 3
  channel_bandwidth_MHz: 100
  common_scs: 30
  nof_antennas_dl: 1
  nof_antennas_ul: 1
  plmn: "00101"
  tac: 7

scheduler_cfg:
  qos_sched:                        # default QoS-aware + PF
    pf_fairness_coeff: 2.0

slicing:
  -
    sst: 1
    sd: 1
    sched_cfg:
      max_prb_policy_ratio: 10    # 10% of 273 ≈ 27 PRBs

pcap:
  mac_enable: true
  mac_filename: /tmp/gnb_27prb.pcap
```

**Expected behavior**:
- DCI shows RIV for 27 contiguous PRBs
- PDSCH appears in ~10 consecutive slots to deliver same data
- Same total throughput (within ~1-2%)

### 2.4 Verification with Wireshark

```
# Open PCAP
wireshark /tmp/gnb_273prb.pcap &

# Filter for DL-SCH grants
# Display filter:
mac-nr.rar || mac-nr.dlsch

# Check fields:
# - "Frequency domain resource assignment" → PRB allocation bitmap/RIV
# - "Time domain resource assignment" → TDRA index (row in TDRA table)
# - "Number of RBs" → should show 273 or 27
```

### 2.5 TDRA Table (Time-Domain Resource Allocation)

srsRAN uses the default TDRA table from TS 38.214 Table 5.1.2.1.1-2:

| TDRA Index | Mapping Type | Start Symbol (S) | Nr. Symbols (L) | S+L |
|-----------|-------------|-------------------|-----------------|-----|
| 0 | Type A | 2 | 12 | 14 |
| 1 | Type A | 2 | 10 | 12 |
| 2 | Type A | 2 | 9 | 11 |
| 3 | Type A | 2 | 7 | 9 |
| ... | ... | ... | ... | ... |

The scheduler picks TDRA index 0 by default (12 symbols). This is **separate** from our PRB cap — it controls vertical (symbol) usage within each slot.

To modify:
```yaml
# In gnb_zmq.yaml (if supported):
cell_cfg:
  pdsch_cfg:
    tdra_table:
      - mapping_type: typeA
        start_symbol: 2
        nof_symbols: 6     # Use only 6 symbols → halves capacity per slot
```

---

## 3. OAI: Step-by-Step

### 3.1 Prerequisites

- OAI gNB built with `build_oai --gNB`
- `gnb.conf` configuration file ready
- RF simulator or USRP connected

### 3.2 Experiment A: Full Frequency-Domain

```
// In gnb.conf — no special changes needed
// OAI defaults to full BWP allocation

MACRLCs = ({
    num_cc = 1;
    dl_max_mcs = 28;
    ul_max_mcs = 28;
});
```

### 3.3 Experiment B: Time-Domain Spreading

OAI does **not** have a config-file knob for PRB capping. You must modify source code:

**File**: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`

```c
// In the function that calls nr_find_nb_rb():
// Find this line:
int rbSize = NRRIV2BW(sched_ctrl->active_bwp->bwp_Common->genericParameters.locationAndBandwidth, MAX_BWP_SIZE);

// Add after it:
if (rbSize > 27) rbSize = 27;  // ← CAP TO 27 PRBs FOR EXPERIMENT B
```

Rebuild:
```bash
cd cmake_targets
./build_oai --gNB -c
```

### 3.4 Alternative: Using `rballoc_mask` Directly

A cleaner approach — restrict the PRB bitmap:

```c
// In nr_schedule_ue_spec(), after rballoc_mask is initialized:
// Zero out PRBs beyond 27
for (int rb = 27; rb < bwp_size; rb++) {
    rballoc_mask[rb] = 0;
}
```

This forces the scheduler to only "see" PRBs 0–26, achieving the 27-PRB cap without touching the algorithm.

---

## 4. Scheduling Policy Comparison

### 4.1 srsRAN: RR vs QoS (with internal PF) with 2+ UEs

| Scenario | `rr_sched` Behavior | `qos_sched` Behavior (default) |
|----------|-------------------|-------------------|
| 2 UEs, equal channel | Alternate: UE0→slot0, UE1→slot1 | Same (equal metrics) |
| 2 UEs, UE0 has better channel | Still alternates (fair) | UE0 gets more slots initially, then PF balances |
| 2 UEs, UE0 has data, UE1 idle | UE0 every slot (skips idle UE1) | Same |
| 1 UE (our setup) | Full allocation every slot | Same as RR |

### 4.2 Frequency-Domain Multiplexing (Multi-UE in Same Slot)

When multiple UEs are scheduled in the **same slot**, the FD allocator splits PRBs:

```
Slot N with 2 UEs and 273 PRBs:
┌─────────────────────┬─────────────────────┐
│   UE0: PRBs 0–136   │  UE1: PRBs 137–272  │
└─────────────────────┴─────────────────────┘
← 137 PRBs →           ← 136 PRBs →
```

srsRAN's `inter_slice_scheduler` controls this split via slice weights:
```yaml
slicing:
  -
    sst: 1
    sd: 1
    sched_cfg:
      max_prb_policy_ratio: 50    # 50% → ~137 PRBs for this slice
  -
    sst: 1
    sd: 2
    sched_cfg:
      max_prb_policy_ratio: 50    # 50% → ~136 PRBs for this slice
```

---

## 5. Connecting to Power Measurement

| Configuration | PA Behavior | Sleep Opportunity | Predicted Power (EARTH) |
|--------------|-------------|-------------------|------------------------|
| 273 PRBs × 1 slot | Full power for 1 slot | 9/10 slots can sleep | **Lower** (SM2: ~80W) |
| 27 PRBs × 10 slots | Low power for 10 slots | No sleep opportunity | **Higher** (no sleep: ~297W at 30% load) |
| 137 PRBs × 2 slots | Medium power for 2 slots | 8/10 slots can sleep | Medium |

**This is the core insight linking scheduler configuration to RU power consumption.**

---

## 6. What to Demo to the Professor

### 6.1 Minimum Viable Demo (ZMQ, no hardware)

1. Run srsRAN gNB + srsUE with ZMQ
2. Generate DL traffic: `iperf3 -c <UE_IP> -t 10 -b 50M`
3. Capture PCAP with both configs (273 and 27 PRBs)
4. Show in Wireshark:
   - Config A: DCI with 273 PRBs, data in 1 slot
   - Config B: DCI with 27 PRBs, data spread across ~10 slots
5. Show throughput is approximately equal

### 6.2 Extended Demo (with power proxy)

1. Same as above, plus:
2. Monitor CPU usage: `mpstat 1` during each experiment
3. Show CPU is active for fewer slots in Config A → correlates with power savings
4. Cross-reference with EARTH model predictions

### 6.3 Slide Outline

```
Slide 1: "Time-Domain vs Frequency-Domain Scheduling in NR"
         - Diagram showing 2-stage scheduler
Slide 2: "273×1 vs 27×10: Same Data, Different Power"
         - TBS calculator results table
Slide 3: "srsRAN Configuration"
         - YAML snippets for both experiments
Slide 4: "Wireshark Verification"
         - Screenshots of DCI fields
Slide 5: "Power Implications"
         - EARTH model predictions
         - Connection to Cell DTX/DRX
```

---

## 7. References

1. srsRAN Project Documentation, "Scheduler Configuration," https://docs.srsran.com/projects/project/en/latest/
2. 3GPP TS 38.214, §5.1.2 "Resource allocation in time and frequency domain"
3. 3GPP TS 38.214, Table 5.1.2.1.1-2 "Default PDSCH time domain resource allocation A"
4. OpenAirInterface Wiki, "NR MAC Scheduler," https://gitlab.eurecom.fr/oai/openairinterface5g/-/wikis/
5. F. Capozzi et al., "Downlink Packet Scheduling in LTE Cellular Networks," IEEE COMST, 2013