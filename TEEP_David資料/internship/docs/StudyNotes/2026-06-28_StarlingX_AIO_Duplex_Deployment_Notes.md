---
title: StarlingX 10.0 AIO-Duplex Deployment on Archimedes — Process Log & Fix Catalogue
---

# StarlingX 10.0 AIO-Duplex Deployment on Archimedes
**Date:** June 19–28, 2026
**OS Base:** Red Hat Enterprise Linux 9 (Archimedes Host), StarlingX 10.0 / Debian (Cluster VMs)
**STX Version:** `24.09` (Build `20250124T210100Z`)
**Server:** Archimedes (`192.168.8.13`)
**Objective:** Deploy a 2-node HA StarlingX AIO-Duplex cluster following the lab handover guide
**Outcome:** 🟡 **In Progress** — `controller-0` fully operational (`available`); `controller-1` reaching `online` state after database surgery, final HA sync pending

---

## 1. Architecture Overview

### Physical Infrastructure
| Item | Detail |
|---|---|
| Server | Archimedes (`192.168.8.13`) |
| Login | `intel` / `bmwlab` → then `sudo -i` |
| Cockpit | `https://192.168.8.13:9090` |
| Root Storage | `/dev/mapper/rhel-root` — only 70 GB (too small) |
| Home Storage | `/dev/mapper/rhel-home` — 856 GB → **VM images stored here** |
| RAM | 92 GB total |
| StarlingX ISO | `mirror.starlingx.windriver.com/.../10.0.0/debian/monolithic/` |

### Virtual Network Layout
Four manual Linux bridges forward traffic from the host NIC (`eno2`) to the VMs:
| Bridge | Subnet | Role |
|---|---|---|
| `stxbr1` | `192.168.214.0/24` | Management Network |
| `stxbr2` | `10.10.10.0/24` | OAM Network |
| `stxbr3` | `192.168.215.0/24` | Cluster-Host Network |
| `stxbr4` | `192.168.216.0/24` | PXE Boot Network |

### VM-to-Interface Mapping (Per Controller)
| VM NIC | Physical Port | Bridge | Network Role |
|---|---|---|---|
| NIC 1 | `enp1s0` | `stxbr2` | OAM |
| NIC 2 | `enp2s0` | `stxbr1` | **Management** |
| NIC 3 | `enp3s0` | `stxbr3` | Cluster-Host |
| NIC 4 | `enp4s0` | `stxbr4` | PXE Boot |

> **Critical:** The Management and PXE networks are on *different* physical cables. This single fact caused the majority of the deployment's problems (see §6).

### controller-0 Final Interface Map
```
[sysadmin@controller-0 ~(keystone_admin)]$ system host-if-list controller-0
+----------+----------+----------+------------+
| name     | class    | type     | ports      |
+----------+----------+----------+------------+
| mgmt0    | platform | ethernet | ['enp2s0'] |
| oam0     | platform | ethernet | ['enp1s0'] |
| cluster0 | platform | ethernet | ['enp3s0'] |
| pxe0     | platform | ethernet | ['enp4s0'] |
+----------+----------+----------+------------+
```

---

## 2. Phase 1 — Hypervisor Preparation & VM Creation

### SATA-Bus Requirement
Virtual disks **must** be attached to the `sata` bus. StarlingX's LVM filter (`cgts-vg`) rejects `virtio`-based block devices entirely. All `virsh`/`virt-install` commands were run with `--disk bus=sata`.

### VM Specifications (Per Controller)
```xml
<vcpu>4</vcpu>
<memory unit='GiB'>16</memory>
<!-- OS disk -->
<disk type='file' device='disk'>
  <source file='/home/intel/stx-images/controller-X-disk0.qcow2'/>
  <target dev='sda' bus='sata'/>
</disk>
<!-- Data disk (for cgts-vg) -->
<disk type='file' device='disk'>
  <source file='/home/intel/stx-images/controller-X-disk1.qcow2'/>
  <target dev='sdb' bus='sata'/>
</disk>
<!-- UEFI/OVMF firmware -->
<os>
  <type arch='x86_64'>hvm</type>
  <loader readonly='yes' type='pflash'>/usr/share/edk2/ovmf/OVMF_CODE.fd</loader>
  <boot dev='cdrom'/>
</os>
```

