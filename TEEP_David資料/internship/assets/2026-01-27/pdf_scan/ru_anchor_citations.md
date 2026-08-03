# RU anchors: citation checklist (Jan 27, 2026)

Goal: eliminate “hand-wavy” parameters by recording the *exact* PDF locations (page + figure/table) for the numeric anchors we used in Week 4.

## A) P12 (RU electrical power anchors)
Source file:
- `assets/2026-01-12/WINLAB Baseline/P12.pdf`

Target items to record (exact page + figure/table label):
- Macro RU: $P_{min}=197\,\text{W}$, $P_{max}=531\,\text{W}$
- Micro RU: $P_{min}=59\,\text{W}$, $P_{max}=110\,\text{W}$
- Definition of load proxy: `ru_load` derived from traffic volume (bytes/hour)
- Measurement point: RU electrical input power (Watts)
- Scenario notes (if present near the figure/table): highway setting, tower range, any RU/radio config

How to capture (fast):
1. Open the PDF.
2. Search for `197`, `531`, `59`, `110`, `ru_load`, and `W`.
3. Write down:
   - PDF page number (as shown by the PDF viewer)
   - If present, the figure/table number and caption text

Fill here:
- Page 1, Section "Equations" ("Basic RU Power Model"): Macro RU $P_{min}=197$ W, $P_{max}=531$ W
- Page 1, Section "Equations" ("Basic RU Power Model"): Micro RU $P_{min}=59$ W, $P_{max}=110$ W
- Page 1, Section "Equations" ("Basic RU Power Model"): `ru_load` is used as the load scaling factor
- Page 1, Section "Highway Traffic Dataset": load proxy derived from traffic volume (bytes/hour) over a 7-day period
- Page 1, Section "O-RAN Architecture": measurement point is the RU individual component, with power ranges in Watts
- Page 1, Sections "Highway Scenario" and "Data Collected/Plots": scenario details (30-mile highway NJ↔NYC; Macro tower range 1000 m; Tx power 45 dBm; max user capacity 6000)

## B) POET (server-side / virtualized RAN reference)
Source file:
- `assets/2026-01-12/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`

Important: POET numbers are **server electrical input power** (PDU/IPMI/etc.), not RU hardware power. Use for CU/DU/Core virtualization context.

Target items to record (exact page + figure/table label):
- The figure/table that shows PDU/IPMI/Scaphandre comparison and mentions baseline/idle/loaded power
- The definition of “load” (e.g., number of UEs / PRB utilization)
- Measurement point: PDU as ground truth

Fill here:
- Page 4, Figure 4: PDU (green) as ground truth for server power; comparison vs IPMI (yellow) and Kepler (blue)
- Page 5, Section "V. RESULTS": baseline/idle and load steps (Baseline 4.13 W; 1 UE 22.2 W; 2 UE 22.9 W; server saturation 330 W at 32-CPU stress)
- Page 2, Section "II. ENERGY EFFICIENCY...": load defined by number of UEs/RRC connections per cell and DL/UL PRB utilization per cell

## Where these anchors are used
- Notebook baseline RU parameters: `notebooks/Week4_Virtual_ORU_Simulation.ipynb` (P12 Macro)
- Sweep includes Macro+Micro anchors and appears in:
  - `assets/2026-01-26/plots/gap_analysis_sensitivity.png`
  - `assets/2026-01-26/plots/gap_analysis_sensitivity_summary.md`

## Done criteria (no placeholders)
- Every numeric anchor used in the notebook has a page + figure/table reference recorded above.
- The Day 9 model note includes those references in the source paragraph.
