# WINLAB Baseline Extraction (2026-01-12)

## Paper(s) and sources
Status: Ready
Deadline: 2026-01-12

**Executive summary (baseline in one minute)**
The baseline for probation is the POET paper, which describes an open-source O-RAN energy-efficiency testing platform. The core measurement approach is a smart PDU queried nominally every 10 seconds as a ground-truth power stream, complemented by IPMI and software estimators (Scaphandre and Kepler), with power and performance metrics exported to Prometheus and visualized in Grafana. The most reproducible first targets are Fig. 4–7 (measurement comparisons and KPI alignment) plus the iPerf scenario with explicit PRB load and throughput numbers.

**Scope sanity check (critical for the stated probation topic: RU power consumption)**
- POET is primarily a **platform + measurement methodology** paper. In the local PDF, **Fig. 4–7 are measurement-method comparison plots** (PDU vs IPMI vs Scaphandre vs Kepler) plus KPI alignment.
- The testbed is described as including **physical O-RUs and SDR-based RUs**, but **RU vendor/model/firmware and RU measurement point are not specified** in the extracted text.
- For probation, this means:
	- Phase 1 (defensible quickly): reproduce the measurement stack behavior (Fig. 4–7 style) and KPI alignment.
	- Phase 2 (aligns with the Topic.md objective): apply the same measurement approach to our local RU and produce RU power-vs-load / power-vs-state sweeps.

**Primary baseline (local paper)**
- Local PDF: `assets/2026-01-12/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`
	- **Paper title (Fact):** POET: A Platform for O-RAN Energy Efficiency Testing
	- **Authors (Fact):** N. K. Shankaranarayanan, Zhuohuan Li, Ivan Seskar, Prasanthi Maddala, Sarat Puthenpura, Alexandru Stancu, Anurag Agarwal
	- **Affiliations (Fact):** Rutgers University WINLAB (NJ, USA); Open Networking Foundation (CA, USA); Cognizant (Bengaluru, India)
	- **Venue/year (Fact):** PDF header uses an IEEE template but includes placeholders (e.g., “©20XX IEEE”); venue/year not explicitly fixed in the header.
	- **Venue/year (Assumption):** Likely 2024-era draft based on citations to June 2024 O-RAN documents and a 2024 COMSNETS reference.
	- **DOI/link:** Not present in extracted metadata; treat as local baseline artifact.
	- **Dataset/code/appendix:** Not identified in quick extraction; check paper body/footnotes.

**Secondary sources (accessible web pages; good for orientation but often omit reproducible config)**
- WINLAB funding announcement (mentions measurement approach and integration goals): https://winlab.rutgers.edu/winlab-receives-ntia-funding-to-develop-next-generation-wireless-communications-technology/
- POET overview / metrics & testing (RCR Reader Forum, 2024-08-28): https://www.rcrwireless.com/20240828/5g/5g-energy-efficiency-metrics-models-and-system-tests-reader-forum
- POET initial observations (RCR Open RAN, 2024-11-06): https://www.rcrwireless.com/20241106/open_ran/5g-energy-efficiency-o-ran
- RU power behavior narratives (RCR 2025-10-20 “Powering the future…”): https://www.rcrwireless.com/20251020/5g/powering-the-future-5g-and-nextg-networks

If there are multiple WINLAB/POET papers, pick one as the primary baseline for probation and list the rest as secondary references.

## Experimental conditions reported
Status: Updated (partial extraction; RU hardware specifics still missing)
Deadline: 2026-01-12

Extract into a structured checklist:

In POET, the testbed includes both physical O-RUs and SDR-based RUs, but the paper does not specify (in the extracted passages) the exact RU models, vendors, or firmware. The measurement stack is explicitly described: power supplied to components is monitored via smart PDUs (Server Technology PRO3X and STV-6521V), server power is also collected via IPMI, and software estimators include Scaphandre and Kepler (RAPL-based). PDU querying is nominally every 10 seconds, while IPMI shows longer averaging behavior and can take on the order of 60 seconds to stabilize; one characterization notes IPMI power lower than PDU by ~10 W on average.