### ISO Boot
The StarlingX 10.0 ISO was attached as a virtual CD-ROM. After initial boot, the installer performed an Anaconda-based Debian install. The CD-ROM was detached post-install and boot order changed to `<boot dev='hd'/>`.

---

## 3. Phase 2 — controller-0 Bootstrap

### Ansible Bootstrap Configuration
The bootstrap is driven by `localhost.yml` placed in the sysadmin home directory:
```yaml
# /home/sysadmin/localhost.yml
system_mode: duplex
dns_servers:
  - 8.8.8.8
external_oam_subnet: 10.10.10.0/24
external_oam_gateway_address: 10.10.10.1
external_oam_floating_address: 10.10.10.2
external_oam_node_0_address: 10.10.10.3
external_oam_node_1_address: 10.10.10.4
management_subnet: 192.168.214.0/24
management_start_address: 192.168.214.2
management_end_address: 192.168.214.50
admin_password: Bmvlabece@13
ansible_become_pass: Bmvlabece@13
```

```bash
ansible-playbook /usr/share/ansible/stx-ansible/playbooks/bootstrap.yaml
```

### Keyring Bypass (Fix #1)
The `virsh console` serial interface hangs whenever the OpenStack CLI attempts to access the Python keyring daemon. This must be disabled **before** sourcing `openrc`.

```bash
# Permanent fix: create keyring override files
mkdir -p /home/sysadmin/.config/python_keyring
cat > /home/sysadmin/.config/python_keyring/keyringrc.cfg << 'EOF'
[backend]
default-keyring=keyring.backends.null.Keyring
EOF

# Also inject into openrc so every CLI call bypasses keyring
cat >> /etc/platform/openrc << 'EOF'
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
export OS_CLIENT_USE_KEYRING=False
EOF
```

> **Lesson:** Without this fix, every `system host-list` or `fm alarm-list` call will freeze the serial terminal indefinitely. Apply before touching any STX CLI.

### openrc "Active Controller" Patch (Fix #2)
The default `/etc/platform/openrc` exits with a fatal error if it detects no "active controller" in the Service Management database. During early bootstrap, this check always fails.

```bash
# Removed the forced-exit block that kills the shell if SM isn't up yet
# Original lines contained: "Active controller not yet available" → exit 1
sudo sed -i '/Active controller not yet available/,/exit 1/d' /etc/platform/openrc
```

---

## 4. Phase 3 — controller-0 Service Recovery

After bootstrap, `controller-0` appeared stuck in `intest` availability, and multiple CLI commands returned HTTP 500 errors. This section documents the three service-level fixes required to reach `available`.

### DNS Resolution Deadlock (Fix #3)
The Keystone identity service and Sysinv API both resolve internal hostnames (`controller.internal`, `controller-0.internal`) via DNS. But the DNS server (`dnsmasq`) is managed by StarlingX itself and was not yet running. A classic deadlock.

```
(HTTP 500) Internal Server Error
```

**Fix:** Manual `/etc/hosts` injection to bypass DNS entirely.
```bash
sudo bash -c 'cat >> /etc/hosts << EOF
192.168.214.1   controller controller.internal
192.168.214.2   controller-0 controller-0.internal
EOF'
```

### dnsmasq Crash (Fix #4)
The `dnsmasq` service crashed on startup because it expected a configuration file that didn't exist yet.

```bash
# Create the missing config file (empty is fine — just needs to exist)
sudo mkdir -p /opt/platform/config/24.09
sudo touch /opt/platform/config/24.09/dnsmasq.addn_conf

# Restart the service
sudo systemctl restart dnsmasq
```

### Sysinv-API Port Binding (Fix #5)
After resolving DNS, `system host-list` returned a *different* HTTP 500, this time because `sysinv-api` (port `6385`) hadn't started. This resolved itself after restarting Sysinv:

```bash
sudo systemctl restart sysinv-api
sudo systemctl restart sysinv-conductor
```

### controller-0 Reaching `available`
After fixes #3–#5, the Fault Management service (`fm-api`) was restarted to clear stale alarms:
```bash
sudo systemctl restart fm-api
```

The maintenance agent (`mtc-agent`) eventually completed its sensor checks and transitioned `controller-0` from `intest` → `available`:
```
[sysadmin@controller-0 ~(keystone_admin)]$ system host-list
+----+--------------+-------------+----------------+-------------+--------------+
| id | hostname     | personality | administrative | operational | availability |
+----+--------------+-------------+----------------+-------------+--------------+
| 1  | controller-0 | controller  | unlocked       | enabled     | available    |
+----+--------------+-------------+----------------+-------------+--------------+
```

