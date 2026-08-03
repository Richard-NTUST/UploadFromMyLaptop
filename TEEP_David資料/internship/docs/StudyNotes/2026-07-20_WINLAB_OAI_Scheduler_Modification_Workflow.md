---
title: WINLAB OAI Scheduler Modification Workflow
date: 2026-07-20
status: working-note
---

# WINLAB OAI Scheduler Modification Workflow

## Current Target

The next roadmap step after stabilizing the OCloud E2E rApp, Docker service, InfluxDB export, and power/throughput merge path is to start modifying the OAI gNB scheduler and compare scheduler variants against Pegatron RU Outlet 2 active power.

The safest first target is not a behavior-changing scheduler patch. It should be a logging-only OAI image that proves we can:

1. modify the OAI source;
2. build and push the image through BMW Jenkins;
3. deploy that image through the HPE Helm chart;
4. run the existing rApp E2E flow;
5. collect scheduler allocation logs, iPerf throughput, and PDU active power for the same time window.

After that is proven, implement the first behavior patch.

## Confirmed Experiment Path

The working OCloud path uses:

```text
rApp endpoint: http://127.0.0.1:19090/gnb/run
HPE server: hpe@192.168.8.26
HPE repo/chart path: /home/hpe/CRAN/ocloud-helm-templates
VNF chart: /home/hpe/CRAN/ocloud-helm-templates/oai-vnf
PNF chart: /home/hpe/CRAN/ocloud-helm-templates/oai-pnf
Namespace observed: ming-ns
Helm releases observed: vnf, pnf
Deployments observed: oai-vnf, oai-pnf-pegatron
RU power source: CortexDC / InfluxDB, pdu_outlet active_power, Outlet 2
```

Live checks on 2026-07-20 confirmed:

```text
BMW account / registry site reachable: https://bmw.ece.ntust.edu.tw/
Jenkins reachable: https://jenkins.bmw.lab/
Jenkins version observed: 2.528.1
Reference Jenkins job reachable: ming-nfapi-Fronthaul72-e2e
Last successful checked build: #87
Build #87 source branch: refs/remotes/origin/nfapi-DelayManagement
Build #87 source commit: 9522317237738e3c4d1f4e006dc3b27faf5904b5
Build #87 commit message: fix(nfapi/vnf): cleanly stop and join VNF timing thread on shutdown
HPE SSH reachable: hpe@192.168.8.26
Current Helm releases:
  pnf  ming-ns  deployed  oai-pnf-pegatron-2.1.0
  vnf  ming-ns  deployed  oai-vnf-2.1.0
Current VNF image:
  bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest
Current pods:
  oai-pnf-pegatron-*  1/1 Running on lavoisier
  oai-vnf-*           1/1 Running on lavoisier
```

Known successful rApp flow:

```text
1. VNF and PNF pods reach Running/Ready.
2. Samsung UE attaches and receives 10.45.x.x.
3. Local iperf3 server listens on ogstun 10.45.0.1.
4. UE-side iPerf client runs through IAPC/ADB.
5. Artifacts are written under runs/.../e2e-ocloud-<timestamp>.
6. InfluxDB Outlet 2 active_power CSV is exported for the run window.
7. merge_winlab_e2e_power.py combines throughput and power.
```

## Scheduler Code Touchpoints

OAI does not expose a simple runtime scheduler-mode toggle for the FDM/TDM behavior we want. The notes identify source changes in:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c
```

Important functions:

```text
nr_dlsch_preprocessor()
  - computes available bandwidth
  - computes max_sched_ues
  - calls pf_dl()

pf_dl()
  - updates UE buffers
  - computes proportional-fair coefficients
  - scans rballoc_mask[] for free contiguous PRBs
  - sets max_rbSize
  - calls nr_find_nb_rb()
  - fills rbStart/rbSize/MCS/TBS in the scheduled PDSCH data
