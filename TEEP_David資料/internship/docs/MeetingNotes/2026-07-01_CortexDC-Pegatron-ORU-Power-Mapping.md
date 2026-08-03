# Meeting Notes

## Meeting Information

| Item | Description |
| ---- | ----------- |
| Date | 2026/07/01 |
| Participants | David, Senior students / Ming |
| Topic | CortexDC / PDU mapping and WINLAB HPE E2E rApp workflow |

---

## 1. Review Pending Tasks

| Pending Task | Owner | Status | Remarks |
| ------------ | ----- | ------ | ------- |
| Confirm Pegatron O-RU PDU outlet | David / Chynna / Peter | Pending | Needed before E2E throughput-power baseline can be treated as valid evidence |
| Confirm CortexDC or InfluxDB export method | David / Chynna | Pending | Need timestamped `active_power` export for the O-RU outlet |
| Confirm E2E nFAPI smoke-test access path | David / Ming | Complete for Bare Metal; OCloud in progress | HPE API wrapper now triggers Bare Metal runs; OCloud trigger works but depends on ready pods and `cloud_e2e.py` parity patch |

---

## 2. Discussion Topics

| Topic | Reference |
| ----- | --------- |
| Which PDU outlet powers the Pegatron O-RU? | CortexDC workbook and Raritan PDU outlet mapping |
| Is the Pegatron O-RU represented in CortexDC, InfluxDB, or only physically on the PDU? | CortexDC conversation and `Server.png` topology |
| Can CortexDC or InfluxDB export timestamped `active_power` for that outlet? | Required for throughput-power alignment |
| How do CortexDC outlet labels map to InfluxDB `outlet1` through `outlet12`? | Needed because current CortexDC labels may not cover all physical outlets |
| Can Bare Metal and OCloud gNB execution share one API? | Implemented as `POST /gnb/run` with `mode: "baremetal"` or `mode: "ocloud"` |
| Can OCloud use the same full iPerf path as Bare Metal? | `cloud_e2e.py` already imports `ue_driver`, but currently hard-codes a 500 Mbps / 10 s lite flow |

---

## 3. Decisions / Outcomes

| Topic | Outcome | Evidence / Notes |
| ----- | ------- | ---------------- |
| rApp location | Created local rApp package under `rapps/winlab_e2e_rapp/` | Wraps HPE-side scripts without storing credentials |
| HPE server | Confirmed HPE server path through WireGuard and SSH | Host: `hpe-ProLiant-DL380-Gen10`; API tested locally on HPE |
| API shape | gNB control should use one endpoint instead of separate Bare Metal and OCloud endpoints | `POST /gnb/run` |
| Bare Metal mode | Uses Ming's direct nFAPI E2E flow through `exp_bandwidth.py` / `e2e_core.py` | Live API run succeeded and collected logs |
| OCloud mode | Uses `cloud_e2e.py` and requires `oai-vnf` / `oai-pnf` pods to be Running and Ready in `ming-ns` | If pods are missing, script exits with pod readiness error |
| Old API aliases | Removed old compatibility endpoints | Removed `POST /cloud/smoke` and `POST /experiments/bandwidth` |
| HPE port binding | Run uvicorn on `127.0.0.1:9090`, not `0.0.0.0:9090` | Open5GS already listens on port `9090` on other loopback IPs; do not kill those processes |
| Bare Metal UE behavior | Samsung UE can be brought online through the API and receives `10.45.0.2` | Live run showed UE online and iPerf execution |
| Bare Metal evidence | Workflow validation run created a log bundle | `/home/hpe/ming-logs/Exp_Bandwidth/0701-1628-100x` |
| OCloud iPerf parity | Need to replace hard-coded lite iPerf in `cloud_e2e.py` with parameterized full `ue_driver.py` path | Prepared `cloud_e2e_full_iperf.py` replacement script |

---

## 4. New Action Items

| Task | Owner | Measurable Deliverable | Due Date | Evidence |
| ---- | ----- | ---------------------- | -------- | -------- |
| Confirm Pegatron O-RU power outlet | David / Chynna / Peter | PDU name, outlet number, and whether the mapping is physical, CortexDC, or InfluxDB-based | Next lab sync | |
| Confirm export method | David / Chynna | Export method for timestamped `active_power`: CSV, Excel, screenshot, API, or InfluxDB query | Next lab sync | |
| Confirm timestamp basis | David / Chynna | Timezone/UTC basis and sampling interval for power data | Next lab sync | |
| Apply OCloud full-iPerf patch | David / Ming | Back up `cloud_e2e.py`, apply parameterized version, run `python3 -m py_compile`, verify `--help` | Next HPE session | `rapps/winlab_e2e_rapp/patches/cloud_e2e_full_iperf.py` |
| Validate OCloud mode | David / Ming | `POST /gnb/run` with `mode:"ocloud"` succeeds with parameterized `bandwidth`, `period`, and `gap_time` | After pod readiness is confirmed | HPE job ID and output |
| Confirm OCloud pod deployment/readiness procedure | Ming | Command sequence for creating/checking `oai-vnf` and `oai-pnf` pods in `ming-ns` | Before OCloud baseline run | `kubectl get pods -n ming-ns -o wide` |
| Update E2E smoke-test run sheet | David | Run sheet updated with `/gnb/run`, Bare Metal/OCloud modes, HPE binding rule, and power-source blocker status | Next documentation pass | Smoke-test run sheet |

---

## 5. Commands / Operational Notes

Run the rApp on HPE:

```bash
export WINLAB_E2E_EXEC_MODE=local
uvicorn winlab_e2e_rapp.app:app --host 127.0.0.1 --port 9090
```

Bare Metal gNB run:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"baremetal","server":"hpe","bandwidth":[100],"period":60,"gap_time":2,"ping":true,"uplink":false,"ue_model":"samsung"}'
```

OCloud dry run:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"ocloud","bandwidth":[100],"period":60,"gap_time":2,"ue_model":"samsung","dry_run":true}'
```

OCloud pod readiness check:

```bash
kubectl get pods -n ming-ns -o wide
```

Do not kill Open5GS processes listening on loopback port `9090`; they are part of the core network path.

---

## Final Message

Today's work produced a repeatable API path for the WINLAB E2E workflow. Bare Metal mode is runnable through the rApp and can produce log bundles. OCloud mode is reachable through the same API, but final parity requires applying the `cloud_e2e.py` full-iPerf patch and confirming pod readiness.

The remaining baseline blocker is still power evidence: no throughput-power result should be treated as final Pegatron O-RU baseline evidence until the PDU outlet and timestamped CortexDC/InfluxDB export path are confirmed.