---

## 5. Phase 4 — controller-1 PXE Installation

### TianoCore UEFI Boot Manager
The OVMF/UEFI KVM configuration does not auto-PXE. The VM drops into the TianoCore EFI shell on first boot. Navigation:
1. Type `exit` in the EFI shell to reach the Boot Manager menu.
2. Select `UEFI PXEv4 (MAC:525400095182)` — the **4th** PXE option, corresponding to `enp4s0` (the PXE network bridge).
3. The ramdisk downloads from `controller-0` and drops into a GRUB screen: `Waiting for this node to be configured.`

> **Note:** The `ESC` key spam technique to intercept boot does not work on virtual serial consoles. The only reliable way to reach the Boot Manager is to let all boot options fail, which drops to the EFI shell, then type `exit`.

### Auto-Discovery vs. Pre-Provisioning
When `controller-1` PXE-boots, `controller-0` auto-discovers it as a blank node (`personality=None`). The personality must be assigned:
```bash
system host-update <ID> hostname=controller-1 personality=controller
```
This triggers the Anaconda OS installation onto `controller-1`'s virtual disk.

---

## 6. The MAC Address Catch-22

This was the central, defining problem of the entire deployment.

### The Trap
StarlingX uses the MAC address of the PXE boot interface as the node's permanent `mgmt_mac`. Because PXE boots over `enp4s0` but the actual management network is on `enp2s0`, the database permanently binds the management IP (`192.168.214.3`) to the **wrong** physical cable.

| What We Need | What the DB Records |
|---|---|
| `mgmt` → `enp2s0` (`52:54:00:cc:91:a1`) | `mgmt` → `enp4s0` (`52:54:00:09:51:82`) |

### Why It Can't Be Fixed Pre-Installation
Every approach was tried and failed:

| Approach | Result |
|---|---|
| Pre-provision with correct MAC (`-m 52:54:00:cc:91:a1`) | PXE boot from `enp4s0` is ignored — MAC doesn't match |
| Auto-discover, then `host-update mgmt_mac=...` | `Change contains restricted {'mgmt_mac'}` — field is locked |
| `-i` / `-b` flags for separate boot/mgmt MAC | Flags don't exist in STX 24.09 CLI |
| `host-port-add` to register secondary port | Command doesn't exist in STX 24.09 |
| Boot PXE from `enp2s0` directly | Times out — `dnsmasq` only listens on the PXE bridge |

### The Solution: Post-Install Database Surgery (Fix #6)
After the node installs and reaches `online`, we surgically swap the interface assignments in `controller-0`'s database:

```bash
# 1. Lock the node
system host-lock -f controller-1
# (Wait for task field to clear)

# 2. Get the UUID of the wrong mgmt network assignment
system interface-network-list controller-1
# → d0d70852-1443-4971-bb54-8d977189d6cc  mgmt0  mgmt

# 3. Sever the wrong assignment
system interface-network-remove d0d70852-1443-4971-bb54-8d977189d6cc

# 4. Rename enp4s0 from mgmt0 to pxe0
system host-if-modify controller-1 mgmt0 -n pxe0

# 5. Build the real mgmt0 on enp2s0
system host-if-modify controller-1 enp2s0 -n mgmt0 -c platform

# 6. Bind networks to correct ports
system interface-network-assign controller-1 pxe0 pxeboot
system interface-network-assign controller-1 mgmt0 mgmt
```

**Result:** The database now correctly maps all four interfaces:
```
system host-if-list controller-1
+----------+----------+----------+------------+
| name     | class    | type     | ports      |
+----------+----------+----------+------------+
| mgmt0    | platform | ethernet | ['enp2s0'] |
| oam0     | platform | ethernet | ['enp1s0'] |
| cluster0 | platform | ethernet | ['enp3s0'] |
| pxe0     | platform | ethernet | ['enp4s0'] |
+----------+----------+----------+------------+
```

---

## 7. Phase 5 — The "Frankenstein Patch" (controller-1 Configuration)

After the OS installs, `controller-1` is a working Linux box but a brain-dead cluster node. The `controllerconfig.service` crashes in a loop because of two interacting bugs: the wrong network cable and the IPsec firewall.