```

Practical levers:

| Mode | Intended meaning | Minimal source change |
|---|---|---|
| `oai_original` | Baseline OAI PF scheduler | No behavior change |
| `oai_logging_only` | Baseline scheduler plus allocation logs | Add logs after scheduling decisions |
| `oai_prb_cap_27` | Narrow per-slot grants for a TDM-like diagnostic | Cap `max_rbSize` before `nr_find_nb_rb()` |
| `oai_single_ue_per_slot` | Strict one UE per slot | Force `max_sched_ues = 1` before `pf_dl()` |

Recommended first behavior patch:

```c
// In pf_dl(), after the free contiguous RB scan sets max_rbSize:
max_rbSize = min(max_rbSize, 27);
```

Recommended strict TDM patch:

```c
// In nr_dlsch_preprocessor(), after default max_sched_ues is computed:
max_sched_ues = 1;
```

For the current single-UE Samsung tests, `max_sched_ues = 1` may not visibly change behavior. The PRB cap is more likely to produce measurable scheduler allocation differences in the first controlled experiment.

## Jenkins Image Build Flow

The BMW Jenkins workflow builds and publishes the OAI gNB image. It does not deploy it by itself.

Internal sites from the notes:

```text
BMW account / registry identity: https://bmw.ece.ntust.edu.tw/
Jenkins CI: https://jenkins.bmw.lab/
Relevant Jenkins tab: nFAPI
Reference job: ming-nfapi-Fronthaul72-e2e
```

Pipeline parameters from the notes:

| Parameter | Meaning | Observed/example value |
|---|---|---|
| `GIT_REPO` | OAI source repository | `https://github.com/bmw-ece-ntust/openairinterface5g` |
| `GIT_BRANCH` | Branch containing the scheduler changes | Jenkins default: `nfapi-DelayManagement-BMW`; build #87 used `nfapi-DelayManagement` |
| `GIT_CREDENTIAL_ID` | Jenkins Git credential if repo is private | `ming_gh_token` or David's credential |
| `QUAY_REPO` | BMW registry namespace | `bmw.ece.ntust.edu.tw/<username>` |
| `TAG` | Image tag | Use explicit experiment tags, not `latest` |
| `REGISTRY_CREDENTIAL_ID` | Jenkins credential for registry push | Current job uses `ming_account`; David needs his own or approved shared credential |
| `E2AP_VERSION` | E2AP build version | Current job/default: `E2AP_V3` |
| `KPM_VERSION` | E2SM-KPM build version | Current job/default: `KPM_V3_00` |

Build stages from the note:

```text
podman build -t ran-base -f docker/Dockerfile.base.ubuntu .
podman build -t ran-build-fhi72 -f docker/Dockerfile.build.fhi72.ubuntu .
podman build -t oai-gnb -f docker/Dockerfile.gNB.fhi72.ubuntu .
podman tag oai-gnb ${QUAY_REPO}/oai-gnb:${TAG}
podman push ${QUAY_REPO}/oai-gnb:${TAG}
```

The live HPE copy of `Jenkins/Jenkinsfile` adds a small but important build detail: the `Build Build Image` stage creates a temporary patched Dockerfile so `E2AP_VERSION` and `KPM_VERSION` are redeclared after the `FROM ran-base AS ran-build-fhi72` boundary. Without that, OAI CMake can receive empty E2 arguments.

Final image shape:

```text
bmw.ece.ntust.edu.tw/<username>/oai-gnb:<tag>
```

Use tags like:

```text
david-oai-original-logonly-20260720
david-oai-prb-cap27-20260720
david-oai-single-ue-slot-20260720
```

## HPE Helm Deployment Flow

After Jenkins pushes the image, HPE Helm must be pointed at that exact image tag.

Known chart/release context:

```text
cd /home/hpe/CRAN/ocloud-helm-templates
helm list -n ming-ns
helm install vnf /home/hpe/CRAN/ocloud-helm-templates/oai-vnf/ -n ming-ns
helm install pnf /home/hpe/CRAN/ocloud-helm-templates/oai-pnf/ -n ming-ns
```

