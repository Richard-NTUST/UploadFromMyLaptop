# srsRAN gNB Configuration Walkthrough: Knobs for 273×1 vs 27×10 Demo (2026-02-27)

Status: Complete
Deadline: 2026-02-27

This note documents every srsRAN Project configuration parameter relevant to the professor's 273×1 vs 27×10 scheduling demonstration. It serves as a reference for setting up the experiments described in the Practical Demonstration Plan (`2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md` §10).

## Table of Contents
- [1. Configuration File Structure](#1-configuration-file-structure)
- [2. Cell Configuration — Achieving 273 PRBs](#2-cell-configuration--achieving-273-prbs)
- [3. RU SDR Configuration — ZMQ Virtual Radio](#3-ru-sdr-configuration--zmq-virtual-radio)
- [4. Scheduler Configuration — The FDM/TDM Knob](#4-scheduler-configuration--the-fdmtdm-knob)
  - [4.1 Default Behavior (FDM)](#41-default-behavior-fdm)
  - [4.2 Forcing 27 PRBs (TDM)](#42-forcing-27-prbs-tdm)
- [5. Logging and Observability](#5-logging-and-observability)
- [6. MAC PCAP — Verifying PRB Allocation](#6-mac-pcap--verifying-prb-allocation)
- [7. Complete Config Examples](#7-complete-config-examples)
  - [7.1 Experiment A: 273 PRBs × 1 Slot](#71-experiment-a-273-prbs--1-slot)
  - [7.2 Experiment B: 27 PRBs × 10 Slots](#72-experiment-b-27-prbs--10-slots)
- [8. UE Configuration Notes](#8-ue-configuration-notes)
- [9. Verification Checklist](#9-verification-checklist)
- [References](#references)

---

## 1. Configuration File Structure

srsRAN Project uses **YAML** configuration for the gNB. The file is organized into top-level sections:

```yaml
# Top-level structure of gnb.yaml
amf:             # Core network (N2 interface)
ru_sdr:          # Radio unit / RF driver
cell_cfg:        # Cell parameters (bandwidth, ARFCN, etc.)
log:             # Logging verbosity
pcap:            # Packet capture
expert_cfg:      # Advanced scheduler and PHY knobs
```

The default configs ship in the `configs/` directory of the srsRAN Project source:
```
srsran_project/configs/
├── gnb_zmq.yml          # ZMQ (virtual radio) config
├── gnb_rf_b200_tdd_n78_20mhz.yml  # USRP B200, 20 MHz
├── gnb_rf_b200_tdd_n78_100mhz.yml # USRP B200, 100 MHz
└── ...
```

---

## 2. Cell Configuration — Achieving 273 PRBs

The number of PRBs is determined by **channel bandwidth** and **subcarrier spacing (SCS)**.

```yaml
cell_cfg:
  dl_arfcn: 632628             # Downlink ARFCN (Band n78, 3.5 GHz)
  band: 78                     # NR Band n78 (TDD)
  channel_bandwidth_MHz: 100   # ← THIS controls PRB count
  common_scs: 30               # ← AND THIS (µ=1 → 30 kHz SCS)
  plmn: "00101"                # PLMN (MCC=001, MNC=01)
  tac: 7                       # Tracking Area Code
  nof_antennas_dl: 1           # Number of DL antennas (SISO for demo)
  nof_antennas_ul: 1           # Number of UL antennas
```

**PRB lookup table** (TS 38.101-1 Table 5.3.2-1):

| Bandwidth (MHz) | SCS (kHz) | PRBs | `base_srate` (MHz) |
|---|---|---|---|
| 5 | 15 | 25 | 7.68 |
| 10 | 15 | 52 | 15.36 |
| 20 | 30 | 51 | 23.04 |
| 40 | 30 | 106 | 46.08 |
| **100** | **30** | **273** | **61.44** |

> **Important:** When changing bandwidth, you **must** also update `base_srate` in the `ru_sdr` section to match.

**For the 273-PRB demo:**
```yaml
cell_cfg:
  channel_bandwidth_MHz: 100    # → 273 PRBs
  common_scs: 30                # → µ=1, 0.5 ms/slot

ru_sdr:
  srate: 61.44                  # Must match 100 MHz bandwidth
  device_args: ...,base_srate=61.44e6,...
```

**For initial testing (safer, lower compute):**
```yaml
cell_cfg:
  channel_bandwidth_MHz: 20     # → 51 PRBs
  common_scs: 30

ru_sdr:
  srate: 23.04
  device_args: ...,base_srate=23.04e6,...
```

---

## 3. RU SDR Configuration — ZMQ Virtual Radio

```yaml
ru_sdr:
  device_driver: zmq            # Virtual RF via ZeroMQ
  device_args: tx_port=tcp://0.0.0.0:2000,rx_port=tcp://srsue:2001,base_srate=61.44e6,id=zmq
  srate: 61.44                  # Sample rate (MUST match bandwidth)
  otw_format: sc12              # Over-the-wire format
  tx_gain: 75                   # TX gain (dB)
  rx_gain: 75                   # RX gain (dB)
```

**Key parameters:**
| Parameter | Purpose | Notes |
|---|---|---|
| `device_driver` | RF backend selection | `zmq` for virtual, `uhd` for USRP |
| `tx_port` | gNB DL → UE | gNB listens on this port |
| `rx_port` | UE UL → gNB | gNB connects to UE's tx_port |
| `base_srate` | Sampling rate for ZMQ | **Must match bandwidth**: 23.04e6 for 20 MHz, 61.44e6 for 100 MHz |
| `srate` | Radio sample rate | Same value as base_srate but in MHz (no `e6`) |

---

## 4. Scheduler Configuration — The FDM/TDM Knob

### 4.1 Default Behavior (FDM)

By default, srsRAN's `intra_slice_scheduler` divides available PRBs equally among active UEs per slot. With 1 UE and enough buffer data, it allocates **all available PRBs to that UE** — this naturally produces Strategy A (273×1).

No special configuration is needed for Experiment A.

### 4.2 Forcing 27 PRBs (TDM)

To limit each slot's grant to 27 PRBs (Strategy B), there are two approaches:

**Approach 1: Slice Configuration (config-only, no code change)**

```yaml
cell_cfg:
  slicing:
    - sst: 1              # Slice Service Type (eMBB)
      sd: 0x000001         # Slice Differentiator
      max_prb: 27          # ← LIMIT: max PRBs per slot for this slice
```

> **Caveat:** This config key may not be present in all srsRAN versions. Check `srsran_project/configs/` for the `slicing` section support.

**Approach 2: Expert Config (`expert_cfg`)**

srsRAN exposes some scheduler knobs via `expert_cfg`:

```yaml
expert_cfg:
  mac:
    sched_cfg:
      pdsch:
        max_nof_rbs: 27              # Limit PDSCH grant to 27 RBs
      pusch:
        max_nof_rbs: 27              # Limit PUSCH grant to 27 RBs
```

> **Caveat:** This may require a recent srsRAN version (2024.w40+). If not available, code modification is needed.

**Approach 3: Code Modification (guaranteed to work)**

In `lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp`, cap the VRB interval:

```cpp
// In schedule_dl_newtx_candidates():
// After computing the candidate interval, clamp it:
unsigned max_rbs = std::min(remaining_rbs, 27u);  // Force 27 PRBs max
```

This is a 1-line change.

---

## 5. Logging and Observability

```yaml
log:
  filename: /tmp/gnb.log         # Log file path
  all_level: info                # Global log level
  mac_level: debug               # ← Set to debug to see per-slot scheduling
  phy_level: warning             # PHY is noisy; keep at warning
  hex_max_size: 32               # Limit hex dump size
```

**Key log messages to look for:**

| Log Pattern | What It Tells You |
|---|---|
| `PDSCH: ... rbSize=273` | Full bandwidth grant (Strategy A) |
| `PDSCH: ... rbSize=27` | Limited grant (Strategy B) |
| `NG connection established` | gNB connected to 5G Core |
| `UE attached` | UE successfully registered |
| `PUSCH: ... rbSize=...` | UL grant size |

At `mac_level: debug`, the scheduler prints per-slot decisions including `rbStart`, `rbSize`, `MCS`, `TBS`, and `nrOfLayers`.

---

## 6. MAC PCAP — Verifying PRB Allocation

```yaml
pcap:
  mac_enable: true               # Enable MAC-layer PCAP
  mac_filename: /tmp/gnb_mac.pcap
  ngap_enable: false             # NGAP PCAP (optional)
  e2ap_enable: false             # E2AP PCAP (optional)
```

**How to analyze the PCAP:**

1. Copy out of container: `docker cp gnb:/tmp/gnb_mac.pcap ./`
2. Open in Wireshark with `mac-nr` dissector
3. Filter: `mac-nr.rar || mac-nr.dlsch`
4. Look for DCI fields:
   - `frequency_domain_assignment` → decode RIV to get `(rbStart, rbSize)`
   - `mcs` → verify MCS index
   - `time_domain_assignment` → TDRA row index

**Expected observations:**

| Experiment | RIV | rbStart | rbSize | DCIs per 10 slots |
|---|---|---|---|---|
| A: 273×1 | 545 | 0 | 273 | 1 |
| B: 27×10 | 7098 | 0 | 27 | 10 |

---

## 7. Complete Config Examples

### 7.1 Experiment A: 273 PRBs × 1 Slot

```yaml
# gnb_exp_a.yaml — Full bandwidth, single burst
amf:
  addr: 10.53.1.2
  bind_addr: 10.53.1.5

ru_sdr:
  device_driver: zmq
  device_args: tx_port=tcp://0.0.0.0:2000,rx_port=tcp://srsue:2001,base_srate=61.44e6,id=zmq
  srate: 61.44
  otw_format: sc12
  tx_gain: 75
  rx_gain: 75

cell_cfg:
  dl_arfcn: 632628
  band: 78
  channel_bandwidth_MHz: 100     # → 273 PRBs
  common_scs: 30
  plmn: "00101"
  tac: 7
  nof_antennas_dl: 1
  nof_antennas_ul: 1

log:
  filename: /tmp/gnb.log
  all_level: info
  mac_level: debug               # See per-slot decisions
  phy_level: warning

pcap:
  mac_enable: true
  mac_filename: /tmp/gnb_mac.pcap
```

### 7.2 Experiment B: 27 PRBs × 10 Slots

```yaml
# gnb_exp_b.yaml — Limited bandwidth, time-spread
amf:
  addr: 10.53.1.2
  bind_addr: 10.53.1.5

ru_sdr:
  device_driver: zmq
  device_args: tx_port=tcp://0.0.0.0:2000,rx_port=tcp://srsue:2001,base_srate=61.44e6,id=zmq
  srate: 61.44
  otw_format: sc12
  tx_gain: 75
  rx_gain: 75

cell_cfg:
  dl_arfcn: 632628
  band: 78
  channel_bandwidth_MHz: 100     # Still 100 MHz total (273 PRBs available)
  common_scs: 30
  plmn: "00101"
  tac: 7
  nof_antennas_dl: 1
  nof_antennas_ul: 1
  slicing:
    - sst: 1
      max_prb: 27               # ← LIMIT: 27 PRBs per slot

log:
  filename: /tmp/gnb.log
  all_level: info
  mac_level: debug
  phy_level: warning

pcap:
  mac_enable: true
  mac_filename: /tmp/gnb_mac.pcap
```

---

## 8. UE Configuration Notes

The UE (`srsRAN_4G srsue`) configuration must match the gNB:

| Parameter | 20 MHz Setup | 100 MHz Setup | Notes |
|---|---|---|---|
| `srate` | `23.04e6` | `61.44e6` | Must match gNB `base_srate` |
| `bands` | 78 | 78 | Must match `cell_cfg.band` |
| `nof_antennas` | 1 | 1 | **Critical:** must be 1 for SISO |
| `base_srate` in `device_args` | `23.04e6` | `61.44e6` | Must match gNB |

> **Warning:** srsRAN_4G's srsUE may not support 100 MHz bandwidth. If the UE crashes at 61.44 MHz sample rate, this is a known limitation. In that case, stay at 20 MHz (51 PRBs) and adjust the demo to 51×1 vs 5×10 equivalence. The TBS calculator script can verify any PRB ratio.

---

## 9. Verification Checklist

Run through this checklist after each experiment:

**Pre-experiment:**
- [ ] `channel_bandwidth_MHz` matches intended PRB count
- [ ] `base_srate` and `srate` match the bandwidth
- [ ] `nof_antennas = 1` in UE config
- [ ] `mac_level: debug` enabled for scheduler visibility
- [ ] `mac_enable: true` for PCAP capture

**Post-experiment:**
- [ ] Check gNB log for `rbSize` values (should match 273 or 27)
- [ ] Extract MAC PCAP: `docker cp gnb:/tmp/gnb_mac.pcap ./`
- [ ] Open PCAP in Wireshark, filter `mac-nr`, inspect DCI RIV
- [ ] Run iperf3 and record throughput for both A and B
- [ ] Verify A throughput ≈ B throughput (within ~3%, per TBS calculator)
- [ ] If Scaphandre running: compare power profiles between A and B

---

## References

1. srsRAN Project Documentation: https://docs.srsran.com/projects/project/en/latest/
2. srsRAN Project Config Reference: `srsran_project/configs/` directory
3. Our project: `2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md` — Scheduler intervention points
4. Our project: `2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md` — TBS verification
5. Our project: `2026-02-27_srsRAN-ZMQ-Unblock-Guide.md` — Setup instructions
6. 3GPP TS 38.101-1, Table 5.3.2-1 — PRBs per bandwidth per SCS
