# 2026-07-21 OAI Scheduler Log-Only Branch and Build Plan

## Goal

Prepare the first low-risk OAI scheduler modification branch for WINLAB testing. This version does not change scheduling behavior yet. It only adds downlink scheduler allocation logs so we can verify the build, deploy, and rApp measurement loop before touching scheduling policy.

## Branch Created

Repository used on HPE:

```bash
/home/hpe/oaiopenairinterface5g-ready-to-push
```

Branch:

```bash
david/oai-scheduler-logonly-20260721
```

Base branch:

```bash
bmw/nfapi-DelayManagement
```

Base commit observed after fetch:

```text
5bbf48af2d fix(nfapi/vnf): cleanly stop and join VNF timing thread on shutdown
```

Note: older workflow notes referenced Jenkins build #87 at commit `9522317237738e3c4d1f4e006dc3b27faf5904b5`, but that exact SHA was not reachable after refreshing the BMW remote. The current BMW branch head has the same shutdown-fix commit message and was used as the practical baseline.

New commit:

```text
31c7aa0477586643a7acdae9c316c61c1ba0cdbf chore(winlab): add DL scheduler allocation log
```

The branch was pushed to BMW GitHub:

```text
https://github.com/bmw-ece-ntust/openairinterface5g/pull/new/david/oai-scheduler-logonly-20260721
```

## Code Change

Changed file:

```text
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c
```

Added log marker:

```text
[WINLAB_SCHED_LOG]
```

Fields logged from the downlink scheduler allocation path:

```text
mode=oai_logging_only
frame
slot
rnti
is_retx
rbStart
rbSize
mcs
tbs
layers
harq_pid
beam
tda
symbol start/count
```

Purpose: once the custom image is running in `ming-ns`, pod logs can confirm that the scheduler path being tested is the modified binary, while the throughput/power behavior should remain equivalent to baseline.

## Jenkins Build

Jenkins job:

```text
https://jenkins.bmw.lab/job/ming-nfapi-Fronthaul72-e2e/
```

Build parameters to use in Jenkins UI:

```text
GIT_REPO=https://github.com/bmw-ece-ntust/openairinterface5g
GIT_BRANCH=david/oai-scheduler-logonly-20260721
GIT_CREDENTIAL_ID=ming_gh_token
QUAY_REPO=bmw.ece.ntust.edu.tw/minghong
TAG=david-oai-scheduler-logonly-20260721
REGISTRY_CREDENTIAL_ID=ming_account
E2AP_VERSION=E2AP_V3
KPM_VERSION=KPM_V3_00
```

Codex could read Jenkins job metadata, but triggering a build through the API failed with HTTP 403 because Jenkins requires an authenticated session/API token for `buildWithParameters`. Use the Jenkins web UI for now, or provide an authenticated API path later.

Expected image after a successful Jenkins build:

```text
bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-scheduler-logonly-20260721
```

## Deploy to ming-ns

Use `ming-ns` for this first test to avoid changing namespace image pull secrets.

Deploy the new VNF image after Jenkins pushes it:

```bash
/home/linuxbrew/.linuxbrew/bin/helm upgrade --install vnf /home/hpe/CRAN/ocloud-helm-templates/oai-vnf \
  -n ming-ns \
  -f /home/hpe/CRAN/ocloud-helm-templates/oai-vnf/values.yaml \
  --set nfimage.repository=bmw.ece.ntust.edu.tw/minghong/oai-gnb \
  --set nfimage.version=david-oai-scheduler-logonly-20260721
```

Confirm rollout:

```bash
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml rollout status deploy/oai-vnf -n ming-ns --timeout=180s
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml get pods -n ming-ns -o wide | grep -E 'oai-vnf|oai-pnf'
```

Confirm the image tag:

```bash
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml describe pod -n ming-ns -l app.kubernetes.io/name=oai-vnf | grep -i 'Image:'
```

## Smoke Test

Run a short rApp smoke test first:

```bash
curl -X POST http://127.0.0.1:19090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ocloud",
    "server": "hpe",
    "target_identity": "hpe-pegatron-ru-o",
    "ue_serial": "R5CN30TMBYR",
    "iapc_host": "sshuser@140.118.162.81",
    "iapc_port": 24,
    "bandwidth": [100],
    "period": 60,
    "gap_time": 2,
    "ue_model": "samsung",
    "uplink": false,
    "settle_time": 30,
    "attach_timeout": 300,
    "keep_ue_online_on_failure": true
  }'
```

Then poll:

```bash
curl http://127.0.0.1:19090/jobs/<job_id>
```

Check scheduler log marker:

```bash
/home/hpe/CRAN/kubectl --kubeconfig=/home/hpe/CRAN/ming-kubeconfig.yaml logs -n ming-ns deploy/oai-vnf --tail=200 | grep WINLAB_SCHED_LOG
```

## Rollback

Rollback VNF to the known current tag:

```bash
/home/linuxbrew/.linuxbrew/bin/helm upgrade --install vnf /home/hpe/CRAN/ocloud-helm-templates/oai-vnf \
  -n ming-ns \
  -f /home/hpe/CRAN/ocloud-helm-templates/oai-vnf/values.yaml \
  --set nfimage.repository=bmw.ece.ntust.edu.tw/minghong/oai-gnb \
  --set nfimage.version=latest
```

## Next Step

1. Trigger Jenkins build with the branch and tag above.
2. Deploy the produced image to `ming-ns` VNF only.
3. Run a 60-second smoke test and confirm `[WINLAB_SCHED_LOG]` appears in VNF logs.
4. If the smoke test passes, run a longer 20-minute or 1-hour rApp test and merge with PDU power data.
