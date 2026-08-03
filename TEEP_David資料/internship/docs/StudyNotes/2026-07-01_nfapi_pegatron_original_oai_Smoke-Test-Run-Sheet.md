---
title: nFAPI Pegatron Original OAI Smoke-Test Run Sheet
---

# nFAPI Pegatron Original OAI Smoke-Test Run Sheet

**Date:** 2026-07-01  
**Run label:** `nfapi_pegatron_original_oai`  
**Purpose:** Prepare a reproducible smoke test for the WINLAB / Pegatron O-RU end-to-end OAI path.  
**Status:** Draft run sheet; not yet final baseline evidence.

---

## 1. Purpose

This run sheet is for a smoke test of the OAI end-to-end path:

```text
HPE / Kubernetes / OAI nFAPI deployment
-> Pegatron O-RU path
-> Android UE access through AnyDesk
-> iPerf traffic from HPE/server side to UE side
```

The goal is to verify that the lab path is runnable and that the evidence capture process is clear.

This is **not** a final baseline run unless the Pegatron O-RU power source is confirmed and timestamp-aligned with the traffic window.

---

## 2. Current Assumptions

| Item | Current Understanding | Status |
| ---- | --------------------- | ------ |
| Architecture | nFAPI | Confirmed from current project direction |
| Scheduler mode | Original / unmodified OAI scheduler | Assumed; verify image/branch before baseline use |
| Run type | Smoke test | Confirmed |
| Traffic source | HPE server side | Observed / needs exact command confirmation |
| Traffic target | UE side through AnyDesk / Android Magic iPerf | Observed |
| UE count | Two UEs visible, but one UE has been tested/observed for iPerf | Needs confirmation for final sweep |
| Power evidence | Outlet 2 Pegatron RU `[O]` OCloud testing power | Physical outlet confirmed by Ravi; timestamped export still needed |
| Final plot eligibility | Excluded until Outlet 2 power export is timestamp-aligned with traffic window | Confirmed rule |

---

## 3. Access Checklist

### VPN

VPN is required.

Use the lab-provided WireGuard configuration file. Do **not** commit WireGuard private keys or VPN credentials into the repository.

Expected VPN checks:

```bash
wg show
ping -c 3 192.168.8.26
```

### HPE Server

```text
SSH target: hpe@192.168.8.26
Host: hpe-ProLiant-DL380-Gen10
```

Observed login identity:

```bash
whoami
hostname
```

Observed output:

```text
hpe
hpe-ProLiant-DL380-Gen10
```

### UE Access

```text
Access method: AnyDesk
Observed AnyDesk ID: 1981446389
UE layout: one AnyDesk session shows two Android UEs side-by-side
Approval/login method: no separate approval observed
Access helper if blocked: Ming
```

Open item:

```text
Confirm whether there is one AnyDesk ID for both UEs or separate IDs for UE1 and UE2.
```

---

## 4. Kubernetes Workspace Status

Observed current Kubernetes identity:

```bash
kubectl config current-context
kubectl config view --minify --output 'jsonpath={..namespace}'; echo
```

Observed output:

```text
Context: ming-context
Default namespace: ming-ns
User: ming@example.com
```

Observed permissions:

```text
ming-ns:
- can create pods: yes
- can create deployments: yes

teep-ns:
- can list pods: no
- can create pods: no
- can create deployments: no

namespace creation:
- attempted david-ns creation failed with Forbidden
```

Operational rule:

```text
Do not deploy or modify resources in ming-ns unless Ming / lab mentor approves.
Use ming-ns only as the known-good reference path until a personal namespace is created and bound.
```

Personal workspace status:

```text
Target namespace: david-ns or teep-david-ns
Status: pending admin creation / RoleBinding
Required for Helm smoke tests: pods, deployments, services, configmaps, secrets
```

Reason:

```text
Helm stores release state in Kubernetes secrets by default, so secret permissions are required.
```

---

## 5. Deployment Reference

Observed HPE working directory:

```bash
cd ~/CRAN/ocloud-helm-templates
```

Observed branch / path context:

```text
~/CRAN/ocloud-helm-templates ‹ming/starlingx/pegatron›
```

Observed directory contents:

