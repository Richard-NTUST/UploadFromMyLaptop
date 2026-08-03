---
title: Pegatron O-RU PDU Outlet Clarification - Ravi and Chynna Context
date: 2026-07-06
---

# Pegatron O-RU PDU Outlet Clarification - Ravi and Chynna Context

**Date:** 2026-07-06  
**Purpose:** Replace the earlier tentative CortexDC power-mapping note with the confirmed PDU outlet schedule from Ravi and the CortexDC/InfluxDB limitations from Chynna's files.

---

## 1. Corrected Status

Do not treat the earlier Outlet 2 assumption as final experiment evidence.

Ravi confirmed the outlet schedule labels, but also clarified that:

```text
CortexDC can't show RU data yet.
```

So the current state is:

```text
PDU physical/schedule mapping: partly known
CortexDC RU asset mapping: not available yet
InfluxDB outlet metrics: likely available as outlet1-outlet12, but mapping must be verified
Final experiment power source: still must be confirmed before baseline plotting
```

---

## 2. Ravi's Confirmed Outlet Schedule

Ravi confirmed that these schedule entries are correct:

| Outlet | Schedule Label | Meaning / Current Interpretation | Use As Final RU Power Source? |
|---|---|---|---|
| Outlet 1 | Pegatron RU [N], OC/DU testing | Physical Pegatron RU for OC/DU testing path | Not unless the experiment uses RU [N] |
| Outlet 2 | Pegatron RU [O], OCloud testing | Physical Pegatron RU for OCloud testing path | Candidate if the current OCloud/nFAPI run uses RU [O] |
| Outlet 11 | Lavoisier, [O-Cloud] OAI NFAPI (PNF), OAI Split 7.2 gNB + Commercial RU | Lavoisier server / O-Cloud NFAPI PNF path with commercial RU context | Likely server-side power, not standalone RU power |

Important distinction:

```text
Outlet 2 sounds like the OCloud Pegatron RU outlet.
Outlet 11 is mapped to Lavoisier in Chynna's workbook and should not automatically be treated as RU-only power.
```

Ravi also asked whether we use the new Pegatron RU:

```text
Do you use New Pegatron RU? -> Pegatron RU 1450
Check if Pegatron RU supports Redfish.
```

This means the next decision depends on which physical RU the current nFAPI/OCloud E2E test is actually using.

---

## 3. What Chynna's Files Confirm

Relevant files checked:

```text
CortexConversation.md  (currently deleted in working tree, read from git)
CortexDC_Data_Inventory_Workbook.xlsx
docs/MeetingNotes/2026-07-01_CortexDC-Pegatron-ORU-Power-Mapping.md
```

### 3.1 CortexConversation.md

The conversation says:

- CortexDC currently manages 13 servers, 1 PDU, and 1 network device.
- CortexDC Assets currently have no RU entries.
- The active PDU is `Raritan PX4-5256CR-C8E8A0`.
- The official PDU has 12 outlets.
- CortexDC only shows complete outlet mapping for 8 server outlets.
- InfluxDB can show `outlet1` through `outlet12`, but the naming is not consistently mapped to the correct server/device.
- The team was asked to physically verify mapping with senior students / Peter if needed.

Key practical quote, paraphrased:

```text
CortexDC can show PDU information only for 8 mapped servers.
InfluxDB shows outlet1-outlet12, but the names do not reliably identify the correct server/device.
```

### 3.2 CortexDC Data Inventory Workbook

The workbook is mostly a server inventory, not an RU inventory. It confirms server-side mappings such as:

| Server | PDU Outlet | Notes |
|---|---|---|
| Joule | Outlet 12 | Server-side power mapping |
| Kepler | Outlet 6 | Server-side power mapping |
| Lavoisier | Outlet 11 | Server-side power mapping |
| Quine | Outlet 5 | Server-side power mapping |
| Newton | Outlet 9 | Server-side power mapping |
| Archmedies | Outlet 8 | Server-side power mapping |
| Inoue | Outlet 10 | Server-side power mapping |

