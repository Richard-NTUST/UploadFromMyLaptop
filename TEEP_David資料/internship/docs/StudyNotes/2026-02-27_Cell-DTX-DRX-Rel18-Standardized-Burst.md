# Cell DTX/DRX (3GPP Rel-18): The Standardized Version of Our Burst Experiment (2026-02-27)

Status: Complete
Deadline: 2026-02-27

This note explains Cell DTX/DRX — the 3GPP Rel-18 feature that standardizes the "burst scheduling" concept we validated empirically on Feb 4 (48% power reduction). It connects each standard mechanism to our existing study notes and experiments.

## Table of Contents
- [Objective](#objective)
- [1. What is Cell DTX/DRX?](#1-what-is-cell-dtxdrx)
- [2. How Cell DTX Works (Downlink)](#2-how-cell-dtx-works-downlink)
  - [2.1 DTX Cycle Configuration](#21-dtx-cycle-configuration)
  - [2.2 Active vs Sleep Symbols](#22-active-vs-sleep-symbols)
  - [2.3 SSB and Paging Exceptions](#23-ssb-and-paging-exceptions)
- [3. How Cell DRX Works (Uplink)](#3-how-cell-drx-works-uplink)
- [4. RRC Configuration (IE CellDTX-DRX)](#4-rrc-configuration-ie-celldtx-drx)
- [5. Mapping to O-RU Sleep Modes](#5-mapping-to-o-ru-sleep-modes)
- [6. Power Savings Model](#6-power-savings-model)
- [7. Connection to Our Project](#7-connection-to-our-project)
  - [7.1 Burst Experiment = Cell DTX Prototype](#71-burst-experiment--cell-dtx-prototype)
  - [7.2 Scheduler Modification = Cell DTX Implementation](#72-scheduler-modification--cell-dtx-implementation)
  - [7.3 TBS Equivalence = Throughput Preservation Proof](#73-tbs-equivalence--throughput-preservation-proof)
- [8. Implementation in OAI and srsRAN](#8-implementation-in-oai-and-srsran)
- [9. Comparison: Our Burst vs Cell DTX/DRX](#9-comparison-our-burst-vs-cell-dtxdrx)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Objective

After reading this note, the reader should be able to:
1. **Explain** what Cell DTX/DRX is and which 3GPP release introduced it.
2. **Map** each Cell DTX mechanism to our existing experiments and study notes.
3. **Quantify** the expected power savings using the EARTH model parameters.
4. **Identify** what srsRAN/OAI changes would be needed to implement Cell DTX.

---

## 1. What is Cell DTX/DRX?

**Cell DTX/DRX** is a 3GPP Release 18 (Rel-18) feature that allows the gNB to **turn off its transmitter and receiver during periods when no data transmission/reception is needed**.

| Term | Full Name | Direction | Meaning |
|---|---|---|---|
| Cell DTX | Cell Discontinuous Transmission | DL (gNB → UE) | gNB stops transmitting during configured "off" periods |
| Cell DRX | Cell Discontinuous Reception | UL (UE → gNB) | gNB stops listening for UL during configured "off" periods |

**Key insight:** Unlike UE-level C-DRX (which has existed since Rel-8), Cell DTX/DRX is a **network-side** feature. The gNB decides when to sleep, not the UE.

**Standards basis:**
- 3GPP TS 38.300 v18.x — NR Overall Architecture, §9.2.27 "Network energy saving"
- 3GPP TS 38.331 v18.x — RRC Protocol, IE `CellDTX-DRX`
- 3GPP TR 38.864 — "Study on network energy saving for NR" (Rel-18 study item)

---

## 2. How Cell DTX Works (Downlink)

### 2.1 DTX Cycle Configuration

Cell DTX defines a periodic cycle where the gNB alternates between **Active** and **Sleep** periods:

```
                    ◄──── Cell DTX Cycle ────►
                    ┌─────────┐               ┌─────────┐
    gNB TX State:   │  ACTIVE  │    SLEEP      │  ACTIVE  │    SLEEP
                    │ (TX ON)  │   (TX OFF)    │ (TX ON)  │   (TX OFF)
                    └─────────┘               └─────────┘
Time ►              ◄─ Active ─►◄── Sleep ──►◄─ Active ─►◄── Sleep ──►
                      Duration     Duration     Duration     Duration
```

The cycle length and active duration are configured via RRC:

| Parameter | Values | Description |
|---|---|---|
| `cellDTX-Cycle` | {ms1, ms2, ms4, ms5, ms10, ms20, ms40, ms80, ms160} | Total cycle duration |
| `cellDTX-Offset` | 0–159 slots | Offset from SFN boundary |
| `cellDTX-ActiveDuration` | {sl1, sl2, sl3, sl4, sl5, sl6, sl7, sl8, sl14, sl20, sl40, sl80, sl160} | Duration of the active (TX ON) window |

### 2.2 Active vs Sleep Symbols

During the **Active period**, the gNB operates normally:
- Transmits PDCCH + PDSCH to scheduled UEs
- Transmits reference signals (CSI-RS, DMRS)
- Full PA power

During the **Sleep period**, the gNB **stops all DL transmission** except:
- SSB (Synchronization Signal Block) — mandatory for cell detection
- Paging occasions — mandatory for idle/inactive UEs

This is *exactly* what our burst experiment simulated: concentrate traffic into short bursts, then go quiet.

### 2.3 SSB and Paging Exceptions

The standard defines **Cell DTX Guard Symbols** around SSB and paging occasions:

```
         ◄──── Sleep Period (TX OFF) ────►
         ........│SSB│........│PO│........
                 ↑ Guard      ↑ Guard
                 symbols      symbols
```

The PA must briefly wake up for these mandatory transmissions. This means Cell DTX power saving is not 100% even during sleep — the SSB periodicity (default: 20 ms) creates a minimum wake-up frequency.

---

## 3. How Cell DRX Works (Uplink)

Cell DRX mirrors Cell DTX for the uplink:

- During **Cell DRX Active duration**, the gNB listens for PUSCH, PUCCH, SRS, and PRACH
- During **Cell DRX Sleep duration**, the gNB can power down its receiver chain
- UEs must align their UL transmissions to the Cell DRX active windows

**Configuration parameters:**

| Parameter | Description |
|---|---|
| `cellDRX-Cycle` | Total cycle (same range as DTX) |
| `cellDRX-Offset` | Offset from SFN boundary |
| `cellDRX-ActiveDuration` | Duration of listening window |

**Power impact:** Receiver power is lower than transmitter power (no PA), but the analog front-end (LNA, ADC, mixers) plus digital baseband processing still consume significant power. Cell DRX allows shutting these down.

---

## 4. RRC Configuration (IE CellDTX-DRX)

3GPP TS 38.331 defines the following IEs:

```
CellDTX-DRX ::= SEQUENCE {
    cellDTX-Cycle           ENUMERATED {ms1, ms2, ms4, ms5, ms10, ms20, ms40, ms80, ms160},
    cellDTX-Offset          INTEGER (0..159),
    cellDTX-ActiveDuration  ENUMERATED {sl1, sl2, sl3, sl4, sl5, sl6, sl7, sl8, sl14, sl20, sl40, sl80, sl160},
    cellDRX-Cycle           ENUMERATED {ms1, ms2, ms4, ms5, ms10, ms20, ms40, ms80, ms160},
    cellDRX-Offset          INTEGER (0..159),
    cellDRX-ActiveDuration  ENUMERATED {sl1, sl2, sl3, sl4, sl5, sl6, sl7, sl8, sl14, sl20, sl40, sl80, sl160}
}
```

**Example configuration for our 27×10 scenario:**

| Parameter | Value | Rationale |
|---|---|---|
| `cellDTX-Cycle` | ms5 (= 10 slots at µ=1) | 10-slot window matches our analysis |
| `cellDTX-ActiveDuration` | sl1 | gNB transmits in 1 slot per cycle (burst) |
| Duty cycle | 1/10 = 10% | PA ON 10% of the time |

---

## 5. Mapping to O-RU Sleep Modes

Cell DTX/DRX maps directly to the O-RAN sleep modes documented in our `2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md`:

| Cell DTX Phase | O-RU Sleep Mode | Wake-up Time | Power State |
|---|---|---|---|
| Active duration | SM0 (Active) | N/A | Full power |
| Sleep (short, < 1 ms) | SM1 (Micro-sleep) | ~10 µs | Digital OFF, RF biased |
| Sleep (medium, 1–10 ms) | SM2 (Light sleep) | ~1 ms | Digital + RF OFF |
| Sleep (long, > 10 ms) | SM3 (Deep sleep) | ~100 ms | Nearly full shutdown |

**Mapping to our study:**

```
Cell DTX Cycle = ms5 (10 slots = 5 ms):
├── Active: 1 slot (0.5 ms) → SM0: PA ON, full 273 PRBs, max power
└── Sleep: 9 slots (4.5 ms) → SM1 or SM2: PA OFF, near-zero dynamic power
```

The 4.5 ms sleep window is long enough for **SM2 (Light sleep)** but too short for SM3. This aligns with the WG4 wake-up time constraints.

---

## 6. Power Savings Model

Using the EARTH model from our `2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md`:

**Without Cell DTX (FDM — current default):**
$$P_{FDM} = P_0 + \Delta_p \cdot P_{max} \cdot x \quad \text{(for all 10 slots)}$$
$$E_{FDM} = 10 \cdot T_{slot} \cdot P_{FDM}$$

**With Cell DTX (TDM — burst):**
$$E_{DTX} = \underbrace{1 \cdot T_{slot} \cdot (P_0 + \Delta_p \cdot P_{max})}_{Active~slot} + \underbrace{9 \cdot T_{slot} \cdot P_{sleep}}_{Sleep~slots}$$

**Average power with DTX:**
$$\bar{P}_{DTX} = \frac{1}{10}(P_0 + \Delta_p \cdot P_{max}) + \frac{9}{10} P_{sleep}$$

### Worked Example (P12 Macro O-RU at 30% load)

| Parameter | Value | Source |
|---|---|---|
| $P_0$ (static) | 197 W | P12 Macro min |
| $\Delta_p$ | 6.32 | Derived from P12: (531−197)/52.86 |
| $P_{max}$ (per antenna) | 52.86 W | P12 Macro max per sector |
| $x$ (load) | 0.3 | 30% PRB utilisation |
| $P_{sleep}$ (SM2) | ~30 W | Literature estimate (~15% of $P_0$) |

**FDM (no DTX):**
$$P_{FDM} = 197 + 6.32 \times 52.86 \times 0.3 = 197 + 100.2 = 297.2~\text{W}$$

**DTX (1/10 duty cycle):**
$$\bar{P}_{DTX} = \frac{1}{10}(197 + 6.32 \times 52.86) + \frac{9}{10} \times 30 = \frac{531}{10} + 27 = 53.1 + 27 = 80.1~\text{W}$$

**Savings: 297.2 − 80.1 = 217.1 W (73% reduction)**

This is even higher than our Feb 4 simulation (103 W) because the simulation used a simpler model. Cell DTX with full SM2 sleep achieves deeper savings.

---

## 7. Connection to Our Project

### 7.1 Burst Experiment = Cell DTX Prototype

Our Feb 4 burst experiment (`docs/StudyNotes/2026-02-04_Burst-Experiment-Validation.md`) was a **proof-of-concept Cell DTX implementation**:

| Our Experiment | Cell DTX Standard |
|---|---|
| iperf3 burst (100% for 30% time) | `cellDTX-ActiveDuration = sl1` with 1/10 duty |
| iperf3 smooth (30% continuous) | No Cell DTX (FDM baseline) |
| CPU race-to-sleep (C-states) | O-RU PA micro-sleep (SM1/SM2) |
| 48% power reduction measured | 73% predicted with real O-RU SM2 |

### 7.2 Scheduler Modification = Cell DTX Implementation

The scheduler changes we identified in `2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md` are the **software-side implementation** of Cell DTX:

- **Cap `max_rbSize = 273`** and **schedule only 1 UE/slot → burst** = Cell DTX active window
- **Leave subsequent slots empty** = Cell DTX sleep window
- The O-RU hardware must support SM1/SM2 to actually save power

### 7.3 TBS Equivalence = Throughput Preservation Proof

Our `2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md` proves that **Cell DTX does not reduce throughput**:

$$TBS(273 \times 1) \approx 10 \times TBS(27 \times 1) \quad (\pm 2.7\%)$$

This means the gNB can deliver the same data in 1 burst slot as in 10 spread slots, confirming that Cell DTX is throughput-neutral.

---

## 8. Implementation in OAI and srsRAN

### Current Status (Feb 2026)

| Stack | Cell DTX Support | Notes |
|---|---|---|
| OAI (2024.w40) | ❌ Not implemented | No CellDTX-DRX IE in RRC; scheduler always FDM |
| srsRAN Project | ❌ Not implemented | `intra_slice_scheduler.cpp` defaults to equal-share FDM |

### What Would Be Needed

**For srsRAN (our target):**

1. **RRC:** Add `CellDTX-DRX` IE to `SIB1` or dedicated RRC signaling
2. **DU MAC Scheduler:** In `intra_slice_scheduler.cpp`:
   ```cpp
   // Pseudo-code: Cell DTX enforcement
   if (current_slot % dtx_cycle_slots < dtx_active_duration) {
       // ACTIVE: schedule normally (full 273 PRBs to UEs)
       schedule_dl_newtx_candidates(candidates, slice);
   } else {
       // SLEEP: skip scheduling, signal O-RU to enter SM1/SM2
       // (via OFH C-Plane "sleep" command)
   }
   ```
3. **O-FH (Open Fronthaul):** Send Section Type 0 C-Plane message with "no data" indication during sleep, allowing the O-RU to enter SM1/SM2
4. **O-RU firmware:** Must support SM1/SM2 and react to the C-Plane sleep signal

---

## 9. Comparison: Our Burst vs Cell DTX/DRX

| Aspect | Our Burst (Feb 4) | Cell DTX/DRX (Rel-18) |
|---|---|---|
| **Mechanism** | iperf3 ON/OFF at application layer | Scheduler-controlled slot-level ON/OFF |
| **Granularity** | ~100 ms bursts | Slot-level (0.5 ms) |
| **Sleep signal** | CPU auto-enters C-states | Explicit O-FH C-Plane sleep command |
| **Throughput guarantee** | Best-effort (iperf rate) | TBS-guaranteed (same MCS, same data volume) |
| **Standardized** | No (ad-hoc experiment) | Yes (3GPP TS 38.331 Rel-18) |
| **Power saving** | 48% (CPU proxy) | 73% predicted (O-RU with SM2) |
| **UE impact** | None (UE unaware) | UE must respect DTX/DRX timing |
| **Always-on signals** | N/A | SSB, Paging must still transmit |

---

## Key Takeaways

1. **Cell DTX/DRX is the 3GPP standard that formalizes our burst experiment.** Our Feb 4 proof-of-concept (48% power reduction) demonstrated the same principle that Cell DTX applies at slot granularity.

2. **The power savings are even greater with real hardware.** Our CPU proxy achieved 48% via C-states; Cell DTX with O-RU SM2 sleep predicts **73% reduction** at 30% load (using P12 Macro parameters).

3. **TBS equivalence enables Cell DTX without throughput loss.** We proved that 273×1 ≈ 10×(27×1) within ±2.7%, meaning burst scheduling delivers the same total data volume.

4. **Neither OAI nor srsRAN implements Cell DTX yet.** This is a research opportunity: implementing Cell DTX in srsRAN's `intra_slice_scheduler.cpp` would be a concrete Stage 2 contribution.

5. **Cell DTX requires O-RU cooperation.** The software scheduler can create the burst pattern, but real power savings only occur if the O-RU hardware supports SM1/SM2 and responds to sleep signals via O-FH.

---

## References

1. 3GPP TR 38.864 v18.0.0, "Study on network energy saving for NR" — §5, §6 (Cell DTX/DRX techniques and evaluation).
2. 3GPP TS 38.331 v18.x, "NR; RRC Protocol" — IE `CellDTX-DRX` definition.
3. 3GPP TS 38.300 v18.x, "NR; Overall Description" — §9.2.27 "Network energy saving".
4. 3GPP TS 38.213 v18.x, "NR; Physical layer procedures for control" — PDCCH monitoring adaptation.
5. O-RAN WG4, "Management Plane Specification" — Sleep mode commands (SM0–SM3).
6. O-RAN WG1, "Network Energy Saving Use Cases and Solutions" — UC1–UC4.
7. Our project: `docs/StudyNotes/2026-02-04_Burst-Experiment-Validation.md` (Empirical validation).
8. Our project: `docs/StudyNotes/2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md` (Sleep modes).
9. Our project: `docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md` (Power model).
10. Our project: `docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md` (Throughput proof).
11. Our project: `docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md` (Scheduler intervention points).
