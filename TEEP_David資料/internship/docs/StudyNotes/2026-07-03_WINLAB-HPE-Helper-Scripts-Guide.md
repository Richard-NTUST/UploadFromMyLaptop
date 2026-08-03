# WINLAB HPE Helper Scripts Guide

Date: 2026-07-03

Purpose: document the helper scripts deployed to HPE for safe WINLAB Bare Metal / OCloud E2E evidence collection.

These helpers are designed to support the throughput-vs-power workflow without changing lab state unless `--live` is explicitly passed.

---

## 1. Location

Local repo:

```text
scripts/
```

HPE deployment path:

```text
/home/hpe/winlab_e2e_rapp/scripts/
```

Run from:

```bash
cd /home/hpe/winlab_e2e_rapp
```

---

## 2. Script Inventory

| Script | Purpose | Safe by Default |
| ------ | ------- | --------------- |
| `collect_winlab_status_snapshot.py` | Read-only status snapshot: rApp health/config/jobs, Helm releases, pods, deployments, NADs, AMF log tail | Yes |
| `run_winlab_ocloud_power_probe.py` | Marked rApp `/gnb/run` probe with UTC/Taipei markers and optional Influx outlet export | Yes if `--dry-run` is passed |
| `summarize_winlab_outlet_power.py` | Summarize exported candidate outlet CSVs into mean/min/max/std/energy | Yes |
| `build_winlab_evidence_report.py` | Build compact `run_report.md` from snapshot/probe evidence folders | Yes |
| `run_winlab_power_workflow.py` | One-command wrapper for snapshot -> probe -> optional outlet summary -> report | Yes; dry-run unless `--live` is passed |

Local-only helper:

| Script | Purpose | Safe by Default |
| ------ | ------- | --------------- |
| `fetch_winlab_hpe_artifacts.py` | Fetch a selected HPE run folder back to the local machine with `scp -r` | Yes with `--dry-run`; otherwise read-only fetch from HPE |

---

## 3. Verified HPE Script Hashes

Captured from HPE on 2026-07-03:

```text
0a66cbefe4ea22d30367bc3fb89b7ee665eaa6f8af002cb4aaaa85c7e8db0ba6  build_winlab_evidence_report.py
d6182f2c28ba1a9202f29dd91266c2b48e269e0af59237375db80a4f69fbe53d  collect_winlab_status_snapshot.py
9beb7f15d07dd0acb2c968dec26f7ba0466fbb29947777b945c5a333dd96abf2  run_winlab_ocloud_power_probe.py
c4cd92b4691e3240d0e149172d6eac7474491476f280e1bc8c3467931d5d0576  run_winlab_power_workflow.py
521ff951bcfc5c24083c4853adff50721ebe0972cacb7b2c567e19122d822771  summarize_winlab_outlet_power.py
```

---

## 4. One-Command Dry Workflows

OCloud dry workflow:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_power_workflow.py \
  --mode ocloud \
  --bandwidth 100 \
  --period 30 \
  --gap-time 2 \
  --ue-model samsung \
  --settle-time 45 \
  --attach-timeout 240
```

Verified output:

```text
/home/hpe/winlab_e2e_rapp/runs/workflow-ocloud-dry-20260703-073208/
```

Bare Metal dry workflow with ping:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_power_workflow.py \
  --mode baremetal \
  --bandwidth 100 \
  --period 30 \
  --gap-time 2 \
  --ue-model samsung \
  --ping
```

Verified output:

```text
/home/hpe/winlab_e2e_rapp/runs/workflow-baremetal-dry-20260703-073603/
```

---

## 5. Live Workflow

Only use `--live` when lab state is ready and the UE/OCloud/Bare Metal path should actually run.

OCloud live workflow:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_power_workflow.py \
  --mode ocloud \
  --bandwidth 100 \
  --period 300 \
  --gap-time 2 \
  --ue-model samsung \
  --settle-time 45 \
  --attach-timeout 240 \
  --live
```

Bare Metal live workflow with ping:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_power_workflow.py \
  --mode baremetal \
  --bandwidth 100 \
  --period 300 \
  --gap-time 2 \
  --ue-model samsung \
  --ping \
  --live
```

---

## 6. Optional Influx Export

Before a live OCloud run, set these only in the HPE shell that has access:

```bash
export INFLUX_URL="http://<host>:8086"
export INFLUX_TOKEN="<token>"
export INFLUX_ORG="<org>"
export INFLUX_BUCKET="<bucket>"
export INFLUX_FIELD="active_power"
export INFLUX_OUTLET_COLUMN="outlet"
```

If outlet names are stored as measurements like `outlet1`, `outlet2`, etc.:

```bash
export INFLUX_OUTLET_COLUMN="_measurement"
```

Candidate outlet list:

```text
outlet1,outlet2,outlet11
```

Ravi confirmed:

```text
Outlet 1 = Pegatron RU [N], OC/DU testing
Outlet 2 = Pegatron RU [O], OCloud testing
Outlet 11 = Lavoisier, [O-Cloud] OAI NFAPI (PNF), OAI Split 7.2 gNB + Commercial RU
```

For current OCloud O-RU throughput-vs-power runs, use Outlet 2. Outlet 11 should be treated as Lavoisier/PNF host-side power, not RU-only power. CortexDC cannot show RU data yet, so use InfluxDB, direct PDU export, or manual export for Outlet 2 `active_power`.

---

## 7. Evidence Outputs

Workflow folder shape:

```text
runs/workflow-<mode>-<dry|live>-YYYYMMDD-HHMMSS/
```

Expected key files:

```text
workflow_summary.json
status_snapshot/summary.json
status_snapshot/run_report.md
probe/markers.csv
probe/request_payload.json
probe/submission.json
probe/job_latest.json        # live jobs only
probe/influx/*.csv           # only if Influx export is configured
probe/candidate_outlet_power_summary.csv
probe/candidate_outlet_power_summary.json
probe/run_report.md
```

---

## 8. Fetch HPE Artifacts Locally

Run from the local repo on Windows:

```powershell
python scripts\fetch_winlab_hpe_artifacts.py `
  --remote-run runs/workflow-ocloud-dry-20260703-073208 `
  --dry-run
```

Fetch to a local evidence folder:

```powershell
python scripts\fetch_winlab_hpe_artifacts.py `
  --remote-run runs/workflow-ocloud-dry-20260703-073208 `
  --output-dir runs\hpe_artifacts
```

Verified temp fetch on 2026-07-03:

```text
Remote:
/home/hpe/winlab_e2e_rapp/runs/workflow-ocloud-dry-20260703-073208

Local temp:
%TEMP%/winlab_hpe_fetch_test_*/workflow-ocloud-dry-20260703-073208
```

The helper checks that the remote directory exists before fetching unless `--skip-remote-check` is passed.

---

## 9. Safety Rules

```text
Default wrapper behavior is dry-run.
Only `--live` starts a real rApp job.
Use Outlet 2 for the current OCloud Pegatron O-RU power trace.
Do not use CortexDC server Outlet 11 as RU-only power.
Because CortexDC cannot show RU data yet, preserve export method and timestamp basis for Outlet 2 before final plotting.
Run uvicorn on 127.0.0.1:9090, not 0.0.0.0:9090.
Do not kill Open5GS processes listening on other 127.0.0.x:9090 addresses.
Do not use the Lavoisier `rrr` RU reboot helper unless coordinated with Ming/lab staff.
```
