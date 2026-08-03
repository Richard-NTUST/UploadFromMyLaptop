# HPE Docker Runbook for WINLAB E2E rApp

This is the command checklist for preparing Docker on the HPE server and then running the containerized rApp beside the current host rApp.

Current constraint:

```text
docker: command not found
```

So Docker is not installed or not available in the current `hpe` user's PATH yet.

## 0. Confirm Host Context

Run on HPE:

```bash
hostname
whoami
pwd
uname -a
cat /etc/os-release
```

Expected:

```text
user: hpe
host: hpe-ProLiant-DL380-Gen10
project: /home/hpe/winlab_e2e_rapp
```

## 1. Check Whether Docker Exists Somewhere

Run:

```bash
command -v docker
command -v docker-compose
command -v docker-compose-v2
ls -la /usr/bin/docker /usr/local/bin/docker /snap/bin/docker 2>/dev/null
systemctl status docker --no-pager
```

If every command says Docker is missing, install Docker.

## 2. Install Docker

Use the Ubuntu/Debian path if HPE is Ubuntu/Debian.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Add the Docker apt repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install Docker Engine and Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Start Docker:

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

## 3. Give `hpe` Docker Permission

Run:

```bash
sudo usermod -aG docker hpe
```

Then log out and log back in to HPE, or run:

```bash
newgrp docker
```

Verify:

```bash
docker ps
docker compose version
```

If this works without `sudo`, Docker is ready for the rApp work.

## 4. Preserve Current rApp

Do not stop the current host rApp.

Verify current API:

```bash
curl http://127.0.0.1:9090/health
pgrep -af "uvicorn|winlab_e2e_rapp|hpe_scripts"
```

Docker will use:

```text
127.0.0.1:19090
```

The current host rApp should remain on:

```text
127.0.0.1:9090
```

## 5. Copy Docker Bundle Into rApp Root

From the HPE project root:

```bash
cd /home/hpe/winlab_e2e_rapp
cp docs/Deployment/winlab_e2e_rapp_docker/Dockerfile .
cp docs/Deployment/winlab_e2e_rapp_docker/docker-compose.yml .
cp docs/Deployment/winlab_e2e_rapp_docker/requirements-container.txt .
cp docs/Deployment/winlab_e2e_rapp_docker/.env.example .env
```

Edit `.env` locally:

```bash
nano .env
```

Set only local secrets there:

```text
IAPC_PASS=<local UE-control password>
```

Do not commit `.env`.

## 6. Build and Start Containerized rApp

Run:

```bash
cd /home/hpe/winlab_e2e_rapp
docker compose up -d --build
docker compose ps
docker compose logs --tail=80 winlab-e2e-rapp
```

Check API:

```bash
curl http://127.0.0.1:19090/health
```

## 7. Smoke Test OCloud Path

Use a short run first:

```bash
curl -X POST http://127.0.0.1:19090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ocloud",
    "server": "hpe",
    "target_identity": "hpe-pegatron-ru-o",
    "ue_serial": "R5CN30TMBYR",
    "iapc_host": "iapc",
    "iapc_port": 24,
    "bandwidth": [100],
    "period": 20,
    "gap_time": 2,
    "ue_model": "samsung",
    "uplink": false,
    "settle_time": 30,
    "attach_timeout": 300,
    "keep_ue_online_on_failure": true
  }'
```

Poll the returned job:

```bash
curl http://127.0.0.1:19090/jobs/<JOB_ID>
```

Expected artifact files:

```text
summary.json
request.json
command.json
command.txt
e2e_stdout.log
iperf-UE-RX.log
iperf_timeseries.csv
iperf_throughput.png
offered_load_throughput.csv
offered_load_throughput.png
ocloud_pod_logs/
```

## 8. If UE iPerf Gets Stale

Clean host iPerf:

```bash
sudo pkill -9 iperf3 || true
pgrep -af iperf3
```

Force-stop Magic iPerf on the UE:

```bash
sshpass -p "$IAPC_PASS" ssh -p 24 iapc \
  'adb -s R5CN30TMBYR shell "am force-stop com.nextdoordeveloper.miperf.miperf; rm -f /data/local/tmp/iperf3_log.json"'
```

Then rerun the short smoke test.

## 9. Stop Only the Docker rApp

This does not stop the current host rApp on port `9090`.

```bash
cd /home/hpe/winlab_e2e_rapp
docker compose down
```

## 10. Remaining Code Follow-Up

Before Docker is fully portable across runner hosts, add API passthrough for:

```text
iperf_bind
```

Needed path:

```text
GNBRunRequest.iperf_bind
/gnb/run command builder
run_e2e_with_artifacts.py --iperf-bind
cloud_e2e.py --iperf-bind <value>
```

`cloud_e2e.py` already supports `--iperf-bind`; the rApp request path still needs to expose and pass it.