### 7.1 — Stop the Crashing Loop
```bash
# On controller-1
sudo systemctl stop controllerconfig.service
sudo rm -f /var/run/.config_fail /var/run/.config_pass
```

### 7.2 — Live-RAM Network Bypass
Because the OS has the management IP on `enp4s0` (wrong cable), we manually move it:
```bash
# On controller-1
sudo ip addr del 192.168.214.3/24 dev enp4s0 2>/dev/null
sudo ip link set enp2s0 up
sudo ip addr add 192.168.214.3/24 dev enp2s0

# Verify
ping -c 4 192.168.214.2
# Must return 0% packet loss
```

> **Warning:** This hack lives in RAM only. Every reboot reverts it. The database surgery (§6) is what makes it permanent.

### 7.3 — IPsec/xfrm Firewall Bypass (Fix #7)
StarlingX 24.09 applies kernel-level IPsec (`xfrm`) policies that block NFS and management traffic between controllers. Additionally, Reverse Path filtering (`rp_filter`) drops packets arriving on unexpected interfaces.

**On controller-0:**
```bash
C0_IP="192.168.214.2"
MGMT_IF=$(ip -o -4 addr show | awk -v ip="$C0_IP" '$4 ~ ip"/" {print $2; exit}')

sudo sysctl -w net.ipv4.conf.all.rp_filter=0
sudo sysctl -w net.ipv4.conf.default.rp_filter=0
sudo sysctl -w net.ipv4.conf.${MGMT_IF}.rp_filter=0

sudo ip xfrm policy add src 192.168.214.2/32 dst 192.168.214.3/32 dir out priority 100 action allow 2>/dev/null || true
sudo ip xfrm policy add src 192.168.214.3/32 dst 192.168.214.2/32 dir in priority 100 action allow 2>/dev/null || true
sudo ip xfrm policy add src 192.168.214.1/32 dst 192.168.214.3/32 dir out priority 100 action allow 2>/dev/null || true
sudo ip xfrm policy add src 192.168.214.3/32 dst 192.168.214.1/32 dir in priority 100 action allow 2>/dev/null || true
```

**On controller-1:**
```bash
C0_IP="192.168.214.2"
C1_IP="192.168.214.3"
VIP_IP="192.168.214.1"
MGMT_IF=$(ip -o -4 addr show | awk -v ip="$C1_IP" '$4 ~ ip"/" {print $2; exit}')

sudo sysctl -w net.ipv4.conf.all.rp_filter=0
sudo sysctl -w net.ipv4.conf.default.rp_filter=0
sudo sysctl -w net.ipv4.conf.${MGMT_IF}.rp_filter=0

sudo ip xfrm policy add src ${C1_IP}/32 dst ${C0_IP}/32 dir out priority 100 action allow
sudo ip xfrm policy add src ${C0_IP}/32 dst ${C1_IP}/32 dir in  priority 100 action allow
sudo ip xfrm policy add src ${C1_IP}/32 dst ${VIP_IP}/32 dir out priority 100 action allow
sudo ip xfrm policy add src ${VIP_IP}/32 dst ${C1_IP}/32 dir in  priority 100 action allow
```

### 7.4 — Patch `controller_config` Script (Fix #8)
The setup script resolves `controller-platform-nfs` via DNS. Since DNS isn't up yet, we hardcode VIP addresses:
```bash
# On controller-1
sudo cp /etc/init.d/controller_config /etc/init.d/controller_config.bak.$(date +%Y%m%d_%H%M%S)

sudo sed -i \
's|curl -sf http://controller:${http_port}/feed/rel-${SW_VERSION}/install_uuid|curl -sf http://192.168.214.1:${http_port}/feed/rel-${SW_VERSION}/install_uuid|' \
/etc/init.d/controller_config

sudo sed -i 's|controller-platform-nfs:|192.168.214.1:|g' /etc/init.d/controller_config
sudo sed -i 's| controller-platform-nfs| 192.168.214.1|g' /etc/init.d/controller_config
```

### 7.5 — Connectivity Test
```bash
sudo /usr/local/bin/connectivity_test -t 10 -i 192.168.214.3 192.168.214.1
echo "exit=$?"
# exit=0  ← SUCCESS
```

### 7.6 — Manual Configuration Execution
```bash
sudo rm -f /var/run/.config_fail /var/run/.config_pass
sudo bash -x /etc/init.d/controller_config start 2>&1 | tee /tmp/controller_config.debug.log
echo "exit=${PIPESTATUS[0]}"
```

