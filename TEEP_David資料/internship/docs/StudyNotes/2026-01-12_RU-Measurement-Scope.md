# RU Power Measurement Scope (2026-01-12)

## Metrics definitions
Status: Finished
Deadline: 2026-01-12

**Executive summary (what we will measure and how)**
This replication will report **real power** $P$ (W) and **energy** $E$ (Wh/J) at a clearly defined measurement point. For Week 1 (probation), we assume we may only have **platform-level power** on the compute host (via a software tool such as Scaphandre/Kepler) and we will label outputs accordingly (“platform power under RU-like workload”). The target measurement point for the actual RU replication is the RU **AC input** using a smart PDU or power analyzer (and we will explicitly document any deviation such as DC-rail measurement). To stay baseline-compatible with POET-style PDU logging once available, we assume a **~10 s** logging cadence and run each scenario for at least **5 minutes** of steady-state so coarse polling and averaging do not dominate the result. The minimal scenario set is: idle → active-idle → low/medium/high load.

Define exactly what “power consumption” means in this replication.

**Primary metric(s) (recommended)**
The primary outputs are **real (active) power** $P$ (W) at the chosen measurement point and **energy** $E$ (Wh/J) integrated over a defined interval. These two are sufficient to support comparisons across scenarios and to compute efficiency metrics later.

**Optional derived metrics (only if traffic accounting is solid)**
If traffic accounting is solid, we can additionally report energy efficiency as either **energy per bit** $\text{J/bit} = \frac{E\,(J)}{\text{bits delivered}}$ or **bits per Joule** $\text{bit/J} = \frac{\text{bits delivered}}{E\,(J)}$. A simpler secondary presentation is **W/(Mb/s)**, but only if “throughput” is defined precisely (e.g., UDP goodput vs TCP goodput vs MAC throughput).

**Measurement point (pick one)**
The measurement point must be chosen explicitly because it changes what is included in “power consumption.” Measuring at **AC input** is the easiest to reproduce and includes PSU losses; measuring at the **DC rail** is closer to device-internal consumption but excludes AC/DC conversion; for **PoE**, measurement must be done at the PSE/injector or via an inline PoE analyzer.

**Power quality and non-idealities to record (if available)**
- **PF (power factor)**, because $\text{PF}=\text{W}/\text{VA}$ and RU/compute loads can be non-sinusoidal.
- Crest factor / harmonics (if your meter supports it).

Basic principles (keep these explicit in the note):
Basic principles: use consistent units (W for power, Wh/J for energy, bps for throughput) and define your averaging/windowing. If using a smart PDU, POET reports querying PDUs nominally every **10 seconds**, so scenarios must be long enough to reach steady-state; if using a power analyzer, you can log finer-grain waveforms but should still report a standard analysis window. Sampling must be sufficient for the phenomenon you want to claim; if you only have coarse polling, treat transients/state-change dynamics as out-of-scope. Finally, keep timestamps aligned (UTC everywhere) and log explicit scenario start/stop markers.

**Proposed defaults for probation (make these explicit unless mentor overrides)**
Proposed defaults for probation: timestamp in UTC; log a scenario ID and start/stop markers in both KPI and power logs; report mean $P$ over the steady-state interval (optionally min/max or p5/p95); report $E$ over the same interval; report mean throughput and mean PRB utilization computed over the same interval; repeat each scenario 3 times and report mean ± std.

**Performance KPIs to log alongside power (from POET paper examples)**
Alongside power, log the KPIs that POET uses for alignment and efficiency interpretation: UE/RRC connections per cell, DL/UL PRB utilization per cell, DL/UL throughput (per cell and per UE), DL/UL data volume (per cell and per UE), latency (per UE and aggregate), and MCS (per UE and aggregate).

**Ground truth vs estimators (recommended framing)**
- Treat PDU / analyzer / DC-supply measurement as **ground truth** (system-level depending on point).
- Treat IPMI / Kepler / Scaphandre / RAPL-style telemetry as **secondary** and document what components they miss.

## Variables and scenarios
Status: Finished
Deadline: 2026-01-12

Variables should be separated into (1) independent variables we control, (2) dependent variables we measure, and (3) controlled variables we keep constant so changes in results remain attributable.

