# Energy & Power Metrics Glossary (Day 3 — 2026-01-14)

Status: Done
Deadline: 2026-01-14

## What this note is
This note is a **short training primer** for the power/energy terms used in this project.

It is written to:
- define the metrics precisely,
- provide the intuition needed to interpret plots,
- explain how the metrics are computed in our analysis workflow.

Context: during probation we are not measuring RU wall power; we are validating a reproducible method using **platform power under RU-like workload**.

## Mental model (one minute)
- **Power (W)** answers: “how fast am I burning energy right now?”
- **Energy (Wh or J)** answers: “how much did I burn over this whole interval?”
- **Efficiency (J/bit or bit/J)** answers: “how much energy did I spend to deliver useful work (data)?”

In our workflow, everything comes down to: pick a window → compute a mean power → integrate power to get energy → optionally divide by delivered bits.

## Core quantities (what we actually compute)
### Power (W)
- **Power** is the *rate of energy use*.
- In plots, we want a time series $P(t)$ so we can see what happens when we change system state.

Key practical idea: the raw power signal usually has noise and steps. That’s why we use **steady-state windows** rather than “instantaneous” samples to make claims.

Notation:
- $P$ is power in W.
- If you see values like 50–200 W, that is a typical compute-host range depending on workload.

### Energy (Wh, J)
- **Energy** is power accumulated over time.
- From sampled power, energy over a window can be approximated by:

$$
E \approx \sum_i P_i \Delta t
$$

- Unit conversions:
  - $1\,Wh = 3600\,J$
  - If $P$ is in W and $t$ is in seconds, $E$ naturally comes out in joules.

Interpretation:
- If a system draws a constant 100 W for 5 minutes, it used:

$$
E = 100\,W \times 300\,s = 30{,}000\,J \approx 8.33\,Wh
$$

### Windowing (warm-up vs steady-state)
We treat each scenario as:
- **Warm-up window** (ignored for scoring)
- **Steady-state window** (used for averages/integrals)

This is important because software systems often have ramps and stabilization periods.

Practical rule for interns:
- If your plot has a step change (e.g., “start load”), the next ~30–120 seconds is usually **not** steady.
- Only compute averages/energy inside windows where the signal is roughly flat.

Recommended default (already used in our repo):
- warm-up: 2 minutes
- steady-state: 5 minutes

## Sampling, polling, and why cadence matters
Power is sampled over time. Two common cases:

1) **Hardware meters / PDUs**: sample/poll at a fixed cadence (often coarse, e.g. 1–10s).
2) **Software estimators**: can be frequent, but may represent a model (CPU-only, container-only, etc.).

Why cadence matters:
- If you sample every 10s, you cannot truthfully claim what happens on 1s timescales.
- Coarse cadence pushes you toward **steady-state comparisons**, not transients.

During probation we are software-only, but we keep the same discipline: we still avoid “fast transient” claims.

## AC vs DC terms (only relevant once hardware exists)

If you’re brand new: AC/DC vocabulary is mostly about **where** and **how** power is measured.
- Measuring at **AC input** includes power supply losses.
- Measuring at **DC rails** excludes AC/DC conversion losses.
- **PoE** measurements depend on where you measure (injector/PSE vs inline analyzer).

### Real power $P$ (W)
- What you pay for (in energy billing terms).
- This is the value you ultimately want for RU wall power once hardware is available.

### Apparent power $S$ (VA)
- Often shown by meters as **volt-amps (VA)**.
- Apparent power exists because AC systems can have current that is not perfectly in-phase with voltage (and/or non-sinusoidal current draw).

### Power factor (PF)

$$
PF = \frac{P\,(W)}{S\,(VA)}
$$

- PF matters for AC systems because a load can draw current without converting all of it to real power.
- For our project: PF is “good to record” once AC measurement is available, but it is **not required** for software-only probation.

One-liner intuition:
- PF close to 1.0 means VA ≈ W.
- PF far from 1.0 means the meter may show much higher VA than W.

## Efficiency metrics (only if traffic accounting is clean)
Efficiency metrics are easy to define but easy to misuse.
The main pitfall is mixing time windows (e.g., using energy from a 5-minute window but bits from a different window).

