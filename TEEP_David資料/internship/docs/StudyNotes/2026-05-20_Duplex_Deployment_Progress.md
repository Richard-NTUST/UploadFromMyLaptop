---
title: StarlingX Duplex (KVM) - Deployment Notes
---

# StarlingX Duplex Deployment Notes
**Date:** May 15–19, 2026
**OS Base:** Ubuntu Host (Hypervisor), StarlingX Release 10 / Debian 11 (VMs)
**Mode:** Duplex (Two virtual controllers on KVM/QEMU)
**Status:** controller-0 unlocked & available; controller-1 sync **unresolved**

---

## 0. Where We Got To

![image](https://hackmd.io/_uploads/SJEJkn91Me.png)
![image](https://hackmd.io/_uploads/Hkk-k3q1Ml.png)
![image](https://hackmd.io/_uploads/HJZ0RoqyGl.png)

| Component | Status |
|---|---|
| controller-0 | `unlocked \| enabled \| available` |
| controller-1 | Destroyed & undefined — PXE boot never succeeded |
| HAProxy | `enabled-active` (after manual CPR each reboot) |
| Keystone | `enabled-active` |
| dnsmasq (PXE) | `enabled-active` in SM but process dead — missing config file |
| Ceph | Unresponsive (`ceph status` hangs — no peer) |
| Kubernetes | `controller-0 Ready` (single node, no workers) |

**Bottom line:** The Hub control plane works. The blocker is getting controller-1 to PXE boot from controller-0 — the `virtual-deployment` scripts spawn VMs with legacy BIOS/CPU defaults that are incompatible with the modern Debian-based StarlingX installer.

---

## 1. Architecture

```
Ubuntu Host (KVM Hypervisor)
├── stxbr1 (OAM)         → 10.10.10.0/24     → Internet access
├── stxbr2 (Management)  → 192.168.204.0/24  → PXE/DHCP, inter-controller
├── stxbr3 (Cluster-Host) → 192.168.206.0/24 → Internal cluster networking
└── stxbr4 (Data)                             → Optional data plane

controller-0 VM (4 NICs → stxbr1–4)
controller-1 VM (4 NICs → stxbr1–4)  ← never successfully booted
```

### Interface Mapping (controller-0)
Discovered via `virsh domiflist` + `ip a` MAC matching:
| KVM Bridge | VM Interface | Network |
|---|---|---|
| stxbr1 | `enp2s1` | OAM |
| stxbr2 | `enp2s2` | Management |
| stxbr3 | `enp3s0` | Cluster-Host |
| stxbr4 | `enp4s0` | Data |

> **Key lesson:** The original guide uses legacy `eth1/eth2/eth3` names. Modern StarlingX (Debian 11) uses predictable names. Always MAC-match using `virsh domiflist` on the host mapped to `ip a` on the VM.

---

## 2. Environment Prep (Host)

### Scorched Earth (wipe previous deployment)
```bash
for vm in $(virsh list --all --name | grep controllerstorage); do
    virsh destroy $vm 2>/dev/null
    virsh undefine $vm --nvram 2>/dev/null
done

for i in {1..4}; do
    sudo ip link set dev stxbr$i down 2>/dev/null
    sudo ip link delete stxbr$i type bridge 2>/dev/null
done

sudo ip route flush 10.10.10.0/24 2>/dev/null
sudo ip route flush 192.168.204.0/24 2>/dev/null
```

### Clone & patch the deployment scripts
```bash
cd /tmp
rm -rf virtual-deployment
git clone https://opendev.org/starlingx/virtual-deployment.git
cd virtual-deployment/libvirt
```

### Fix: Nehalem CPU architecture bug
The `virtual-deployment` XML templates hardcode a 2008 Intel Nehalem CPU. Modern Debian kernels throw illegal instruction faults and hang at `Booting from Hard Disk...`. Patch to `host-passthrough`:
```bash
python3 -c "
import glob, re
for path in glob.glob('/tmp/virtual-deployment/libvirt/xml/*.xml'):
    with open(path, 'r') as f: text = f.read()
    patched = re.sub(r\"<cpu match='exact'>\s*<model fallback='forbid'>Nehalem</model>\s*(<topology[^>]+>).*?</cpu>\", r\"<cpu mode='host-passthrough' check='none'>\n    \g<1>\n  </cpu>\", text, flags=re.DOTALL)
    with open(path, 'w') as f: f.write(patched)
"
```

### Fix: Use the Release 10 ISO
The latest upstream ISO (`20260422`) fatally crashes on a deprecated Docker manifest (`quay.io/stackanetes/kubernetes-entrypoint:v0.3.1`). The author confirmed Release 10 (`20250125`) works.
```bash
sudo cp ~/Downloads/downloads/starlingx-intel-x86-64-20250125173922-cd.iso /var/lib/libvirt/images/
export ISO_PATH=/var/lib/libvirt/images/starlingx-intel-x86-64-20250125173922-cd.iso
```

### Build bridges & VMs
```bash
sudo bash setup_network.sh
sudo bash setup_configuration.sh -c controllerstorage -i $ISO_PATH
```

---

## 3. Pre-Ansible Network Hotwire (controller-0 VM)

The Ansible bootstrap crashes immediately with `Nexthop has invalid gateway` because the OAM interface hasn't been configured yet. We must manually bind the IP **before** running Ansible.

```bash
virsh console controllerstorage-controller-0
# Login: sysadmin / sysadmin → change to Password0102030!
```

```bash
sudo ip address add 10.10.10.3/24 dev enp2s1
sudo ip link set up dev enp2s1
sudo ip route add default via 10.10.10.1 dev enp2s1
ping -c 4 8.8.8.8   # Must succeed (0% loss)
```

### Switch to SSH (escape serial console with `Ctrl+]`)
The serial console has a tiny buffer that corrupts long paste commands. SSH prevents this:
```bash
ssh-keygen -f '/home/jdavidp/.ssh/known_hosts' -R '10.10.10.3'
ssh sysadmin@10.10.10.3
```

---

## 4. Ansible Bootstrap

### Write the duplex localhost.yml
```bash
sudo mkdir -p /home/sysadmin
cat << 'EOF' | sudo tee /home/sysadmin/localhost.yml
system_mode: duplex

admin_username: admin
admin_password: Password0102030!
sysadmin_password: Password0102030!

dns_servers:
  - 8.8.8.8
  - 8.8.4.4

pxeboot_subnet: 169.254.202.0/24
pxeboot_start_address: 169.254.202.1
pxeboot_end_address: 169.254.202.254

management_subnet: 192.168.204.0/24
management_start_address: 192.168.204.1
management_end_address: 192.168.204.254
management_multicast_subnet: 239.1.1.0/28

cluster_host_subnet: 192.168.206.0/24
cluster_host_start_address: 192.168.206.1
cluster_host_end_address: 192.168.206.254

cluster_pod_subnet: 172.16.0.0/16
cluster_service_subnet: 10.96.0.0/12

oam_subnet: 10.10.10.0/24
oam_gateway_address: 10.10.10.1
oam_floating_address: 10.10.10.2
oam_node_0_address: 10.10.10.3
oam_node_1_address: 10.10.10.4
EOF
```

> **Key difference from Simplex:** Uses `oam_*` keys instead of `external_oam_*`, and requires `oam_node_0_address` + `oam_node_1_address` for the dual-controller setup.

> **Warning:** The author's config included `management_interface: ens2`, which we stripped because it's a CentOS naming convention. This caused Ansible to bind `mgmt` and `cluster-host` to the loopback (`lo`) instead of a physical interface — resulting in a "cannot unlock on virtual interface" error later. This was fixable via live surgery (see Section 6).

### Run the bootstrap
```bash
sudo ansible-playbook /usr/share/ansible/stx-ansible/playbooks/bootstrap.yml \
  -e "override_files_dir=/home/sysadmin" -v
```

**Result:** `failed=0` after ~18 minutes. Image download took ~654s (all cached from previous runs).

---

## 5. Control Plane CPR (Post-Bootstrap, Pre-Unlock)

Immediately after Ansible finishes, the control plane enters a deadlock cascade. **Do NOT unlock the node yet.** Apply these fixes first:

### 5.1 DNS Identity Fix
Ansible maps `controller.internal` incorrectly. We must point it to the Floating VIP where Keystone actually listens:
```bash
sudo vi /etc/hosts
# Add 'controller.internal' and 'controller-0.internal' to the correct lines:
# 192.168.204.2    controller-0 controller-0.internal
# 192.168.204.1    controller controller.internal registry.local controller-platform-nfs
```

> ⚠️ **Critical:** Do NOT use a broad `sed 's/192.168.204.2/192.168.204.1/g'` — this will overwrite the node's own hostname mapping and crash the Service Manager's identity resolution. This happened to us and required a full re-bootstrap.

### 5.2 HTTP/HTTPS Protocol Mismatch Fix
`sysinv-api` talks to Keystone via plain HTTP, but HAProxy enforces SSL:
```bash
sudo sed -i 's/http:\/\/controller.internal/https:\/\/controller.internal/g' /etc/sysinv/sysinv.conf
```

### 5.3 HAProxy Circular Backend Fix
HAProxy's backend points to `controller.internal:5000`, which resolves back to its own front door:
```bash
sudo sed -i 's/controller.internal:5000/192.168.204.1:5000/g' /etc/haproxy/haproxy.cfg
```

### 5.4 Service Restart
```bash
sudo systemctl restart sysinv-api.service sm.service
```

### 5.5 Loopback Audit Bypass (iptables)
The Service Manager health-checks HAProxy and the registry via `127.0.0.1`. Because of our DNS bypass, they refuse the connection. NAT-redirect loopback to the management IP:
```bash
sudo iptables -t nat -I OUTPUT -d 127.0.0.1 -p tcp --dport 9002 -j DNAT --to-destination 192.168.204.1:9002
sudo iptables -t nat -I OUTPUT -d 127.0.0.1 -p tcp --dport 5000 -j DNAT --to-destination 192.168.204.1:5000
```

### Verify
```bash
sudo sm-dump | grep haproxy
# haproxy  enabled-active  enabled-active
```

---

## 6. Interface Re-assignment (Live Surgery)

Because we omitted `management_interface` from the bootstrap config, Ansible bound `mgmt` and `cluster-host` to the loopback. StarlingX refuses to unlock with management on a virtual interface. We fixed this without re-bootstrapping:

```bash
source /etc/platform/openrc

# Check current assignments
system interface-network-list controller-0
# lo → mgmt, lo → cluster-host   ← WRONG

# Strip networks off loopback (use UUIDs from above command)
system interface-network-remove <mgmt-uuid>
system interface-network-remove <cluster-host-uuid>

# Bind to correct physical interfaces
system host-if-modify controller-0 enp2s2 -c platform
system interface-network-assign controller-0 enp2s2 mgmt

system host-if-modify controller-0 enp3s0 -c platform
system interface-network-assign controller-0 enp3s0 cluster-host

# Bind OAM
system host-if-modify controller-0 enp2s1 -c platform
system interface-network-assign controller-0 enp2s1 oam
```

### Configure Ceph storage
```bash
system host-disk-list controller-0
# /dev/sdb = 200GB unallocated

system host-stor-add controller-0 osd <sdb-uuid>
system storage-backend-add ceph --confirmed
```

---

## 7. Unlock controller-0

### Fix: UUID Parse Error
The first `system host-unlock` threw a Python `TypeError: one of the hex, bytes, bytes_le, fields, or int arguments must be given` because the live interface surgery left `config_target` as `None`. Fixed by bouncing the conductor:
```bash
sudo systemctl restart sysinv-conductor.service
system host-unlock controller-0
```

**Result:** `task: Unlocking` — node reboots.

### Post-Reboot Recovery
After every reboot, **Puppet wipes** manual `/etc/hosts` and `iptables` changes. Must re-apply the CPR:

1. Wait ~5 min for Floating VIP (`192.168.204.1`) to bind to `enp2s2`
2. Re-edit `/etc/hosts` (add `controller.internal`, `controller-0.internal`)
3. Re-apply `sed` patches on `sysinv.conf` and `haproxy.cfg`
4. Re-apply `iptables` NAT rules
5. Restart SM: `sudo systemctl restart sm.service`

```bash
source /etc/platform/openrc
system host-list
# controller-0 | unlocked | disabled | intest   → then → available ✅
```

---

## 8. Controller-1 Sync (UNRESOLVED ❌)

This is where we hit a wall. The objective was to PXE boot controller-1 from controller-0 to form the Duplex HA pair.

### What We Tried

**Problem 1: dnsmasq not running**
`controller-0` is supposed to act as the PXE/DHCP server, but `dnsmasq` never started. Root cause: missing config file at `/opt/platform/config/24.09//dnsmasq.addn_conf` (note the double-slash — a path construction bug). Creating the file manually allowed `dnsmasq --test` to pass, but the `systemd` wrapper still refused to start it.

**Problem 2: `virtual-deployment` script spawns incompatible VMs**
The `setup_configuration.sh` script creates controller-1 with:
- Legacy BIOS (but StarlingX PXE installer writes an EFI bootloader)
- `pc-q35-xenial` machine type (modern Debian 11 kernels crash on this)
- Fragmented CPU topology (4 sockets × 1 core — causes 0MB RAM report)

**Fix attempts:**
- `virsh edit` to inject `<os firmware='efi'>` and change machine type to `q35`
- Virt-Manager to force 1 Socket, 4 Cores, 1 Thread topology
- `system host-delete controller-1` to clear stale inventory
- Disk wipe via `qemu-img create` to remove legacy partition tables

**Result:** controller-1 either hung at `Booting from Hard Disk...` (CPU 100%, disk I/O 0), got `PXE-E16: No valid offer received`, or received `Access Denied` from controller-0's PXE service.

### Root Cause
The `virtual-deployment` repository's scripts are designed for CentOS-era StarlingX and have not been updated for the modern Debian-based releases. The VM hardware defaults are fundamentally incompatible with the UEFI-based installer.

### Recommended Next Step
For the next attempt, skip the `setup_configuration.sh` script entirely for controller-1 and use `virt-install` with correct settings from the start:
```bash
virt-install \
  --name controllerstorage-controller-1 \
  --ram 28672 \
  --vcpus 4 \
  --cpu host-passthrough,cache.mode=passthrough \
  --disk path=/var/lib/libvirt/images/controllerstorage-controller-1-0.img,size=500,bus=sata,format=qcow2 \
  --os-variant=debian11 \
  --network bridge=stxbr1,model=virtio \
  --network bridge=stxbr2,model=virtio \
  --network bridge=stxbr3,model=virtio \
  --network bridge=stxbr4,model=virtio \
  --boot firmware=efi \
  --graphics vnc \
  --noautoconsole
```
Then manually set topology in Virt-Manager to **1 Socket, 4 Cores, 1 Thread** before the first PXE boot.

---

## 9. Cleanup & Session Management

### Shut down controller-0 properly
```bash
source /etc/platform/openrc
system host-lock controller-0    # Graceful platform stop
sudo shutdown now                # Or from host: virsh shutdown controllerstorage-controller-0
```

### Clean up controller-1 (already done)
```bash
virsh destroy controllerstorage-controller-1
virsh undefine controllerstorage-controller-1 --nvram
sudo rm -f /var/lib/libvirt/images/controllerstorage-controller-1-0.img
```

### Re-enter a session
```bash
virsh start controllerstorage-controller-0
# Wait ~5 min for boot + SM promotion
ssh sysadmin@10.10.10.3
source /etc/platform/openrc
system host-list
```

> If `system host-list` returns `HTTP 500`, re-apply the CPR patches from Section 5 — Puppet wipes them on every reboot.

---

## Issues Summary

| # | Issue | Root Cause | Fix |
|---|---|---|---|
| 1 | Ansible crash: `Nexthop has invalid gateway` | OAM interface not configured before bootstrap | Manual IP hotwire before Ansible (Section 3) |
| 2 | `system host-list` returns `None` | HAProxy routing loop + HTTP/HTTPS mismatch | `sed` patches on `sysinv.conf` + `haproxy.cfg` (Section 5) |
| 3 | HAProxy stuck in `enabling-throttle` | SM health-checks via loopback → connection refused | `iptables` NAT redirect (Section 5.5) |
| 4 | SM identity crisis (`sm.db not available`) | Broad `sed` clobbered node hostname mapping | Manual `vi /etc/hosts` — never use wildcards (Section 5.1) |
| 5 | `Cannot unlock on virtual interface` | Missing `management_interface` in config | Live interface re-assignment (Section 6) |
| 6 | UUID `TypeError` on unlock | Live surgery left `config_target` as None | Restart `sysinv-conductor` (Section 7) |
| 7 | Puppet wipes all manual fixes on reboot | By design — Puppet enforces config on state transitions | Re-apply CPR after every reboot (Section 7) |
| 8 | controller-1 PXE boot fails | `virtual-deployment` scripts use legacy BIOS/CPU defaults | Use `virt-install` with UEFI + correct topology (Section 8) |
| 9 | dnsmasq won't start | Missing `/opt/platform/config/24.09//dnsmasq.addn_conf` | Created manually — but `systemd` wrapper still fails |
| 10 | Deprecated Docker manifest crash | `kubernetes-entrypoint:v0.3.1` uses dropped v1 schema | Use Release 10 ISO instead of latest (Section 2) |