Independent variables include the traffic/load profile (idle, active-idle, and low/medium/high load defined by throughput and/or PRB utilization), RU operational state (active/idle/sleep if supported), any RF output power sweep (if controllable), the distinction between frequency-domain vs time-domain loading, antenna-chain configuration (if configurable), and radio configuration parameters (bandwidth, duplexing, SCS/numerology) where applicable.

Dependent variables include real power vs time, energy per scenario, and (optionally) derived efficiency metrics such as J/bit or bit/J. Supporting telemetry such as RU M-Plane (if available), IPMI, CPU utilization, and temperature should be logged to aid interpretation and debugging.

Controlled variables that must remain constant across runs include firmware/software versions, ambient conditions (as feasible), and physical/electrical setup (cabling, supply voltage, measurement configuration).

Scenarios should be defined as a small matrix of (state × load × radio config) with a fixed run structure and duration.

**Minimal scenario set (recommended for probation)**
For probation (software-only), interpret “RU states” as **scenario states of the workload pipeline**:
- S1 idle (no traffic)
- S2 active-idle (stack/tools on, no traffic)
- S3/S4/S5 low/medium/high offered load (throughput-defined)

When RU hardware + a meter are available, the same scenario structure is reused and the measurement point is moved to RU AC input.

**Run structure (works even with slow PDU polling)**
Use a simple run structure: 1–2 minutes warm-up after configuration changes, 3–5 minutes steady-state measurement per scenario (longer if your PDU polling is slow), optional 1 minute cooldown, and at least 3 repeats per scenario to estimate noise.

## Replication acceptance criteria
Status: Finished
Deadline: 2026-01-12

Define “success” in a way that you can defend:
- **Metric alignment**: same metric definitions and measurement point as WINLAB/POET (or explicitly justify differences).
- **Scenario alignment**: same workload/state transitions and run durations.
- **Trend match**: curves have the same qualitative behavior (monotonicity, knee points, relative ordering between scenarios).
- **Quantitative tolerance (optional)**: pick a reasonable error band *after* you see your instrumentation noise.

Note: if you cannot match the measurement point (e.g., baseline measured DC but you only have AC), document the deviation and compare trends rather than absolute values.

Practical tolerance guidance (keep qualitative until you can measure your noise floor):
- When comparing different measurement methods (e.g., PDU vs IPMI), expect systematic offsets; focus on trend agreement and record the bias.

## Tomorrow (Jan 13) follow-ups
Status: Done

Outcome:
- Frozen definitions captured in `docs/StudyNotes/2026-01-13_Boundaries.md`.
- For the WSL2 pilot (Day 4), RU model/firmware and RU input power measurement are explicitly out of scope; results are labelled “platform power under RU-like workload” and power is reported as unavailable when counters are missing.

## Sources used (web)
- POET baseline paper (local PDF): `assets/2026-01-12/Workload Definition/POET_A_Platform_for_O-RAN_Energy_Efficiency_Testing.pdf`
- WINLAB NTIA funding announcement (mentions monitored PDUs + dynamic DC supply for “ground truth” energy): https://winlab.rutgers.edu/winlab-receives-ntia-funding-to-develop-next-generation-wireless-communications-technology/
- POET methodology / metrics overview (RCR Reader Forum): https://www.rcrwireless.com/20240828/5g/5g-energy-efficiency-metrics-models-and-system-tests-reader-forum
- POET observations & tool comparisons (RCR Open RAN): https://www.rcrwireless.com/20241106/open_ran/5g-energy-efficiency-o-ran
- AC power measurement concepts (W/VA/PF/crest factor): https://www.weschler.com/reference/guides/ac-power-measurement-guide/
- Tektronix power measurement app note (wiring/logging concepts): https://www.tek.com/en/documents/application-note/power-measurements-ac-dc-power-supplies
- Tektronix PA3000 datasheet (example analyzer specs): https://www.tek.com/en/datasheet/pa3000-power-analyzer-datasheet
- Yokogawa PZ4000 technical report (example analyzer specs): https://www.yokogawa.com/library/resources/yokogawa-technical-reports/pz4000-power-analyzer/
