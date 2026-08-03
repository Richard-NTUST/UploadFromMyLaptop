# Daily Note

## Date

**Date:** 2026/07/07

---

## Short-term Goal

Turn the WINLAB Pegatron O-RU E2E smoke flow into a repeatable evidence-producing run: one endpoint trigger should execute the test, collect logs, generate throughput CSV/plot artifacts, and leave only the PDU power export as the remaining blocker for throughput-vs-power analysis.

### Goal 1: Integrate E2E artifact generation into the rApp endpoint

* Milestone 1: Route Bare Metal E2E runs through a wrapper that preserves Ming log/plot behavior, Due 2026/07/07
* Milestone 2: Route OCloud E2E runs through the same wrapper and add missing artifact capture, Due 2026/07/07
* Milestone 3: Verify `/gnb/run` creates a single artifact directory with logs, CSV, plot, and metadata, Due 2026/07/07

### Goal 2: Confirm the power-data path for the Pegatron RU [O] experiment

* Milestone 1: Confirm Outlet 2 active_power exists in InfluxDB, Due 2026/07/07
* Milestone 2: Identify that export permission is blocked for Chynna's account, Due 2026/07/07
* Milestone 3: Prepare Ravi follow-up for read/export permission or an existing export method, Due 2026/07/07

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Inspect rApp endpoint and Ming log/plot scripts | rApp artifact integration | Clear map of current `/gnb/run`, Bare Metal, OCloud, log, and plot code paths | | HPE source inspection |
| P2 | Integrate artifact wrapper into both E2E modes | Endpoint parity | Bare Metal and OCloud endpoint calls both create evidence directories | | Updated HPE rApp scripts |
| P3 | Validate OCloud endpoint run after integration | E2E evidence | Successful OCloud run with UE attach, iPerf, pod logs, CSV, and plot | | Job `16d9967f-1bb5-4305-aadd-ccb15bc7d6de` |
| P4 | Confirm Outlet 2 active_power availability | Power data blocker | Proof that Outlet 2 active_power exists in InfluxDB | | Chynna screenshot |
| P5 | Define remaining permission request | Power export path | Short Ravi message asking for read/export method for Outlet 2 active_power | | Message draft |

Before starting work:

* [x] Treat Ming as E2E flow owner.
* [x] Treat Ravi as PDU wiring/export-permission escalation owner.
* [x] Treat Chynna's screenshot as availability proof, not final data.
* [x] Do not claim final throughput-vs-power results until timestamped Outlet 2 power data is exported.

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Inspect rApp endpoint and Ming log/plot scripts | Complete | | `/home/hpe/winlab_e2e_rapp`, `/home/hpe/ming-logs`, and OCloud `cloud_e2e.py` inspected |
| Integrate artifact wrapper into both E2E modes | Complete | | `/gnb/run` now calls `run_e2e_with_artifacts.py` for Bare Metal and OCloud |
| Validate OCloud endpoint run after integration | Complete | | Job `16d9967f-1bb5-4305-aadd-ccb15bc7d6de` succeeded |
| Confirm Outlet 2 active_power availability | Complete | | Chynna found Outlet 2 active_power in InfluxDB and shared a screenshot |
| Define remaining permission request | Complete | | Ravi should be asked for read/export access or an existing export path |

### Progress Summary

The rApp endpoint was updated so `/gnb/run` no longer only launches the E2E test. It now launches an artifact wrapper that records the command, request, stdout, summary metadata, logs, throughput CSV, throughput-over-time plot, and offered-load throughput plot.

The wrapper path on the HPE server is:

```text
/home/hpe/winlab_e2e_rapp/scripts/run_e2e_with_artifacts.py
```

The endpoint now routes both modes through that wrapper:

```text
mode=baremetal
mode=ocloud
```

For OCloud, the wrapper fills the previous evidence gap by pulling UE-side iPerf output, parsing it into a time series, generating a plot, and copying VNF/PNF pod logs into the artifact directory.

The clean successful OCloud validation run was:

```text
Job ID: 16d9967f-1bb5-4305-aadd-ccb15bc7d6de
Status: succeeded
Return code: 0
Mode: ocloud
RU path: Pegatron RU [O]
UE model: samsung
UE IP: 10.45.0.4
Traffic: downlink iperf3 reverse mode
Target bitrate: 100 Mbps
Duration: 150 s
Gap time: 2 s
Started UTC: 2026-07-07T07:16:38Z
Finished UTC: 2026-07-07T07:20:00Z
Taiwan time window: 2026-07-07 15:16:38 to 15:20:00 GMT+8
```

Observed pod readiness:

```text
PNF: oai-pnf-pegatron-844485c99b-dzfgl Running & Ready
VNF: oai-vnf-696c88996d-246rk Running & Ready
```

iPerf result:

```text
Transfer: 1.75 GBytes
Bitrate: 100 Mbits/sec
Loss: 0/1391683 datagrams, 0%
```

Artifact directory:

```text
/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260707-071638
```

Important artifact files:

```text
command.json
command.txt
e2e_stdout.log
iperf-UE-RX.log
iperf_timeseries.csv
iperf_throughput.png
offered_load_throughput.csv
offered_load_throughput.png
ocloud_pod_logs/
request.json
summary.json
```

Local workspace copies were also saved for the current throughput result:

```text
iperf_timeseries.csv
iperf_throughput.png
```

The throughput CSV is the cleaned data used for plotting. It has the core columns:

```text
start_s,end_s,mbps
```

The rApp was also generalized so `/gnb/run` can accept per-run identity parameters while keeping the current HPE defaults:

```text
server
target_identity
ue_serial
iapc_host
iapc_port
```

Power-side progress: Chynna found `Outlet 2 active_power` in InfluxDB. This confirms the expected RU power source is visible in the database. However, her account cannot export or save query results, so screenshots are only temporary evidence.

The final throughput-vs-power plot still requires timestamped rows for:

```text
measurement: pdu_outlet
sensor_name: Outlet 2
field: active_power
time window: 2026-07-07 15:16:38 to 15:20:00 GMT+8
```

Because Chynna's export permission is restricted, Ravi is the better next escalation target for either read-only InfluxDB access, an export permission change, or an existing CSV/API/dashboard export path.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Export Outlet 2 active_power | Required for final throughput-vs-power alignment | Ask Ravi for read-only InfluxDB/export access or the existing export method |
| Match throughput and power windows | Requires both iPerf CSV and timestamped power CSV | Join `iperf_timeseries.csv` with Outlet 2 active_power over the same GMT+8/UTC window |
| Validate Bare Metal artifact path | OCloud path is validated; Bare Metal should still be tested end-to-end | Run one Bare Metal `/gnb/run` after the environment is stable |

### Today's Biggest Lesson

```text
The endpoint can now produce repeatable E2E evidence in one run. The remaining
research blocker is no longer E2E execution or throughput plotting; it is access to
timestamped Outlet 2 active_power export from InfluxDB.
```

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Ask Ravi for Outlet 2 active_power read/export access | Power export blocker | Read-only InfluxDB access, export permission, or a confirmed existing export method |
| P2 | Export the exact power window for the successful OCloud run | Throughput-vs-power baseline | CSV/table with timestamp and active_power for 2026-07-07 15:16:38 to 15:20:00 GMT+8 |
| P3 | Generate first throughput-vs-power plot | Baseline analysis | Plot combining `iperf_timeseries.csv` and Outlet 2 active_power |
| P4 | Run Bare Metal endpoint validation | Bare Metal/OCloud parity | Bare Metal artifact directory with logs, CSV, plot, and summary |
