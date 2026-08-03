# O-RAN Principles — Part 2: RIC, Interfaces, and Work Groups (2026-01-16)

Status: Complete
Deadline: 2026-01-16

This note continues Part 1 (architecture fundamentals) and focuses on the control/management layers and the interfaces that matter when we talk about telemetry, policies, and closed-loop optimization.

Part 1 is in:
- `docs/StudyNotes/2026-01-16_O-RAN Principles.md`

## Table of contents
- [RIC overview (Non-RT vs Near-RT)](#ric-overview-non-rt-vs-near-rt)
- [Key interfaces (A1, E2, O1, O2, Open FH, F1/E1)](#key-interfaces-a1-e2-o1-o2-open-fh-f1e1)
- [O-RAN work groups (WG1–WG10)](#o-ran-work-groups-wg1wg10)
- [Why this matters for the RU power project](#why-this-matters-for-the-ru-power-project)

## RIC overview (Non-RT vs Near-RT)
O-RAN introduces controller layers (RICs) to support optimization/control loops at different time scales.

- **Non-RT RIC** (Non Real-Time)
  - Control loop: typically ≥ 1 second
  - Runs inside/alongside SMO
  - Hosts **rApps** (longer-horizon optimization, policies, analytics, ML lifecycle)

- **Near-RT RIC** (Near Real-Time)
  - Control loop: ≥ 10 ms and < 1 second
  - Hosts **xApps** (time-sensitive optimization/control)
  - Talks to E2 nodes (e.g., CU/DU functions) via E2

## Key interfaces (A1, E2, O1, O2, Open FH, F1/E1)
A minimal “mental map” for interfaces:

- **A1**: Non-RT RIC → Near-RT RIC
  - Policies and enrichment info that guide near-real-time behavior

- **E2**: Near-RT RIC ↔ E2 Nodes
  - The near-real-time control/data interface to RAN functions (typically CU/DU level)

- **O1**: SMO ↔ managed network functions
  - Operations/administration/management plane

- **O2**: SMO ↔ O-Cloud
  - Orchestration/management for cloud infrastructure hosting RAN functions

- **Open Fronthaul (FH)**: O-DU ↔ O-RU
  - Transport for split functions (commonly referenced: option 7.2x family)

- **F1**: O-CU ↔ O-DU
  - 3GPP-defined split interface used in 5G deployments

- **E1**: CU-CP ↔ CU-UP
  - Control/user plane coordination in split CU

## O-RAN work groups (WG1–WG10)
Common high-level grouping (memorization aid):

- WG1: Use cases + overall architecture
- WG2: Non-RT RIC + A1
- WG3: Near-RT RIC + E2
- WG4: Open Fronthaul
- WG5: Open CU interfaces (F1/E1/etc) alignment
- WG6: Cloudification + orchestration
- WG7: White-box hardware
- WG8: Stack reference design (O-CU/O-DU software stack guidance)
- WG9: Open transport (x-haul)
- WG10: OAM + O1

## Why this matters for the RU power project
- If we later ingest RU/DU/CU KPIs (PRB utilization, throughput, etc.), the “source” and timing will often be tied to these interfaces and management layers.
- For probation, we keep it simple: **iperf throughput + timestamps** are enough to validate our measurement pipeline, but we now have the vocabulary to map future KPIs to the right layer.
- When writing results, keep the separation clear:
  - **Measurement point** (RU AC input vs platform estimator)
  - **Workload definition** (throughput/PRB/utilization)
  - **Control/telemetry plane** (O1/O2/E2/A1 where applicable)
