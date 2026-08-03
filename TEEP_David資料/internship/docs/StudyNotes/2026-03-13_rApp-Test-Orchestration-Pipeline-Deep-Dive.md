# rApp Test Orchestration Pipeline — Data Flow, Storage & TEIV Integration

**Date:** 2026-03-13  
**Source:** `External/rApp/rapp-cicd-ocloud/`

---

## 1. Overview

The rApp is a **Flask-based CI/CD orchestrator** for automated O-RAN gNB testing. The [Mar 10 summary](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-10_External-Repos-Summary.md) covered the high-level architecture. This note goes deeper into the **data pipeline** (how test definitions flow from YAML files through the orchestration engine, how metrics are collected in parallel from multiple sources, and how results end up in two complementary storage systems (SQLite for operational state, InfluxDB for time-series analytics)). It also covers the TEIV (Topology Exposure and Inventory) integration that maps tests to the live network topology.

---

## 2. Test Case Definition System

### 2.1 YAML Structure

Each test case is a YAML file in `test_cases/`. The lab has **12 pre-defined test cases** covering a matrix of:

| Dimension | Options |
|-----------|---------|
| **gNB Architecture** | `monolithic` (single process), `f1` (CU-DU split), `nfapi` (nFAPI interface) |
| **O-RU Vendor** | `liteon`, `pegatron` |
| **Worker Node** | `joule` (Xeon), `kepler` (other) |

Example (`f1-liteon-joule.yaml`):
```yaml
testId: f1-liteon-joule-cpu-bandwidth
testType: BANDWIDTH_SCALING
target:
    oduUrn: urn:o-ran:gnb:joule-liteon         # TEIV topology entity
    sideloadInstanceId: 139d2f51-b3c2-...      # registered sideloader
    cluster: cc1397ba-b1c4-...                 # O2 cluster ID
nf:
  - artifactName: oai-cu                       # NF 1: CU
    artifactRepoUrl: https://...ocloud-helm-templates.git
    branch: starlingx/liteon
    image:
      repository: oaisoftwarealliance/oai-gnb-fhi72
      version: 2026.w04
    extra:
      amfhost: 192.168.8.103
  - artifactName: oai-du-fhi-72                # NF 2: DU
    ...
    parameters:
        wr_isolcpus: [8, 14]                   # sweep: 8 or 14 isolated CPUs
        iperf_bandwidth_mbps: [100, 400, 700]  # sweep: 3 throughput levels
    baseline:
      wr_isolcpus: 10
      memory: 32Gi
      hugepages: 10Gi
execution:
    runsPerCase: 1
    stabilizationTime: 30     # seconds after deploy before testing
    iperfDuration: 60         # seconds per iperf run
```

**Key design:** The `parameters` section defines axes for combinatorial sweep. With `wr_isolcpus: [8,14]` and `iperf_bandwidth_mbps: [100,400,700]`, the engine generates **6 permutations** (`itertools.product`) and runs each one sequentially.

### 2.2 Multi-NF Support

The `nf` list can contain multiple Network Functions. For F1-split tests, both CU and DU are deployed as separate Helm releases. For monolithic tests, a single NF suffices. Each NF has its own Helm repo URL, branch, image tag, and parameter space.

---

## 3. Supporting Modules — Data Sources

### 3.1 `ue_client.py` — Samsung Phone Control (401 lines)

Controls a physical Samsung SM-G9860 (Galaxy S21 Ultra) via **ADB-over-SSH** (Paramiko, port 24). This is the actual 5G UE used for end-to-end testing.

| Category | Method | How |
|----------|--------|-----|
| **Attachment** | `is_attached()` | Checks `rmnet_data0` for `10.45.*` IP (5G SA data plane) |
| **Signal** | `get_signal()` | Parses `CellSignalStrengthNr` from `dumpsys telephony.registry` for RSRP/RSRQ/SINR |
| **Cell Detection** | `get_detected_cells()` | Extracts serving + neighbor cells with PCI, TAC, ARFCN, NCI from `dumpsys telephony.registry` |
| **Network Type** | `get_network_type()` | Reads `getRilDataRadioTechnology` — expecting `20(NR_SA)` |
| **Airplane Mode** | `set_airplane_mode()` | `cmd connectivity airplane-mode enable/disable` — used to force re-attachment |
| **Throughput** | `run_iperf()` | Runs `/data/local/tmp/iperf3` on the phone with UDP downlink (`-R`), returns JSON |
| **Cell Info** | `get_cell_info()` | `CellIdentityNr` with PCI, TAC, ARFCN, MCC, MNC, NCI, operator name |
| **Radio Logging** | `capture_radio_log()` | `adb logcat -b radio` capture for debugging |