#### First Failure: Missing Puppet Hieradata
The script successfully mounted NFS, copied certificates, synced puppet cache, but crashed at:
```
fatal_error 'Host configuration not yet available for this node
(controller-1=192.168.214.3); aborting configuration.'
```
**Cause:** `controller-1.yaml` did not exist in `/opt/platform/puppet/24.09/hieradata/`.
**Fix:** Restart `sysinv-agent` and `mtcClient` on `controller-1` to force inventory report. This pushed `controller-1` to `online` in `host-list`, which triggered `controller-0` to generate the `.yaml` file.

```bash
# On controller-1
sudo systemctl restart sysinv-agent
sudo systemctl restart mtcClient
```

```bash
# Verify on controller-0
ls -l /opt/platform/puppet/24.09/hieradata/controller-1.yaml
# -rw------- 1 root root 20995 Jun 22 19:53 controller-1.yaml  ← EXISTS
```

---

## 8. Phase 6 — Interface Amnesia & Unlock Cycle

### The Problem: Node Had No OAM/Cluster Config
When we deleted the pre-provisioned ghost node (ID 10) to resolve the MAC Catch-22, we vaporized its entire network configuration profile. The auto-discovered replacement (ID 11) only knew about `enp4s0` (PXE). It had no OAM or Cluster-Host interface configured.

### Rebuilding the Profile
We used `system host-unlock controller-1` as a diagnostic — it rejects the unlock and prints the exact missing requirement.

**Missing OAM interface:**
```
Can not unlock a controller host without an oam interface.
```
```bash
system host-if-modify controller-1 enp1s0 -n oam0 -c platform
system interface-network-assign controller-1 oam0 oam
```

**Missing Cluster-Host interface:**
```
Cannot unlock host controller-1 without configuring a cluster-host interface.
```
```bash
system host-if-modify controller-1 enp3s0 -n cluster0 -c platform
system interface-network-assign controller-1 cluster0 cluster-host
```

### Successful Unlock
With all four interfaces mapped, the unlock succeeded:
```
| task | Unlocking |
```
This triggered Puppet to apply manifests and gracefully reboot `controller-1`.

---

## 9. Phase 7 — The Reboot Loop & Poisoned Cache

### The Core Problem
After every reboot, `controller-1` boots with the management IP on `enp4s0` (wrong cable) and the IPsec firewall active. It cannot reach `controller-0` to download the corrected blueprint. It panics and falls back to its **local cached hieradata** — which was generated *before* our database surgery and still contains the toxic `mgmt → enp4s0` mapping.

```
No active controller found, will try to config using local cached hieradata.
```

This creates a vicious cycle: every reboot re-applies the wrong configuration.

### Breaking the Loop
**1. Force lock the node:**
```bash
system host-lock -f controller-1
# Wait for task field to clear
```

**2. Burn the poisoned cache (on controller-1):**
```bash
sudo rm -rf /etc/puppet/cache/hieradata/*
```

**3. Stop the auto-config service, apply full Frankenstein patch** (§7.1 through §7.4).

**4. Manually execute `controller_config`** while the tunnel is open.

**5. Unlock from controller-0** the instant the tunnel is up:
```bash
system host-unlock controller-1
```

### The Critical Timing
The "smash and grab" technique: apply the live-RAM network hack on `controller-1`, then *immediately* run `system host-unlock controller-1` on the master node before the tunnel drops. This forces `controller-1` to download the fresh blueprint over the live connection instead of using the poisoned cache.

When the script reaches `Applying puppet controller manifest...`, Puppet rewrites the network configuration to disk, then initiates a graceful reboot:
```
Applying puppet controller manifest...
         Stopping Session 1 of user sysadmin.
[  OK  ] Stopped target Multi-User System.
```

---

## 10. Current Status & Known Issues

### Cluster State (As of June 28, 2026)

| Node | Administrative | Operational | Availability |
|---|---|---|---|
| controller-0 | unlocked | enabled | **available** ✅ |
| controller-1 | unlocked | disabled | online → failed (cycling) |

### What Works
- `controller-0` is fully operational and stable
- Database surgery is confirmed persistent — `mgmt0 → enp2s0` in the interface list
- `config_status: None` — no configuration errors remain
- `controller-1` reaches `online` natively after successful Puppet runs

### Remaining Blockers