It also defines `PDU active_power` as outlet power measured by the PDU and says to check InfluxDB or the PDU dashboard for that field.

### 3.3 July 1 Meeting Note

The July 1 meeting note still treated the Pegatron O-RU outlet as pending:

```text
Confirm Pegatron O-RU PDU outlet: Pending
Confirm CortexDC or InfluxDB export method: Pending
Confirm timestamp basis: Pending
```

Ravi's July 6 clarification advances the outlet schedule, but it does not remove the export/mapping blocker because CortexDC still cannot show RU data directly.

---

## 4. Redfish Clarification

Ravi suggested checking whether the new Pegatron RU 1450 supports Redfish.

Why this matters:

| If Pegatron RU 1450 supports Redfish | If it does not support Redfish |
|---|---|
| CortexDC may eventually ingest RU telemetry directly if credentials/API integration are added | RU power must be measured indirectly through PDU/InfluxDB outlet power |

Working assumption until verified:

```text
Do not assume Pegatron RU Redfish support.
Treat PDU outlet active_power as the practical measurement path for near-term throughput-vs-power experiments.
```

Also note: typical O-RUs are more likely to expose management through O-RAN M-plane mechanisms such as NETCONF/YANG than server-style Redfish, but vendor hardware must be checked directly.

---

## 5. Current Decision Tree

Before using a power trace, answer this:

```text
Which physical RU is active in the current nFAPI/OCloud E2E run?
```

Then select the power source:

| Experiment Setup | Candidate Power Source | Confidence | Required Verification |
|---|---|---|---|
| Uses Pegatron RU [O] / OCloud testing RU | Outlet 2 `active_power` | Medium | Confirm actual RU in run and InfluxDB outlet2 export |
| Uses Pegatron RU [N] / OC-DU testing RU | Outlet 1 `active_power` | Medium | Confirm actual RU in run and InfluxDB outlet1 export |
| Uses Lavoisier-side OAI NFAPI PNF server path | Outlet 11 for Lavoisier server power | High for server power, low for RU-only power | Do not label as RU-only unless physical wiring proves it |
| Uses new Pegatron RU 1450 | Unknown until hardware mapping is checked | Unknown | Confirm outlet and Redfish/M-plane/PDU path |

---

## 6. What Not To Do

Do not make these claims yet:

```text
Outlet 2 is definitely the current experiment's RU power source.
Outlet 11 is RU power.
CortexDC can export Pegatron RU power directly.
Redfish is available on Pegatron RU 1450.
```

Acceptable current wording:

```text
Ravi confirmed the schedule labels for outlets 1, 2, and 11.
CortexDC cannot show RU data yet.
For the OCloud Pegatron RU path, Outlet 2 is the likely candidate, but the active RU and InfluxDB export must be verified before final baseline plotting.
```

---

## 7. Immediate Next Checks

1. Confirm which physical RU is active in the current OAI nFAPI / OCloud E2E test.

```text
Pegatron RU [N]?
Pegatron RU [O]?
New Pegatron RU 1450?
Commercial RU connected through Lavoisier path?
```

2. Confirm whether InfluxDB has outlet-level active power for the candidate outlet.

```text
outlet1 active_power
outlet2 active_power
outlet11 active_power
```

3. Confirm timestamp basis.

```text
Taiwan local time?
UTC?
InfluxDB server time?
```

4. Export a short known window and compare against a controlled event.

Example validation:

```text
Turn on / start RU or start test window.
Record start/end time.
Export candidate outlet active_power.
Check whether the trace changes plausibly.
```

---

## 8. Updated Baseline Rule

The throughput-vs-power baseline should not be considered valid until this tuple is known:

```text
run_id
active RU identity
PDU name
PDU outlet number
InfluxDB/CortexDC measurement name
power field, e.g. active_power
timestamp basis
sampling interval
iperf/rApp start time
iperf/rApp end time
```

For now, the most likely path is:

```text
Use InfluxDB/PDU outlet active_power, not CortexDC RU asset telemetry.
```
