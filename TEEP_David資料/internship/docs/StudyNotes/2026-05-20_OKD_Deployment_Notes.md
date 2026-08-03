---
title: OKD Hub & Slave Node (SNO) - Complete Deployment Guide
---

# OKD Hub & Slave Node Deployment Guide
**Date:** May 2026
**OS Base:** Red Hat Enterprise Linux 9.4 (Host), OKD 4.20 / SCOS (Cluster)
**Domain:** `david.internal` (custom — to avoid collision with existing `lab.internal` hub)

## 0. Testing End Results
![Screenshot from 2026-05-19 22-44-55](https://hackmd.io/_uploads/ry-z8ZckGe.png)
![Screenshot from 2026-05-19 22-44-34](https://hackmd.io/_uploads/ByZG8WcJzx.png)
![Screenshot from 2026-05-19 22-44-11](https://hackmd.io/_uploads/HyWfU-91Mx.png)
![Screenshot from 2026-05-19 22-41-19](https://hackmd.io/_uploads/S1lGUWq1Me.png)
![Screenshot from 2026-05-19 22-36-20](https://hackmd.io/_uploads/Bk-MU-91zg.png)

## 1. Architecture Overview

We deployed a two-tier O-RAN edge infrastructure using the `pti-rtp` Ansible automation:

* **Hub Cluster (`master-0-vm`):** An OKD All-in-One (AIO) control plane running as a KVM virtual machine on the deployment host (`worker-rt` at `192.168.8.76`). This hosts Advanced Cluster Management (Stolostron/ACM), O2IMS, and the Metal3 bare-metal provisioner.
* **Slave Node (`kepler-du`):** A physical Dell server (`192.168.8.43`) provisioned remotely via Zero-Touch Provisioning (ZTP) from the Hub. Configured for telco workloads with hardware PTP and persistent SCTP.

### Network Layout
| Interface | IP | Role |
|---|---|---|
| `eno1` (host) | `192.168.10.79/24` | Management / iDRAC network |
| `eno2` → `bridge0` (host) | `192.168.8.76/24` | Production / Lab network (SSH entry point) |
| `master-0-vm` (KVM) | `192.168.8.210` | OKD Hub API + Console |
| Slave node | `192.168.8.43` | SNO edge node |
| Pi-hole DNS | `192.168.8.72` | Lab DNS server |
| Gateway | `192.168.8.9` | Lab router |

---

# Part 1: OKD Hub Deployment

## 2. Host Preparation & Dependencies

**Reference:** [pti-rtp](https://github.com/bmw-ece-ntust/pti-rtp)

```bash
# Clone the repo (we used a GitHub PAT for auth)
dnf install -y git
cd /root
git clone https://github.com/bmw-ece-ntust/pti-rtp.git
cd pti-rtp/okd
```

### Fix: Remove `libvirt-python` from pip
RHEL 9 provides `libvirt-python` as a system package. Compiling it from pip causes build failures.
```bash
sed -i '/^libvirt-python$/d' requirements.txt
```

### Set up the Python venv and install dependencies
```bash
python3 -m venv okd-env
source okd-env/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

### System packages
```bash
dnf install https://dl.fedoraproject.org/pub/epel/epel{,-next}-release-latest-9.noarch.rpm
dnf group install "Development Tools"
subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
dnf install python3-devel python3-libvirt python3-netaddr ansible pip pkgconfig \
  libvirt-devel python-lxml nmstate wget make
sudo dnf install ansible
```

### KVM setup
```bash
dnf group install "Virtualization Host" "Virtualization Hypervisor" \
  "Virtualization Tools" "Virtualization Client"
systemctl enable --now libvirtd
virsh list --all   # Should return an empty table
```

### Install Go 1.24.3
The O2IMS operator requires Go to compile. We installed it manually:
```bash
wget https://go.dev/dl/go1.24.3.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
go version   # go1.24.3 linux/amd64
```

---

## 3. Bridge Network Configuration

> ⚠️ **DANGER ZONE:** Adding `eno2` to a bridge will momentarily kill your SSH session. Paste the entire block at once. If you get disconnected, wait 15 seconds and SSH back in.

### Fix: Restart NetworkManager first
After `dnf update`, `nmcli` (v1.54) and `NetworkManager` (v1.46) version mismatch causes `802-3-ethernet.mac-address-denylist: unknown property` errors.
```bash
systemctl restart NetworkManager
```

### Create the physical bridge (paste all at once)
```bash
nmcli connection add type bridge ifname bridge0 con-name bridge0
nmcli connection modify bridge0 ipv4.addresses 192.168.8.76/24
nmcli connection modify bridge0 ipv4.gateway 192.168.8.9
nmcli connection modify bridge0 ipv4.method manual
nmcli connection modify bridge0 ipv4.dns "8.8.8.8 192.168.8.72"
nmcli connection up bridge0
nmcli connection add type bridge-slave ifname eno2 master bridge0
nmcli connection up bridge0
nmcli connection up bridge-slave-eno2
```

### Create the KVM virtual network (`br0-okd`)
```bash
cat << 'EOF' > /tmp/br0-okd.xml
<network>
  <name>br0-okd</name>
  <forward mode="bridge"/>
  <bridge name="bridge0"/>
</network>
EOF

virsh net-define /tmp/br0-okd.xml
virsh net-start br0-okd
virsh net-autostart br0-okd
virsh net-list --all
# br0-okd should show as active/yes/yes
```

---

## 4. Ansible Inventory & Domain Configuration

### Generate SSH key
```bash
ssh-keygen -t ed25519 -C "root@worker-rt" -f ~/.ssh/id_ed25519 -N ""
```

### `hosts.yml`
```bash
mkdir -p /root/pti-rtp/okd/inventory/host_vars/master-0-vm
mkdir -p /root/pti-rtp/okd/inventory/group_vars/all

cat << 'EOF' > /root/pti-rtp/okd/inventory/hosts.yml
deployer:
  hosts:
    localhost:
      ansible_connection: local
kvm:
  hosts:
    localhost:
      ansible_connection: local
ocloud:
  hosts:
    master-0-vm:
EOF
```

### `group_vars/all/vars.yml`
Key tweak: `ocloud_domain_name` is `david.internal` (not `lab.internal`) to avoid collision.
```bash
cat << EOF > /root/pti-rtp/okd/inventory/group_vars/all/vars.yml
---
ocloud_infra: vm
ocloud_platform: okd
ocloud_topology: aio
ocloud_platform_okd_ssh_pubkey: "$(cat ~/.ssh/id_ed25519.pub)"
ocloud_cluster_name: "ocloud-vm-okd-aio"
ocloud_domain_name: "david.internal"
ocloud_network_mode: "bridge"
ocloud_net_bridge: "bridge0"
ocloud_net_name: "br0-okd"
ocloud_net_cidr: "192.168.8.0/24"
ocloud_cluster_net_cidr: "10.128.0.0/14"
ocloud_cluster_net_hostprefix: 23
ocloud_service_net_cidr: "172.30.0.0/16"
ocloud_network_type: "OVNKubernetes"
ocloud_dns_servers:
  - "192.168.8.72"
ocloud_ntp_servers:
  - "time.google.com"
ocloud_setup_golang_url: "https://go.dev/dl/go1.24.3.linux-amd64.tar.gz"
EOF
```

### `host_vars/master-0-vm/vars.yml`
```bash
cat << 'EOF' > /root/pti-rtp/okd/inventory/host_vars/master-0-vm/vars.yml
---
role: master
ip_address: 192.168.8.210
ocloud_infra_vm_mem_gb: 48
mac_addresses:
  ens3: "52:54:00:ab:cd:01"
network_config:
  interfaces:
    - name: "ens3"
      type: "ethernet"
      state: "up"
      ipv4:
        enabled: true
        dhcp: false
        address:
          - ip: "192.168.8.210"
            prefix-length: 24
  routes:
    config:
      - destination: "0.0.0.0/0"
        next-hop-address: "192.168.8.9"
        next-hop-interface: "ens3"
EOF
```

---

## 5. Playbook Patches (Critical Bug Fixes)

These patches **must** be applied before running the playbook.

### 5.1 Fix MAC Address bug in `virt.xml.j2`
```bash
cp /root/pti-rtp/okd/roles/ocloud_infra_vm/templates/virt.xml.j2 \
   /root/pti-rtp/okd/roles/ocloud_infra_vm/templates/virt.xml.j2.bak

sed -i "s/hostvars\[ocloud_host\]\['mac_addresses'\].get(interface_name)/hostvars[ocloud_host]['mac_addresses'].get(hostvars[ocloud_host]['mac_addresses'].keys() | list | first)/g" \
  /root/pti-rtp/okd/roles/ocloud_infra_vm/templates/virt.xml.j2

sed -i "s/hostvars\[ocloud_host\]\[\"mac_addresses\"\]\[interface_name\]/hostvars[ocloud_host]['mac_addresses'].values() | list | first/g" \
  /root/pti-rtp/okd/roles/ocloud_infra_vm/templates/virt.xml.j2
```

### 5.2 Bypass self-signed certificate validation & extend Stolostron timeout
```bash
for f in \
  /root/pti-rtp/okd/roles/ocloud_platform_stolostron/tasks/main.yml \
  /root/pti-rtp/okd/roles/ocloud_platform_mco/tasks/main.yml \
  /root/pti-rtp/okd/roles/ocloud_platform_o2ims/tasks/main.yml \
  /root/pti-rtp/okd/roles/ocloud_platform_okd/handlers/main.yml \
  /root/pti-rtp/okd/roles/ocloud_platform_okd/tasks/version.yml \
  /root/pti-rtp/okd/roles/ocloud_token/tasks/main.yml \
  /root/pti-rtp/okd/roles/ocloud_compliance/tasks/main.yml; do

  cp "$f" "$f.bak"
  sed -i 's/    kubeconfig: "{{ ocloud_kubeconfig }}"/    kubeconfig: "{{ ocloud_kubeconfig }}"\n    validate_certs: false/g' "$f"
done

sed -i 's/MINUTE -gt 900/MINUTE -gt 1500/g' \
  /root/pti-rtp/okd/roles/ocloud_platform_stolostron/tasks/main.yml
```

### 5.3 Patch O2IMS: Add `local-path-provisioner` storage & fix PostgreSQL image
OKD SNO lacks a default StorageClass, which blocks the O2IMS PostgreSQL database. We replaced the entire O2IMS task file to install `local-path-provisioner`, grant it the privileged SCC, set it as the default StorageClass, and patch the postgres image to `quay.io/sclorg/postgresql-16-c9s:c9s`.

The historical raw chat export that originally contained this patch should not be treated as a required handover artifact. If the task file must be recreated, rebuild it from the four requirements above: install `local-path-provisioner`, grant the SCC, mark `local-path` as default, and patch the PostgreSQL image.

---

## 6. DNS Configuration (Required Preflight)

### Requirement
The OKD bootstrap requires local DNS records for the API and wildcard apps domains before the playbook starts. If the host resolver only points to public DNS, names such as `api.ocloud-vm-okd-aio.david.internal` will not resolve to the Hub VM and the installer will wait indefinitely.

### Pi-hole + Local Hosts Setup

**On the Pi-hole server (`192.168.8.72`):**
```bash
ssh infidel@192.168.8.72   # Password: bmwlab123
sudo tee /home/infidel/pihole/etc-dnsmasq.d/okd.conf > /dev/null << 'EOF'
address=/api.ocloud-vm-okd-aio.david.internal/192.168.8.210
address=/api-int.ocloud-vm-okd-aio.david.internal/192.168.8.210
address=/.apps.ocloud-vm-okd-aio.david.internal/192.168.8.210
address=/master-0.ocloud-vm-okd-aio.david.internal/192.168.8.210
EOF
podman restart pihole
exit
```

**On `worker-rt`:**
```bash
echo -e "nameserver 192.168.8.72\nnameserver 8.8.8.8" > /etc/resolv.conf

echo "192.168.8.210 api.ocloud-vm-okd-aio.david.internal api-int.ocloud-vm-okd-aio.david.internal" >> /etc/hosts

dig +short api.ocloud-vm-okd-aio.david.internal
# Should return: 192.168.8.210
```

---

## 7. Deployment & Post-Install Fixes

### Run the playbook
```bash
cd /root/pti-rtp/okd
source okd-env/bin/activate
ansible-playbook -i inventory/hosts.yml playbooks/ocloud.yml
```
* No `--become` password needed — you're already root, and the CoreOS `core` user has passwordless sudo.
* The `Monitor OKD platform deployment` handler will sit for **45–90 minutes**. This is normal.
* To watch logs from a second terminal: `tail -f $(ls -dt /root/ocloud.*/| head -1)cfg/.openshift_install.log`
* Percentage will jump around wildly (50% → 1% → 68%). This is normal — API server restarts reset the CVO counter.

### Ensure `kubernetes` Python library is available
The post-install Ansible tasks use `kubernetes.core.k8s`, so the system Python needs the Kubernetes client library available.
```bash
/usr/bin/python3 -m pip install kubernetes
```

### Pin the kubeconfig path
The playbook's `kubernetes.core.k8s` module should use the generated kubeconfig explicitly rather than relying on an interactive shell export:
```bash
mkdir -p ~/.kube
cp /root/ocloud.2026-05-17.30mkn0s0/cfg/auth/kubeconfig ~/.kube/config

echo 'ocloud_kubeconfig: "/root/ocloud.2026-05-17.30mkn0s0/cfg/auth/kubeconfig"' \
  >> /root/pti-rtp/okd/inventory/group_vars/all/vars.yml
```
Then re-ran the playbook. It skipped all completed tasks and finished Stolostron + O2IMS in ~14 minutes.

### Final Result (Hub)
```
PLAY RECAP
master-0-vm  : ok=41  changed=33  unreachable=0  failed=0  skipped=13  rescued=0  ignored=0
```

### Accessing the Console
* **URL:** `https://console-openshift-console.apps.ocloud-vm-okd-aio.david.internal`
* **Username:** `kubeadmin`
* **Password:** `FLkrt-Gc9UH-P9tWr-43VcX`

On your local PC, add to `/etc/hosts` (or `C:\Windows\System32\drivers\etc\hosts`):
```
192.168.8.210 console-openshift-console.apps.ocloud-vm-okd-aio.david.internal oauth-openshift.apps.ocloud-vm-okd-aio.david.internal
```

### Checkpoint: KVM Snapshot
Before starting the slave node deployment, we took a snapshot:
```bash
virsh snapshot-create-as --domain master-0-vm \
  --name "hub-completed-checkpoint" \
  --description "Clean OKD Hub installation before SNO deployment" \
  --atomic

# To revert if needed:
# virsh snapshot-revert master-0-vm hub-completed-checkpoint
```

---

# Part 2: Slave Node (SNO) Deployment via ZTP

## 8. Session State Recovery
Every time you reconnect, run this to restore your environment:
```bash
sudo su -
cd /root/manifests-examples
source /root/pti-rtp/okd/okd-env/bin/activate
export KUBECONFIG=/root/ocloud.2026-05-17.30mkn0s0/cfg/auth/kubeconfig
oc get nodes   # Should show master-0-vm Ready
```

## 9. Clone Manifests & Patch the Provisioning Request

```bash
cd /root
git clone https://github.com/bmw-ece-ntust/manifests-examples.git
cd manifests-examples
```

### Copy `oc` and `kubectl` to system path
The Ansible playbook buried these inside the staging directory:
```bash
NEW_DIR=$(ls -dt /root/ocloud.*/ | head -1)
cp ${NEW_DIR}bin/oc /usr/local/bin/
cp ${NEW_DIR}bin/kubectl /usr/local/bin/
oc version --client   # Client Version: 4.18.41
```

### Patch `kepler-leo-gnb.yaml`
```bash
# Inject your SSH key
sed -i 's|sshPublicKey:.*|sshPublicKey: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIM/mjCJ6uBq5r55hqo4Gir8f4jJ4aCQAqeQ+eg5sKevZ root@worker-rt|g' \
  provisioningrequests/kepler-leo-gnb.yaml

# Fix the gateway
sed -i 's|next-hop-address: 192.168.8.103|next-hop-address: 192.168.8.9|g' \
  provisioningrequests/kepler-leo-gnb.yaml

# Fix the deprecated API version
sed -i 's|o2ims.provisioning.oran.org/v1alpha1|clcm.openshift.io/v1alpha1|g' \
  provisioningrequests/kepler-leo-gnb.yaml
```

---

## 10. Patch Cluster Templates & Install Prerequisites

### Patch the templates
```bash
# Extend installation timeout from 90m to 240m
sed -i 's|clusterInstallationTimeout: "90m"|clusterInstallationTimeout: "240m"|g' \
  clustertemplates/okd-4.19/sno-du/clusterinstance-defaults-v1.yaml

# Update deprecated API version
sed -i 's|o2ims.provisioning.oran.org/v1alpha1|clcm.openshift.io/v1alpha1|g' \
  clustertemplates/okd-4.19/sno-du/sno-du-okd-v4-19.yaml

# Update deprecated 'templates' field
sed -i 's|  templates:|  templateDefaults:|g' \
  clustertemplates/okd-4.19/sno-du/sno-du-okd-v4-19.yaml

# Apply to the cluster
oc delete configmap clusterinstance-defaults-v1 -n sno-du-okd-v4-19 --ignore-not-found
oc apply -k clustertemplates/okd-4.19/
```

### Install PolicyGenerator plugin
```bash
mkdir -p ~/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator

curl -L https://github.com/open-cluster-management-io/policy-generator-plugin/releases/download/v1.17.0/linux-amd64-PolicyGenerator \
  -o ~/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator/PolicyGenerator

chmod +x ~/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator/PolicyGenerator
```

### Install standalone `kustomize`
```bash
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
mv kustomize /usr/local/bin/
kustomize version   # v5.8.1
```

### Spin up Metal3 & apply policies
```bash
oc apply -f provisioningrequests/metal3-prov.yaml
oc apply -f provisioningrequests/metal3-svc.yaml
oc apply -f clusterimagesets/4.19.0-okd-scos.19.yaml
oc apply -f policytemplates/okd-4.19/sno-du/ns.yaml

kustomize build --enable-alpha-plugins policytemplates/okd-4.19/ | oc apply -f -
```

### Pre-flight verification
```bash
oc get policy -n ztp-sno-du-okd-v4-19
# Should show 3 policies with empty COMPLIANCE STATE (waiting for target cluster)

oc get pods -n openshift-machine-api | grep metal3
# Should show pods in Running state
```

---

## 11. Launch Zero-Touch Provisioning

```bash
oc apply -f provisioningrequests/kepler-leo-gnb.yaml
```

### Monitor the automation
```bash
watch -n 30 "echo '=== Agent ===' && oc get agent -A && \
  echo '=== BMH ===' && oc get bmh -A && \
  echo '=== ProvisioningRequest ===' && oc get provisioningrequest"
```

**Expected progression:**
1. BMH: `registering` → `preparing` → `provisioning` → `provisioned`
2. Agent: (empty) → appears → `Done`
3. ProvisioningRequest: `progressing` → `fulfilled`

This takes **45–90 minutes**. The bare-metal server is being remotely wiped and reinstalled via iDRAC.

### Final Result (ZTP)
```
=== Agent ===
NAMESPACE   NAME                                   CLUSTER     APPROVED   ROLE     STAGE
kepler-du   2d6298a9-e6d3-a195-9807-fb00eaeb6191   kepler-du   true       master   Done

=== BMH ===
NAMESPACE   NAME                             STATE         ONLINE   AGE
kepler-du   sno-00.ocloud-vm-bmw.lab.local   provisioned   true     3h17m

=== ProvisioningRequest ===
NAME                                   PROVISIONPHASE   PROVISIONDETAILS
0953dcad-66cc-487b-a43c-f36b586f604f   fulfilled        Provisioning request has completed successfully
```

---

## 12. Post-Install: PTP & SCTP Configuration

### Fix: SSH host key changed
The ZTP wipe regenerated the server's SSH identity. Clear the stale fingerprint:
```bash
ssh-keygen -R 192.168.8.43
ssh -o StrictHostKeyChecking=accept-new core@192.168.8.43 "hostname"
# sno-00.ocloud-vm-bmw.lab.local
```

### Verify hardware timestamping
```bash
ssh core@192.168.8.43 "ethtool -T ens8f0 | grep -E 'hardware|Precise'"
# hardware-transmit / hardware-receive / hardware-raw-clock
# Hardware timestamp provider qualifier: Precise (IEEE 1588 quality)
```

### Fix: Toolbox container not initialized
CoreOS is immutable — you must compile inside a `toolbox` container. On a fresh install, it doesn't exist yet:
```bash
ssh core@192.168.8.43 "toolbox create --assumeyes"
```

### Compile and install `linuxptp`
```bash
ssh core@192.168.8.43 "toolbox run sudo dnf install -y gcc make wget tar && \
  toolbox run bash -c 'cd /tmp && \
  wget -q https://sourceforge.net/projects/linuxptp/files/latest/download -O linuxptp.tar.gz && \
  tar xf linuxptp.tar.gz && cd linuxptp-* && make && \
  cp ptp4l phc2sys /var/home/core/'"

ssh core@192.168.8.43 "sudo cp /var/home/core/ptp4l /var/home/core/phc2sys /usr/local/bin/ && \
  sudo chmod +x /usr/local/bin/ptp4l /usr/local/bin/phc2sys"
```

### Configure PTP services (domain 24)
```bash
# Create config
ssh core@192.168.8.43 "sudo mkdir -p /etc/linuxptp && sudo tee /etc/linuxptp/ptp4l.conf > /dev/null << 'EOF'
[global]
domainNumber            24
slaveOnly               1
time_stamping           hardware
tx_timestamp_timeout    50
logging_level           6
summary_interval        0

[ens8f0]
network_transport       L2
hybrid_e2e              0
EOF"

# Create ptp4l systemd service
ssh core@192.168.8.43 "sudo tee /etc/systemd/system/ptp4l.service > /dev/null << 'EOF'
[Unit]
Description=Precision Time Protocol (PTP) service
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
ExecStart=/usr/local/bin/ptp4l -i ens8f0 -H -2 -s -f /etc/linuxptp/ptp4l.conf -m
[Install]
WantedBy=multi-user.target
EOF"

# Create phc2sys systemd service
ssh core@192.168.8.43 "sudo tee /etc/systemd/system/phc2sys.service > /dev/null << 'EOF'
[Unit]
Description=Synchronize system clock or PTP hardware clock (PHC)
After=ptp4l.service
[Service]
Type=simple
ExecStart=/usr/local/bin/phc2sys -a -r -r -n 24 -m
[Install]
WantedBy=multi-user.target
EOF"

# Disable NTP and enable PTP
ssh core@192.168.8.43 "sudo timedatectl set-ntp false"
ssh core@192.168.8.43 "sudo systemctl daemon-reload && \
  sudo systemctl enable ptp4l phc2sys && \
  sudo systemctl start ptp4l phc2sys"
```

### Configure persistent SCTP
```bash
ssh core@192.168.8.43 "echo 'sctp' | sudo tee /etc/modules-load.d/sctp.conf"
```

---

## 13. Final Verification

### Hub Infrastructure
```bash
oc get nodes
# master-0-vm   Ready   control-plane,master,worker   8h   v1.33.5

oc get clusterversion
# version   4.20.0-okd-scos.12   True   False   8h

oc get multiclusterhub -n open-cluster-management
# multiclusterhub   Running   7h48m   2.15.0

oc get pods -n oran-o2ims
# All pods Running (alarms-server, artifacts-server, cluster-server, etc.)

oc get multiclusterobservability
# observability   7h40m
```

### Edge Node Provisioning
```bash
oc get bmh -A
# kepler-du   sno-00.ocloud-vm-bmw.lab.local   provisioned   true

oc get agent -A
# kepler-du   ...   kepler-du   true   master   Done

oc get policy -n ztp-sno-du-okd-v4-19
# v1-perf-configuration-policy    enforce   Compliant
# v1-sriov-configuration-policy   enforce   Compliant
# v1-subscriptions-policy         enforce   Compliant
```

### Telco Workload Tuning
```bash
ssh core@192.168.8.43 "sudo journalctl -u ptp4l -n 10 | grep rms"
# rms    5   max    8   freq -13684 +/-   8   delay   141 +/-   1

ssh core@192.168.8.43 "sudo journalctl -u phc2sys -n 10 | grep offset"
# CLOCK_REALTIME phc offset   -7   s2   freq   +610   delay   589

ssh core@192.168.8.43 "cat /etc/modules-load.d/sctp.conf"
# sctp
```

**PTP rms of 5–7 nanoseconds and phc2sys offset of ~10ns = sub-millisecond hardware synchronization confirmed.**

---

## Quick Reference: Cleanup & Recovery

### Destroy a failed Hub VM (start over)
```bash
virsh destroy master-0-vm
virsh undefine master-0-vm --remove-all-storage
rm -rf /root/ocloud.*/
```

### Revert Hub to checkpoint
```bash
virsh snapshot-revert master-0-vm hub-completed-checkpoint
```

### Re-enter a session after disconnect
```bash
sudo su -
cd /root/manifests-examples
source /root/pti-rtp/okd/okd-env/bin/activate
export KUBECONFIG=/root/ocloud.2026-05-17.30mkn0s0/cfg/auth/kubeconfig
oc get nodes
```
