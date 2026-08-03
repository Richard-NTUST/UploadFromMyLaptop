# Daily Note

## Date

**Date:** 2026/07/08

---

## Short-term Goal

Validate the OCloud E2E artifact path at higher offered loads, identify the failure boundary, and prepare the rApp for Docker deployment without replacing the currently running host process.

### Goal 1: Validate OCloud throughput sweep behavior

* Milestone 1: Run a multi-step offered-load sweep through `/gnb/run`, Due 2026/07/08
* Milestone 2: Identify where the OCloud path becomes unstable, Due 2026/07/08
* Milestone 3: Confirm a clean sanity run still produces CSV and plot artifacts, Due 2026/07/08

### Goal 2: Prepare Docker containerization plan

* Milestone 1: Confirm the two configurable server roles, Due 2026/07/08
* Milestone 2: Keep the current host rApp untouched while preparing Docker files, Due 2026/07/08
* Milestone 3: Define configurable defaults for the runner host and UE-control host, Due 2026/07/08

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Run full offered-load sweep attempt | OCloud validation | Determine whether 100-1000 Mbps completes | | Job `62eee274-37a4-4448-8e67-794a1bd46e4e` |
| P2 | Recover and isolate failure | OCloud validation | Identify high-load/iPerf cleanup issue and recover UE/iPerf state | | Job output and cleanup commands |
| P3 | Run clean short sanity test | Artifact validation | Confirm CSV and plot generation after cleanup | | Job `0845ea8a-e98f-4674-8da0-5eeb313ec74b` |
| P4 | Confirm second server identity | Docker preparation | Treat Server 2 as UE-control host, not Lavoisier/OCloud | | Confirmed conversation context |
| P5 | Draft Docker deployment bundle | Docker preparation | Dockerfile, compose, env example, and deployment notes | | `docs/Deployment/winlab_e2e_rapp_docker/` |

Before starting work:

* [x] Do not kill or replace the current host rApp.
* [x] Treat Docker as a side-by-side deployment on a separate API port first.
* [x] Make both the runner host and UE-control host configurable.
* [x] Keep final throughput-vs-power blocked until Outlet 2 active_power export is available.

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Run full offered-load sweep attempt | Partial | | Job `62eee274-37a4-4448-8e67-794a1bd46e4e` reached the 900 Mbps step and was stopped |
| Recover and isolate failure | Complete | | Magic iPerf package force-stopped; host and UE iPerf cleanup performed |
| Run clean short sanity test | Complete | | Job `0845ea8a-e98f-4674-8da0-5eeb313ec74b` succeeded with CSV and plot artifacts |
| Confirm second server identity | Complete | | Server 2 confirmed as UE-control side: `iapc` / Android UE path |
| Draft Docker deployment bundle | Complete locally | | Docker bundle prepared under `docs/Deployment/winlab_e2e_rapp_docker/` |

### Progress Summary

The 100-1000 Mbps OCloud sweep started correctly through the rApp:

```text
Job ID: 62eee274-37a4-4448-8e67-794a1bd46e4e
Mode: ocloud
Bandwidths: 100,200,300,400,500,600,700,800,900,1000 Mbps
Period: 60 s
Gap: 2 s
UE IP: 10.45.0.9
```

The sweep reached the 900 Mbps step and stalled. It was stopped by terminating the inner `cloud_e2e.py` path, allowing the wrapper to save partial artifacts:

```text
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260708-025454
Return code: -15 inside wrapper summary
UE iPerf samples: 540
Generated: iperf_timeseries.csv, iperf_throughput.png, offered_load_throughput.csv, offered_load_throughput.png
```

A follow-up 100-800 Mbps run completed at the E2E level, but did not produce throughput plots because the pulled UE JSON was an iPerf error JSON with no intervals:

```text
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260708-033419
E2E status: succeeded
UE iPerf samples: 0
Problem: UE iPerf JSON contained no intervals
```

After cleanup, a short 100 Mbps sanity test passed cleanly:

```text
Job ID: 0845ea8a-e98f-4674-8da0-5eeb313ec74b
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260708-040533
UE IP: 10.45.0.10
Target bitrate: 100 Mbps
Duration: 20 s
Loss: 0/185888, 0%
UE iPerf samples: 20
Generated: iperf_timeseries.csv, iperf_throughput.png, offered_load_throughput.csv, offered_load_throughput.png
```

The Dockerization discussion clarified the two-server flow:

```text
Server 1: HPE / rApp / OCloud runner
Server 2: iapc / UE-control host / Android ADB and Magic iPerf path
```

Docker deployment files were drafted locally under:

```text
docs/Deployment/winlab_e2e_rapp_docker/
```

The Docker deployment is designed to run beside the current host rApp, not replace it:

```text
Current host rApp: 127.0.0.1:9090
Containerized rApp default: 127.0.0.1:19090
```

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Apply Docker files on HPE | SSH from this workspace was denied | Copy the bundle into `/home/hpe/winlab_e2e_rapp` once HPE access works |
| Add API-level `iperf_bind` passthrough | Needed to make runner-side server IP fully configurable | Add `iperf_bind` to `/gnb/run`, wrapper args, and `cloud_e2e.py --iperf-bind` call |
| Re-run clean 100-800 sweep | Needed for clean official offered-load plot | Run after sanity pass, with UE/iPerf cleanup if needed |
| Export Outlet 2 active_power | Required for throughput-vs-power analysis | Ravi/InfluxDB export permission remains needed |

### Today's Biggest Lesson

```text
The rApp artifact path works, but high-load sweeps expose UE/iPerf state issues.
Containerization must model two hosts explicitly: the HPE runner and the iapc/UE-control
host. Docker should first run beside the current rApp on a separate port, not replace it.
```

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Apply Docker bundle on HPE without stopping current rApp | Containerization | Containerized rApp reachable on `127.0.0.1:19090` |
| P2 | Add `iperf_bind` passthrough to rApp request path | Full runner configurability | `/gnb/run` can configure the local UPF/ogstun bind address |
| P3 | Re-run clean 100-800 OCloud sweep | Baseline throughput evidence | Clean offered-load CSV/PNG from 100 to 800 Mbps |
| P4 | Request/export Outlet 2 active_power | Power alignment | Timestamped power CSV for the matched iPerf window |