| Issue | Description | Severity |
|---|---|---|
| Puppet cache fallback | If `controller-1` boots without active tunnel, it reads stale hieradata and re-applies wrong config | 🔴 Critical |
| `Reboot Failed` ghost state | Maintenance Agent freezes on stale reboot ticket; requires `pkill -9 mtcAgent` to clear | 🟡 Major |
| 30-minute PXE timeout | Each reboot wastes ~5 min cycling through PXE options before falling to HDD boot | 🟡 Major |
| ATA/disk errors on forced shutdown | Virtual SATA controller throws `READ FPDMA QUEUED` errors during aggressive reboots — cosmetic only | 🟢 Minor |

### Next Steps
1. Clear the `Reboot Failed` state via `pkill -9 -f mtcAgent` on controller-0
2. Force-lock, re-apply the Frankenstein patch with burned cache, unlock
3. Monitor DRBD storage sync and HA service convergence
4. Once `controller-1` reaches `available`, strip `<boot dev='network'/>` from the VM XML to eliminate PXE timeout

---

## 11. CLI Quirks & Gotchas (STX 24.09)

| Bug | Symptom | Workaround |
|---|---|---|
| `ast.Name` parser crash | `system host-update controller-1 location="rack1"` → `malformed node or string` | Wrap values in single-inside-double quotes: `"'rack1'"` — or avoid the field entirely |
| `dictionary update` crash | Certain `host-update` key=value pairs crash the Python CLI parser | Restart `sysinv-conductor` to trigger config regeneration instead |
| `mgmt_mac` restriction | Cannot modify `mgmt_mac` on any discovered or provisioned host | Must delete and re-add the host, or use interface surgery |
| Binary log files | `grep` on `/var/log/sysinv.log` returns `binary file matches` | Always use `grep -a` (ascii mode) |
| `Host must be locked` race | Lock command visually returns but node stays `unlocked` if unreachable | Use `system host-lock -f controller-1` and poll `task` field until blank |

---

## 12. Fix Catalogue (Quick Reference)

| # | Fix | Where | Persists Across Reboot? |
|---|---|---|---|
| 1 | Keyring bypass (`null.Keyring`) | controller-0 | ✅ Yes (file-based) |
| 2 | `openrc` active-controller patch | controller-0 | ✅ Yes (file edit) |
| 3 | `/etc/hosts` DNS override | controller-0 | ✅ Yes (file edit) |
| 4 | `dnsmasq.addn_conf` dummy file | controller-0 | ✅ Yes (file create) |
| 5 | `sysinv-api` / `sysinv-conductor` restart | controller-0 | ⚠️ Service restarts are persistent |
| 6 | Interface database surgery (MAC swap) | controller-0 DB | ✅ Yes (database) |
| 7 | xfrm/rp_filter bypass | Both controllers | ❌ No — RAM only, lost on reboot |
| 8 | `controller_config` NFS hostname patch | controller-1 | ❌ No — script resets on reinstall |

---

## 13. Lessons Learned

### Architecture
- **StarlingX strictly binds `mgmt_mac` to the PXE boot interface.** If your management and PXE networks use different physical cables, you **must** perform post-install database surgery. There is no pre-provisioning workaround in STX 24.09.
- **SATA bus is mandatory for VM disks.** StarlingX's `cgts-vg` LVM filter silently rejects `virtio` block devices.
- **Serial consoles and Python keyring are incompatible.** The keyring backend must be explicitly set to `null` before any OpenStack CLI usage over `virsh console`.

### Deployment Strategy
- **Never delete a pre-provisioned host unless you plan to rebuild its entire interface profile.** The `system host-delete` command vaporizes OAM, Cluster-Host, and all network assignments — not just the personality.
- **The `controllerconfig.service` auto-start is the enemy.** It races ahead of manual fixes and writes failure flags before you can log in. Always `systemctl stop controllerconfig.service` as the very first action on a freshly booted sub-node.
- **Burn the Puppet cache** (`rm -rf /etc/puppet/cache/hieradata/*`) before every unlock attempt. Stale cached hieradata is the #1 cause of the reboot-to-wrong-interface loop.

### Operational Tips
- Use `system host-unlock` as a diagnostic tool — it prints the exact missing requirement before rejecting.
- Poll `system host-show controller-1 | grep task` obsessively. Never run commands while the `task` field is non-empty.
- The `fm alarm-list --nowrap` command is your best friend for understanding why a node is stuck in `failed`.