For workload, POET references end-to-end testing with iPerf and includes an Amarisoft UE-emulator plus modem/phone UEs. One explicitly reported scenario is an all-OAI bare-metal (rfsim) iPerf test where 1 UE corresponds to DU PRB load of 70% and aggregate DU DL throughput of 65 Mb/s, while 2 UEs corresponds to DU PRB load of 100% and aggregate DU DL throughput of 84 Mb/s (42 Mb/s per UE). Radio configuration and environment details (band/bandwidth/SCS, MIMO, scheduler, ambient/cabling) are still not specified in a reproducible way in the extracted text and will need to be determined for our local setup.

Missing details to flag explicitly:
- [x] Not specified (paper): Exact RU model/vendor/firmware and whether RU measurement is AC vs DC
	- Local decision (probation): software-only; no RU measurement point yet.
- [x] Not specified (paper): Exact time synchronization method across power + KPI streams
	- Local decision: log everything in UTC and use explicit `utc_markers.txt` anchors per run.
- [x] Not specified (paper): Exact scenario durations (warm-up/steady-state)
	- Local decision (frozen in Boundaries): 2 min warm-up + 5 min steady-state.

## Reported results to reproduce
Status: Updated (figure IDs extracted; RU hardware baselines still partially from web)
Deadline: 2026-01-12

For each plot/table, capture:

1) Figure/Table ID:
2) X-axis and units:
3) Y-axis and units:
4) Scenarios/curves included:
5) Key takeaways (1–3 bullets):
6) What you need to reproduce it (data + config + run duration):

Primary “target plots” from the POET paper (figure list):

- **Fig. 1.** O-RAN Architecture
- **Fig. 2.** Multi-pronged O-RAN EE/KPI metric collection approach
- **Fig. 3.** O-RAN energy-efficiency test system architecture
- **Fig. 4.** Characterization and comparison of power measurements from PDU
- **Fig. 5.** Top: Power measurements from PDU (green), IPMI (yellow), and scenarios as described in section III. (caption wraps in extraction)
- **Fig. 6.** Scaphandre-based power measurements and O1-like performance
- **Fig. 7.** Kepler-based power measurements for a multi-node Kubernetes ... (caption wraps in extraction)

## What to reproduce first (probation-ready)

1) **Fig. 4–7: measurement-method comparison + KPI alignment**
- Goal: show you can reproduce the “shape” and relative offsets of PDU vs IPMI vs software estimators.
- Minimum requirements:
	- Smart PDU power log at ~10 s cadence
	- IPMI power log (expect slower stabilization)
	- At least one workload step test (CPU or RAN workload), long enough to capture steady-state

Important note (to avoid drifting away from the probation topic): these plots validate the measurement pipeline; they do not automatically prove RU-specific power behavior unless the measurement point is on (or dominated by) the RU.

2) **iPerf scenario from POET paper (numeric target)**
- Scenario: all-OAI bare-metal deployment (rfsim) iPerf throughput test
- Target numbers (Fact, paper):
	- 1 UE: DU PRB Load **70%**, aggregate DU DL throughput **65 Mb/s**
	- 2 UEs: DU PRB Load **100%**, aggregate DU DL throughput **84 Mb/s** (**42 Mb/s per UE**)

If we can hit these numeric targets and log power + KPIs with aligned timestamps, we have a defensible baseline replication even before RU hardware-specific sweeps.

Candidate “target plots” implied by the accessible baseline sources:

1) **Power measurement tool comparison (PDU vs IPMI vs software estimators)**
- Figure/Table ID: **Fig. 4 / Fig. 5 / Fig. 6 / Fig. 7**
- X-axis: time
- Y-axis: power (W)
- Scenarios: at least one steady scenario across multiple methods
- Key takeaways (paper/web):
	- **Fact (paper):** PDU and IPMI track similarly but IPMI shows longer averaging (~60s stabilization) and lower reported power (example: ~10 W lower on average in one characterization).
	- **Fact (paper):** Software tools (Scaphandre/Kepler) provide useful trend/process/container insight but are not full-system ground truth.