```text
cloud_e2e.py
fix_multus_shim.sh
host-debug-pod.yaml
Jenkins
logs_e2e_20260629_010538
logs_e2e_20260630_013345
oai-cu
oai-cu-cp
oai-cu-up
oai-du-fhi-72
oai-gnb-fhi-72
oai-nr-ue
oai-pnf
oai-vnf
README.md
server-configs
```

Main charts for the nFAPI / Pegatron path:

```text
VNF chart: /home/hpe/CRAN/ocloud-helm-templates/oai-vnf
PNF chart: /home/hpe/CRAN/ocloud-helm-templates/oai-pnf
```

Observed install command:

```bash
helm install vnf /home/hpe/CRAN/ocloud-helm-templates/oai-vnf/
helm install pnf /home/hpe/CRAN/ocloud-helm-templates/oai-pnf/
```

Observed namespace from K9s:

```text
ming-ns
```

Observed pod names during earlier deployment attempt:

```text
oai-pnf-pegatron-844485c99b-ng6ch
oai-vnf-696c88996d-wqbbc
```

Later observed pod state:

```text
Many oai-pnf and oai-vnf pods were Terminating.
Latest pnf/vnf pods were Pending.
```

Interpretation:

```text
This was described as E2E cleanup / test-state churn. Do not treat this pod state as the stable baseline.
Confirm clean pod state before smoke testing.
```

Pod status check method:

```text
Primary observed tool: k9s
Alternative: kubectl get pods -n <namespace>
```

Current known-good OCloud check:

```bash
export KUBECONFIG=/home/hpe/CRAN/ming-kubeconfig.yaml
/home/linuxbrew/.linuxbrew/bin/helm list -n ming-ns
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml get pods -n ming-ns -o wide
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml get network-attachment-definitions -n ming-ns
```

Verified on 2026-07-03 15:20 Asia/Taipei:

```text
Helm:
pnf  ming-ns  deployed  oai-pnf-pegatron-2.1.0
vnf  ming-ns  deployed  oai-vnf-2.1.0

Pods:
oai-pnf-pegatron-844485c99b-2d7fh  1/1  Running  lavoisier
oai-vnf-696c88996d-qp4pg           1/1  Running  lavoisier

NetworkAttachmentDefinitions:
oai-pnf-pegatron-nfapi
oai-pnf-pegatron-ru-cplane
oai-pnf-pegatron-ru-uplane
oai-vnf-n2
oai-vnf-nfapi
```

OCloud Helm recovery procedure used after `ming-ns` had no VNF/PNF resources:

```bash
export KUBECONFIG=/home/hpe/CRAN/ming-kubeconfig.yaml
cd /home/hpe/CRAN/ocloud-helm-templates

# Inspect first if releases still exist:
/home/linuxbrew/.linuxbrew/bin/helm list -n ming-ns -a
/home/linuxbrew/.linuxbrew/bin/helm status vnf -n ming-ns || true
/home/linuxbrew/.linuxbrew/bin/helm status pnf -n ming-ns || true

# Clean install path used after releases were absent:
/home/linuxbrew/.linuxbrew/bin/helm install vnf /home/hpe/CRAN/ocloud-helm-templates/oai-vnf/ -n ming-ns
/home/linuxbrew/.linuxbrew/bin/helm install pnf /home/hpe/CRAN/ocloud-helm-templates/oai-pnf -n ming-ns

# Confirm recovery:
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml get pods -n ming-ns -o wide
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml get network-attachment-definitions -n ming-ns
```

Expected recovery signal:

```text
VNF and PNF pods both reach 1/1 Running.
NAD resources exist before running cloud_e2e.py.
AMF log later shows gNB-N2 accepted from 192.168.8.199.
```

### Pre-Test Status Snapshot

