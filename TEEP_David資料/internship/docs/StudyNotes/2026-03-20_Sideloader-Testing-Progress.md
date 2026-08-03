# Sideloader Service Testing Progress (Local Validation)

**Date:** 2026-03-20  
**Source Repo:** `External/sideloaderService/nino-sideloader-service/`  
**Related Report:** `runs/current_sweep/sideloader_api_test_report_2026-03-20.md`

---

## 1) Objective

Run active local testing of the Sideloader Service endpoints in a non-destructive way, verify service startup and API behavior, and classify outcomes into:
- Functional
- Expected / environment-limited
- Needs review
- Known defect (deferred)

---

## 2) Environment Used

- Host OS: Linux (local laptop/workstation)
- Python virtual environment created at project root: `venv/`
- Installed dependencies include: Flask, requests, pyyaml, kubernetes, paramiko, numpy
- Service launch mode: local Flask (`app.py`) with test env vars
  - `SVC_PORT=8080`
  - `RAPP_URL=http://127.0.0.1:5999` (dummy/offline for local-only run)
  - `NODE_NAME=local-test`

---

## 3) What Was Executed Today

1. **Code sanity check**
   - `python -m compileall .` inside sideloader repo
   - Result: pass (all modules compiled)

2. **Service startup validation**
   - Launched local app from `app.py`
   - Health endpoint check succeeded: `GET /health -> 200`

3. **Comprehensive endpoint sweep (non-destructive)**
   - Declared routes in app: **33**
   - Tested routes: **32**
   - Coverage: **32/33**
   - Intentionally untested: `POST /ptp/inject_fault` (disruptive by design)

---

## 4) Results Summary

From `runs/current_sweep/sideloader_api_test_report_2026-03-20.md`:

- **Successful:** 18
- **Expected fail / environment-limited:** 13
- **Code fail:** 1
- **Needs review:** 0

### Successful endpoints (main highlights)
- `GET /health`
- `GET /cpu/governor`
- `GET /cpu/idle_states`
- `GET /memory/oom_check`
- `GET /disk/usage`
- `GET /irq/affinity`
- `GET /stress/status`
- `GET /ptp/comprehensive`
- `POST /cpu/monitor`
- `POST /cpu/context_switches`
- `POST /memory/monitor`
- `POST /hugepages/monitor`
- `POST /disk/monitor`
- `POST /perf/context_switches`
- `POST /power/monitor`
- `POST /network/monitor`
- `POST /network/link_down`
- `POST /stress/kill`

### Expected fail / environment-limited endpoints
- `GET /dpdk/status` -> 404 (`no DPDK devices found`)
- `GET /ptp/time_properties` -> 200 with error (`pmc command failed`)
- `GET /ptp/current_data` -> 200 with error (`pmc command failed`)
- `GET /ptp/parent_data` -> 200 with error (`pmc command failed`)
- `GET /ptp/port_state` -> 200 with error (`pmc command failed`)
- `POST /ptp/monitor` -> 200 with error (`no samples collected`)
- `POST /ptp/status` -> 200 with error (`pmc failed`)
- `POST /process/threads` -> 200 with error (`no samples collected`)
- `POST /process/affinity` -> 404 (`no process matching nr-softmodem`)
- `POST /perf/sched_latency` -> 200 with error (`failed to collect latency data`)
- `POST /network/vlan_fault` -> 400 (`interface required`, validation path)
- `POST /stress/memory` -> 400 (`unknown stress type: invalid`, validation path)
- `POST /stress/cpu` -> 400 (`unknown stress type: invalid`, validation path)

### Code-fail endpoint
- `POST /power/ipmi` -> 500 (ImportError: missing `IPMIPowerCollector` symbol)

---

## 5) Known Issue (Deferred)

- **Endpoint:** `POST /power/ipmi`
- **Observed:** HTTP 500
- **Reason:** Import error for missing `IPMIPowerCollector` in `collectors/power.py`
- **Status for now:** **Deferred by request** (documented, not fixed in this session)

---

## 6) Interpretation for Project Progress

Today confirms that:
1. The Sideloader service now runs reliably in local mode for most read-only monitoring paths.
2. Previously error-prone monitor endpoints now return structured data for CPU/memory/disk/network/power baseline paths.
3. Remaining non-500 failures are mostly environment/tooling dependent (PTP stack, DPDK devices, `nr-softmodem`, perf constraints, or validation payloads).
4. One concrete server-side defect remains tracked: `POST /power/ipmi`.

---

## 7) Reproducible Runbook (Start → Test → Check)

### A. Start

```bash
cd ~/Videos/TEEP
source venv/bin/activate

python External/sideloaderService/nino-sideloader-service/app.py
```

If needed, launch with explicit env vars:

```bash
SVC_PORT=8080 RAPP_URL=http://127.0.0.1:5999 NODE_NAME=local-test \
python External/sideloaderService/nino-sideloader-service/app.py
```

### B. Test (quick)

```bash
curl -sS http://127.0.0.1:8080/health
curl -sS http://127.0.0.1:8080/cpu/governor
curl -sS -H 'Content-Type: application/json' \
  -d '{"duration":1,"include_timeseries":false}' \
  http://127.0.0.1:8080/power/monitor
```

### C. Test (thorough, non-destructive)

Use the same endpoint sweep script approach as today (GET + safe POST monitor calls), excluding:
- `POST /ptp/inject_fault`
- destructive stress/fault runs on real interfaces/services

### D. Check results

1. Confirm service alive:
```bash
curl -sS http://127.0.0.1:8080/health
```
2. Review endpoint report:
```bash
cat runs/current_sweep/sideloader_api_test_report_2026-03-20.md
```
3. Classify outcomes by category:
- Functional
- Expected/environment-limited
- Needs review
- Deferred known defect (`/power/ipmi`)

---

## 8) Next Suggested Session

- Re-run the same sweep in Kubernetes/privileged pod context where host namespaces, PTP utilities, and target processes exist.
- Keep `/power/ipmi` tracked as known defect until implementation decision is made.
