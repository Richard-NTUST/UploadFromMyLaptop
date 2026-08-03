# Daily Note

## Date

**Date:** 2026/07/17

---

## Short-term Goal

Recover the OCloud E2E test path, run a successful Dockerized rApp test, export matching Outlet 2 active-power data, and validate the throughput-power merge script.

### Goal 1: Restore OCloud E2E test execution

* Milestone 1: Recover VNF/PNF pod readiness, Due 2026/07/17
* Milestone 2: Run a 100 Mbps OCloud smoke test through Dockerized rApp, Due 2026/07/17

### Goal 2: Validate power-data merge

* Milestone 1: Export Outlet 2 `active_power` from InfluxDB for the run window, Due 2026/07/17
* Milestone 2: Run `merge_winlab_e2e_power.py`, Due 2026/07/17
* Milestone 3: Preserve merged summary CSV, Due 2026/07/17

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Stabilize OCloud pods | Goal 1 | VNF/PNF Running and Ready | | HPE pod status |
| P2 | Run Dockerized rApp E2E test | Goal 1 | Successful job through `127.0.0.1:19090` | | Job `ce4d30b0-abb6-409e-96b0-74a55c1c7c79` |
| P3 | Export Outlet 2 power CSV | Goal 2 | PDU active-power CSV | | `pdu_data_20260717_083250_083840.csv` |
| P4 | Validate merge script | Goal 2 | Throughput-power summary CSV | | `power_throughput_summary_20260717_083449.csv` |
| P5 | Write study note and daily log | Reporting | Notes and old daily log entry | | This file and `Daily-Logs.md` |

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Stabilize OCloud pods | Complete | | PNF/VNF restored for the successful test |
| Run Dockerized rApp E2E test | Complete | | Job `ce4d30b0-abb6-409e-96b0-74a55c1c7c79` succeeded |
| Export Outlet 2 power CSV | Complete | | `pdu_data_20260717_083250_083840.csv` |
| Validate merge script | Complete | | `power_throughput_summary_20260717_083449.csv` |
| Write study note and daily log | Complete | | `docs/StudyNotes/2026-07-17_WINLAB_E2E_Power_Merge_Validation.md` |

### Progress Summary

The Dockerized rApp successfully triggered an OCloud 100 Mbps downlink test:

```text
Job: ce4d30b0-abb6-409e-96b0-74a55c1c7c79
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260717-083449
UE IP: 10.45.0.3
Result: 100 Mbps, 60 s, 0% packet loss
```

The matching InfluxDB/CortexDC PDU export used Outlet 2 `active_power`:

```text
pdu_data_20260717_083250_083840.csv
```

The merge script was patched to handle InfluxDB nanosecond timestamps and validated against the run artifact.

Final merged output:

```text
power_throughput_summary_20260717_083449.csv
```

The merged row shows:

```text
100 Mbps offered load -> 99.996 Mbps RX throughput
Average Outlet 2 active power: 40.04 W
PDU samples inside iPerf window: 1
```

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Improve power confidence | 60 s run only captured one PDU sample | Use longer periods or repeated runs |
| Automate InfluxDB export | Current export is manual | Add token-safe API integration later |
| Test multi-load merge | Current validated row is one offered-load point | Run longer 100/200/300 Mbps sweep when lab is free |

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Run longer OCloud test windows | Power-confidence improvement | Multiple PDU samples per load |
| P2 | Validate merge script on multi-load sweep | Analysis pipeline | Multi-row throughput-power CSV |
| P3 | Decide token-safe Influx export design | Automation | Manual export replaced or documented |
