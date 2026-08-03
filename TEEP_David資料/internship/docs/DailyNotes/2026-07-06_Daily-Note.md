# Daily Note

## Date

**Date:** 2026/07/06

---

## Short-term Goal

Advance the WINLAB Pegatron O-RU baseline from unclear ownership into a runnable OCloud E2E smoke path with a known RU power candidate.

### Goal 1: Resolve the active RU path and power-source candidate

* Milestone 1: Confirm which RU path Ming's E2E tests use, Due 2026/07/06
* Milestone 2: Map the active RU path to the PDU outlet schedule, Due 2026/07/06
* Milestone 3: Separate wiring ownership from CortexDC/InfluxDB export ownership, Due 2026/07/06

### Goal 2: Verify OCloud E2E execution with controlled traffic parameters

* Milestone 1: Verify `cloud_e2e.py` supports parameterized iPerf controls, Due 2026/07/06
* Milestone 2: Confirm OCloud VNF/PNF pods can become Running and Ready, Due 2026/07/06
* Milestone 3: Run one OCloud 100 Mbps smoke test and capture the job result, Due 2026/07/06

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Reconcile Ming, Ravi, and Chynna responsibilities | Active RU path and power-source candidate | Clear ownership split for E2E, wiring, and data export | | This daily note and power-mapping study note |
| P2 | Confirm active E2E path | Ming E2E workflow | Current E2E tests identified as Pegatron RU [O] path | | Ming confirmation recorded in context |
| P3 | Map Pegatron RU [O] to PDU outlet | Ravi PDU schedule | Outlet 2 treated as the RU power candidate for Pegatron RU [O] | | PDU outlet schedule image / Ravi schedule |
| P4 | Verify parameterized OCloud script | OCloud / Bare Metal parity | `cloud_e2e.py --help` shows bandwidth, period, gap-time, UE model, and uplink controls | | HPE terminal output |
| P5 | Run OCloud 100 Mbps smoke test | E2E validation | Successful `/gnb/run` job with iPerf result and pod readiness evidence | | Job ID `f75e676a-a8b5-4661-8940-7204052eab3f` |

Before starting work:

* [x] Treat Ravi as wiring/PDU schedule owner, not E2E flow owner.
* [x] Treat Ming as the E2E flow owner.
* [x] Treat Chynna as the remaining CortexDC/InfluxDB export-path owner.
* [x] Do not claim final throughput-vs-power evidence until `outlet2 active_power` export is available.

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Reconcile Ming, Ravi, and Chynna responsibilities | Complete | | Ownership split clarified in this note |
| Confirm active E2E path | Complete | | Ming confirmed both Bare Metal and OCloud use Pegatron RU [O] |
| Map Pegatron RU [O] to PDU outlet | Complete | | PDU schedule maps Pegatron RU [O] / OCloud testing to Outlet 2 |
| Verify parameterized OCloud script | Complete | | `cloud_e2e.py --help` includes `--bandwidth`, `--period`, `--gap-time`, `--ue-model`, `--uplink`, `--settle-time`, and `--attach-timeout` |
| Run OCloud 100 Mbps smoke test | Complete | | Job `f75e676a-a8b5-4661-8940-7204052eab3f` succeeded with return code 0 |

### Progress Summary

Ming confirmed that the current E2E tests use the Pegatron RU [O] path for both Bare Metal and OCloud. This resolves the E2E-side uncertainty.

The PDU outlet schedule maps:

```text
Outlet 1: Pegatron RU [N], OC/DU testing
Outlet 2: Pegatron RU [O], OCloud testing
Outlet 11: Lavoisier, OAI nFAPI PNF / OAI Split 7.2 gNB + Commercial RU
```

Therefore, the current power-source candidate for the Pegatron RU [O] E2E path is:

```text
Outlet 2 active_power
```

This is still not final baseline power evidence because Chynna's export path for timestamped `outlet2 active_power` remains pending.

The OCloud script was confirmed to support parameterized iPerf controls:

```text
--bandwidth
--period
--gap-time
--ue-model
--uplink
--iperf-bind
--settle-time
--attach-timeout
```

After resolving pod readiness, one OCloud run succeeded through the rApp:

```text
Job ID: f75e676a-a8b5-4661-8940-7204052eab3f
Status: succeeded
Return code: 0
Start UTC: 2026-07-06T08:10:27.549611Z
Finish UTC: 2026-07-06T08:12:09.557730Z
Mode: ocloud
RU path: Pegatron RU [O]
UE model: samsung
UE IP: 10.45.0.2
Traffic: downlink iperf3 reverse mode
Target bitrate: 100 Mbps
Duration: 60 s
Gap time: 2 s
```

Observed pod readiness:

```text
PNF: oai-pnf-pegatron-844485c99b-4c6cc Running & Ready
VNF: oai-vnf-696c88996d-zrnmv Running & Ready
```

iPerf result:

```text
Transfer: 716 MBytes
Bitrate: 100 Mbits/sec
Loss: 0/557021 datagrams, 0%
```

Log directory reported by the OCloud script:

```text
logs_e2e_20260706_161204
```

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Export `outlet2 active_power` | Required before final throughput-vs-power baseline | Ask Chynna for CortexDC/InfluxDB/PDU export method and timestamp basis |
| Gather full run artifacts | Needed before plotting or reporting the smoke run | Save job JSON, pod state, Helm state, VNF/PNF logs, and iPerf output |
| Generate first smoke-run plot | Useful for validating the analysis path | Parse the run output and create a simple throughput-over-time or run-summary plot |

### Today's Biggest Lesson

```text
The ownership split matters. Ming answers which E2E path is active, Ravi answers what the
PDU schedule/wiring says, and Chynna remains the owner for how to export timestamped
power data. With Ming's O-path confirmation and Ravi's schedule, Outlet 2 is the right
candidate, but the final baseline still depends on exporting outlet2 active_power.
```

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Gather full OCloud run logs and API artifacts | Evidence quality | Saved job JSON, pod state, Helm state, VNF/PNF logs, and iPerf output for job `f75e676a-a8b5-4661-8940-7204052eab3f` |
| P2 | Generate a first plot from the OCloud smoke-run data | Analysis pipeline | Basic plot or run summary from the 100 Mbps OCloud iPerf result |
| P3 | Follow up with Chynna on `outlet2 active_power` export | Power-baseline blocker | Export method, timestamp basis, sampling interval, and example power CSV/query |
| P4 | Prepare next controlled OCloud/Bare Metal comparison run | Baseline preparation | Repeatable command set for matching traffic windows once power export is available |
