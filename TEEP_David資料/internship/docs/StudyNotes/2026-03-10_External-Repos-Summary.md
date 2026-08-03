# External Repos Summary: rApp + Sideloader Service + Kubernetes Setup

**Date:** 2026-03-10  
**Sources:**
- rApp: `External/rApp/rapp-cicd-ocloud/`
- Sideloader: `External/sideloaderService/nino-sideloader-service/`
- K8s Guide: `External/kubernetes/nino-c-ran-installation/`

---

## 1. rApp — gNB Test Orchestration Framework

### What It Does

A **Flask-based test orchestrator** (1229-line `app.py`) that automates end-to-end O-RAN gNB testing. It is the **brain** of the CI/CD test pipeline. It deploys gNBs, runs tests, collects metrics, and stores results.

### Key Capabilities

| Capability | How |
|-----------|-----|
| **VNF Lifecycle** | Deploys/terminates gNB instances via NFO (Network Function Orchestrator) O2DMS API |
| **UE Control** | Controls a Samsung Android phone (SM-G9860) via ADB-over-SSH — airplane mode toggle, iperf throughput tests, signal readouts (RSRP/RSRQ/SINR) |
| **Sideload Integration** | Calls the Sideloader Service to collect system metrics (CPU/memory/power/disk/network/PTP) during tests |
| **Parameterized Testing** | Loads YAML test cases, generates permutations of parameters (bandwidth, CPU limits, etc.), runs all combinations automatically |
| **Result Storage** | SQLite (local) + InfluxDB (time-series) for results; raw JSON dumps per execution |
| **O-RAN SME Compliance** | Deployed via rApp Manager → ACM → Kong gateway with versioned API routes |

### Architecture Flow

```
User → POST /tests/run/{test_id}
  → Load YAML test case (with NF definitions + parameters)
  → Generate parameter permutations (itertools.product)
  → For each permutation:
      → Build Helm values (resource limits, image config)
      → Deploy gNB via NFO API (POST /vnf_instances/ → /deployments/ → /instantiate/)
      → Wait stabilization (default 30s)
      → For each run (default 3x):
          → Toggle airplane mode → check UE reattachment
          → Parallel: fetch sideload metrics (8 threads: CPU/mem/disk/power/net/hugepages/PTP/thread)
          → Run iperf test (configurable bandwidth + duration)
          → Record results
      → Compute averages (throughput, jitter, loss, RSRP, RSRQ, SINR, CPU breakdown)
      → Store in DB + save raw JSON
      → Terminate gNB deployment
```

### Helm Chart (`chart/`)

Standard K8s deployment:
- **Deployment:** Single replica, Flask container on port 5000, ClusterIP service
- **PVC:** 10Gi persistent volume for test results (`/app/test_results`)
- **Env vars:** NFO_BASE_URL, RAPP_URL, INFLUXDB credentials, ADB_MACHINE_SSH config, ACM appId
- **Resources:** 500m–1000m CPU, 512Mi–1Gi memory

### Notable Design Patterns

1. **Multi-NF deployment** — Test cases can define multiple NFs (e.g., gNB + sideloader), each with separate Helm values and parameter spaces.
2. **Dual-path endpoints** — Every route supports both `/path` and `/<version>/path` (e.g., `/tests/list` and `/tests/1.0.0/list`) for Kong SME gateway compatibility.
3. **Thread-per-metric collection** — 8 daemon threads fetch sideload metrics concurrently during each test run, preventing one slow metric from blocking others.

---

## 2. Sideloader Service — Node-Level Monitoring Agent

### What It Does

A **privileged Flask pod** (486-line `app.py`) deployed as a "sidecar" on each worker node. It exposes REST endpoints for **real-time system monitoring and fault injection** — the rApp calls these during test runs.

### Key Capabilities