Live `oai-vnf/values.yaml` image keys:

```yaml
nfimage:
  repository: bmw.ece.ntust.edu.tw/minghong/oai-gnb
  version: latest
  pullPolicy: Always
```

Live deployment template renders:

```yaml
image: "{{ .Values.nfimage.repository }}:{{ .Values.nfimage.version }}"
```

Therefore, the deployment override shape is:

```bash
helm upgrade --install vnf /home/hpe/CRAN/ocloud-helm-templates/oai-vnf \
  -n ming-ns \
  -f /home/hpe/CRAN/ocloud-helm-templates/oai-vnf/values.yaml \
  --set nfimage.repository=bmw.ece.ntust.edu.tw/<username>/oai-gnb \
  --set nfimage.version=<tag>
```

Verification commands:

```bash
kubectl get pods -n ming-ns -o wide
kubectl describe pod -n ming-ns <oai-vnf-pod> | grep -i "Image:"
helm get values -n ming-ns vnf --all
kubectl get configmap -n ming-ns -o yaml
```

Record these for every scheduler run:

```text
OAI Git repo
OAI branch
OAI commit
Jenkins build URL
Full pushed image reference
Helm release
Namespace
VNF pod image
Chart values snapshot
OAI ConfigMap snapshot
rApp run ID
InfluxDB power export file
Merged power/throughput CSV
```

## Recommended Step-by-Step Plan

1. Confirm current known-good VNF image and OAI commit.
2. Create a scheduler logging-only branch from the known-good OAI branch.
3. Add allocation logs around `pf_dl()` output: frame, slot, RNTI, `rbStart`, `rbSize`, MCS, TBS, mode label.
4. Build the logging-only image through Jenkins with an explicit tag.
5. Deploy the image through the HPE `oai-vnf` Helm chart.
6. Run a short 60 s E2E test at 100 or 200 Mbps.
7. Confirm the VNF pod logs contain scheduler allocation lines and the rApp artifacts still generate normally.
8. Run a 20 min or 1 h baseline with the logging-only image.
9. Implement `oai_prb_cap_27`.
10. Repeat the same E2E plus power merge workflow.
11. Compare:
    - offered load vs RX throughput;
    - scheduler allocation shape;
    - average/min/max Outlet 2 active power;
    - stability and UE attach behavior.

## What Is Still Incomplete

The high-level workflow is complete enough to start, but the production-safe details are incomplete. Before modifying and deploying a custom scheduler image, ask Ming or inspect HPE for:

1. Should David build from a personal fork/branch or a BMW organization branch?
2. What `GIT_CREDENTIAL_ID` and `REGISTRY_CREDENTIAL_ID` should David use?
3. What registry namespace should David push to: personal namespace or a shared project namespace?
4. Does the VNF chart require an `imagePullSecret` change when using David's registry namespace?
5. Can David deploy custom VNF images in `ming-ns`, or should scheduler tests move to `david-ns`?
6. If using `david-ns`, are the required NADs and SR-IOV resources available there?
7. What is the rollback command to restore the known-good VNF image after a custom image test?
8. Which log level or config flag is needed so `LOG_I` / `LOG_D` scheduler logs are visible in `kubectl logs`?
9. What exact scheduler labels does the professor expect: `original`, `time-domain`, `frequency-domain`, or the more implementation-specific `original`, `prb_cap_27`, `single_ue_per_slot`?

## Current Recommendation

Yes, scheduler modification is the next technical step, but do it in this order:

1. logging-only custom OAI image;
2. short E2E validation;
3. long baseline run with scheduler logs;
4. PRB-cap behavior patch;
5. repeat E2E and power merge;
6. only then expand to stricter time-domain or multi-UE modes.

This avoids mixing three unknowns at once: custom source code, custom image deployment, and scheduler behavior changes.