**Hardcoded device ID:** `R5CN30TMBYR` — specific to the lab's Samsung phone.

### 3.2 `sideload_client.py` — Out-of-Band RT Validation (152 lines)

Separate from the Sideloader Service's REST API, this client uses **`kubectl exec` + `nsenter`** for direct host-level checks:

| Method | Purpose |
|--------|---------|
| `check_cpu_isolation()` | Reads `/sys/devices/system/cpu/isolated` |
| `check_tuned_profile()` | Runs `tuned-adm active` on the host |
| `check_irq_affinity()` | Reads `/proc/irq/*/smp_affinity_list` |
| `get_rt_throttling()` | Reads `sched_rt_runtime_us` |
| `trigger_perf_record()` | Starts `perf record` in background on the host |
| `generate_flamegraph()` | Pipes perf data through `FlameGraph/stackcollapse-perf.pl` |

### 3.3 `teiv_client.py` — Topology Inventory (121 lines)

Queries the **TEIV** (Topology Exposure and Inventory) service at `http://192.168.8.69:30180`. TEIV is the O-RAN SMO's inventory of all deployed network functions.

```
TEIV API: /topology-inventory/v1alpha11/domains/RAN/
    ├── entity-types/ODUFunction/entities     → list of gNBs
    ├── entity-types/NRCellDU/entities        → list of cells
    └── relationship-types/ODUFUNCTION_PROVIDES_NRCELLDU/relationships
```

**Vendor-aware Helm branching:** `get_helm_branch_for_odu()` maps ODU names to Helm branches (`starlingx/pegatron`, `starlingx/liteon`, `starlingx/jura`), enabling vendor-specific configurations to be selected automatically from the topology.

---

## 4. Dual Storage System

### 4.1 SQLite (`db.py`, 451 lines) — Operational State

**8 tables** for operational tracking:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `nfo_deployments` | Every Helm deploy/terminate via NFO | instance_id, operation_id, node_name, config JSON |
| `ue_operations` | Airplane mode toggles, data enables | operation, details JSON |
| `sideload_registry` | Active sideloader pods | instance_id, node_name, ip_address, port, last_seen |
| `sideload_rt_reports` | RT configuration snapshots | isolated_cpus, tuned_profile, rt_throttling_us, hugepages |
| `sideload_operations` | Every metric fetch request | url, parameters JSON, result JSON |
| `test_executions` | Test run metadata | test_id, gnb_instance_id, sideload_instance_id, oru_vendor |
| `ue_measurements` | Per-phase UE readings | attached, rsrp, rsrq, sinr, throughput_mbps |
| `sideload_ips` | Multi-IP validation for sideloaders | ip_address, reachable |
| `test_results` | Aggregated averages per execution | avg_throughput, avg_jitter, avg_loss, avg_cpu, cpu_breakdown JSON |

**Sideloader registration:** Uses `UPSERT` pattern — `register_sideload()` checks by `node_name` first, updates if exists, inserts if new.

### 4.2 InfluxDB (`influx_writer.py`, 314 lines) — Time-Series Analytics

**8 measurement types** written as InfluxDB points:

| Measurement | Tags | Fields | Source |
|-------------|------|--------|--------|
| `test_execution` | test_id, oru_vendor, execution_id | throughput, jitter, loss, RSRP/RSRQ/SINR, CPU | rApp aggregation |
| `thread_cpu` | test_id, oru_vendor, thread_name, core | cpu_percent | Sideloader `/process/threads` |
| `cpu_core_usage` | test_id, cpu_name | usage_percent | Sideloader `/cpu/monitor` |
| `memory_usage` | test_id | total/free/available/used/used_percent | Sideloader `/memory/monitor` |
| `disk_io` | test_id, device | read/write KB/s, read/write IOPS | Sideloader `/disk/monitor` |
| `hugepages_usage` | test_id | total/free/reserved/surplus/used/used_percent | Sideloader `/hugepages/monitor` |
| `teiv_odu` | entity_urn, odu_name | gNBId, MCC, MNC, FHI timing (T1a/Ta4) | TEIV API |
| `teiv_cell` | entity_urn, cell_name | nRPCI, nRTAC, arfcnDL, arfcnUL, bSChannelBwDL | TEIV API |

