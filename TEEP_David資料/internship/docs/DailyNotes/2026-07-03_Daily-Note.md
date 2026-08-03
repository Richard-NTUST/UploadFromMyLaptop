# Daily Note

## Date

**Date:** 2026/07/03

---

## Short-term Goal

Prepare and, if lab state allows, test the OCloud version of the WINLAB E2E workflow with parameterized traffic controls.

### Goal 1: Validate OCloud parameterized run path

* Milestone 1: Confirm `oai-vnf` and `oai-pnf` pod readiness in `ming-ns`, Due 2026/07/03
* Milestone 2: Apply or verify the parameterized `cloud_e2e.py` path, Due 2026/07/03
* Milestone 3: Trigger OCloud through the unified `/gnb/run` API using `bandwidth`, `period`, and `gap_time`, Due 2026/07/03

### Goal 2: Preserve evidence quality for later baseline use

* Milestone 1: Save job response, UTC markers, pod state, and iPerf output if a run executes, Due 2026/07/03
* Milestone 2: Mark the run as smoke/parity evidence, not final power baseline evidence, unless O-RU power mapping is confirmed, Due 2026/07/03

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Check OCloud pod readiness | OCloud gNB mode | `oai-vnf` and `oai-pnf` status from `ming-ns` | | `kubectl get pods -n ming-ns -o wide` output |
| P2 | Back up and apply/verify parameterized `cloud_e2e.py` | OCloud / Bare Metal parity | `python3 -m py_compile cloud_e2e.py` and `--help` output | | HPE terminal output |
| P3 | Start the HPE rApp locally | Unified E2E trigger | rApp listening on `127.0.0.1:9090` | | `uvicorn` output |
| P4 | Trigger OCloud run with parameters | OCloud parameterized smoke test | API response for `mode:"ocloud"` using selected traffic settings | | Job response / job ID |
| P5 | Save evidence and classify result | Baseline evidence quality | Clearly labeled smoke/parity evidence bundle | | iPerf output, UTC markers, pod state, run note |

Before starting work:

* [x] Confirm this is an OCloud smoke/parity test, not final power baseline.
* [x] Confirm power mapping is still required before final throughput-power claims.
* [x] Capture exact commands and timestamps if the lab run proceeds.

---

## Planned Commands

Check pods:

```bash
kubectl get pods -n ming-ns -o wide
```

Compile and inspect the patched OCloud script:

```bash
cd /home/hpe/CRAN/ocloud-helm-templates
cp cloud_e2e.py cloud_e2e.py.bak_20260703
cp /path/to/cloud_e2e_full_iperf.py cloud_e2e.py
python3 -m py_compile cloud_e2e.py
python3 cloud_e2e.py --help
```

Start the rApp on HPE:

```bash
export WINLAB_E2E_EXEC_MODE=local
uvicorn winlab_e2e_rapp.app:app --host 127.0.0.1 --port 9090
```

Trigger OCloud through the unified API:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"ocloud","bandwidth":[100],"period":60,"gap_time":2,"ue_model":"samsung","dry_run":false}'
```

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Check OCloud pod readiness | Planned / pending evidence | | |
| Apply or verify parameterized `cloud_e2e.py` | Planned / pending evidence | | |
| Trigger OCloud run through `/gnb/run` | Planned / pending evidence | | |
| Save smoke/parity evidence | Planned / pending evidence | | |

### Progress Summary

The working direction for today is to test the OCloud version with parameterized traffic controls. The expected configuration is:

```text
mode: ocloud
bandwidth: [100]
period: 60
gap_time: 2
ue_model: samsung
dry_run: false
```

This should be treated as OCloud smoke/parity validation. It should not be used as final throughput-power baseline evidence unless the Pegatron O-RU power source and timestamped `active_power` export are confirmed.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| OCloud pod readiness | `cloud_e2e.py` depends on ready `oai-vnf` and `oai-pnf` pods | Confirm pods in `ming-ns` before live run |
| OCloud iPerf parity | OCloud needs the same traffic knobs as Bare Metal | Verify the parameterized `cloud_e2e.py` patch |
| Pegatron O-RU power mapping | Required before final baseline evidence | Confirm PDU outlet and export path with CortexDC / InfluxDB team |

### Today's Biggest Lesson

```text
The OCloud test should be handled as a parity check first: prove that the same traffic
parameters can be passed through the OCloud path, then decide whether the evidence is
strong enough for baseline use after power mapping is confirmed.
```

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Fill in actual OCloud run result | July 3 OCloud test | Job ID, pod state, iPerf output, and run classification |
| P2 | Update smoke-test run sheet if OCloud command changes | E2E runbook quality | Current command sequence and observed failure/success mode |
| P3 | Continue Pegatron O-RU power mapping follow-up | Power-baseline blocker | Confirmed outlet/export/timestamp basis |