- Needs to reproduce:
	- Same device(s), same scenario timing, same polling cadence, synchronized timestamps

2) **O-RU power vs utilization / offered load**
- Figure/Table ID: Needs paper
- X-axis: load metric (PRB utilization % and/or throughput)
- Y-axis: power (W) and/or energy (Wh)
- Scenarios: idle → active-idle → increasing load
- Key takeaways (web):
	- **Fact (example datapoint):** A medium-power O-RU is described at ~59 W at “active-idle” (~0% utilization).
- Needs to reproduce:
	- Clear definition of load, run duration, and whether measurement is AC or DC

3) **O-RU power vs RF output power (including low-power regime)**
- Figure/Table ID: Needs paper
- X-axis: RF output power (W or dBm)
- Y-axis: input power (W) and/or PA efficiency (%)
- Scenarios: sweep RF output, compare RU classes
- Key takeaways (web):
	- **Fact:** Power amplifier efficiency is strongly non-linear; low RF output has low efficiency.
	- **Fact (narrative):** At very low RF output (e.g., ~1 W), “idle/overhead” dominates energy consumption.
- Needs to reproduce:
	- RF output calibration method and exact sweep points

4) **Frequency-domain vs time-domain loading effect**
- Figure/Table ID: Needs paper
- X-axis: loading type or loading factor
- Y-axis: power (W)
- Scenarios: keep average throughput similar; vary how resources are allocated
- Key takeaways (web):
	- **Fact (narrative):** Power can differ depending on whether loading is primarily frequency-domain or time-domain.
- Needs to reproduce:
	- Scheduler/resource allocation definitions and measurement synchronization

## Notes / assumptions
Status: Updated (pending PDF deep dive)
Deadline: 2026-01-12

Rules:
- Use **Fact:** and **Assumption:** labels.
- When a detail is missing, prefer adding it as an open question instead of silently assuming.

**Fact:** POET platform descriptions reference smart PDUs, IPMI, and software estimators (Kepler/Scaphandre) with a metrics pipeline (Prometheus/Grafana).

**Fact:** WINLAB describes “ground truth” energy measurements for PNFs like O-RUs using monitored PDUs and a dynamic DC power supply.

**Assumption:** The primary baseline figures you want to reproduce are reported in `assets/2026-01-12/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`.

**Open questions / needs PDF extraction (high priority)**
- Full figure captions for Fig. 5 and Fig. 7 (caption lines wrap in extracted text; verify directly in the PDF)
- Exact RU models/vendors/firmware
- Exact measurement point (AC vs DC) used for each reported result
- Exact polling/sampling/averaging, and time synchronization method
- Exact workload definitions and radio configuration parameters

**RU-specific extraction checklist (must-have for the Topic.md objective)**
- [ ] Which POET experiments/results actually include a **physical O-RU** (vs SDR RU / server-only power)?
- [ ] For those experiments: measurement point (AC/DC/PoE), instrument type, and polling/averaging.
- [ ] RU state definitions used (idle vs active-idle vs load) and how “load” is defined.
- [x] If POET does not contain RU-specific sweeps: pick the best RU-focused baseline among local PDFs under `assets/2026-01-12/WINLAB Baseline/` and `assets/2026-01-12/Target Plots/`.
	- Picked baseline (next extraction target): `assets/2026-01-12/WINLAB Baseline/O-RAN.SuFG.Potential Energy Savings Features in O-RAN white paper 2025-01.pdf`
	- Rationale: most directly RU-energy focused by title; used to ground RU state/feature language if POET lacks RU sweeps.

## Tomorrow (Jan 13) follow-ups
Status: Done

Outcome:
- Local “frozen” decisions (warm-up/steady windows, load definition, labeling rules) recorded in `docs/StudyNotes/2026-01-13_Boundaries.md`.
- RU model/firmware + RU input power measurement point explicitly deferred until hardware/instrument access.
