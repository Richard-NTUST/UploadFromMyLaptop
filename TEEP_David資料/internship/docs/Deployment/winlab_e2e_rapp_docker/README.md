# WINLAB E2E rApp Docker Bundle

This bundle is meant to be copied into `/home/hpe/winlab_e2e_rapp` on the HPE server after the live source tree is backed up. It does not replace or stop the current host rApp by default.

## Server Roles

Server 1 is the rApp/E2E runner:

```text
Default: hpe@192.168.8.26
Runs: rApp API, cloud_e2e.py, kubectl checks, local iperf3 server on ogstun
Default API: 127.0.0.1:19090 for Docker, leaving 127.0.0.1:9090 untouched
Default iperf bind: 10.45.0.1
```

Server 2 is the UE-control host:

```text
Default: iapc:24
Runs: ADB control, Magic iPerf app control, UE-side iperf client, UE JSON pull
Default UE serial: R5CN30TMBYR
Default Magic iPerf package: com.nextdoordeveloper.miperf.miperf
Password: set locally through IAPC_PASS in .env; do not commit it
```

## Install Beside Current rApp

From `/home/hpe/winlab_e2e_rapp`:

```bash
cp docs/Deployment/winlab_e2e_rapp_docker/Dockerfile .
cp docs/Deployment/winlab_e2e_rapp_docker/docker-compose.yml .
cp docs/Deployment/winlab_e2e_rapp_docker/requirements-container.txt .
cp docs/Deployment/winlab_e2e_rapp_docker/.env.example .env
```

Edit `.env` and set `IAPC_PASS` locally.

Build and run the containerized API on port `19090`:

```bash
docker compose up -d --build
curl http://127.0.0.1:19090/health
```

The existing host rApp on `127.0.0.1:9090` should remain running.

## Test Command

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

## Required Code Follow-Up

The current rApp already accepts per-run UE-control fields:

```text
ue_serial
iapc_host
iapc_port
```

The Docker environment also defines `WINLAB_E2E_IPERF_BIND`, but the API should expose and pass this as `iperf_bind` before Docker is considered fully portable across lab runner hosts. `cloud_e2e.py` already supports `--iperf-bind`; the missing part is passing it through `/gnb/run` and `run_e2e_with_artifacts.py`.

Recommended API addition:

```text
GNBRunRequest.iperf_bind: str = "10.45.0.1"
run_e2e_with_artifacts.py --iperf-bind
command_for(ocloud) -> cloud_e2e.py --iperf-bind <value>
```