| Category | Endpoints | What It Monitors/Does |
|----------|----------|----------------------|
| **CPU** | `/cpu/monitor`, `/cpu/governor`, `/cpu/idle_states`, `/cpu/context_switches` | Per-core usage (with breakdown), frequency governor, C-state config, context switches |
| **Memory** | `/memory/monitor`, `/hugepages/monitor`, `/memory/oom_check` | System RAM, hugepage allocation (critical for DPDK/OAI), OOM killer events |
| **Power** | `/power/monitor`, `/power/ipmi` | **RAPL** power consumption + optional **iDRAC/Redfish** or **IPMI** — exactly like our Scaphandre approach! |
| **Network** | `/network/monitor`, `/dpdk/status` | Interface stats including **DPDK/SR-IOV** device detection |
| **Disk** | `/disk/monitor`, `/disk/usage` | I/O statistics, space utilization |
| **Process** | `/process/threads`, `/process/affinity`, `/perf/context_switches`, `/perf/sched_latency` | Per-thread CPU of `nr-softmodem`, CPU pinning/affinity, scheduler latency via `perf` |
| **PTP** | `/ptp/monitor`, `/ptp/status`, `/ptp/comprehensive`, `/ptp/time_properties`, `/ptp/current_data`, `/ptp/parent_data`, `/ptp/port_state` | Precision Time Protocol sync status — critical for O-RAN fronthaul timing |
| **Fault Injection** | `/network/vlan_fault`, `/network/link_down`, `/stress/memory`, `/stress/cpu`, `/ptp/inject_fault` | VLAN fault injection, link down simulation, Memory/CPU stress testing, PTP service disruption |

### Helm Chart (`Charts/`)

**Highly privileged deployment** — this is the most noteworthy part:
- `hostPID: true`, `hostNetwork: true`, `hostIPC: true` — sees all host processes and network
- `securityContext.privileged: true` with `SYS_ADMIN`, `SYS_PTRACE`, `PERFMON` capabilities
- Mounts `/tmp` from host via hostPath volume
- No resource limits defined (intentional — it needs to inspect the entire node)
- Uses `nodeSelector` and `tolerations` to target specific worker nodes (e.g., `kubernetes.io/hostname: joule`, `dedicated: 5g-radio`)

### Self-Registration

On startup, the sideloader runs a `register_loop()` thread that periodically POSTs its IP/port to the rApp's `/sideload/register` endpoint. The rApp validates reachability (tries all IPs, picks first working one) and stores the mapping in its DB.

### Connection to Our TEEP Work

The **`/power/monitor` endpoint** does exactly what our Scaphandre/RAPL setup does — reads RAPL energy counters at 1s intervals and returns timeseries data. Additionally, it supports iDRAC/Redfish and IPMI as alternative power sources. This means the Sideloader is essentially a **production-grade version of our measurement methodology**, deployed as a Kubernetes-native service.

---

## 3. Kubernetes Installation Guide (nino-c-ran-installation)

### What It Is

An **automated provisioning system** for deploying OAI FH 7.2 (Fronthaul Split 7.2) on a vanilla Kubernetes cluster. This is the infrastructure layer that the rApp and Sideloader run on.

### Architecture

```
Master Node                          Worker Node (RT)
├── Kubernetes API (:6443)           ├── RT Kernel (RHEL 9.4)
├── Cilium CNI                       ├── SR-IOV enabled NIC
├── Multus CNI + SR-IOV plugin       ├── VFIO driver
├── OpenEBS (storage)                ├── Hugepages (1G × 40)
└── CRI-O runtime                   ├── CPU isolation (housekeeping cores)
                                     └── CRI-O runtime
```

### Minimum Specs

| | Master | Worker |
|-|--------|--------|
| **OS** | RHEL 9.0+ | RHEL 9.0+ |
| **CPU** | 8-core, 2 GHz | 16-core, 2 GHz |
| **RAM** | 16 GB | 32 GB |
| **K8s/CRI-O** | 1.28+ | 1.28+ |
| **Special HW** | — | NUMA + SR-IOV NIC |

### Setup Flow

**Master node** (`master_setup.sh`):
```bash
./scripts/provision/k8s-setup.sh \
  --runtime crio \
  --api-address 192.168.8.XXX \
  --pod-network 10.42.0.0/16 \
  --service-network 10.43.0.0/16 \
  --multi-node
```

