# DCI Formats & PDCCH: The Scheduler's Air Interface Output (2026-02-26)

Status: Complete
Deadline: 2026-02-26

This note explains how the MAC scheduler's PRB allocation decision (studied in the 02-24 note) is **communicated to the UE** via Downlink Control Information (DCI) on the Physical Downlink Control Channel (PDCCH). It covers the DCI formats used for DL/UL scheduling, the bit-level encoding of frequency and time domain resource assignments, CORESET/search space configuration, and worked examples for our 273-PRB and 27-PRB scheduling scenarios.

## Table of Contents
- [Objective](#objective)
- [1. Where DCI Fits in the Scheduling Chain](#1-where-dci-fits-in-the-scheduling-chain)
- [2. DCI Format Overview](#2-dci-format-overview)
  - [2.1 The Four Scheduling DCI Formats](#21-the-four-scheduling-dci-formats)
  - [2.2 Fallback vs Non-Fallback](#22-fallback-vs-non-fallback)
- [3. DCI Format 1_0 — DL Scheduling (Fallback)](#3-dci-format-1_0--dl-scheduling-fallback)
  - [3.1 Field Breakdown](#31-field-breakdown)
  - [3.2 Frequency Domain Resource Assignment](#32-frequency-domain-resource-assignment)
  - [3.3 Time Domain Resource Assignment](#33-time-domain-resource-assignment)
- [4. DCI Format 1_1 — DL Scheduling (Non-Fallback)](#4-dci-format-1_1--dl-scheduling-non-fallback)
  - [4.1 Field Breakdown](#41-field-breakdown)
  - [4.2 Additional Fields for MIMO and BWP Switching](#42-additional-fields-for-mimo-and-bwp-switching)
- [5. DCI Format 0_0 / 0_1 — UL Scheduling](#5-dci-format-0_0--0_1--ul-scheduling)
- [6. Resource Allocation Type 0 vs Type 1](#6-resource-allocation-type-0-vs-type-1)
  - [6.1 Type 0: Bitmap (RBG-based)](#61-type-0-bitmap-rbg-based)
  - [6.2 Type 1: Contiguous (RIV-based)](#62-type-1-contiguous-riv-based)
  - [6.3 Which Type is Used?](#63-which-type-is-used)
- [7. RIV Encoding: Worked Examples](#7-riv-encoding-worked-examples)
  - [7.1 Scenario A: 273 PRBs in 1 Slot](#71-scenario-a-273-prbs-in-1-slot)
  - [7.2 Scenario B: 27 PRBs in 1 Slot](#72-scenario-b-27-prbs-in-1-slot)
  - [7.3 Bit-Level Representation](#73-bit-level-representation)
- [8. CORESET and Search Space](#8-coreset-and-search-space)
  - [8.1 What is a CORESET?](#81-what-is-a-coreset)
  - [8.2 Search Spaces](#82-search-spaces)
  - [8.3 Aggregation Levels and Blind Decoding](#83-aggregation-levels-and-blind-decoding)
  - [8.4 PDCCH Overhead Impact on Available PRBs](#84-pdcch-overhead-impact-on-available-prbs)
- [9. How OAI and srsRAN Build DCIs](#9-how-oai-and-srsran-build-dcis)
  - [9.1 OAI DCI Construction](#91-oai-dci-construction)
  - [9.2 srsRAN DCI Construction](#92-srsran-dci-construction)
- [10. Connection to Our Scheduling Scenarios](#10-connection-to-our-scheduling-scenarios)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Objective

After reading this note, the reader should be able to:
1. **Identify** which DCI format carries which scheduling information.
2. **Decode** the frequency domain resource assignment field to extract `(rbStart, rbSize)`.
3. **Explain** how the 273-PRB full-bandwidth grant and the 27-PRB narrowband grant are encoded differently in DCI.
4. **Understand** how CORESET and search spaces consume PRBs that reduce the available bandwidth for PDSCH/PUSCH.

---

## 1. Where DCI Fits in the Scheduling Chain

The MAC scheduler (studied in the 02-24 note) outputs a scheduling decision. But this decision must be **signalled to the UE over the air interface**. The signal chain is:

```
MAC Scheduler Decision     DCI Construction       Channel Coding        PDCCH Transmission
┌──────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ UE #1 gets       │     │ Format 1_1:  │     │ Polar coding │     │ Mapped to CCEs   │
│ rbStart=0        │ --> │ freq=RIV(545)│ --> │ + CRC + RNTI │ --> │ in CORESET       │
│ rbSize=273       │     │ time=row 2   │     │ masking      │     │ (aggregation     │
│ MCS=20           │     │ MCS=20       │     │              │     │  level 4 or 8)   │
│ nrOfLayers=2     │     │ layers=2     │     │              │     │                  │
└──────────────────┘     └──────────────┘     └──────────────┘     └──────────────────┘
        ↑                                                                    ↓
   gNB_scheduler_dlsch.c                                              UE receives PDCCH
   (OAI) or                                                           blind-decodes DCI
   intra_slice_scheduler.cpp                                          extracts (rbStart,
   (srsRAN)                                                           rbSize, MCS, ...)
                                                                      reads PDSCH at those
                                                                      PRBs
```

**Key insight:** The DCI is the "contract" between the gNB and UE. If the scheduler decides to give 273 PRBs to a UE, this decision is only effective if the DCI correctly encodes it and the UE successfully decodes the PDCCH.

---

## 2. DCI Format Overview

### 2.1 The Four Scheduling DCI Formats

3GPP TS 38.212 §7.3 defines the following DCI formats:

| DCI Format | Direction | Purpose | Complexity |
|---|---|---|---|
| **Format 0_0** | UL | Schedule PUSCH (one cell) | Compact (fallback) |
| **Format 0_1** | UL | Schedule PUSCH (one cell) | Full-featured |
| **Format 1_0** | DL | Schedule PDSCH (one cell) | Compact (fallback) |
| **Format 1_1** | DL | Schedule PDSCH (one cell) | Full-featured |
| Format 2_0 | — | Slot format indication | Group-common |
| Format 2_1 | — | Pre-emption indication | Group-common |
| Format 2_2 | — | TPC commands (PUCCH/PUSCH) | Group-common |
| Format 2_3 | — | TPC commands (SRS) | Group-common |
| Format 2_6 | — | Power saving (wake-up) | Group-common |

For our scheduling analysis, **only 0_0, 0_1, 1_0, and 1_1 matter**. The Format 2_x DCIs are group-common control messages, not user-specific scheduling grants.

### 2.2 Fallback vs Non-Fallback

| Aspect | Fallback (0_0 / 1_0) | Non-Fallback (0_1 / 1_1) |
|---|---|---|
| **When used** | Initial access, RRC setup, fallback | Normal UE-specific scheduling |
| **Search space** | Common search space | UE-specific search space |
| **BWP reference** | Initial BWP or CORESET 0 | Active BWP (can be full 273 PRBs) |
| **MIMO support** | Single layer only | Multi-layer (up to 8 layers) |
| **Size alignment** | DCI 0_0 padded to match DCI 1_0 size | Independent sizes |
| **Typical use in steady state** | Rare (fallback only) | **Primary scheduling format** |

**Important:** DCI 0_0 and 1_0 have the **same size** within a search space (0_0 is zero-padded if shorter). This allows the UE to distinguish them by a 1-bit "Identifier for DCI formats" field (0 = UL, 1 = DL).

---

## 3. DCI Format 1_0 — DL Scheduling (Fallback)

### 3.1 Field Breakdown

DCI Format 1_0 with CRC scrambled by C-RNTI:

| Field | Bits | Description |
|---|---|---|
| Identifier for DCI formats | 1 | Always `1` (= DL) |
| **Frequency domain resource assignment** | $\lceil \log_2(N_{BWP}^{RB} \cdot (N_{BWP}^{RB}+1)/2) \rceil$ | RIV encoding of `(rbStart, rbSize)` |
| **Time domain resource assignment** | 4 | Row index into `pdsch-TimeDomainAllocationList` |
| VRB-to-PRB mapping | 1 | 0 = non-interleaved, 1 = interleaved |
| Modulation and coding scheme | 5 | Index into MCS Table 1 or 2 (TS 38.214) |
| New data indicator | 1 | Toggle for new TB vs retransmission |
| Redundancy version | 2 | 0, 1, 2, or 3 |
| HARQ process number | 4 | Identifies HARQ process (0–15) |
| Downlink assignment index | 2 | For HARQ-ACK codebook |
| TPC command for scheduled PUCCH | 2 | Power control adjustment |
| PUCCH resource indicator | 3 | Which PUCCH resource to use for ACK |
| PDSCH-to-HARQ_feedback timing | 3 | k1 ∈ {1,2,3,4,5,6,7,8} slots |

**Total size** (for BWP = 273 PRBs): 1 + 16 + 4 + 1 + 5 + 1 + 2 + 4 + 2 + 2 + 3 + 3 = **44 bits** (+ CRC)

### 3.2 Frequency Domain Resource Assignment

The frequency domain resource assignment field carries a **Resource Indication Value (RIV)** that encodes the contiguous PRB allocation `(rbStart, rbSize)`:

$$RIV = \begin{cases} N_{BWP}^{size}(L_{RBs} - 1) + RB_{start} & \text{if } (L_{RBs} - 1) \leq \lfloor N_{BWP}^{size}/2 \rfloor \\ N_{BWP}^{size}(N_{BWP}^{size} - L_{RBs} + 1) + (N_{BWP}^{size} - 1 - RB_{start}) & \text{otherwise} \end{cases}$$

Where:
- $N_{BWP}^{size}$ = number of PRBs in the BWP (e.g., 273)
- $L_{RBs}$ = number of contiguously allocated PRBs (= `rbSize`)
- $RB_{start}$ = starting PRB index within the BWP (= `rbStart`)

The **number of bits** for this field:
$$N_{bits} = \lceil \log_2(N_{BWP}^{size} \cdot (N_{BWP}^{size}+1)/2) \rceil$$

For $N_{BWP}^{size} = 273$:
$$N_{bits} = \lceil \log_2(273 \times 274 / 2) \rceil = \lceil \log_2(37,401) \rceil = \lceil 15.19 \rceil = 16 \text{ bits}$$

### 3.3 Time Domain Resource Assignment

This 4-bit field is an **index** (0–15) into the `pdsch-TimeDomainAllocationList` configured by RRC. Each row specifies:

| Parameter | Description | Typical Value |
|---|---|---|
| **k0** | Slot offset from DCI to PDSCH | 0 (same slot) |
| **mappingType** | Type A (slot-based) or Type B (mini-slot) | Type A |
| **startSymbolAndLength (SLIV)** | Encodes (startSymbol, nrOfSymbols) | S=2, L=12 |

SLIV encoding (per TS 38.214 §5.1.2.1):
$$SLIV = \begin{cases} 14 \cdot (L - 1) + S & \text{if } (L - 1) \leq 7 \\ 14 \cdot (14 - L + 1) + (14 - 1 - S) & \text{if } (L - 1) > 7 \end{cases}$$

Where $S$ = start symbol, $L$ = number of symbols.

For typical PDSCH (S=2, L=12): SLIV = 14 × (12 − 1) + 2 = **156**

---

## 4. DCI Format 1_1 — DL Scheduling (Non-Fallback)

### 4.1 Field Breakdown

DCI Format 1_1 is the **primary scheduling format** used during normal operation:

| Field | Bits | Description |
|---|---|---|
| Carrier indicator | 0 or 3 | Cross-carrier scheduling (0 if single carrier) |
| Identifier for DCI formats | 1 | Always `1` (= DL) |
| **Bandwidth part indicator** | 0–2 | Which BWP to use (up to 4 configured) |
| **Frequency domain resource assignment** | Variable | RA Type 0 (bitmap) or Type 1 (RIV) |
| **Time domain resource assignment** | 0–4 | Row index into `pdsch-TimeDomainAllocationList` |
| VRB-to-PRB mapping | 0 or 1 | Only if RA Type 1 + interleaving configured |
| PRB bundling size indicator | 0 or 1 | Static or dynamic bundling |
| Rate matching indicator | 0–2 | Rate match around CSI-RS/SSB |
| ZP CSI-RS trigger | 0–2 | Zero-power CSI-RS activation |
| MCS [TB1] | 5 | Modulation and coding scheme, transport block 1 |
| NDI [TB1] | 1 | New data indicator, TB1 |
| RV [TB1] | 2 | Redundancy version, TB1 |
| MCS [TB2] | 5 | For 2-codeword MIMO (rank > 4) |
| NDI [TB2] | 1 | |
| RV [TB2] | 2 | |
| HARQ process number | 4 | |
| Downlink assignment index | 0, 2, or 4 | |
| TPC command for PUCCH | 2 | |
| PUCCH resource indicator | 3 | |
| PDSCH-to-HARQ timing | 0–3 | Configurable via RRC |
| Antenna port(s) and layers | 4–6 | DMRS port and layer mapping |
| TCI (Transmission Configuration) | 0 or 3 | QCL indication for beamforming |
| SRS request | 2 | |
| CBGTI | 0–8 | Code Block Group transmission info |
| CBGFI | 0–1 | Code Block Group flushing |
| DMRS sequence init | 1 | |

### 4.2 Additional Fields for MIMO and BWP Switching

Compared to Format 1_0, Format 1_1 adds:
- **BWP indicator**: Allows scheduling on a different BWP (e.g., switch from a narrow 20 MHz BWP to the full 100 MHz BWP for burst transmission)
- **Two transport blocks**: Supports codeword-to-layer mapping for rank > 4
- **Antenna ports**: Specifies which DMRS ports → how many MIMO layers
- **TCI**: Beam indication for beamformed PDSCH
- **Rate matching**: Avoids collisions with CSI-RS/SSB resources

**For our power analysis:** DCI 1_1 is what the scheduler uses to grant the full 273 PRBs (or 27 PRBs) to a UE in normal operation.

---

## 5. DCI Format 0_0 / 0_1 — UL Scheduling

The UL scheduling DCIs mirror DL:

| Field | 0_0 (Fallback) | 0_1 (Non-Fallback) |
|---|---|---|
| Identifier | 1 bit (= 0, UL) | 1 bit (= 0, UL) |
| Frequency domain RA | RIV (same formula as DL) | RA Type 0 or 1 |
| Time domain RA | 4 bits (index into `pusch-TimeDomainAllocationList`) | Variable |
| Frequency hopping | 1 bit | 0–1 bits |
| MCS | 5 bits | 5 bits |
| NDI | 1 bit | 1 bit |
| RV | 2 bits | 2 bits |
| HARQ process | 4 bits | 4 bits |
| TPC for PUSCH | 2 bits | 2 bits |
| **Additional (0_1 only)** | — | BWP indicator, SRS resource, precoding info, antenna ports, CSI request, PTRS-DMRS, etc. |

**For UL scheduling of 273 PRBs:** The same RIV formula applies. The gNB sends DCI 0_0 or 0_1 to tell the UE to transmit PUSCH on all 273 PRBs.

---

## 6. Resource Allocation Type 0 vs Type 1

### 6.1 Type 0: Bitmap (RBG-based)

Resource Allocation Type 0 uses a **bitmap** where each bit corresponds to a **Resource Block Group (RBG)**:

| BWP Size (PRBs) | RBG Size P (Config 1) | RBG Size P (Config 2) | Number of RBGs |
|---|---|---|---|
| 1–36 | 2 | 4 | 18 (Config 1) |
| 37–72 | 4 | 8 | 18 (Config 1) |
| 73–144 | 8 | 16 | 18 (Config 1) |
| **145–275** | **16** | **16** | **⌈(273+p)/16⌉ = 18** |

(p = offset for first RBG alignment; per TS 38.214 Table 5.1.2.2.1-1)

For BWP = 273 PRBs: 18 bits needed (one bit per RBG of 16 PRBs, except the first/last which may be smaller).

**Advantage:** Can allocate **non-contiguous** PRBs (useful for frequency-selective scheduling).
**Disadvantage:** Coarser granularity (16-PRB groups, not individual PRBs).

### 6.2 Type 1: Contiguous (RIV-based)

Resource Allocation Type 1 uses $\lceil \log_2(N_{BWP}(N_{BWP}+1)/2) \rceil$ bits to encode a **contiguous** allocation via the RIV formula.

For BWP = 273 PRBs: **16 bits** needed.

**Advantage:** Fine-grained (individual PRB granularity), compact encoding.
**Disadvantage:** Allocation must be contiguous.

### 6.3 Which Type is Used?

| Configuration | OAI | srsRAN |
|---|---|---|
| **DCI 1_0 (fallback)** | Type 1 only (hardcoded) | Type 1 only |
| **DCI 1_1 (non-fallback)** | Type 1 only (assertion enforced) | Configurable (Type 0, Type 1, or dynamic) |
| **DCI 0_0 / 0_1** | Type 1 | Type 1 |

OAI explicitly enforces Type 1:
```c
AssertFatal(pdsch_Config == NULL
    || pdsch_Config->resourceAllocation 
       == NR_PDSCH_Config__resourceAllocation_resourceAllocationType1,
    "Only frequency resource allocation type 1 is currently supported\n");
```

**For our analysis:** Both stacks use **Type 1 (contiguous RIV)**, which means our 273-PRB grant is encoded as a single RIV value, and the 27-PRB grant is a different RIV value.

---

## 7. RIV Encoding: Worked Examples

### 7.1 Scenario A: 273 PRBs in 1 Slot

**Given:** $N_{BWP}^{size} = 273$, $RB_{start} = 0$, $L_{RBs} = 273$

**Step 1:** Check condition: $(L_{RBs} - 1) = 272 > \lfloor 273/2 \rfloor = 136$ → Use **second formula**

**Step 2:** Compute RIV:
$$RIV = 273 \times (273 - 273 + 1) + (273 - 1 - 0) = 273 \times 1 + 272 = \mathbf{545}$$

**Step 3:** Binary representation (16 bits):
$$545_{10} = 0000\,0010\,0010\,0001_2$$

**Verification (reverse decode):**
Given RIV = 545:
- Try $L = N_{BWP} - \lfloor RIV / N_{BWP} \rfloor + 1 = 273 - \lfloor 545/273 \rfloor + 1 = 273 - 2 + 1 = 272$? No, check: if $RIV / N_{BWP} < N_{BWP}/2$... Actually the UE decodes by trying both formulas.
- With formula 2 path: $\lfloor 545/273 \rfloor = 1$, remainder = $545 - 273 = 272$
  - $L_{RBs} = N_{BWP} - 1 + 1 = 273$, $RB_{start} = N_{BWP} - 1 - 272 = 0$ ✓

### 7.2 Scenario B: 27 PRBs in 1 Slot

**Given:** $N_{BWP}^{size} = 273$, $RB_{start} = 0$, $L_{RBs} = 27$

**Step 1:** Check condition: $(L_{RBs} - 1) = 26 \leq \lfloor 273/2 \rfloor = 136$ → Use **first formula**

**Step 2:** Compute RIV:
$$RIV = 273 \times (27 - 1) + 0 = 273 \times 26 = \mathbf{7098}$$

**Step 3:** Binary representation (16 bits):
$$7098_{10} = 0001\,1011\,1011\,1010_2$$

### 7.3 Bit-Level Representation

| Scenario | rbStart | rbSize | RIV (decimal) | RIV (16-bit binary) |
|---|---|---|---|---|
| A: Full BW | 0 | 273 | 545 | `0000 0010 0010 0001` |
| B: 27 PRBs | 0 | 27 | 7098 | `0001 1011 1011 1010` |
| B: 27 PRBs (offset) | 27 | 27 | 7125 | `0001 1011 1101 0101` |
| B: 28 PRBs | 0 | 28 | 7371 | `0001 1100 1100 1011` |

The complete DCI 1_0 for Scenario A (44 bits total) would look like:
```
[1] [0000001000100001] [0010] [0] [10100] [1] [00] [0000] [00] [00] [000] [001]
 ↑        ↑              ↑    ↑     ↑     ↑   ↑    ↑      ↑    ↑    ↑     ↑
 DL  freq_domain=RIV545  TDRA VRB  MCS20  NDI RV  HARQ   DAI  TPC  PUCCH k1
```

---

## 8. CORESET and Search Space

### 8.1 What is a CORESET?

A **Control Resource Set (CORESET)** defines a specific region in the resource grid where the UE searches for PDCCH (and therefore DCI):

```
Frequency ▲
 PRB 272  │ .............. .............. ..............
          │ 
 PRB  48  │ ████████████████████████████ ..............  ← CORESET (48 PRBs × 2 symbols)
 PRB   0  │ ████████████████████████████ ..............
          └──Sym 0─Sym 1──────Sym 2────────────── Sym 13──►
          ◄─── PDCCH ────►◄──────── PDSCH ────────────────►
```

A CORESET is characterized by:
- **Frequency span**: Set of 6-PRB blocks (Resource Block Groups) in frequency
- **Duration**: 1, 2, or 3 OFDM symbols
- **CCE-to-REG mapping**: Interleaved or non-interleaved

### 8.2 Search Spaces

A **Search Space** defines *where* within the CORESET and *when* (which slots) the UE must monitor for PDCCH:

| Search Space Type | Purpose | DCI Formats Monitored | Typical Configuration |
|---|---|---|---|
| **Type0** (Common) | SIB1 (SI-RNTI) | 1_0 | Derived from PBCH MIB |
| **Type1** (Common) | Paging (P-RNTI) | 1_0 | Configured by SIB1 |
| **Type2** (Common) | RAR (RA-RNTI) | 1_0 | Configured by SIB1 |
| **Type3** (Common) | Group-common | 2_0, 2_1, 2_2 | Configured by RRC |
| **UE-specific** | Normal scheduling | **0_0, 0_1, 1_0, 1_1** | Configured by RRC |

**Key:**
- In **Common Search Space (CSS)**, the BWP reference for DCI 1_0 is the **Initial BWP** (which may be smaller than 273 PRBs, e.g., 48 PRBs).
- In **UE-specific Search Space (USS)**, the BWP reference for DCI 1_1 is the **Active BWP** (which can be the full 273 PRBs).

### 8.3 Aggregation Levels and Blind Decoding

Each DCI is mapped to one or more **Control Channel Elements (CCEs)**. The number of CCEs depends on the **aggregation level**:

| Aggregation Level | CCEs Used | REGs Used | Purpose |
|---|---|---|---|
| 1 | 1 | 6 | High SNR, small DCI |
| 2 | 2 | 12 | |
| 4 | 4 | 24 | **Typical for UE-specific** |
| 8 | 8 | 48 | Low SNR or large DCI |
| 16 | 16 | 96 | Cell edge UEs |

Each CCE = 6 REGs (Resource Element Groups), and each REG = 1 PRB × 1 OFDM symbol.

The UE performs **blind decoding**: it tries to decode DCI at each aggregation level and each candidate position within the search space, using its RNTI to check the CRC.

**Blind decoding budget** (per slot): Up to 44 PDCCH candidates across all search spaces and aggregation levels (TS 38.213 §10.1).

### 8.4 PDCCH Overhead Impact on Available PRBs

The CORESET occupies PRBs in the first 1–3 symbols of a slot. These symbols are **shared** between PDCCH and PDSCH:
- If CORESET uses symbols 0–1 (duration = 2), then PDSCH can start at symbol 2
- This means PDSCH gets **12 out of 14 symbols** (for Type A mapping with S=2, L=12)

The PDCCH symbols reduce the available REs for PDSCH but do **not** reduce the number of PRBs in frequency. The PDSCH can still span all 273 PRBs — it just starts at a later symbol.

**Impact on our scenarios:**
- Both the 273-PRB and 27-PRB grants have the same CORESET overhead
- The TDRA field (k0=0, S=2, L=12) means PDSCH uses symbols 2–13, regardless of grant size
- The overhead per slot is constant, not proportional to PRBs

---

## 9. How OAI and srsRAN Build DCIs

### 9.1 OAI DCI Construction

In OAI, the DCI is constructed in `gNB_scheduler_dlsch.c` after the PF scheduler decides the allocation:

```c
// In nr_schedule_ue_spec() → after pf_dl() decides rbStart, rbSize:
nfapi_nr_dl_dci_pdu_t *dci_pdu = &dl_dci_req->dci_pdu[DCI_idx];

// Populate DCI fields
dci_pdu->rnti = rnti;
dci_pdu->PayloadSizeBits = nr_dci_size(dci_format, ...);

// Fill PDSCH PDU
pdsch_pdu->BWPSize = bwpSize;        // 273
pdsch_pdu->BWPStart = bwpStart;      // 0
pdsch_pdu->rbStart = rbStart;        // 0 (for full BW)
pdsch_pdu->rbSize = rbSize;          // 273 (for full BW)
pdsch_pdu->resourceAlloc = 1;        // RA Type 1
pdsch_pdu->mcsIndex[0] = mcs;        // from MCS table
pdsch_pdu->nrOfLayers = nrOfLayers;  // 1, 2, or 4

// The FAPI interface carries these to the PHY, which:
// 1. Encodes the DCI (Polar code)
// 2. Maps it to PDCCH in the CORESET
// 3. Encodes the PDSCH data (LDPC)
// 4. Maps it to the allocated PRBs
```

### 9.2 srsRAN DCI Construction

In srsRAN, the DCI is built in `ue_cell_grid_allocator.cpp`:

```cpp
// After intra_slice_scheduler decides the VRB interval:
dci_dl_info dci;
dci.type = dci_dl_rnti_config_type::c_rnti_f1_1;  // Format 1_1
dci.freq_domain_assignment = compute_riv(bwp_size, rb_start, rb_size);
dci.time_domain_assignment = tdra_index;  // Row in TDRA list
dci.mcs = mcs_index;
dci.ndi = new_data ? 1 : 0;
dci.rv = rv_index;
dci.harq_id = harq_id;
// ... antenna ports, TCI, etc.
```

The `compute_riv()` function implements the exact RIV formula from TS 38.214:
```cpp
unsigned compute_riv(unsigned bwp_size, unsigned rb_start, unsigned rb_size) {
    if ((rb_size - 1) <= bwp_size / 2) {
        return bwp_size * (rb_size - 1) + rb_start;
    } else {
        return bwp_size * (bwp_size - rb_size + 1) + (bwp_size - 1 - rb_start);
    }
}
```

---

## 10. Connection to Our Scheduling Scenarios

| Aspect | 273 PRBs × 1 Slot | 27 PRBs × 10 Slots |
|---|---|---|
| **DCI format** | 1_1 (or 1_0) | 1_1 (or 1_0) |
| **Frequency domain RA** | RIV = 545 | RIV = 7098 |
| **RA bits** | 16 | 16 |
| **Time domain RA** | Index pointing to row with k0=0, S=2, L=12 | Same (each slot has its own DCI) |
| **DCIs per 10 slots** | **1** | **10** |
| **PDCCH overhead** | 1 CORESET occupation | 10 CORESET occupations |
| **PDCCH blind decodes** | 1 successful decode | 10 successful decodes |

**The DCI overhead difference:**
- Strategy A (273×1): 1 DCI × ~44 bits = 44 bits of control overhead
- Strategy B (27×10): 10 DCIs × ~44 bits = 440 bits of control overhead (10× more)
- Additionally, each DCI occupies CCEs in the CORESET, reducing PDCCH capacity for other UEs

**Power implication of PDCCH:**
- PDCCH itself requires the PA to be active during CORESET symbols
- In Strategy A, only 1 slot has CORESET activity for this UE
- In Strategy B, all 10 slots have CORESET activity → PA cannot sleep during CORESET symbols even in "data-empty" periods

---

## Key Takeaways

1. **DCI is the bridge** between the MAC scheduler's internal decision and the UE's actual reception. The scheduler outputs `(rbStart, rbSize, MCS, layers)` which gets encoded into DCI fields.

2. **DCI Format 1_1 (C-RNTI)** is the primary format for normal DL scheduling. It supports full BWP switching, multi-layer MIMO, and both RA Type 0 (bitmap) and Type 1 (RIV).

3. **Resource Allocation Type 1 (RIV)** is used by both OAI and srsRAN. The full 273-PRB grant encodes as RIV = 545; the 27-PRB grant encodes as RIV = 7098. Both fit in 16 bits.

4. **CORESET and search spaces** define where the UE looks for PDCCH. The CORESET occupies the first 1–3 symbols of a slot, reducing the available symbols for PDSCH but not the PRB count.

5. **DCI overhead scales with scheduling frequency:** The 27×10 strategy requires 10 DCIs vs 1 DCI for 273×1, adding 10× more control channel overhead and preventing CORESET symbols from being sleep-eligible.

6. **The RNTI identifies the UE:** The CRC of the DCI is masked with the UE's C-RNTI. Each UE blind-decodes all PDCCH candidates and checks if the CRC matches its RNTI.

---

## References

1. 3GPP TS 38.212 v17.x, "NR; Multiplexing and channel coding" — §7.3 (DCI formats, field definitions).
2. 3GPP TS 38.214 v17.x, "NR; Physical layer procedures for data" — §5.1.2.2 (Frequency domain RA Type 0/1), §5.1.2.1 (Time domain RA), §5.1.3 (TBS determination).
3. 3GPP TS 38.213 v17.x, "NR; Physical layer procedures for control" — §10 (PDCCH search spaces, CORESET, blind decoding), §11 (Slot format indication).
4. ShareTechNote, "5G/NR — DCI" ([sharetechnote.com](https://www.sharetechnote.com/html/5G/5G_DCI.html)).
5. Our project: `docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md` (Scheduler internals).
6. Our project: `docs/StudyNotes/2026-02-12_5G-NR-Resource-Grid-and-Scheduling-Fundamentals.md` (Resource grid foundation).
7. OAI Source Code, `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c` — DCI construction after PF scheduling.
8. srsRAN Project Source Code, `lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp` — DCI construction and RIV computation.
