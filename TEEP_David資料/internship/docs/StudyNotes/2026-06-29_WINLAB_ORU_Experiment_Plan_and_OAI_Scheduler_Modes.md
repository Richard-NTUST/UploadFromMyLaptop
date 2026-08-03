---
title: WINLAB / Pegatron O-RU Experiment Plan and OAI Scheduler Mode Draft
---

# WINLAB / Pegatron O-RU Experiment Plan and OAI Scheduler Mode Draft

**Date:** June 29, 2026  
**Purpose:** Prepare the baseline experiment plan, CSV formats, and tentative OAI scheduler mode design while waiting for Ming and Chynna's guidance.  
**Scope:** This note is a working plan. The scheduler definitions must be confirmed with Prof. Ray / Ming before implementation.

---

## 1. Why Not Start with Local StarlingX AIO-Simplex

Installing StarlingX AIO-Simplex locally is not the best waiting task unless the team confirms the WINLAB/rApp test depends on a local O-Cloud sandbox.

Reasons:

- The professor's current goal is OAI scheduler + Pegatron RU + CortexDC/PDU power measurement.
- A local STX install will not match the lab server, RU, PDU, timing, or CortexDC path.
- It can consume one or more days and pull the work back into infrastructure setup.
- The useful immediate work is to prepare the experiment schema, scheduler modes, and OAI patch/logging plan so the team responses can be acted on quickly.

Keep STX AIO-Simplex as an optional sandbox only if:

- Ming says the Test Automation rApp must be tested locally first.
- The lab O-Cloud is unavailable and a dry-run deployment target is needed.
- The OKD/STX setup team asks for a specific local reproduction.

---

## 2. Current Lab Clues from Local Repos

### Pegatron Test Cases in rApp

The local rApp repo already contains Pegatron test cases under:

```text
External/rApp/rapp-cicd-ocloud/test_cases/
```

Relevant Pegatron/Joule test cases:

| Test case | Architecture | Target | Sweep variables | Runtime defaults |
|---|---|---|---|---|
| `f1-pegatron-joule-cpu-bandwidth` | F1 split, CU/DU | Pegatron O-RU on Joule | `wr_isolcpus: [8,14]`, `iperf_bandwidth_mbps: [100,400,700]` | `runsPerCase: 1`, `stabilizationTime: 30`, `iperfDuration: 60` |
| `mono-pegatron-joule-cpu-bandwidth` | Monolithic gNB | Pegatron O-RU on Joule | `wr_isolcpus: [8,14]`, `iperf_bandwidth_mbps: [100,400,700]` | `runsPerCase: 1`, `stabilizationTime: 30`, `iperfDuration: 60` |
| `nfapi-pegatron-joule-cpu-bandwidth` | nFAPI split, PNF/VNF | Pegatron O-RU on Joule | `wr_isolcpus: [8,10]`, `iperf_bandwidth_mbps: [100,400,700]` | `runsPerCase: 1`, `stabilizationTime: 30`, `iperfDuration: 60` |

Important: the raw YAML files include private repository URLs and credentials. Do not copy those into public notes, reports, or screenshots.

### rApp Metric Collection Behavior

The rApp function `fetch_sideload_metrics()` collects metrics in parallel during each test run. It saves raw JSON dumps for:

- thread CPU,
- core CPU,
- memory,
- disk,
- hugepages,
- power,
- network,
- PTP.

The power path currently calls:

```text
POST <sideload_url>/power/monitor
```

The Sideloader service also exposes:

```text
POST /power/monitor
POST /power/ipmi
```

The `/power/monitor` path uses RAPL and optional iDRAC/Redfish. The `/power/ipmi` path uses `ipmitool dcmi power reading`.

For the professor's final target, Chynna's CortexDC/PDU path is still the critical ground-truth source. The Sideloader power path is useful as a secondary or parallel source if the team wants it.

---

## 3. Experiment Goals

### Goal A - Baseline Replication

Reproduce the existing Pegatron RU E2E throughput-power result with the original OAI scheduler.

Deliverable:

```text
X-axis: E2E throughput
Y-axis: Pegatron RU power consumption
Curve: OAI original scheduler
```

### Goal B - Scheduler Comparison

Compare original OAI against time-domain and frequency-domain scheduler variants.

Deliverable:

```text
X-axis: E2E throughput
Y-axis: Pegatron RU power consumption
Curves:
  - OAI original scheduler
  - OAI time-domain scheduler
  - OAI frequency-domain scheduler
```

---

## 4. Tentative Experiment Matrix

### Phase 0 - Clarify Workflow

Before running anything:

