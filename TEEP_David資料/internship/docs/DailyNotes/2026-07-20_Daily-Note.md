# Daily Note

## Date

**Date:** 2026/07/20

---

## Short-term Goal

Validate a longer Dockerized OCloud E2E run, harden the long-run merge logic, and merge the throughput artifact with matching Outlet 2 PDU active-power data.

### Goal 1: Validate long-run OCloud execution

* Milestone 1: Prepare VNF/PNF, UE, and iPerf state, Due 2026/07/20
* Milestone 2: Run a longer 200 Mbps OCloud E2E test through the Dockerized rApp, Due 2026/07/20

### Goal 2: Prepare final throughput-power merge

* Milestone 1: Preserve the completed run artifact snapshot, Due 2026/07/20
* Milestone 2: Update merge script window selection for long-run artifacts, Due 2026/07/20
* Milestone 3: Export matching Outlet 2 `active_power` data and run merge, Due 2026/07/20

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | -------------- | ---------------- |
| P1 | Prepare OCloud E2E environment | Goal 1 | Ready PNF/VNF and clean iPerf state | | Pod status and preflight checks |
| P1 | Run long 200 Mbps OCloud test | Goal 1 | Successful rApp job and artifact directory | | Job `3bb047b9-2b21-48b5-bc3b-d66f2a79dcba` |
| P2 | Analyze throughput artifacts | Goal 2 | Throughput sample summary | | `iperf_timeseries.csv` and `offered_load_throughput.csv` |
| P2 | Harden merge script | Goal 2 | Actual interval window selection | | `scripts/merge_winlab_e2e_power.py` |
| P3 | Export PDU data and run merge | Goal 2 | `power_throughput_summary_20260720_061120.csv` | | `pdu_data_20260720_061120_064208.csv` and merged summary |

---

## Review

| Task | Status | Actual Time | Evidence |
| ---- | ------ | ----------- | -------- |
| Prepare OCloud E2E environment | Complete | | PNF/VNF Running and Ready before the run |
| Run long 200 Mbps OCloud test | Complete | | Job `3bb047b9-2b21-48b5-bc3b-d66f2a79dcba` succeeded |
| Analyze throughput artifacts | Complete | | Local artifact snapshot under `runs/hpe_artifacts/e2e-ocloud-20260720-061120` |
| Harden merge script | Complete | | `merge_winlab_e2e_power.py` now prefers actual iPerf interval duration |
| Export PDU data and run merge | Complete | | `power_throughput_summary_20260720_061120.csv` |

### Progress Summary

The Dockerized rApp completed a longer OCloud run through `127.0.0.1:19090`:

```text
Job: 3bb047b9-2b21-48b5-bc3b-d66f2a79dcba
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260720-061120
Target: hpe-pegatron-ru-o
UE serial: R5CN30TMBYR
Offered load: 200 Mbps
Started UTC: 2026-07-20T06:11:20.657146Z
Finished UTC: 2026-07-20T06:42:08.218506Z
Captured UE samples: 1676
Average RX throughput: 199.892 Mbps
```

The run confirms that the watchdog changes prevent the long-run endpoint from hanging indefinitely. The important caveat is that the submitted one-hour request produced about 1676 captured one-second UE samples, so it should be treated as a successful long-run stability test rather than a strict 3600-second evidence window.

The merge script was updated so it uses actual captured iPerf interval duration when intervals exist. This avoids selecting PDU samples across a requested duration that is longer than the real traffic evidence.

Final throughput-power merge result:

```text
Output: power_throughput_summary_20260720_061120.csv
Offered load: 200 Mbps
Average RX throughput: 199.892 Mbps
Average Outlet 2 active power: 40.097 W
Min/Max Outlet 2 active power: 38.03 W / 41.58 W
PDU samples inside window: 31
```

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Confirm strict one-hour behavior | The long request finalized before 3600 captured samples | Use repeated 20-minute windows or investigate UE-side iPerf early termination |

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Decide long-run experiment shape | Baseline quality | One strict one-hour run or repeated 20-minute windows |
| P2 | Repeat merged run at another offered load | Baseline quality | Additional throughput-power CSV row |