Use this before a live OCloud or Bare Metal test to capture read-only evidence:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/collect_winlab_status_snapshot.py
```

The snapshot collects:

```text
hostname and date
rApp /health, /config, and /jobs
Helm releases in ming-ns
pods, deployments, and NetworkAttachmentDefinitions in ming-ns
last 80 lines of /home/hpe/open5gs_logs/amf.log
```

Verified snapshot on 2026-07-03 15:27 Asia/Taipei:

```text
/home/hpe/winlab_e2e_rapp/runs/status-snapshot-20260703-072739/
```

All snapshot commands returned `0`. The snapshot confirmed both OCloud pods were `1/1 Running`, five NAD resources were present, and the rApp health endpoint was OK.

---

## 6. Image / Build Reference

Observed Jenkins pipeline parameters suggest the gNB image is built from:

```text
GIT_REPO: https://github.com/bmw-ece-ntust/openairinterface5g
GIT_BRANCH: nfapi-DelayManagement-BMW
QUAY_REPO: bmw.ece.ntust.edu.tw/minghong
TAG: latest
Final pushed image shape: bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest
```

Important caveat:

```text
Do not rely on `latest` as final experiment evidence.
For smoke testing, record it as observed.
For baseline experiments, verify the exact pod image, branch, and commit.
```

Before any smoke test, record:

```bash
kubectl describe pod -n <namespace> <pod-name> | grep -i "Image:"
helm get values -n <namespace> <release-name> --all
```

If `helm get values` fails due to permissions, record the failure and save the chart `values.yaml` / `configmap.yaml` used for deployment.

---

## 7. OAI Runtime Configuration

Important config files:

```text
oai-vnf/values.yaml
oai-vnf/templates/configmap.yaml
oai-pnf/values.yaml
oai-pnf/templates/configmap.yaml
```

Fields to verify before treating a run as baseline:

```text
architecture: nFAPI
scheduler_mode: original OAI / unmodified
OAI image repository:
OAI image tag:
OAI branch:
OAI commit:
dl_frequencyBand:
absoluteFrequencySSB:
dl_absoluteFrequencyPointA:
TDD pattern:
namespace:
Helm release:
```

Suggested commands:

```bash
kubectl get pods -n <namespace>
kubectl describe pod -n <namespace> <pod-name> | grep -i "Image:"
helm get values -n <namespace> vnf --all
helm get values -n <namespace> pnf --all
kubectl get configmap -n <namespace> -o yaml
```

If using a local chart directory, also save:

```bash
git -C ~/CRAN/ocloud-helm-templates status --short
git -C ~/CRAN/ocloud-helm-templates rev-parse --abbrev-ref HEAD
git -C ~/CRAN/ocloud-helm-templates rev-parse HEAD
```

---

## 8. UE Procedure

Observed UE flow:

1. Connect to AnyDesk.
2. View the two Android UEs side-by-side.
3. Turn off airplane mode on the target UE.
4. Wait for the status indicator to change from no network to `5G`.
5. Open PingTest.
6. Record public and private IPs shown by PingTest.
7. Activate Magic iPerf.
8. Start iPerf command from the HPE/server side.

Evidence to record:

```text
AnyDesk ID:
UE selected:
UE visible status before attach:
UE visible status after attach:
PingTest public IP:
PingTest private IP:
Magic iPerf status:
Screenshot filenames:
```

---

## 9. iPerf / Traffic Procedure

Preferred path is the rApp API on HPE:

```bash
cd /home/hpe/winlab_e2e_rapp
export WINLAB_E2E_EXEC_MODE=local
uvicorn winlab_e2e_rapp.app:app --host 127.0.0.1 --port 9090
```

Health check:

```bash
curl http://127.0.0.1:9090/health
```

Expected response:

```json
{"status":"ok","version":"0.1.0","exec_mode":"local","ssh_target":null}
```

Current rApp endpoints:

| Endpoint | Method | Purpose |
| -------- | ------ | ------- |
| `/health` | GET | API health and execution mode |
| `/config` | GET | Visible non-secret config |
| `/jobs` | GET | List recent jobs |
| `/jobs/{job_id}` | GET | Poll a specific async job |
| `/ue/action` | POST | UE airplane mode, status, IP, reboot, iPerf, ensure-online actions |
| `/gnb/run` | POST | Unified Bare Metal / OCloud gNB + UE/iPerf flow |
| `/experiments/cleanup` | POST | Cleanup helper |
| `/datasets/build` | POST | Dataset builder wrapper |
| `/plots/throughput-latency` | POST | Plot wrapper |

Old compatibility endpoints such as `/experiments/bandwidth` and `/cloud/smoke` were intentionally removed. Use `/gnb/run`.

### Verified rApp Command Table

Dry-runs verified on HPE at 2026-07-03 15:20 Asia/Taipei:

| Mode | API request | Underlying command |
| ---- | ----------- | ------------------ |
| OCloud | `POST /gnb/run` with `{"mode":"ocloud","bandwidth":[100],"period":300,"gap_time":2,"ue_model":"samsung","settle_time":45,"attach_timeout":240,"keep_ue_online_on_failure":true,"dry_run":true}` | `python3 /home/hpe/CRAN/ocloud-helm-templates/cloud_e2e.py --bandwidth 100 --period 300 --gap-time 2 --ue-model samsung --settle-time 45 --attach-timeout 240 --keep-ue-online-on-failure` |
| Bare Metal | `POST /gnb/run` with `{"mode":"baremetal","server":"hpe","bandwidth":[100],"period":300,"gap_time":2,"ping":true,"uplink":false,"ue_model":"samsung","dry_run":true}` | `OAI_UE_MODEL=samsung python3 /home/hpe/ming-logs/exp_bandwidth.py --server hpe --bandwidth 100 --period 300 --gap-time 2 --ping` |

OCloud dry-run:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"ocloud","bandwidth":[100],"period":300,"gap_time":2,"ue_model":"samsung","settle_time":45,"attach_timeout":240,"keep_ue_online_on_failure":true,"dry_run":true}'
```