| Topic | Ask |
|---|---|
| rApp test case | Which Pegatron test case should be treated as the thesis baseline? F1, monolithic, or nFAPI? |
| OAI deployment | Which OAI image/tag/branch is currently used for Pegatron? |
| Scheduler patch path | Should scheduler changes be a new image tag, Helm value, branch, or manual binary replacement? |
| Power source | Does CortexDC export RU power per test ID, per timestamp window, or via manual CSV? |
| Data alignment | What timestamp format and timezone does CortexDC use? |

### Phase 1 - Original OAI Baseline

Start with the existing test case and original OAI scheduler.

Suggested first baseline:

| Field | Tentative Value |
|---|---|
| O-RU | Pegatron |
| Node | Joule, unless Ming says Kepler |
| Architecture | Start with Ming's thesis architecture, likely F1 or monolithic |
| Scheduler mode | `oai_original` |
| Offered rates | Existing rApp sweep: `100, 400, 700 Mbps` |
| Runs | Existing: 1 per case; thesis-quality target: 3 per case |
| Stabilization | Existing: 30 s; PDU-quality target may need >=120 s |
| Traffic duration | Existing: 60 s; PDU-quality target may need >=300 s |
| Power source | CortexDC/PDU ground truth, plus Sideloader/RAPL/IPMI if available |

Reason for longer target durations:

- POET-style PDU sampling is often about 10 s.
- IPMI/BMC values can take around 60 s to stabilize.
- A 60 s run can work for a smoke test, but a 5 min steady-state window is more defensible for final plots.

### Phase 2 - Baseline Data-Rate Sweep

Run original OAI scheduler across offered rates and collect:

- offered bitrate,
- measured E2E throughput,
- RU power,
- optional PRB utilization,
- optional OAI MAC allocation logs.

Initial sweep options:

| Sweep | Offered Rate Points | Use |
|---|---|---|
| rApp existing | `100, 400, 700 Mbps` | Matches local test case definitions |
| POET anchors | `65, 84 Mbps` or equivalent per-UE split | Aligns with WINLAB / POET reported scenarios |
| Dense curve | `0, 50, 100, 200, 400, 700 Mbps` | Better regression and curve shape |

Do not mix all sweeps in the first run. Start with the rApp existing sweep, then add POET anchor points once the pipeline works.

### Phase 3 - Scheduler Logging Validation

Before changing scheduler behavior, add or enable logging to prove what OAI allocates.

Minimum scheduler log fields:

| Field | Why |
|---|---|
| frame, slot | Align scheduler decisions with traffic and power windows |
| RNTI | Identify UE |
| scheduler_mode | Distinguish original/time/frequency runs |
| rbStart | Frequency placement |
| rbSize | PRB allocation size |
| MCS | Throughput/TBS interpretation |
| TBS | Transport bytes per grant |
| nrOfLayers | MIMO effect |
| beam index | Multi-beam sanity check if relevant |

### Phase 4 - Scheduler Variant Runs

After definitions are confirmed, run the same data-rate sweep for each scheduler mode.

Target comparison:

| Mode | Status | Expected code behavior |
|---|---|---|
| `oai_original` | Required baseline | Existing PF scheduler |
| `oai_time_domain` | Tentative | Schedule fewer UEs per slot or rotate UEs across slots |
| `oai_frequency_domain` | Tentative | Keep same-slot frequency sharing / wide PRB grants |
| `oai_prb_cap_27` | Optional diagnostic | Cap per-grant RB size to about 27 RBs |

---

## 5. OAI Scheduler Code Path Verified Locally

Local source tree:

```text
OAI/openairinterface5g/openair2/LAYER2/NR_MAC_gNB/
```

Important files:

| File | Role |
|---|---|
| `gNB_scheduler.c` | Top-level per-slot scheduler entry |
| `gNB_scheduler_dlsch.c` | DL scheduler, including `pf_dl()` and `nr_dlsch_preprocessor()` |
| `gNB_scheduler_primitives.c` | `nr_find_nb_rb()` and related scheduler helpers |

### Current OAI DL Flow

Verified local flow in `gNB_scheduler_dlsch.c`:

```text
nr_dlsch_preprocessor()
  - sets n_rb_sched[i] = carrier bandwidth
  - computes max_sched_ues from bandwidth / CCE estimate
  - calls pf_dl()

pf_dl()
  - updates EWMA throughput: UE->dl_thr_ue = (1-a) old + a current_bytes
  - computes PF coefficient from hypothetical TBS / historical throughput
  - sorts UEs by coefficient
  - finds free contiguous RB block in rballoc_mask[]
  - calls nr_find_nb_rb() to choose rbSize
  - calls post_process_dlsch()
  - marks rballoc_mask[] for allocated RBs
```

Important local line anchors:

- `pf_dl()` starts at `gNB_scheduler_dlsch.c:610`.
- EWMA throughput uses `a = 0.01f` at `gNB_scheduler_dlsch.c:643`.
- `min_rbSize = 5` at `gNB_scheduler_dlsch.c:734`.
- Frequency allocation block search is around `gNB_scheduler_dlsch.c:786-791`.
- `nr_find_nb_rb()` is called around `gNB_scheduler_dlsch.c:869-879`.
- `nr_dlsch_preprocessor()` computes `max_sched_ues` around `gNB_scheduler_dlsch.c:894-915`.
- `nr_find_nb_rb()` is defined in `gNB_scheduler_primitives.c:637-697`.

### What `nr_find_nb_rb()` Does

`nr_find_nb_rb()` receives:

- modulation order,
- code rate,
- number of layers,
- OFDM symbols,
- DMRS overhead,
- bytes to transport,
- minimum RB count,
- maximum RB count.

It returns:

- TBS in bytes,
- chosen RB count.

Behavior:

- If max RBs cannot fit all bytes, it returns false but leaves `nb_rb = nb_rb_max`.
- If min RBs are enough, it returns min RBs.
- Otherwise it binary-searches for the smallest RB count that fits the bytes.

This means `max_rbSize` is a strong cap: if the scheduler caps `max_rbSize` at 27, OAI cannot allocate more than 27 RBs for that grant.

---

## 6. Tentative OAI Scheduler Modes

These mode definitions are drafts. They should be confirmed before code changes.

### Mode 0 - `oai_original`

No code change.

Behavior:

- Existing OAI proportional-fair behavior.
- Multiple UEs can be scheduled in one slot if PDCCH/RB resources allow.
- Each UE receives a contiguous RB range.
- This is the baseline curve.

What to log:

```text
mode=oai_original frame slot rnti rbStart rbSize mcs tbs
```

### Mode 1 - `oai_prb_cap_27`

Diagnostic / 27x10-style mode.

Implementation idea:

```c
max_rbSize = min(max_rbSize, 27);
```

Location:

```text
gNB_scheduler_dlsch.c
inside pf_dl()
after get_rb_alloc() sets max_rbSize
before nr_find_nb_rb()
```

Expected behavior:

- Each PDSCH grant is limited to about 27 RBs.
- Large buffers spill across more slots.
- This directly tests the 273x1 vs 27x10 concept.
- It may reduce instantaneous bandwidth and increase latency.

Risk:

- This is not necessarily "time-domain scheduler" in the strict one-UE-per-slot sense.
- It is a useful diagnostic mode even if the final label changes.

### Mode 2 - `oai_single_ue_per_slot`

Strict TDM-style mode.

Implementation idea:

```c
max_sched_ues = 1;
```

Location:

```text
gNB_scheduler_dlsch.c
inside nr_dlsch_preprocessor()
after default max_sched_ues calculation
before pf_dl()
```

Expected behavior:

- At most one UE gets new DL data in each slot.
- With enough buffer, that UE may receive a large contiguous RB grant.
- UE service alternates over time according to PF ordering.

Risk:

- With one UE, this may look similar to original OAI.
- With insufficient buffer, it can waste PRBs.
- It may not create empty slots unless traffic is burst-shaped.

### Mode 3 - `oai_frequency_domain`

Tentative label for a deliberate same-slot frequency-sharing behavior.

Potential interpretation:

- Keep multiple UEs schedulable per slot.
- Allow wide contiguous RB allocation.
- Preserve OAI's default PF/FDM behavior as the frequency-domain scheduler.

Possible implementation:

- No code change beyond logging and explicit mode labeling.
- Or set a high grant cap, e.g. full BWP, and allow `max_sched_ues > 1`.

Open question:

- If Prof. Ray expects a separately implemented "frequency-domain scheduler," then original OAI may not be enough. This must be clarified.

### Mode Selection Strategy

Do not hardcode multiple experimental patches manually if avoidable. Prefer one mode variable:

```text
OAI_SCHED_MODE=original
OAI_SCHED_MODE=prb_cap_27
OAI_SCHED_MODE=single_ue_per_slot
OAI_SCHED_MODE=frequency_domain
```

Possible implementation methods:

| Method | Pros | Cons |
|---|---|---|
| Environment variable | Easy in Kubernetes/Helm | Need to verify OAI process environment path |
| Config file parameter | Cleaner for deployment | Requires config parser work |
| Compile-time macro | Fastest patch | Requires separate images per mode |
| Hardcoded branch/image tag | Simple for first trial | Risk of confusion across experiments |

For the first proof, a compile-time macro or hardcoded image tag is acceptable. For repeatable thesis work, use an explicit runtime/config mode.

---