### Energy per bit (J/bit)

$$
\text{J/bit} = \frac{E\,(J)}{\text{bits delivered}}
$$

- Lower is better.

Interpretation:
- If $J/bit$ goes down as load increases, that often means your system has a fixed “overhead” that gets amortized at higher throughput.

### Bits per joule (bit/J)

$$
\text{bit/J} = \frac{\text{bits delivered}}{E\,(J)}
$$

- Higher is better.

### Practical note on “bits delivered”
In probation we use `iperf3` as the primary source of transferred bytes for the **steady-state** window.

Minimum discipline:
- Always record the **iperf mode** (TCP/UDP), target rate, and achieved throughput.
- Use the same steady-state window to compute both energy and bits.

## Workload terms (what “RU-like workload” means in software-only)
In probation we don’t have RU hardware access. So “RU-like workload” means:
- a RAN software stack / simulation that produces sustained network and compute load, and
- a controlled traffic generator (`iperf3`) that lets us define low/medium/high load points.

We treat CPU utilization and throughput as “sanity signals” that the system is actually doing work.

## “Idle” vs “Active-idle” (operational definitions)
These are *state-style* definitions that we can apply even in software-only tests:
- **Idle:** stack not running / cell not enabled; no user traffic.
- **Active-idle:** stack running + cell enabled (if applicable) + no user traffic.

The key idea: we want two “no traffic” states that differ in whether the system is actually active.

Why we care:
- Many systems consume a large fraction of their peak power even when doing “no traffic” work.
- The idle→active-idle delta is often where energy-saving features matter.

## Load definition (software-first)
- **Primary load knob:** throughput target (DL Mbps) driven by `iperf3`.
- **Secondary context (if available):** CPU utilization.

We avoid PRB% as a hard requirement in probation because PRB telemetry may not be accessible.

If you can’t get PRB%:
- that’s fine for probation; just record throughput and the exact configuration.
- later, PRB% becomes valuable for explaining *why* two systems with the same throughput consume different power.

## What we can and cannot claim during software-only probation
### We can claim
- A repeatable *method*: definitions, scenario structure, logging, time alignment, and analysis computations.
- “Platform power under RU-like workload” trends (idle vs active-idle vs load).

### We cannot claim
- RU wall power / RU AC input results.
- Fine transient behavior unless sampling is sufficiently fast and validated.

## Worked example (numbers)
Assume:
- Steady-state window = 5 minutes (300s)
- Mean power over that window = 120 W
- `iperf3` reports 300 Mbits delivered in that same window

Energy:

$$
E = 120\,W \times 300\,s = 36{,}000\,J = 10\,Wh
$$

Energy per bit:

$$
J/bit = \frac{36{,}000}{300 \times 10^6} = 1.2 \times 10^{-4}\,J/bit
$$

This is the kind of computation we want to be able to reproduce reliably.

## Minimum outputs we should be able to produce from any run
- A **power vs time** plot with scenario boundaries marked.
- A small table of:
  - mean power (W) over the steady-state window
  - energy (Wh or J) over the steady-state window
  - achieved throughput over the steady-state window

## Related notes
- Boundaries: `docs/StudyNotes/2026-01-13_Boundaries.md`
- Analysis plan: `docs/StudyNotes/2026-01-14_Analysis-Plan.md`
- Risks: `docs/StudyNotes/2026-01-14_Risks-and-Questions.md`

## Suggested Day-3 learning path (if you feel lost)
1) Read “Mental model” + “Core quantities” until you can explain power vs energy in one sentence.
2) Read “Windowing” + “Sampling cadence” to understand why we avoid transient claims.
3) Read “Efficiency metrics” + “Worked example” and recompute the numbers yourself.
4) Jump to `2026-01-14_Analysis-Plan.md` and verify you understand each plot/table and how it’s computed.

## Practical next step (software-only)
If power estimation is not set up yet, start here:
- `docs/StudyNotes/2026-01-14_Power-Estimator-Setup-Scaphandre.md`
