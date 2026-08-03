# 5G NR Physical Layer: Resource Grid & Scheduling Fundamentals (2026-02-12)

Status: Complete
Deadline: 2026-02-12

This note provides the physical-layer foundation needed to understand the srsRAN scheduler deep-dive and the TDM vs FDM power analysis. It explains how 5G NR organizes time and frequency resources into a grid, and how the scheduler populates that grid — which directly determines whether the O-RU Power Amplifier can sleep.

## Table of Contents
- [Objective](#objective)
- [1. Why the Resource Grid Matters for Power](#1-why-the-resource-grid-matters-for-power)
- [2. Time Domain Structure](#2-time-domain-structure)
  - [Hierarchy: Frame → Subframe → Slot → Symbol](#hierarchy-frame--subframe--slot--symbol)
  - [Numerology (µ) — The Scaling Parameter](#numerology-µ--the-scaling-parameter)
  - [Slot Duration Table](#slot-duration-table)
  - [OFDM Symbol Duration](#ofdm-symbol-duration)
- [3. Frequency Domain Structure](#3-frequency-domain-structure)
  - [Subcarrier and Resource Block (RB)](#subcarrier-and-resource-block-rb)
  - [Bandwidth Parts (BWP)](#bandwidth-parts-bwp)
  - [Number of RBs vs Channel Bandwidth](#number-of-rbs-vs-channel-bandwidth)
- [4. The Resource Grid](#4-the-resource-grid)
  - [Resource Element (RE)](#resource-element-re)
  - [Grid Visualization](#grid-visualization)
  - [What Lives in the Grid](#what-lives-in-the-grid)
- [5. Slot Formats and TDD Patterns](#5-slot-formats-and-tdd-patterns)
  - [Symbol Types: D, U, F](#symbol-types-d-u-f)
  - [Common TDD Patterns](#common-tdd-patterns)
  - [Why This Matters for Power](#why-this-matters-for-power)
- [6. Reference Signals and Overhead](#6-reference-signals-and-overhead)
  - [SS/PBCH Block (SSB)](#sspbch-block-ssb)
  - [CSI-RS (Channel State Information Reference Signal)](#csi-rs-channel-state-information-reference-signal)
  - [DMRS (Demodulation Reference Signal)](#dmrs-demodulation-reference-signal)
  - [Power Implications of "Always-On" Signals](#power-implications-of-always-on-signals)
- [7. How the Scheduler Fills the Grid](#7-how-the-scheduler-fills-the-grid)
  - [The Scheduling Loop (Every Slot)](#the-scheduling-loop-every-slot)
  - [FDM Scheduling (Current srsRAN Default)](#fdm-scheduling-current-srsran-default)
  - [TDM Scheduling (Power-Optimized)](#tdm-scheduling-power-optimized)
  - [Visual Comparison: FDM vs TDM](#visual-comparison-fdm-vs-tdm)
- [8. Mini-Slots and Flexible Scheduling](#8-mini-slots-and-flexible-scheduling)
- [9. Cell DTX/DRX (3GPP Rel-18)](#9-cell-dtxdrx-3gpp-rel-18)
  - [What It Is](#what-it-is)
  - [How It Creates Sleep Opportunities](#how-it-creates-sleep-opportunities)
  - [Connection to Our Burst Experiment](#connection-to-our-burst-experiment)
- [10. Connection to Our Project](#10-connection-to-our-project)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Objective

To provide a self-contained reference so that someone reading the srsRAN scheduler deep-dive or the O-RAN Energy Saving deep-dive can understand:
1. **What** the scheduler is allocating (RBs, symbols, slots).
2. **Why** FDM wastes power (because the PA is on for the entire symbol duration regardless of how many subcarriers are used).
3. **How** TDM, Cell DTX/DRX, and sleep modes map to physical REs in the grid.

---

## 1. Why the Resource Grid Matters for Power

The O-RU Power Amplifier (PA) is the dominant energy consumer (60–80% of total RU power). The PA's power consumption depends on **how the resource grid is filled**:

- **Symbol with ANY data → PA must be ON** for the duration of that symbol (~71 µs at µ=0).
- **Symbol with ZERO data → PA can potentially sleep** (if sleep mode latency allows wake-up before the next active symbol).

Therefore, the scheduler's decision about *where* to place data in the grid directly determines the PA's duty cycle and, consequently, the RU's energy consumption.

**The core insight:** Spreading data across many symbols (FDM) keeps the PA busy in every slot. Compressing data into few symbols (TDM) creates idle symbols where the PA can sleep.

---

## 2. Time Domain Structure

### Hierarchy: Frame → Subframe → Slot → Symbol

5G NR inherits the LTE frame hierarchy but adds flexibility through **numerology**:

```
┌──────────────────────────────────────────────────────────────┐
│                    Radio Frame = 10 ms                        │
│  ┌──────┐ ┌──────┐ ┌──────┐        ┌──────┐                │
│  │SF #0 │ │SF #1 │ │SF #2 │  ...   │SF #9 │                │
│  │ 1 ms │ │ 1 ms │ │ 1 ms │        │ 1 ms │                │
│  └──┬───┘ └──────┘ └──────┘        └──────┘                │
│     │                                                        │
│     ▼  (Subframe contains 2^µ slots)                        │
│  ┌─────────┐ ┌─────────┐                                    │
│  │  Slot 0 │ │  Slot 1 │   (µ=1 → 2 slots per subframe)   │
│  │ 0.5 ms  │ │ 0.5 ms  │                                    │
│  └──┬──────┘ └─────────┘                                    │
│     │                                                        │
│     ▼  (Each slot has 14 OFDM symbols, normal CP)           │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐│
│  │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13││
│  └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘│
└──────────────────────────────────────────────────────────────┘
```

**Fixed constants (regardless of numerology):**
- 1 Radio Frame = **10 ms**
- 1 Subframe = **1 ms**
- 1 Slot = **14 OFDM symbols** (normal CP) or **12 symbols** (extended CP)
- 1 Subframe = $2^\mu$ slots

### Numerology (µ) — The Scaling Parameter

The numerology parameter µ defines the subcarrier spacing (SCS), which in turn determines the OFDM symbol duration and slot length. It's the key flexibility mechanism in NR:

| µ | SCS (kHz) | Slot Duration | Slots/Subframe | Slots/Frame | Primary Use |
|---|---|---|---|---|---|
| 0 | 15 | 1 ms | 1 | 10 | FR1 sub-3 GHz (LTE-compatible) |
| 1 | 30 | 0.5 ms | 2 | 20 | FR1 sub-6 GHz (common 5G) |
| 2 | 60 | 0.25 ms | 4 | 40 | FR1/FR2 crossover |
| 3 | 120 | 0.125 ms | 8 | 80 | FR2 mmWave |
| 4 | 240 | 62.5 µs | 16 | 160 | FR2 SSB only |

**Scaling rule:** Each increment of µ **doubles** the SCS and **halves** the symbol/slot duration. This comes from the fundamental OFDM relationship:

$$T_{symbol} = \frac{1}{\Delta f} = \frac{1}{15 \times 2^\mu \text{ kHz}}$$

### Slot Duration Table

| µ | SCS | Symbol Duration (incl. CP) | Slot Duration (14 symbols) |
|---|---|---|---|
| 0 | 15 kHz | ~71.4 µs | 1 ms |
| 1 | 30 kHz | ~35.7 µs | 0.5 ms |
| 2 | 60 kHz | ~17.8 µs | 0.25 ms |
| 3 | 120 kHz | ~8.9 µs | 0.125 ms |

### OFDM Symbol Duration

Each OFDM symbol consists of:
- **Useful symbol period:** $T_u = 1/\Delta f$ (carries data)
- **Cyclic Prefix (CP):** Guard interval to absorb multipath delay spread

| µ | OFDM Symbol (µs) | CP Duration (µs) | Total (µs) |
|---|---|---|---|
| 0 | 66.67 | 4.69 | 71.35 |
| 1 | 33.33 | 2.34 | 35.68 |
| 2 | 16.67 | 1.17 | 17.84 |
| 3 | 8.33 | 0.57 | 8.92 |

**Power implication:** At µ=1 (30 kHz SCS, common for 5G NR), one symbol is ~36 µs. The PA must be energized for each active symbol. If the scheduler leaves 1 symbol idle, that's only ~36 µs of potential sleep — barely enough for the fastest sleep mode (SM1, ~µs range).

---

## 3. Frequency Domain Structure

### Subcarrier and Resource Block (RB)

- **Subcarrier:** The smallest frequency unit. Spacing = $15 \times 2^\mu$ kHz.
- **Resource Block (RB):** 12 contiguous subcarriers in the frequency domain.
  - RB bandwidth = $12 \times \Delta f = 12 \times 15 \times 2^\mu$ kHz

| µ | SCS | RB Bandwidth |
|---|---|---|
| 0 | 15 kHz | 180 kHz |
| 1 | 30 kHz | 360 kHz |
| 2 | 60 kHz | 720 kHz |
| 3 | 120 kHz | 1.44 MHz |

**The RB is the fundamental scheduling unit in the frequency domain.** The scheduler assigns RBs to UEs. In srsRAN, the `intra_slice_scheduler` decides how many RBs each UE gets.

### Bandwidth Parts (BWP)

A **BWP** is a contiguous set of RBs within the carrier that a UE is configured to operate on. BWPs allow:
- Narrower-bandwidth UEs to save power by not monitoring the full carrier.
- Network to dynamically switch UEs between wide (high-data) and narrow (low-power) BWPs.

This is another energy-saving lever: if a UE doesn't need high throughput, it can be moved to a narrow BWP, reducing de-modulation complexity and allowing the RU to potentially reduce active antenna elements.

### Number of RBs vs Channel Bandwidth

For µ=1 (30 kHz SCS), the most common 5G sub-6 GHz configuration:

| Channel BW | Number of RBs |
|---|---|
| 10 MHz | 24 |
| 20 MHz | 51 |
| 40 MHz | 106 |
| 50 MHz | 133 |
| 80 MHz | 217 |
| 100 MHz | 273 |

**273 RBs at 100 MHz** is the maximum for FR1 with 30 kHz SCS. This is the number referenced in the srsRAN scheduler deep-dive when discussing how FDM spreads 273 RBs across multiple UEs per slot.

---

## 4. The Resource Grid

### Resource Element (RE)

The **Resource Element (RE)** is the smallest unit in the grid:
- **1 RE = 1 subcarrier × 1 OFDM symbol**
- It carries one complex-valued modulation symbol (e.g., one QPSK/16QAM/64QAM/256QAM symbol).

### Grid Visualization

The resource grid for one slot with 100 MHz bandwidth (µ=1):

```
Frequency ▲
(subcarriers)
          │
RB #272   │ ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
(12 SCs)  │ │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
          │ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
          │ │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ...    │ │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │
          │ │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
RB #1     │ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
(12 SCs)  │ │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
          │ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
RB #0     │ │RE │RE │RE │RE │RE │RE │RE │RE │RE │RE │RE │RE │RE │RE │
(12 SCs)  │ │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
          │ └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
          └──────────────────────────────────────────────────────────────►
            Sym Sym Sym Sym Sym Sym Sym Sym Sym Sym Sym Sym Sym Sym   Time
             0   1   2   3   4   5   6   7   8   9  10  11  12  13
            ◄────────────────── 1 Slot ─────────────────────────────►
```

**Total REs per slot:** $273 \text{ RBs} \times 12 \text{ SCs} \times 14 \text{ symbols} = 45{,}864 \text{ REs}$

This is the "canvas" the scheduler has to paint on every slot (0.5 ms at µ=1).

### What Lives in the Grid

Not all REs carry user data. Some are reserved for:

| Signal/Channel | Purpose | Power Impact |
|---|---|---|
| **SSB** (SS/PBCH Block) | Cell broadcast: synchronization + system info | Must be transmitted periodically (20 ms default) — **non-negotiable power baseline** |
| **PDCCH** (Control Channel) | DL control info, scheduling grants | 1–3 symbols per slot (CORESET) |
| **DMRS** | Demodulation reference signals | Sprinkled within each scheduled PDSCH/PUSCH allocation |
| **CSI-RS** | Channel measurement signals | Configurable periodicity |
| **PDSCH** | DL user data | Scheduled by the MAC layer — **this is what the scheduler controls** |
| **PUSCH** | UL user data | Scheduled by the MAC layer |
| **SRS** | Sounding reference signal (UL) | UL channel estimation |

---

## 5. Slot Formats and TDD Patterns

### Symbol Types: D, U, F

In TDD mode (shared spectrum for DL and UL), each symbol in a slot is designated:
- **D** = Downlink (gNB transmits, UE receives)
- **U** = Uplink (UE transmits, gNB receives)
- **F** = Flexible (can be used for either, or left empty as a guard)

3GPP defines 56+ predefined **Slot Formats** (38.213, Table 11.1.1-1). Examples:

| Format | Symbols 0–13 | Description |
|---|---|---|
| 0 | D D D D D D D D D D D D D D | All downlink |
| 1 | U U U U U U U U U U U U U U | All uplink |
| 2 | F F F F F F F F F F F F F F | All flexible |
| 28 | D D D D D D D D D D D D F U | DL-heavy with 1 UL symbol |
| 34 | D F U U U U U U U U U U U U | UL-heavy with DL control |

### Common TDD Patterns

A typical 5G NR deployment (e.g., n78 band, 30 kHz SCS) uses a repeating pattern of slot formats:

**DDDSU pattern** (common in many deployments):
```
Slot 0: D D D D D D D D D D D D D D   (all DL)
Slot 1: D D D D D D D D D D D D D D   (all DL)
Slot 2: D D D D D D D D D D D D D D   (all DL)
Slot 3: D D D D D D D D D D F F F U   (mostly DL, 1 UL, guard)
Slot 4: U U U U U U U U U U U U U U   (all UL)
                                        ← pattern repeats (2.5 ms) →
```

**Ratio:** 3.5 DL : 0.5 guard : 1 UL → ~70% DL, ~20% UL, ~10% guard.

### Why This Matters for Power

In formats 0 (all DL) and 1 (all UL):
- **All 14 symbols are active** → PA is ON for the entire slot.
- **Zero sleep opportunity** within the slot.

In format 34 (D F U...U):
- **Only 1 DL symbol** → PA could potentially sleep after symbol 0's DL transmission.
- **But:** The UE switches to UL reception in the remaining symbols, so the RU's Rx chains stay active.

**Key realization:** Even in UL-heavy slots, the RU's receive chain (LNA, ADC) consumes power. True "deep sleep" requires slots where the RU has **nothing to transmit AND nothing to receive** — which requires coordination at the network level (Cell DTX/DRX).

---

## 6. Reference Signals and Overhead

### SS/PBCH Block (SSB)

The **SSB** is a 4-symbol × 20-RB (240 subcarrier) block containing:
- PSS (Primary Synchronization Signal)
- SSS (Secondary Synchronization Signal)
- PBCH (Physical Broadcast Channel) + DMRS

**Key properties:**
- Default periodicity: **20 ms** (can be configured to 5, 10, 20, 40, 80, 160 ms).
- Must be transmitted even when there are **zero connected UEs** — it's how UEs discover and synchronize to the cell.
- At sub-6 GHz (Cases A/B/C): up to **4 or 8 SSB beams** per burst.
- At mmWave (Cases D/E): up to **64 SSB beams** per burst.

**Power implication:** SSBs represent a non-negotiable baseline power cost. Reducing SSB periodicity (e.g., from 20 ms to 160 ms) is one of the simplest energy-saving mechanisms (related to NES UC1/UC3). The 3GPP Rel-18 "SSB-less SCell Operation" feature aims to eliminate SSBs on secondary cells entirely.

### CSI-RS (Channel State Information Reference Signal)

Used by UEs to measure channel quality for CQI/PMI/RI reporting. Configurable periodicity (4, 5, 8, 10, 16, 20, 32, 40, 64, 80, 160, 320, 640 slots).

**Power implication:** CSI-RS can be a non-trivial overhead at high periodicities. During energy-saving modes, CSI-RS periodicity should be relaxed.

### DMRS (Demodulation Reference Signal)

Transmitted within each scheduled PDSCH/PUSCH allocation. The UE uses DMRS to estimate the channel for that specific allocation.

**Power implication:** DMRS overhead scales with the number of scheduled allocations. FDM scheduling (many small allocations per slot) requires more DMRS than TDM scheduling (one large allocation per slot) for the same total data volume.

### Power Implications of "Always-On" Signals

```
Power ▲
      │
      │  ┌──── SSB burst (4 symbols × 20 RBs) ────┐
      │  │                                          │
      │  │   ┌── CSI-RS (periodic) ──┐              │
      │  │   │                       │              │
  PA  │──┼───┼───────────────────────┼──────────────┼──────
 ON   │  │   │   User Data (PDSCH)   │              │
      │  │   │                       │              │
      │  └───┘                       └──────────────┘
      │
  PA  │  ............  potential sleep  .......................
 OFF  │
      └──────────────────────────────────────────────────────► Time
         0 ms        5 ms            10 ms          15 ms   20 ms
```

Even without user traffic, the gNB transmits SSBs every 20 ms. With CSI-RS configured, additional "always-on" symbols further reduce the sleep-capable window.

---

## 7. How the Scheduler Fills the Grid

### The Scheduling Loop (Every Slot)

Every Transmission Time Interval (TTI = 1 slot), the MAC scheduler:

1. **Reserves overhead:** SSB symbols, CORESET for PDCCH, CSI-RS.
2. **Collects UE requests:** Buffer status reports, scheduling requests.
3. **Applies policy:** Round Robin, Proportional Fair, Max Throughput, etc.
4. **Allocates RBs:** Assigns a frequency-domain grant (contiguous or non-contiguous RBs) to each scheduled UE.
5. **Fills the grid:** Places PDSCH allocations (with DMRS) into the remaining REs.
6. **Sends the grid to L1/PHY:** Which modulates, beamforms, and sends to the RU via Open Fronthaul.

### FDM Scheduling (Current srsRAN Default)

FDM = **Frequency Division Multiplexing**: multiple UEs share the same time slots but are separated in frequency.

```
Frequency ▲
          │ ┌─────────┬─────────┬─────────┬─────────┐
 RB 200+  │ │  UE #4  │  UE #4  │  UE #4  │  UE #4  │
          │ ├─────────┼─────────┼─────────┼─────────┤
 RB 136+  │ │  UE #3  │  UE #3  │  UE #3  │  UE #3  │
          │ ├─────────┼─────────┼─────────┼─────────┤
 RB  68+  │ │  UE #2  │  UE #2  │  UE #2  │  UE #2  │
          │ ├─────────┼─────────┼─────────┼─────────┤
 RB   0+  │ │  UE #1  │  UE #1  │  UE #1  │  UE #1  │
          │ └─────────┴─────────┴─────────┴─────────┘
          └──── Slot N ──── Slot N+1 ── Slot N+2 ── Slot N+3 ──► Time
```

**Power consequence:**
- Every slot has data across the **full bandwidth** → every symbol is "active."
- The PA operates at reduced power spectral density per subcarrier but is **ON for 14/14 symbols.**
- **Zero empty symbols → zero sleep opportunity.**

This is the behavior described in the srsRAN deep-dive: `get_max_grants_and_rb_grant_size` splits RBs equally among waiting UEs, ensuring every slot is fully occupied in frequency.

### TDM Scheduling (Power-Optimized)

TDM = **Time Division Multiplexing**: each UE gets the full bandwidth but only for certain slots.

```
Frequency ▲
          │ ┌─────────┬─────────┬─────────┬─────────┐
 RB 200+  │ │  UE #1  │  UE #2  │  EMPTY  │  EMPTY  │
          │ │ (ALL RBs)│(ALL RBs)│ (SLEEP) │ (SLEEP) │
 RB 136+  │ │         │         │         │         │
          │ │         │         │         │         │
 RB  68+  │ │         │         │         │         │
          │ │         │         │         │         │
 RB   0+  │ │         │         │         │         │
          │ └─────────┴─────────┴─────────┴─────────┘
          └──── Slot N ──── Slot N+1 ── Slot N+2 ── Slot N+3 ──► Time
                 ACTIVE    ACTIVE      💤 SLEEP   💤 SLEEP
```

**Power consequence:**
- Slots N and N+1 use full bandwidth (100% frequency utilization) for one UE each.
- Slots N+2 and N+3 are **completely empty** → PA can enter SM1/SM2.
- **50% duty cycle → substantial power savings** (our burst experiment showed ~48% reduction at iso-throughput).

**Trade-off:** UE latency increases because each UE must wait for its assigned slot. For eMBB (video streaming, downloads), this is acceptable. For URLLC (ultra-reliable low-latency), it is not.

### Visual Comparison: FDM vs TDM

```
         FDM (always on)                    TDM (burst + sleep)
   ┌──┬──┬──┬──┬──┬──┬──┬──┐       ┌──┬──┬──┬──┬──┬──┬──┬──┐
   │U1│U1│U1│U1│U1│U1│U1│U1│       │A │A │ 💤│ 💤│A │A │ 💤│ 💤│
   │U2│U2│U2│U2│U2│U2│U2│U2│       │L │L │   │   │L │L │   │   │
   │U3│U3│U3│U3│U3│U3│U3│U3│       │L │L │SLP│SLP│L │L │SLP│SLP│
   │U4│U4│U4│U4│U4│U4│U4│U4│       │  │  │   │   │  │  │   │   │
   └──┴──┴──┴──┴──┴──┴──┴──┘       └──┴──┴──┴──┴──┴──┴──┴──┘
   PA: ON  ON  ON  ON  ON  ON       PA: ON  ON  OFF OFF ON  ON  OFF OFF
   Power: ████████████████████       Power: ████████░░░░████████░░░░
```

---

## 8. Mini-Slots and Flexible Scheduling

5G NR allows scheduling at **sub-slot granularity** using mini-slots (2, 4, or 7 symbols). This is primarily for URLLC (low latency), but it has power implications:

- **Positive:** Mini-slot allocations can leave the remaining symbols in the slot empty → potential for intra-slot micro-sleep.
- **Negative:** More scheduling overhead (more PDCCH, more DMRS per data volume).

For energy saving, mini-slots could enable **symbol-level sleep** within a slot:
```
Slot: [PDCCH | DATA | DATA | DMRS | DATA |  💤  |  💤  |  💤  |  💤  |  💤  |  💤  |  💤  |  💤  |  💤 ]
       sym 0   sym 1  sym 2  sym 3  sym 4  sym 5  sym 6  sym 7  sym 8  sym 9  sym10  sym11  sym12  sym13
```

This is conceptually similar to the O-RAN SM1 (light sleep, µs wake-up), where the PA sleeps for individual symbols.

---

## 9. Cell DTX/DRX (3GPP Rel-18)

### What It Is

**Cell DTX (Discontinuous Transmission)** and **Cell DRX (Discontinuous Reception)** are 3GPP Rel-18 features that configure **periodic active/non-active patterns** for the gNB:

- **Cell DTX:** gNB does not transmit during non-active DL periods.
- **Cell DRX:** gNB does not monitor UL during non-active UL periods.

### How It Creates Sleep Opportunities

The gNB is configured with:
- An **active period** (e.g., 5 ms) where normal scheduling occurs.
- A **non-active period** (e.g., 15 ms) where the gNB can instruct the RU to enter sleep mode.

```
Time ──────────────────────────────────────────────────────►
        ┌──────────┐                    ┌──────────┐
  Active│ Schedule │    Non-Active      │ Schedule │    Non-Active
  Period│ normally │    (RU can sleep)  │ normally │    (RU can sleep)
        └──────────┘                    └──────────┘
        ◄── 5 ms ──►◄──── 15 ms ──────►◄── 5 ms ──►◄─── 15 ms ───►
```

**Duty cycle:** 5/20 = 25% active → potential power savings of up to ~75% on the PA component.

### Connection to Our Burst Experiment

Our burst experiment (2026-02-04) created exactly this pattern at the application layer:
- **Smooth (FDM proxy):** 30% constant rate → CPU/PA always active → 21.78 W.
- **Burst (TDM proxy):** 30% duty cycle at max rate → CPU races to sleep → 11.25 W.

Cell DTX/DRX standardizes this concept at the protocol level, making it interoperable and UE-aware. Our experiment is an empirical proof-of-concept for the same mechanism.

---

## 10. Connection to Our Project

| Concept from This Note | Project Experiment / Note |
|---|---|
| **OFDM symbol duration (~36 µs at µ=1)** | Defines the minimum sleep window the scheduler can create. SM1 (µs wake-up) can exploit individual empty symbols; SM2 (ms wake-up) needs multiple consecutive empty slots. |
| **273 RBs at 100 MHz** | The "total bandwidth" the srsRAN scheduler splits across UEs in FDM mode (scheduler deep-dive). |
| **FDM = all symbols active** | Explains why the default srsRAN scheduler prevents sleep → our "flat 50W band" in Week 3 load sweep. |
| **TDM = empty slots for sleep** | Explains why the proposed scheduler mod (`max_ue_grants = 1`) would create sleep opportunities → validated by burst experiment. |
| **SSB = always-on baseline** | Even with perfect TDM scheduling, SSBs force 4 active symbols every 20 ms. This sets a minimum PA duty cycle. |
| **Cell DTX/DRX (Rel-18)** | The standardized protocol version of our burst experiment. When FR1 UEs support Rel-18, this can be tested end-to-end. |
| **BWP switching** | A potential future experiment: move low-data UEs to narrow BWP → reduce the number of active RBs → reduce PA power per symbol. |
| **14 symbols per slot** | At µ=1, one slot = 0.5 ms. Our 10-second Scaphandre polling cadence averages over ~20,000 slots. We cannot resolve per-slot behavior — only aggregate effects. |

---

## Key Takeaways

1. **The resource grid is the bridge between scheduling decisions and PA power.** Every filled symbol keeps the PA on; every empty symbol is a potential sleep opportunity.

2. **FDM (srsRAN default) maximizes bandwidth utilization but prevents sleep.** All UEs share every slot → 14/14 symbols active → PA never turns off.

3. **TDM concentrates data in time, creating idle periods.** This is what the srsRAN scheduler modification targets and what our burst experiment validated.

4. **Reference signals (SSB, CSI-RS) are always-on overhead** that limit the minimum achievable PA duty cycle. Reducing SSB periodicity and CSI-RS frequency are low-hanging NES optimizations.

5. **Cell DTX/DRX (Rel-18) is the standardized version of TDM bursting** — it gives the gNB a protocol-compliant way to tell UEs "I won't be transmitting/receiving for the next N ms."

6. **At µ=1 (30 kHz), one symbol is ~36 µs.** SM1 (µs wake-up) can exploit symbol-level gaps; SM2 (ms wake-up) requires slot-level or multi-slot-level gaps.

7. **Our 10-second Scaphandre cadence cannot resolve per-slot behavior.** It measures the aggregate effect of scheduling patterns over thousands of slots — which is the correct abstraction for energy-level analysis.

---

## References

1. 3GPP TS 38.211 v17.6.0, "NR; Physical channels and modulation" (Resource grid, numerology, frame structure definitions).
2. 3GPP TS 38.213 v17.2.0, "NR; Physical layer procedures for control" (Slot formats, SS/PBCH beam management, Cell DTX/DRX).
3. 3GPP TS 38.214, "NR; Physical layer procedures for data" (PDSCH/PUSCH resource allocation).
4. 3GPP TS 38.300 v17.x, "NR; Overall description Stage 2" (Table 5.1-1: Supported numerologies).
5. Ericsson Technology Review, "5G NEW RADIO: Designing for the Future — The 5G NR Physical Layer," 2017.
6. Qualcomm, "Making 5G NR a Reality," White Paper, 2018.
7. ShareTechnote, "5G/NR Frame Structure," https://www.sharetechnote.com/html/5G/5G_FrameStructure.html.
8. O-RAN.WG1.NESUC-R003-v02.00, §7 (TDM scheduling prioritisation statement).
9. Our project: `docs/StudyNotes/2026-02-03_srsRAN-Scheduler-Deep-Dive.md` (FDM code path analysis).
10. Our project: `docs/StudyNotes/2026-02-04_Burst-Experiment-Validation.md` (TDM proxy validation — 48% power savings).