## 7. CSV Data Model

Use three levels of data:

1. Run summary: one row per experiment run.
2. Power time series: many rows per run.
3. Scheduler allocation log: many rows per run, one row per scheduled grant.

### 7.1 Run Summary CSV

Path template:

```text
runs/winlab_oru/<date>/run_summary.csv
```

Columns:

```csv
run_id,date_utc,test_case_id,architecture,node,oru_vendor,oru_id,scheduler_mode,scheduler_mode_impl,oai_image,oai_commit,ue_count,offered_rate_mbps,iperf_duration_s,stabilization_s,steady_state_start_utc,steady_state_end_utc,e2e_throughput_mbps_mean,e2e_throughput_mbps_p50,e2e_throughput_mbps_p95,prb_util_dl_pct_mean,ru_power_w_mean,ru_power_w_median,ru_power_w_p05,ru_power_w_p95,power_source,power_sample_interval_s,cortexdc_export_ref,rapp_exec_id,raw_power_file,raw_iperf_file,raw_scheduler_log,notes
```

Required fields for the final plot:

- `scheduler_mode`
- `e2e_throughput_mbps_mean`
- `ru_power_w_mean` or `ru_power_w_median`

### 7.2 Power Time-Series CSV

Path template:

```text
runs/winlab_oru/<date>/power_timeseries.csv
```

Columns:

```csv
run_id,timestamp_utc,source,power_w,voltage_v,current_a,energy_wh,energy_j,sample_interval_s,raw_source_ref,notes
```

Power source values:

- `cortexdc_pdu`
- `pdu_snmp`
- `sideloader_rapl`
- `sideloader_ipmi`
- `idrac_redfish`

Use `cortexdc_pdu` as the ground-truth source if available.

### 7.3 Scheduler Allocation CSV

Path template:

```text
runs/winlab_oru/<date>/scheduler_allocations.csv
```

Columns:

```csv
run_id,timestamp_utc,frame,slot,rnti,scheduler_mode,rb_start,rb_size,mcs,tbs_bytes,nr_of_layers,beam_idx,harq_pid,is_retx,dl_thr_ue,coeff_ue,notes
```

This CSV is for proving that the scheduler mode actually changed PRB allocation behavior.

### 7.4 UTC Markers

Path template:

```text
runs/winlab_oru/<date>/utc_markers.txt
```

Format:

```text
2026-06-29T00:00:00.000Z RUN_START run_id=run001 scheduler_mode=oai_original test_case=f1-pegatron-joule-cpu-bandwidth offered_rate_mbps=100
2026-06-29T00:00:30.000Z STABILIZATION_END run_id=run001
2026-06-29T00:05:30.000Z STEADY_END run_id=run001
2026-06-29T00:05:31.000Z RUN_STOP run_id=run001
```

---

## 8. Plot Plan

### Plot 1 - Baseline Original OAI

```text
X: e2e_throughput_mbps_mean
Y: ru_power_w_median
Curve: oai_original
```

Use this for milestone 1.

### Plot 2 - Scheduler Comparison

```text
X: e2e_throughput_mbps_mean
Y: ru_power_w_median
Curves:
  - oai_original
  - oai_time_domain
  - oai_frequency_domain
```

Use median power for the main plot if PDU/CortexDC has visible outliers. Include mean/p05/p95 in the table or error bars.

### Plot 3 - Scheduler Verification

```text
X: slot index or time
Y: rb_size
Color: scheduler_mode
Group: rnti
```

This is not necessarily for the professor's final plot, but it is important evidence that the code changed scheduling behavior.

---

## 9. Immediate To-Do While Waiting

1. Keep the DM questions open and wait for Ming/Chynna's workflow answers.
2. Do not request final data before understanding the workflow.
3. Prepare blank CSV files from the templates in `templates/`.
4. Read the active OAI commit or image tag once Ming confirms the deployment path.
5. Draft an OAI logging-only patch first.
6. Confirm whether final scheduler labels should be:
   - original / time-domain / frequency-domain, or
   - original / PRB-cap / single-UE-per-slot.
7. Once the first baseline run is possible, capture one original OAI sweep before changing scheduler code.

---

## 10. Summary

The most productive waiting-time work is not another local StarlingX install. It is to prepare the Pegatron RU experiment plan, CSV schema, and OAI scheduler intervention design. The local OAI source confirms that the key levers are `max_sched_ues` in `nr_dlsch_preprocessor()` and `max_rbSize` before `nr_find_nb_rb()` in `pf_dl()`. The rApp test cases already show a Pegatron/Joule bandwidth sweep at 100/400/700 Mbps, but the exact thesis baseline architecture and CortexDC/PDU export path still need confirmation from Ming and Chynna.