**Worker node** (`worker_setup.sh`):
```bash
./scripts/provision/worker_setup.sh \
  --master-ip <master_ip> \
  --join-token <token> \
  --join-hash <hash> \
  --rh-org-id <org_id> \
  --rh-activation-key <key> \
  --housekeeping-cpus 6 \
  --hugepage-count 40 \
  --hugepage-size 1G \
  --crio-version 1.31 \
  --k8s-version 1.31
```

### Included Helm Charts

The `charts/` directory includes pre-packaged charts for the full O-RAN stack:
- **OAI gNB** (oai, ocloud-helm-templates) — the actual 5G base station
- **Prometheus + cAdvisor** — monitoring
- **Loki** — log aggregation
- **Kong** — API gateway (for SME)
- **PTP Agent** — precision timing
- **Retina** — network observability
- **SR-IOV network metrics exporter** — NIC telemetry
- **srsRAN Project** — alternative gNB stack

---

## Kubernetes Setup Commands (Ubuntu 24.04 Adaptation)

The lab guide targets RHEL 9.4 with CRI-O. Below are the adapted commands used on **Ubuntu 24.04** with **containerd** as the container runtime.

### Pre-flight

```bash
# 1. Disable swap
sudo swapoff -a
sudo sed -i '/swap/d' /etc/fstab

# 2. Load required kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# 3. Set sysctl parameters
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system

# 4. Disable UFW (interferes with pod-to-service FORWARD traffic)
sudo ufw disable
```

### Configure containerd (replaces CRI-O from the guide)

```bash
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd
```

### Install kubeadm + kubelet (v1.31)

```bash
# Add Kubernetes apt repo
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg --yes
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update

# Install + hold version
sudo apt-get install -y kubelet kubeadm conntrack
sudo apt-mark hold kubelet kubeadm

# Enable kubelet
sudo systemctl enable --now kubelet
```

### Initialize cluster

```bash
# Init with Cilium-compatible pod CIDR (10.0.0.0/8) + lab's service CIDR
sudo kubeadm init \
  --pod-network-cidr=10.0.0.0/8 \
  --service-cidr=10.43.0.0/16 \
  --cri-socket=unix:///var/run/containerd/containerd.sock

# Set up kubeconfig
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Remove control-plane taint (single-node cluster)
kubectl taint nodes --all node-role.kubernetes.io/control-plane-

# Set FORWARD policy to ACCEPT (Cilium/kube-proxy manage filtering)
sudo iptables -P FORWARD ACCEPT
```

### Install Cilium CNI (v1.16.5)

```bash
# Install Cilium CLI
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
curl -L --fail --remote-name-all \
  "https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-amd64.tar.gz{,.sha256sum}"
sha256sum --check cilium-linux-amd64.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-amd64.tar.gz /usr/local/bin
rm -f cilium-linux-amd64.tar.gz{,.sha256sum}

# Install Cilium into cluster
cilium install --version 1.16.5

# Verify
cilium status --wait
kubectl get nodes        # should show Ready
kubectl get pods -A      # all pods should be 1/1 Running
```

### Troubleshooting Notes

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| `conntrack not found` | Missing dependency on Ubuntu | `sudo apt-get install -y conntrack` |
| CoreDNS stuck at 0/1 (i/o timeout to 10.43.0.1) | UFW FORWARD chain policy DROP blocking pod→service traffic | `sudo ufw disable` + `sudo iptables -P FORWARD ACCEPT` |
| Pod CIDR mismatch | kubeadm `--pod-network-cidr=10.42.0.0/16` vs Cilium default `10.0.0.0/8` | Use `--pod-network-cidr=10.0.0.0/8` to match Cilium |

### Resulting Cluster

```
Node:    noobplatinum-ideapad-pro-5-14iah10 (Ready, control-plane)
K8s:     v1.31.14
Runtime: containerd 2.2.1 (SystemdCgroup=true)
CNI:     Cilium 1.16.5
Pod CIDR:     10.0.0.0/8
Service CIDR: 10.43.0.0/16
```
