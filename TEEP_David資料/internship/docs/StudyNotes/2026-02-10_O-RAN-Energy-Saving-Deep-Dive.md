# O-RAN Energy Saving Deep Dive: Standards, Sleep Modes & Project Connection (2026-02-10)

Status: Complete
Deadline: 2026-02-10

This note synthesises the O-RAN Alliance Network Energy Savings (NES) specifications and academic literature, mapping each mechanism back to the measurements and experiments conducted in this internship. It draws primarily from eight source documents provided in `assets/2026-02-10/`.

## Table of Contents
- [Objective](#objective)
- [Source Documents](#source-documents)
- [1. Why O-RAN Energy Saving Matters](#1-why-o-ran-energy-saving-matters)
- [2. NES Standardisation Timeline](#2-nes-standardisation-timeline)
- [3. The Four Core NES Use Cases (WG1)](#3-the-four-core-nes-use-cases-wg1)
  - [UC1 – Carrier / Cell Switch Off and On](#uc1--carrier--cell-switch-off-and-on)
  - [UC2 – RF Channel Reconfiguration](#uc2--rf-channel-reconfiguration)
  - [UC3 – Advanced Sleep Mode Selection](#uc3--advanced-sleep-mode-selection)
  - [UC4 – O-Cloud Resource Energy Saving](#uc4--o-cloud-resource-energy-saving)
- [4. O-RU Sleep Modes SM0–SM3 (WG4 / WG7)](#4-o-ru-sleep-modes-sm0sm3-wg4--wg7)
  - [Sleep Mode Definitions](#sleep-mode-definitions)
  - [CUS-Plane Commands](#cus-plane-commands)
  - [Energy Savings Estimates](#energy-savings-estimates)
- [5. RIC Control Loops for NES](#5-ric-control-loops-for-nes)
  - [Non-RT RIC (rApps) — Policy Guidance](#non-rt-ric-rapps--policy-guidance)
  - [Near-RT RIC (xApps) — Real-Time Execution](#near-rt-ric-xapps--real-time-execution)
  - [A1 Policy Interface (WG2)](#a1-policy-interface-wg2)
- [6. Energy Measurement KPIs (WG7 / SuFG)](#6-energy-measurement-kpis-wg7--sufg)
- [7. Next-Phase Features (SuFG White Paper)](#7-next-phase-features-sufg-white-paper)
- [8. RU Power Modelling in Simulation](#8-ru-power-modelling-in-simulation)
- [9. xApp-Based Energy Saving — Academic Approach](#9-xapp-based-energy-saving--academic-approach)
- [10. Connection to Our Project](#10-connection-to-our-project)
  - [What the Standards Validate](#what-the-standards-validate)
  - [What Our Data Adds](#what-our-data-adds)
  - [Implementation Gaps Remaining](#implementation-gaps-remaining)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Objective

To build a thorough understanding of the O-RAN Alliance's NES framework so the team can:
1. **Contextualise** the Week 3–4 power measurements within a standards-based framework.
2. **Identify** which NES mechanisms the srsRAN/O-DU scheduler experiments already exercise.
3. **Map** future work items (TDM bursting, sleep-mode integration) to the correct WG specs.

---

## Source Documents

| # | Document | Short Name |
|---|---|---|
| 1 | O-RAN.WG1.NESUC-R003-v02.00 | **WG1 NESUC** — NES Use Cases Technical Report |
| 2 | O-RAN.WG7.NES.0-R003-v03.0 | **WG7 NES** — NES Procedures & Performance Metrics |
| 3 | O-RAN.WG2.TS.A1AP-R004-v05.00 | **WG2 A1AP** — A1 Interface Protocol |
| 4 | O-RAN.WG4.TS.MP.0-R004-v19.00 | **WG4 MP** — Management Plane Specification |
| 5 | O-RAN.SuFG.TR.NES-Analysis-R004-v01.01 | **SuFG NES Analysis** — Energy Measurements Analysis |
| 6 | O-RAN.SuFG White Paper (Jan 2025) | **SuFG WP** — Potential Energy Savings Features |
| 7 | Liang et al., arXiv 2405.10116v1 (May 2024) | **Liang2024** — xApps for EE in O-RAN |
| 8 | Wadud & Afraz, arXiv 2509.10978v1 (Sep 2025) | **Wadud2025** — RU Energy Modeling in ns3-oran |

---

## 1. Why O-RAN Energy Saving Matters

Mobile radio access networks consume roughly **80 % of total network energy**, with the Radio Unit (O-RU) — specifically its Power Amplifier (PA) — being the dominant contributor. The O-RAN Alliance positions NES as a first-class initiative because:

* **Operational cost**: energy is the largest recurring OpEx item for operators.
* **Environmental commitments**: MoU signatories (DT, Orange, Telefónica, TIM, Vodafone) have listed energy efficiency as a top-priority requirement for Open RAN commercial readiness.
* **Architectural opportunity**: O-RAN's disaggregated design (O-RU / O-DU / O-CU) with open interfaces (E2, A1, O1, Open FH) allows *intelligence-driven* energy management that monolithic RANs cannot achieve.

> "Radio unit consume most amount of energy in a Mobile Network. Hence O-RAN focused mostly on achieving energy savings in O-RU as part of NES Phase 1 and 2." — *SuFG White Paper, §3*

---

## 2. NES Standardisation Timeline

| Phase | Period | Key Deliverables |
|-------|--------|------------------|
| **Phase 1** | 2022–2023 | WG1 UCTG Technical Report published (Mar 2023). Identified 4 NES use cases. Cell/Carrier Shutdown normative work via O1. |
| **Phase 2** | 2023–Jul 2024 | RF Channel ES (UC2) specified by WG2/WG3/WG4. Advanced Sleep Modes (UC4) specified by WG4 with RIC controls in WG2/WG3. O-RU Deep Hibernate mode added. A1 Policy & E2-SM CCC enhancements. WG6 O-Cloud ES TR. |
| **Phase 3 (next)** | 2025+ | PA dynamic voltage bias adaptation, renewable energy coordination, Artificial Load Generation, O-Cloud intelligent orchestration, 3GPP Rel-18 DTX/DRX integration. |

---

## 3. The Four Core NES Use Cases (WG1)

The WG1 NESUC Technical Report (R003-v02.00) defines four use cases. Each can be deployed with the **Non-RT RIC**, the **Near-RT RIC**, or both.

### UC1 – Carrier / Cell Switch Off and On

**Problem:** Capacity cells or carriers with minimal traffic still consume full power.

**Solution:** Intelligently switch off cells or carriers; hand traffic to neighbouring intra-RAT or inter-RAT cells. When load rises, switch them back on.

**O-RAN actors:**
* **Non-RT RIC** (rApp) analyses long-term traffic patterns and generates A1 policies.
* **Near-RT RIC** (xApp) receives E2 KPMs and executes carrier on/off via E2 control towards the O-DU.
* **O-DU** modifies the Open Fronthaul configuration.

**Energy savings estimate (WG7):**
* All RF carriers switched off → **80–99 %** savings on the O-RU.
* Single RF band switched off → **40–50 %**.
* Single component carrier switched off → **a few %**.

### UC2 – RF Channel Reconfiguration

**Problem:** At low traffic, all Tx/Rx antenna arrays remain active even though a subset would suffice.

**Solution:** Dynamically reduce the number of active Tx/Rx arrays within the O-RU.

**How it works:**
1. Near-RT RIC sends E2 control message to O-DU.
2. O-DU reconfigures the O-RU via Open FH (WG4 M-Plane or C-Plane).
3. O-RU deactivates specific antenna branches.

**Energy savings:** Reducing Tx/Rx array count can yield **tens of percent** savings — roughly proportional to the number of arrays disabled.

### UC3 – Advanced Sleep Mode Selection

**Problem:** Different O-RU vendors implement different sleep modes (SM0–SM3) with different capabilities and wake-up times. How does the system choose the optimal sleep mode for a given traffic pattern?

**Solution — the Capability Exposure Flow:**
1. **O-RU** exposes its supported sleep modes and their parameters to the **O-DU** via M-Plane.
2. **O-DU** aggregates capability data from all connected O-RUs and exposes a common SM set to the **SMO / RIC**.
3. **Non-RT RIC** (rApp) uses AI/ML to train a model on traffic patterns and SM transition costs. It generates an **A1 Policy** specifying SM utilisation guidance (e.g., "prefer SM2 during 02:00–06:00").
4. **Near-RT RIC** (xApp) refines the guidance in real time using E2 KPMs and issues SM configuration commands.
5. **O-DU** instructs the O-RU to enter/exit the designated sleep mode via CUS-plane Section Type 4 commands (TRX_CONTROL, ASM).

> **Critical quote from WG1 §7:**
> *"O-DU may prioritize time-domain scheduling over frequency domain scheduling or may compress data transmission to increase the number of symbols or slots without data."*

This statement directly validates the TDM-bursting hypothesis explored in our srsRAN scheduler deep-dive and the Week 4 burst experiment.

### UC4 – O-Cloud Resource Energy Saving

**Problem:** O-Cloud infrastructure (servers hosting O-CU/O-DU/Near-RT RIC) wastes energy on idle nodes and under-utilised CPUs.

**Sub-use cases:**
* **Cloud Node Shutdown** — consolidate NFs onto fewer physical nodes, shut down idle ones.
* **CPU Core Frequency / Pinning** — scale down CPU frequency during low demand.
* **C-State Usage** — deploy NFs with specific C-state configurations so unused cores enter deeper sleep.
* **Cluster Mode Selection** — switch between high-performance and energy-saving cluster modes.

**O-RAN actors:** SMO + Non-RT RIC provide guidance to FOCOM via the O2 interface.

> **Our relevance:** Scaphandre/RAPL measures exactly this — the CPU package power of the O-DU host. Our Week 3–4 experiments already show how CPU power scales with iperf3 load on the DUT.

---

## 4. O-RU Sleep Modes SM0–SM3 (WG4 / WG7)

### Sleep Mode Definitions

The WG4 CUS-plane specification and WG7 NES Procedures define a hierarchy of sleep modes, each trading deeper power savings for longer wake-up latency.

| Mode | Name | Description | Approx. Wake-up Time |
|------|------|-------------|---------------------|
| **SM0** | Idle / No sleep | Baseline active mode; all components powered. | — |
| **SM1** | Light sleep | PA and some digital processing suspended; synchronisation maintained. | ~µs range |
| **SM2** | Deep sleep | RF chains powered down; only clock and minimal control logic active. | ~ms range |
| **SM3** | Hibernate / Deep hibernate | M-Plane disconnected; near-complete power-down. Recovery via timer-based wake-up. | Seconds–minutes |

**Note:** Exact wake-up times are vendor-dependent and must be reported by the O-RU via M-Plane capability advertisement.

### CUS-Plane Commands

Sleep modes are activated via **Section Type 4** messages on the Open Fronthaul CUS-plane:

* **TRX_CONTROL** — controls individual transceiver chains (on/off/transition).
* **ASM (Advanced Sleep Mode)** — selects the target sleep level (SM1/SM2/SM3).

WG7 also maps NES features to **Section Type 8** (sleep acknowledgements and status reports).

### Energy Savings Estimates

From WG7 NES §5.2:

| NES Action | Estimated Savings |
|---|---|
| All RF carriers switched off | 80–99 % |
| RF band switched off | 40–50 % |
| Component carrier switched off | A few % |
| Rx/Tx array element reduction | Tens of % |
| Active Low Power Mode (relaxed ACLR/ACS) | Vendor-specific |

WG7 also provides a **Diurnal O-RU Power Calculator** framework that models 24-hour power consumption by allocating percentage time per hour across SM0–SM3 states, then weighting by each mode's power draw. This can be used for planning and capacity assessment.

---

## 5. RIC Control Loops for NES

### Non-RT RIC (rApps) — Policy Guidance

Time scale: **> 1 second** (typically minutes to hours).

Responsibilities for NES:
1. Collect O-Cloud Inventory & telemetry data (via O2).
2. Collect PM data including resource utilisation, mobility, and energy consumption (via O1).
3. Train & deploy AI/ML models to generate policies based on O1 & O2 data.
4. Generate **A1 Policies** for O-Cloud or E2 Nodes based on priority, load, and energy consumption.

### Near-RT RIC (xApps) — Real-Time Execution

Time scale: **10 ms – 1 s**.

Responsibilities for NES:
1. Collect traffic and energy-related data from E2 Nodes.
2. Collect E2 Node and O-RU capabilities (including SM support).
3. Execute E2 policies based on guidance provided by Non-RT RIC.
4. Issue RC switch-off / sleep-mode commands based on real-time load (as in Liang et al.'s xApp design).

### A1 Policy Interface (WG2)

The A1 interface carries three types of messages:
* **A1 Policy** — guidance from Non-RT RIC → Near-RT RIC (e.g., "target energy saving of X % while maintaining QoS threshold Y").
* **A1 Enrichment Information** — contextual data (e.g., ML model outputs, traffic predictions).
* **A1 Machine Learning** — model deployment from Non-RT RIC to Near-RT RIC.

For NES specifically, the A1 Policy can encode:
* QoS and energy saving requirements.
* High-level guidance on RAT / frequency layer / cell selection.
* SM utilisation preferences (e.g., "prefer SM2 when load < 20 %").

---

## 6. Energy Measurement KPIs (WG7 / SuFG)

### Standard KPIs from WG7

| KPI | Definition | Unit |
|-----|-----------|------|
| **DEE** (Data Energy Efficiency) | Data volume delivered per unit energy consumed | bit/J |
| **DEERU** | DEE specific to the O-RU | bit/J |
| **LEE** (Latency Energy Efficiency) | Latency performance per unit energy | (0.1 ms · J)⁻¹ |
| **DL_O-RU_Energy_Efficiency** | DL throughput / O-RU power consumption | bit/s/W |

### 3GPP PEE Measurements (from SuFG Analysis)

3GPP TS 28.552 defines Power/Energy/Environmental (PEE) metrics for 5G Physical Network Functions:

| Attribute | Description |
|-----------|-------------|
| PEE.AvgPower | Average power consumed over measurement period (W) |
| PEE.MinPower | Minimum power consumed (W) |
| PEE.MaxPower | Maximum power consumed (W) |
| PEE.Energy | Energy consumed (kWh) |
| PEE.AvgTemperature | Average temperature (°C) |

### SuFG Gap Analysis Findings

The SuFG NES Analysis identified critical gaps in current O-RAN specs:

1. **WG6 lacks a standardised data model for O2 PM measurements** — only supplier-proprietary dictionaries exist.
2. **No consensus on exposing hardware-level measurements** (CPU, NIC, accelerator) to SMO.
3. **No framework for computing energy efficiency** at hardware level (e.g., Compute/Watt).
4. All O-Cloud energy work remains at **study level** — no normative PM specs yet.

> **Our approach comparison:** We use **Scaphandre + Prometheus + RAPL** to measure CPU package power (µW granularity, ~10 s cadence). This is analogous to the O-Cloud PEE.AvgPower metric. Our methodology, while not O2-compliant, implements the *intent* of the SuFG recommendations at an experimental level.

---

## 7. Next-Phase Features (SuFG White Paper)

The SuFG White Paper (Jan 2025) proposes features for NES Phase 3+:

### O-RU Features
1. **Enhanced Coordination with Power Source** — O-RU reports whether it runs on battery/solar/grid; O-DU adjusts energy saving aggressiveness accordingly.
2. **PA Dynamic Voltage Bias Adaptation** — dynamically reduce PA backoff margin during low/no traffic, improving PA efficiency.
3. **Artificial Load Generation (ALG)** — inject controlled test load into O-RU to measure realistic energy consumption patterns without real UE traffic. Useful for xApp/rApp training.
4. **O-RU Dual Mode Operation** — switch between high-performance and energy-saving hardware modes.

### O-Cloud Features
5. **Intelligent Energy Management & Orchestration** — lifecycle management for VNFs/CNFs with energy focus; host consolidation for underutilised servers.
6. **Carbon-Efficient Workload Placement** — move CNFs to data centres with renewable power; integrate carbon footprint measurement.
7. **Energy-Efficient CNF Design** — design CNFs to exploit C-states (for bursty workloads) and P-states (for sustained workloads); leverage Acceleration Abstraction Layer (AAL).
8. **Enhanced Coordination between Data Centre, O-Cloud & NFs** — temperature/cooling coordination, energy-cost-aware scheduling.

### 3GPP Rel-18 Integration
9. **SSB-less SCell Operation** — reduce SSB broadcast power by deriving timing from other serving cells.
10. **Cell DTX/DRX** — configure periodic active/non-active patterns for gNB DL/UL to create guaranteed idle periods.
11. **Spatial & Power Domain Techniques** — antenna muting, power reduction based on spatial domain analysis.

> **Cell DTX/DRX (item 10)** is conceptually identical to the TDM bursting idea we explored in the srsRAN scheduler deep-dive. The 3GPP Rel-18 feature standardises what our burst experiment tested at the application layer.

---

## 8. RU Power Modelling in Simulation

Wadud & Afraz (2025) present the first ns3-oran RU power model. Key equations:

**Active mode:**

$$P_{\text{active}} = n_{\text{trx}} \cdot \frac{P_{\text{PA}} + P_0}{(1 - \delta_{\text{DC}})(1 - \delta_{\text{MS}})(1 - \delta_{\text{cool}})}$$

Where:
* $n_{\text{trx}}$ = number of transceiver chains
* $P_{\text{PA}} = \frac{P_{\text{tx}}}{\eta_{\text{PA}} \cdot (1 - \delta_{\text{af}})}$ (PA consumption, dominant term)
* $P_0 = P_{\text{RF}} + P_{\text{BB,proc}} + P_{\text{mmWave}}$ (fixed overhead)
* $\delta_{\text{DC}}$, $\delta_{\text{MS}}$, $\delta_{\text{cool}}$ = DC-DC, mains supply, cooling loss factors

**Sleep mode:**

$$P_{\text{standby}} = n_{\text{trx}} \cdot P_{\text{sleep}}, \quad P_{\text{sleep}} < P_0$$

### Reference Power Values (from Table II)

| Cell Type | Max Tx Power | PA Efficiency | Power per TRX Chain | Total BS Power | Coverage |
|-----------|-------------|---------------|--------------------:|---------------:|----------|
| Macro | 43–49 dBm | 25–35 % | 380–750 W | 6–20 kW | 1–5 km |
| Micro | 38–43 dBm | 30–40 % | 140–295 W | 1–4 kW | 200–500 m |
| Pico | 30–35 dBm | 35–45 % | 50–105 W | 0.2–1 kW | 50–200 m |
| Femto | 20–25 dBm | 40–50 % | 10–30 W | 20–240 W | 10–50 m |
| mmWave SC | 20–33 dBm | 25–40 % | 50–135 W | 1–6 kW | 50–300 m |

> **Key insight:** PA efficiency for macro cells is only **25–35 %**, meaning **65–75 % of PA input power is wasted as heat**. This is why sleep modes and PA dynamic voltage adaptation have such large potential impact.

---

## 9. xApp-Based Energy Saving — Academic Approach

Liang et al. (2024) propose two xApps for RC (Radio Card) switching in an O-RAN Near-RT RIC:

**xApp 1 — Idle RC Detection:**
* Iterate through all RCs.
* Check `RRC.ConnMean` KPM (connected UE count).
* If a RC has **zero UEs** → switch it to sleep mode.

**xApp 2 — Low-Load RC Consolidation:**
* After xApp 1, identify RCs with resource block usage and throughput below threshold.
* Attempt to **reassign UEs** from low-load RCs to other RCs, subject to:
  * RSRP ≥ γ_min (signal quality constraint)
  * Target RC load ≤ 50 % (overload prevention)
* If all UEs successfully reassigned → switch the low-load RC to sleep.

**Results:** Up to **50 % power savings** with minimal UE count (10 UEs across 12 O-RUs / 24 RCs) in the TeraVM RIC simulator.

**Power model used:**

$$P_{\text{RC}} = \sum_{m} \alpha_m \cdot P_{\text{Active}} + (1-\alpha_m) \cdot P_{\text{Sleep}} + \alpha_m \cdot \frac{P_{\text{tx}}}{\eta} \cdot P_{\text{RBusage}}^m$$

Where $\alpha_m \in \{0,1\}$ is the active/sleep indicator for RC $m$.

---

## 10. Connection to Our Project

### What the Standards Validate

| Our Experiment | O-RAN Standards Basis |
|---|---|
| **Scaphandre/RAPL CPU power measurement** | Implements the intent of SuFG PEE.AvgPower / O-Cloud energy metrics (3GPP TS 28.552). Our µW-cadence RAPL polling is more granular than the standard requires. |
| **Load sweep (idle → low → mid → high)** | Mirrors the traffic scenarios that drive UC1 (Carrier Switch Off), UC2 (RF Channel Reconfig), and UC3 (Sleep Mode Selection). Each load level corresponds to a different NES action zone. |
| **Burst experiment (TDM vs FDM)** | Directly exercises the mechanism described in WG1 §7: *"O-DU may prioritize time-domain scheduling over frequency domain scheduling."* Also conceptually identical to 3GPP Rel-18 Cell DTX/DRX. |
| **srsRAN scheduler deep-dive** | Identifies the exact code path where the O-DU makes the FDM-vs-TDM decision — the same decision point that the Near-RT RIC xApp would influence via E2 control. |
| **Two-host topology test** | Validates measurement methodology under realistic multi-hop conditions, separating DUT power from traffic-sink power (analogous to isolating O-RU power from O-Cloud power). |

### What Our Data Adds

1. **Empirical baseline for O-DU host power**: We have measured power at idle (~3.3 W CPU pkg), low load (~6 W), and high load (~15–16 W) on commodity laptop hardware. This provides a concrete data point for the O-Cloud power models that the standards leave as abstract formulas.

2. **Proportionality evidence**: Our load-vs-power regression shows near-linear scaling (R² > 0.85 across most runs), confirming the `P_data ∝ RBusage` term in the Liang et al. and Wadud & Afraz models.

3. **Repeatability metrics**: CV < 5 % across repeated runs demonstrates that RAPL-based measurement is stable enough for NES KPI reporting.

### Implementation Gaps Remaining

| Gap | Standards Reference | What We Would Need |
|---|---|---|
| **No actual O-RU** | WG7 SM0–SM3 definitions | Real O-RU hardware (e.g., Benetel RAN550) to measure PA-level power and exercise sleep modes. |
| **No RIC integration** | WG2 A1 / WG3 E2 | Deploy OSC Non-RT RIC + Near-RT RIC to generate A1 policies and issue E2 SM commands. |
| **No TDM scheduler mod** | WG1 §7 ("prioritize TDM") | Modify `srsRAN` `intra_slice_scheduler` to pack grants in time instead of frequency (as designed in the scheduler deep-dive). |
| **No diurnal profile** | WG7 diurnal calculator | Run a 24-hour sweep with realistic traffic profile to feed the WG7 hourly SM allocation model. |
| **No container-level energy** | SuFG REC-004 / REC-005 | Instrument individual containers (O-CU, O-DU) with cgroup-level energy accounting. |

---

## Key Takeaways

1. **The O-RAN NES framework is a three-layer system**: *policy* (Non-RT RIC / rApp) → *execution* (Near-RT RIC / xApp) → *actuation* (O-DU / O-RU via Open FH). Our experiments operate at the execution/actuation boundary.

2. **Sleep modes SM0–SM3 are the primary O-RU power lever**, but they require tight coordination with the scheduler. The WG1 statement about TDM prioritisation is the standards-level justification for the burst experiment.

3. **PA efficiency is the bottleneck**: at 25–35 % for macro cells, most input power is wasted. PA dynamic voltage bias adaptation (Phase 3) addresses this directly.

4. **Measurement standardisation is immature**: the SuFG Analysis found that O-Cloud PM reporting has no normative data model yet. Our Scaphandre/RAPL approach is ahead of the spec in granularity but behind in standardised interfaces.

5. **xApp-based RC switching can achieve 50 % savings** (Liang et al.), but requires the Near-RT RIC + E2 interface that srsRAN does not natively support. Bridging this gap is a key future work item.

6. **Cell DTX/DRX (3GPP Rel-18)** formalises the concept of periodic idle slots — precisely what our burst experiment creates at the application layer. When NR UEs supporting Rel-18 become available, this can be tested end-to-end.

---

## References

1. O-RAN.WG1.NESUC-R003-v02.00, "Network Energy Saving Use Cases Technical Report," O-RAN Alliance, Mar 2023.
2. O-RAN.WG7.NES.0-R003-v03.0, "Network Energy Savings Procedures and Performance Metrics," O-RAN Alliance, 2024.
3. O-RAN.WG2.TS.A1AP-R004-v05.00, "A1 Interface: Application Protocol," O-RAN Alliance, 2024.
4. O-RAN.WG4.TS.MP.0-R004-v19.00, "Management Plane Specification," O-RAN Alliance, 2024.
5. O-RAN.SuFG.TR.NES-Analysis-R004-v01.01, "Energy Measurements Analysis Report," O-RAN Alliance SuFG, 2025.
6. O-RAN.WP.Potential Energy Savings Features-v01.00, "Potential Energy Savings Features in O-RAN," O-RAN Alliance SuFG White Paper, Jan 2025.
7. X. Liang et al., "Enhancing Energy Efficiency in O-RAN Through Intelligent xApps Deployment," arXiv:2405.10116v1, May 2024.
8. A. Wadud and N. Afraz, "RU Energy Modeling for O-RAN in ns3-oran," arXiv:2509.10978v1, Sep 2025.
9. 3GPP TS 28.552 v18.5.0, "Management and orchestration; 5G performance measurements."
10. ETSI ES 203 228 v1.4.1, "Environmental Engineering (EE); Assessment of mobile network energy efficiency," Apr 2022.
