---
title: OKD Hub Deployment on Newton - Verification Attempt and Failure Catalogue
---

# OKD Hub Deployment on Newton
**Date:** June 10-17, 2026  
**Host:** Newton (`192.168.8.53`)  
**Target:** OKD Hub VM (`master-0-vm`, `192.168.8.210`)  
**Reference guide:** [Local OKD deployment guide](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-05-20_OKD_Deployment_Notes.md)  
**Outcome:** Blocked during OKD Agent-Based Installer registration. The Newton/Kepler direct-lab attempt is separate from the successful local OKD guide and needs an internal mirror or disconnected-install preparation before it can be considered reproducible.

---

## 0. Blocker Video Documentation

Video Showcase: [YouTube Link](https://youtu.be/Lrx1OX6RnU8)

## 1. Scope and Relationship to the Local OKD Note

This was not the same attempt as the successful local OKD deployment note.

| Item | Local OKD note | Newton attempt |
|---|---|---|
| Note | `docs/StudyNotes/2026-05-20_OKD_Deployment_Notes.md` | This note |
| Host | `worker-rt` (`192.168.8.76`) | Newton (`192.168.8.53`) |
| Hub VM | `master-0-vm` (`192.168.8.210`) | `master-0-vm` (`192.168.8.210`) |
| Result | Hub and SNO workflow documented successfully | Hub VM reached assisted-service, then failed at agent registration |
| Main blocker | None for the local run after preflight fixes | Lab network / registry access for required OKD images |

The Newton host was shared with senior thesis data, so the host OS was off-limits. The authorized scope was only to remove stale VMs and reuse the existing `bridge0`.

---

## 2. Starting State and Authorizations

| Server | Role | Constraint |
|---|---|---|
| Newton (`192.168.8.53`) | OKD Hub host | Do not wipe host OS; only remove unused VMs |
| Kepler (`192.168.8.43`) | OKD slave node | Locked by existing SNO; intended to be reprovisioned later through Hub/ZTP |
| Archimedes (`192.168.8.13`) | StarlingX VM host | Separate STX track |

Newton had stale VMs: `master-0-vm`, `worker-0`, and `ctr-00`. `bridge0` already existed and was to be reused.

### Timeline Summary

The work from June 10 onward followed these phases:

| Phase | What happened | Result |
|---|---|---|
| Authorization and cleanup | Confirmed Newton could not be wiped, then removed only stale libvirt guests | Host OS preserved; old VM state cleared |
| Fresh `pti-rtp` setup | Re-cloned private repo, prepared Python/Ansible environment, installed virtualization dependencies and Go | OKD playbook could run from a clean baseline |
| Inventory and patching | Reused `bridge0`, created `br0-okd`, built inventory for `master-0-vm`, and applied the local-guide patches | Playbook reached VM creation and OpenShift installer wait |
| Bootstrap triage | Confirmed VM booted, had the intended MAC/IP, had DNS records, and had the ISO attached | Failure was not simple DNS, ARP, or libvirt attachment |
| Registry/network investigation | Tested DNS, Quay pulls, IPv6, offload, NAT, MTU, and host connectivity | Direct image pulls remained unreliable from the VM |
| Air-gap experiment | Side-loaded `scos-content.tar` and patched assisted-service image references | Assisted Service could start, but registration/token/env issues remained |
| Stop decision | Recorded evidence and moved Newton out of the verification path | Guide needs mirror/disconnected preparation before retry |

---

## 3. Newton Cleanup

The old Newton VM state was removed without touching the host OS:

```bash
virsh destroy master-0-vm
virsh destroy worker-0
virsh destroy ctr-00

virsh undefine master-0-vm --remove-all-storage
virsh undefine worker-0 --remove-all-storage
virsh undefine ctr-00 --remove-all-storage
```

Observed result:

- `master-0-vm` was running and was destroyed successfully.
- `worker-0` and `ctr-00` were already powered off, so `virsh destroy` returned "domain is not running".
- All three VM definitions and their associated images were removed by `virsh undefine --remove-all-storage`.

This confirmed Newton was ready for a fresh OKD Hub VM.

---

## 4. OKD Hub Preparation

The `pti-rtp` repository had to be cloned fresh because the existing working copy was dirty and on a non-baseline branch. The repository is private, so GitHub PAT authentication was required.

```bash
cd /root
rm -rf pti-rtp
git clone https://github.com/bmw-ece-ntust/pti-rtp.git
cd /root/pti-rtp/okd
sed -i '/^libvirt-python$/d' requirements.txt

python3 -m venv okd-env
source okd-env/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

System dependencies and Go were installed:

```bash
dnf install -y https://dl.fedoraproject.org/pub/epel/epel{,-next}-release-latest-9.noarch.rpm
dnf group install -y "Development Tools"
dnf install -y python3-devel python3-libvirt python3-netaddr ansible pip pkgconfig \
  libvirt-devel python-lxml nmstate wget make

dnf group install -y "Virtualization Host" "Virtualization Hypervisor" \
  "Virtualization Tools" "Virtualization Client"
systemctl enable --now libvirtd

wget https://go.dev/dl/go1.24.3.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
go version
```

Observed result: dependencies and Ansible collections installed cleanly; `go version` returned `go1.24.3 linux/amd64`.

The existing `/root/pti-rtp` checkout had local modifications on `bridge-mode`, so it was treated as disposable for this verification attempt. The fresh clone avoided mixing prior experimental edits with the guide-verification work.

---

## 5. Network and Inventory Configuration

Newton reused the existing `bridge0`; no host bridge recreation was needed.

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
```

The Hub VM inventory was built around `master-0-vm` at `192.168.8.210`:

```yaml
ocloud_cluster_name: "ocloud-vm-okd-aio"
ocloud_domain_name: "david.internal"
ocloud_network_mode: "bridge"
ocloud_net_bridge: "bridge0"
ocloud_net_name: "br0-okd"
ocloud_net_cidr: "192.168.8.0/24"
ocloud_dns_servers:
  - "192.168.8.72"
```

```yaml
role: master
ip_address: 192.168.8.210
ocloud_infra_vm_mem_gb: 48
mac_addresses:
  ens3: "52:54:00:ab:cd:01"
```

RHEL `noclobber` was enabled on Newton, so overwriting generated files required either removing the target file first or using `>|` for carefully selected shell redirections.

Important inventory/setup details:

- Newton generated and used `/root/.ssh/id_ed25519` for VM access.
- `vars.yml` used an unquoted heredoc when embedding the SSH public key so the key content expanded correctly.
- Generated inventory and patch files sometimes had to be removed first with `rm -f` because normal `>` redirection failed under `noclobber`.
- `/etc/resolv.conf` was treated carefully because it can be a managed file or symlink on RHEL; the safe overwrite form was `>| /etc/resolv.conf` rather than deleting it.
- The default route for the VM was through `192.168.8.9`, and DNS was pointed at the lab Pi-hole `192.168.8.72`.

---

## 6. Required Playbook Patches

The same guide-level patches from the local OKD workflow were applied:

1. Remove `libvirt-python` from `requirements.txt`.
2. Patch `virt.xml.j2` MAC lookup to avoid dictionary/interface mismatches.
3. Add `validate_certs: false` to Kubernetes module tasks that use the self-signed OKD API.
4. Extend Stolostron timeout.
5. Replace the O2IMS task flow to add `local-path-provisioner`, grant privileged SCC, set `local-path` as default StorageClass, and use `quay.io/sclorg/postgresql-16-c9s:c9s`.

DNS was pointed at the lab Pi-hole (`192.168.8.72`) and Newton `/etc/hosts` was amended for:

- `api.ocloud-vm-okd-aio.david.internal`
- `api-int.ocloud-vm-okd-aio.david.internal`
- `.apps.ocloud-vm-okd-aio.david.internal`
- `master-0.ocloud-vm-okd-aio.david.internal`

The O2IMS patch had to be reconstructed because the referenced conversation file from the local run was unavailable. The reconstructed task flow matched the successful local guide: install `local-path-provisioner`, grant the required SCC, set `local-path` as the default StorageClass, create the O2IMS namespace/resources, and patch PostgreSQL to the CentOS Stream image.

---

## 7. Deployment Progress

The playbook reached the virtual Hub deployment path:

```bash
cd /root/pti-rtp/okd
source okd-env/bin/activate
ansible-playbook -i inventory/hosts.yml playbooks/ocloud.yml
```

The VM was created, attached to `bridge0`, and visible on the network:

```bash
arp -n | grep 192.168.8.210
# 192.168.8.210 ether 52:54:00:ab:cd:01 C bridge0
```

The agent ISO was attached:

```bash
virsh dumpxml master-0-vm | grep -i iso
# /var/lib/libvirt/images/master-0-vm-image.iso
```

The OpenShift wait stage eventually timed out:

```text
Bootstrap failed to complete: bootstrap process timed out: context deadline exceeded
Get "https://api.ocloud-vm-okd-aio.david.internal:6443/...": dial tcp 192.168.8.210:6443: connect: connection refused
```

The installer log confirmed that the Agent-Based Installer never reached the expected API initialization state:

```text
Agent Rest API never initialized. Bootstrap Kube API never initialized.
```

The VM could be reached over SSH intermittently as `core@192.168.8.210`, but it repeatedly regenerated host keys or lost `authorized_keys` after resets, requiring:

```bash
ssh-keygen -R 192.168.8.210
ssh -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes \
  -i ~/.ssh/id_ed25519 core@192.168.8.210
```

Triage checks performed before moving to registry/network diagnosis:

```bash
virsh list --all
ping -c 4 192.168.8.210
dig @192.168.8.72 +short api.ocloud-vm-okd-aio.david.internal
grep -R "ssh-ed25519" inventory group_vars host_vars
arp -n | grep 192.168.8.210
virsh dumpxml master-0-vm | grep -i iso
```

Observed results:

- `master-0-vm` was running.
- `ping 192.168.8.210` worked.
- Pi-hole DNS returned `192.168.8.210` for the OKD API records.
- The ARP entry showed `52:54:00:ab:cd:01`, matching the inventory MAC and ruling out an obvious IP conflict.
- The ISO was attached as `master-0-vm-image.iso`.
- `virsh console master-0-vm` did not provide useful output because the guest console was not routed to serial.

---

## 8. Failure Point

The decisive failure was the Agent Registration phase, not VM creation.

What worked:

- Newton cleanup.
- Private `pti-rtp` checkout.
- Python/Ansible dependencies.
- Bridge reuse and `br0-okd` libvirt network.
- Hub VM creation.
- Static IP/MAC mapping for `master-0-vm`.
- Assisted Service could be made to start after local payload workarounds.

What failed:

- OKD bootstrap did not complete normally.
- `agent-register-cluster.service` and `agent-register-infraenv.service` failed during registration.
- Direct and indirect attempts to fetch required OKD payload metadata/images from `quay.io` were unstable or blocked.
- Host-side masquerading / gateway hijacking did not turn the attempt into a reproducible path.

Representative commands used to expose the failure:

```bash
sudo systemctl status assisted-service.service
sudo systemctl restart agent-register-cluster.service agent-register-infraenv.service
journalctl -u agent-register-cluster.service -n 30 --no-pager
```

The key evidence from the transcript is that the registration path still depends on external OKD images/metadata such as:

```text
quay.io/okd/scos-release@sha256:d50cd96ea250a859118f53ac60dc3beb90aa32d84f0ef6f66d46f1347da9fae6
quay.io/okd/scos-content@sha256:06d8984e4bc8d958eacc8566e293721f916ad08466c2f9ff8b227e2a92d115fb
```

Direct VM-side pulls and agent logs exposed the registry failure pattern. Representative errors included:

```text
read tcp 192.168.8.210:...-><quay-ip>:443: read: connection reset by peer
lookup quay.io: i/o timeout
network is unreachable
Start request repeated too quickly.
```

When the VM or installer attempted to pull required content, SSH sessions also often ended with:

```text
Read from remote host 192.168.8.210: Connection reset by peer
Connection to 192.168.8.210 closed.
client_loop: send disconnect: Broken pipe
```

The checks tried to narrow this down:

```bash
sudo arping -D -I ens3 -c 4 192.168.8.210
sudo nmcli con mod "$CONN" ipv4.dns "192.168.8.72 8.8.8.8"
sudo ethtool -K ens3 tx off rx off tso off gso off gro off
sudo nmcli con mod "$CONN" ipv6.method disabled
sudo ip link set dev ens3 mtu 1360
```

Host-side tests from Newton showed the physical host could reach the internet cleanly enough for basic checks:

```bash
ping -c 20 8.8.8.8
# 20 packets transmitted, 20 received, 0% packet loss
```

That made the failure more specific than "Newton has no network": the VM/installer path to large external OKD/SCOS artifacts was unreliable under lab network conditions.

This was sufficient to classify the Newton direct-lab guide as not reproducible under the current network assumptions.

---

## 9. Air-Gap Workarounds Tried

Several non-guide workarounds were attempted to prove whether the problem was the installer itself or registry/network access:

### Local payload side-load

```bash
scp -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes \
  -i ~/.ssh/id_ed25519 /tmp/scos-content.tar core@192.168.8.210:/tmp/

sudo systemctl stop assisted-service.service assisted-service-db.service \
  assisted-service-pod.service agent-register-cluster.service

sudo podman load -i /tmp/scos-content.tar
```

This could load the local payload when done before watchdog resets, but it was not stable or sufficient for a clean install. The reliable ordering was:

1. Clear stale host keys with `ssh-keygen -R 192.168.8.210`.
2. Copy `/tmp/scos-content.tar` to the VM.
3. SSH into `core@192.168.8.210`.
4. Stop assisted-service and registration services before loading the tarball.
5. Run `sudo podman load -i /tmp/scos-content.tar`.

Trying to load the tarball while the services were still racing often caused the SSH session to break or the live ISO state to reset.

### Generator override and env patching

```bash
sudo bash -c 'echo -e "#!/bin/bash\nexit 0" > /usr/local/bin/get-container-images.sh'
sudo chmod +x /usr/local/bin/get-container-images.sh
sudo sed -i \
  's|quay.io/okd/scos-content@sha256:06d8984e4bc8d958eacc8566e293721f916ad08466c2f9ff8b227e2a92d115fb|sha256:bddddbefb7e1d8ffc3e01a0b9831ddde2c4558387cf364af00236482e6fb3912|g' \
  /usr/local/share/assisted-service/agent-images.env
```

After the side-load and patch, `assisted-service.service` could reach the point where it started the HTTP handler on `:8090`. That proved the local payload workaround was not totally dead, but it did not complete the install.

Later attempts exposed additional manual-workaround fragility:

- `agent-register-cluster.service` still failed or hit unavailable-resource errors.
- Assisted Service reported token/signature validation failures in the registration path.
- Some attempted patches targeted the wrong env file. `images.env` was too small and lacked `SERVICE_IMAGE`, while `assisted-service.env` / `agent-images.env` carried different parts of the runtime configuration.
- A few commands were accidentally run on Newton rather than inside the OKD VM, which produced "No such file or directory" and confirmed those files only existed in the live ISO environment.
- Because the VM was a live agent ISO, resets could discard local modifications.

The side-load experiment was useful for diagnosis, but it was not a replacement for a proper disconnected install.

### Host NAT / gateway hijack

On Newton:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
sudo iptables -t nat -A POSTROUTING -s 192.168.8.210/32 -j MASQUERADE
```

Inside the VM:

```bash
IFACE=$(ip route | grep default | awk '{print $5}')
sudo ip route replace default via 192.168.8.53 dev $IFACE
sudo systemctl restart agent-register-cluster.service agent-register-infraenv.service
```

This did not produce a reproducible registration path.

Other network workarounds tried during the same phase included:

- Temporarily stopping `firewalld` on Newton.
- Adding a targeted MASQUERADE rule for `192.168.8.210/32`.
- Forcing the VM default route through Newton.
- Disabling IPv6 inside the VM to avoid unreachable IPv6 Quay endpoints.
- Lowering the VM MTU to `1360` in case of path-MTU issues.

None of these converted the run into a clean, repeatable guide path.

---

## 10. Current Status

| Component | Status |
|---|---|
| Newton host OS | Preserved |
| Old Newton VMs | Removed |
| `bridge0` | Reused |
| `master-0-vm` | Created during attempts |
| OKD Hub API | Did not become reliably available on `:6443` |
| Assisted Service | Could be made active during workaround attempts |
| Agent registration | Failed |
| Kepler SNO/slave | Not validated because Hub was unavailable |

Kepler remains dependent on a working Hub/ZTP path. It should not be counted as independently verified by this Newton attempt.

This is also why the Kepler path was not continued directly. Kepler was expected to be wiped and reinstalled through Hub/ZTP, so using it manually would not validate the intended workflow. Since the Hub never reached a reliable registration/install state, Kepler remained out of scope for this Newton verification.

---

## 11. Required Fix Before Retrying

The Newton OKD path should not be rerun as a normal "open internet" install until one of these prerequisites exists:

1. Internal mirror registry for OKD/SCOS release payloads and image metadata.
2. Fully disconnected OKD install assets prepared ahead of time.
3. Network policy exception for the Hub VM's traffic to required registries.