**TEIV topology snapshots:** The rApp periodically writes network topology state into InfluxDB, enabling correlation between gNB configuration changes (e.g., new O-DU deployment) and metric changes (e.g., power consumption shift).

**FHI timing parameters in InfluxDB:** The `teiv_odu` measurement stores fronthaul timing windows (T1a_cp_dl_min/max, T1a_up_min/max, Ta4_min/max) — these are the exact O-RAN FH 7.2 timing constraints we studied in the K8s installation guide.

---

## 5. End-to-End Data Flow

```
Test Case YAML
    │
    ▼
rApp: Load + Generate Permutations (itertools.product)
    │
    ├── For each permutation:
    │     │
    │     ├──→ NFO API: Deploy gNB Helm chart
    │     │       └── SQLite: record_nfo_deployment()
    │     │
    │     ├──→ Wait stabilization (30s)
    │     │
    │     ├──→ TEIV: Get ODU + Cell entities
    │     │       ├── SQLite: upsert_teiv_cache()
    │     │       └── InfluxDB: write_teiv_snapshot()
    │     │
    │     ├──→ For each run (default 3x):
    │     │     │
    │     │     ├── UE: airplane mode ON → OFF
    │     │     │     └── SQLite: record_ue_operation()
    │     │     │
    │     │     ├── UE: wait reattachment (10.45.*)
    │     │     │
    │     │     ├── PARALLEL (8 threads):
    │     │     │     ├── Sideloader: /cpu/monitor
    │     │     │     ├── Sideloader: /memory/monitor
    │     │     │     ├── Sideloader: /disk/monitor
    │     │     │     ├── Sideloader: /power/monitor
    │     │     │     ├── Sideloader: /network/monitor
    │     │     │     ├── Sideloader: /hugepages/monitor
    │     │     │     ├── Sideloader: /ptp/monitor
    │     │     │     └── Sideloader: /process/threads
    │     │     │           └── SQLite: record_sideload_operation()
    │     │     │           └── InfluxDB: write_{metric}_monitor()
    │     │     │
    │     │     ├── UE: run_iperf() (UDP DL)
    │     │     │     └── SQLite: record_ue_measurement()
    │     │     │
    │     │     └── UE: get_signal() (RSRP/RSRQ/SINR)
    │     │
    │     ├──→ Compute averages across runs
    │     │     ├── SQLite: record_test_results()
    │     │     └── InfluxDB: write_test_result()
    │     │
    │     └──→ NFO API: Terminate gNB deployment
    │
    └── Save raw JSON per execution
```

---

## 6. Connections

| rApp Feature | TEEP Relevance |
|---|---|
| **Parameter sweep (`itertools.product`)** | The current load sweep experiments (L/M/H × 3 repeats) are a simplified version of this — the rApp automates what we did manually with bash scripts |
| **Parallel metric collection (8 threads)** | During our experiments, we collected only power (Scaphandre). The rApp shows the production approach: collect CPU, memory, power, disk, network, hugepages, PTP, and thread-level metrics simultaneously |
| **Dual storage (SQLite + InfluxDB)** | The current approach (raw `power_uw.txt` + `markers.csv` → Python analysis) maps to the rApp's InfluxDB timeseries path. In Stage 2, we could write our measurements into the same InfluxDB for unified dashboarding |
| **TEIV integration** | When deploying on the lab K8s cluster, we can query TEIV to get the actual O-DU/Cell configuration instead of hardcoding it |
| **UE control via ADB** | The rApp automates exactly what a manual tester would do: toggle airplane mode, check signal, run iperf. Understanding this flow is essential for Stage 2 end-to-end testing |
| **12 test case matrix** | The monolithic/F1/NFAPI x vendor x node matrix shows how to structure experiments for different gNB deployment architectures. This is relevant when we compare power under different CU-DU split configs |