OCloud live smoke run:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"ocloud","bandwidth":[100],"period":300,"gap_time":2,"ue_model":"samsung","settle_time":45,"attach_timeout":240,"keep_ue_online_on_failure":true}'
```

Bare Metal dry-run:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"baremetal","server":"hpe","bandwidth":[100],"period":300,"gap_time":2,"ping":true,"uplink":false,"ue_model":"samsung","dry_run":true}'
```

Bare Metal live smoke run:

```bash
curl -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{"mode":"baremetal","server":"hpe","bandwidth":[100],"period":300,"gap_time":2,"ping":true,"uplink":false,"ue_model":"samsung"}'
```

Poll a job:

```bash
curl http://127.0.0.1:9090/jobs/<job_id>
```

Historical manual iPerf understanding:

```text
Source: HPE server side
Target: UE private IP shown in PingTest / Magic iPerf
Likely command shape: iperf <UE_PRIVATE_IP> -t 10
Protocol: needs confirmation
Smoke-test duration: 10 s observed / 60 s preferred for cleaner smoke evidence
Target bitrate: 100M if using UDP rate control; needs exact command confirmation
```

Open item:

```text
Confirm exact iPerf command from Ming or HPE shell history before running.
```

Recommended smoke-test metadata:

```text
run_id: nfapi_original_smoke_001
ue_count:
ue_private_ip:
server_ip:
iperf_command:
traffic_protocol:
target_bitrate_mbps:
duration_s:
iperf_start_utc:
iperf_end_utc:
measured_throughput_mbps:
packet_loss_or_retransmits:
raw_output_file:
```

Prefer saving output to a file:

```bash
iperf <UE_PRIVATE_IP> -t 10 | tee iperf_nfapi_original_smoke_001.txt
```

If using `iperf3` and JSON is available:

```bash
iperf3 -c <UE_PRIVATE_IP> -t 60 --json | tee iperf_nfapi_original_smoke_001.json
```

Use the actual lab-supported command if different.

---

## 10. Timing / UTC Markers

Local lab time is Taiwan time:

```text
Asia/Taipei = UTC+8
```

For reproducible evidence, record UTC markers where possible.

Suggested marker file:

```text
runs/winlab_oru/2026-07-01/nfapi_original_smoke_001/utc_markers.txt
```

Marker format:

```text
<UTC timestamp> RUN_START run_id=nfapi_original_smoke_001
<UTC timestamp> POD_HEALTH_CONFIRMED namespace=<namespace>
<UTC timestamp> UE_ATTACHED ue=<ue_id> ip=<ue_private_ip>
<UTC timestamp> IPERF_START command="<command>"
<UTC timestamp> IPERF_END
<UTC timestamp> RUN_STOP
```

Useful command:

```bash
date -u +"%Y-%m-%dT%H:%M:%S.%3NZ"
```

---

## 11. CortexDC / PDU Power Status

Current status:

```text
Pegatron O-RU PDU outlet: Outlet 2 for current OCloud Pegatron RU [O]
CortexDC representation: CortexDC cannot show RU data yet
InfluxDB representation: likely outlet2 if labels match PDU outlet numbers; confirm before final plot
timestamped active_power export: still needed
CortexDC outlet to InfluxDB outlet mapping: use Outlet 2 mapping; CortexDC RU view unavailable
```

Rule for this smoke test:

```text
If Outlet 2 active_power export is unavailable or timestamp basis is unknown, exclude the run from the final throughput-vs-power plot.
Use the run only as E2E access/path validation or power-pipeline validation.
```

If Chynna / Peter / Ming confirms the power source before the run, record:

```text
PDU model:
PDU outlet: Outlet 2
CortexDC asset name: unavailable for RU at this time
InfluxDB measurement/field:
active_power units:
sampling interval:
timestamp timezone:
export method:
export file:
```

---

## 12. Evidence Folder

Proposed run folder:

```text
runs/winlab_oru/2026-07-01/nfapi_original_smoke_001/
```

Recommended files:

```text
run_summary.md
utc_markers.txt
iperf_nfapi_original_smoke_001.txt
ue_pingtest_screenshot.png
ue_5g_attach_screenshot.png
k9s_pods_screenshot.png
helm_values_vnf.yaml
helm_values_pnf.yaml
configmap_snapshot.yaml
pod_describe_vnf.txt
pod_describe_pnf.txt
power_export_placeholder.md
```

Minimum smoke-test evidence:

```text
1. pod health evidence;
2. UE attach / IP evidence;
3. iPerf command and output;
4. UTC start/end markers;
5. note explaining whether RU power mapping was confirmed or pending.
```

---

## 13. Pass / Fail Criteria

| Result | Criteria |
| ------ | -------- |
| Pass | Pods healthy, UE attached to 5G, UE IP known, iPerf produces throughput, evidence saved |
| Partial pass | E2E traffic works but CortexDC/PDU Pegatron O-RU power mapping is missing |
| Fail | HPE access blocked, Kubernetes deployment blocked, pods unhealthy, UE cannot attach, UE IP unavailable, or iPerf fails |

For this smoke test, a partial pass is still useful because it validates the E2E path while the power source is being confirmed.

---

## 14. Open Questions

| Question | Owner / Source | Status |
| -------- | -------------- | ------ |
| Should David use `ming-ns` under supervision, or wait for a personal namespace? | Ming / lab mentor | Pending |
| Who will create and bind `david-ns` or `teep-david-ns`? | lab mentor / admin | Pending |
| What is the exact iPerf command used in the known-good E2E flow? | Ming | Pending |
| Is `bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest` the current known-good original-OAI image? | Ming / Helm values | Pending |
| Is the deployed scheduler truly original/unmodified OAI? | Ming / image branch / commit | Pending |
| Which PDU outlet powers the current OCloud Pegatron O-RU? | Ravi | Confirmed: Outlet 2 |
| Can InfluxDB, direct PDU, or manual export provide timestamped `active_power` for Outlet 2? | Chynna / Ravi / Peter | Pending |
| Does InfluxDB label Outlet 2 as `outlet2`? | Chynna / Ravi / Peter | Pending |

---

## 15. OCloud Power Probe Workflow

Purpose:

```text
Create exact UTC/Taipei start-end markers around a rApp OCloud run, then query
Outlet 2 power once InfluxDB, direct PDU, or manual export access is available.
```

Confirmed outlet mapping:

| Outlet | Working Interpretation |
| ------ | ---------------------- |
| `outlet1` | Pegatron RU [N], OC/DU testing; not current OCloud path |
| `outlet2` | Pegatron RU [O], OCloud testing; use for current OCloud O-RU power |
| `outlet11` | Lavoisier / OCloud OAI NFAPI host path; not RU-only |

Probe script on HPE:

```text
/home/hpe/winlab_e2e_rapp/scripts/run_winlab_ocloud_power_probe.py
```

One-command workflow wrapper on HPE:

```text
/home/hpe/winlab_e2e_rapp/scripts/run_winlab_power_workflow.py
```

Candidate outlet summary script on HPE:

```text
/home/hpe/winlab_e2e_rapp/scripts/summarize_winlab_outlet_power.py
```

Dry-run command:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_ocloud_power_probe.py \
  --mode ocloud \
  --bandwidth 100 \
  --period 30 \
  --gap-time 2 \
  --ue-model samsung \
  --settle-time 45 \
  --attach-timeout 240 \
  --dry-run
```

Live marked OCloud command:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_ocloud_power_probe.py \
  --mode ocloud \
  --bandwidth 100 \
  --period 300 \
  --gap-time 2 \
  --ue-model samsung \
  --settle-time 45 \
  --attach-timeout 240 \
  --outlets outlet2
```

Optional InfluxDB environment, once credentials and endpoint are known:

```bash
export INFLUX_URL="http://<host>:8086"
export INFLUX_TOKEN="<token>"
export INFLUX_ORG="<org>"
export INFLUX_BUCKET="<bucket>"
export INFLUX_FIELD="active_power"

# Use this if the outlet label is a tag/column.
export INFLUX_OUTLET_COLUMN="outlet"

# Use this instead if measurements are literally named outlet1/outlet2/etc.
# export INFLUX_OUTLET_COLUMN="_measurement"
```

Expected output folder:

```text
runs/YYYY-MM-DD/winlab-ocloud-power-probe-HHMMSS/
```

Expected files:

```text
markers.csv
request_payload.json
submission.json
job_latest.json
summary.json
influx_export_summary.json
influx/outlet2.csv
```

After a probe run with Influx-exported outlet CSVs, summarize outlet traces:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/summarize_winlab_outlet_power.py runs/YYYY-MM-DD/winlab-ocloud-power-probe-HHMMSS
```

Expected summary outputs:

```text
candidate_outlet_power_summary.csv
candidate_outlet_power_summary.json
```

Use Outlet 2 as the target OCloud O-RU power trace. Outlet 1 and Outlet 11 can still be collected as comparison traces if useful, but they are not the current OCloud RU power label.

Recommended one-command dry workflow:

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

This is safe by default because it passes `--dry-run` to the rApp probe. To start an actual run, add `--live` deliberately:

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

Verified dry workflow output:

```text
/home/hpe/winlab_e2e_rapp/runs/workflow-ocloud-dry-20260703-073208/
```

The verified dry workflow created:

```text
workflow_summary.json
status_snapshot/run_report.md
probe/run_report.md
```

Verified Bare Metal dry workflow with ping:

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

Output:

```text
/home/hpe/winlab_e2e_rapp/runs/workflow-baremetal-dry-20260703-073603/
```

Verified underlying dry-run command:

```bash
OAI_UE_MODEL=samsung python3 /home/hpe/ming-logs/exp_bandwidth.py --server hpe --bandwidth 100 --period 30 --gap-time 2 --ping
```

Build a compact Markdown evidence report from any snapshot or probe run folder:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/build_winlab_evidence_report.py runs/status-snapshot-YYYYMMDD-HHMMSS
python3 scripts/build_winlab_evidence_report.py runs/YYYY-MM-DD/winlab-ocloud-power-probe-HHMMSS
```

Verified report outputs:

```text
/home/hpe/winlab_e2e_rapp/runs/status-snapshot-20260703-072739/run_report.md
/home/hpe/winlab_e2e_rapp/runs/ocloud-dry-run-doc-20260703-152056/run_report.md
```

Do not use outlet power data as final Pegatron O-RU evidence until Outlet 2 `active_power` is timestamp-aligned with the traffic window and the export label/timestamp basis are recorded.

---

## 16. Short Conclusion

The current known-good operational reference is Ming's `ming-ns` path on the HPE server. David's personal Kubernetes workspace is not available yet and requires admin namespace creation / RoleBinding.

Until a personal namespace is ready, the safe workflow is:

```text
observe Ming's working flow
-> document exact commands, configs, and evidence
-> prepare smoke-test run sheet
-> run only with Ming / lab mentor approval
-> exclude result from final power plot unless Outlet 2 power export is timestamp-aligned with the traffic window
```
