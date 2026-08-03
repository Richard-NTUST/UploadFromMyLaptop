# QA Review & Obstacles - StarlingX KVM Deployment

**Target Document:** `starlingx-cluster-setup.md`
**Test Environment:** Ubuntu Host (Debian 11 StarlingX Monolithic ISO)

### Executive Summary
The deployment guide contains several issues that prevent a successful installation when using modern StarlingX releases (8.0+). The underlying `virtual-deployment` scripts generate incompatible virtual hardware, and the guide's networking instructions contain subnet mismatches and reference outdated CentOS-based naming conventions. 

---

### Mirror Link Changes: The ISO is now obtained from 
```
https://mirror.starlingx.windriver.com/mirror/starlingx/release/latest_release/debian/bullseye/amd64/monolithic/outputs/iso/starlingx-intel-x86-64-20260422094655-cd.iso
```
Other than that, the link for virtual-deployment still works fine as in the note. 

---

### Steps Executed

a. Virtual Deployment in /tmp folder
```
cd /tmp
git clone https://opendev.org/starlingx/virtual-deployment.git
cd virtual-deployment/libvirt
```

b. Change CPU mode from Nehalem (as my device doesn't use a Nehalem architecture chip)
```py
import glob, re
for path in glob.glob('/tmp/virtual-deployment/libvirt/xml/*.xml'):
    with open(path, 'r') as f: text = f.read()
    patched = re.sub(r\"<cpu match='exact'>\s*<model fallback='forbid'>Nehalem</model>\s*(<topology[^>]+>).*?</cpu>\", r\"<cpu mode='host-passthrough' check='none'>\n    \g<1>\n  </cpu>\", text, flags=re.DOTALL)
    with open(path, 'w') as f: f.write(patched)
```

![Screenshot from 2026-04-28 20-08-28](https://hackmd.io/_uploads/H12XGHR6bl.png)

c. Run setup_network.sh
```
sudo bash setup_network.sh
```

d. Run setup_configuration.sh with the ISO
```
export ISO_PATH=/var/lib/libvirt/images/starlingx-intel-x86-64-20260422094655-cd.iso
sudo bash setup_configuration.sh -c controllerstorage -i $ISO_PATH
```

e. Select Debian Controller Install, Serial Console

![gambar](https://hackmd.io/_uploads/Hyjqq-yR-l.png)

f. Edit localhost.yml

```
sudo mkdir -p /home/sysadmin
sudo vi /home/sysadmin/localhost.yml
```

g. Localhost Config
```yml
system_mode: simplex
dns_servers:
  - 8.8.8.8
  - 8.8.4.4

pxeboot_subnet: 169.254.202.0/24
management_subnet: 192.168.204.0/24
management_start_address: 192.168.204.3
management_end_address: 192.168.204.50

cluster_host_subnet: 192.168.206.0/24
cluster_pod_subnet: 172.16.0.0/16
cluster_service_subnet: 10.96.0.0/12

external_oam_subnet: 10.10.10.0/24
external_oam_gateway_address: 10.10.10.1
external_oam_floating_address: 10.10.10.2

admin_username: admin
admin_password: Password0102030!
sysadmin_password: Password0102030!
```

h. Run Ansible
```
sudo ansible-playbook /usr/share/ansible/stx-ansible/playbooks/bootstrap.yml \
  -e "override_files_dir=/home/sysadmin" -v
```

--> Ansible Result (Failed on default route configuration)
```
TASK [bootstrap/bringup-essential-services : Configure the default route] ******
Tuesday 28 April 2026  13:25:31 +0000 (0:00:00.179)       0:02:51.686 ********* 
fatal: [localhost]: FAILED! => changed=true 
  cmd: ip route replace default via 10.10.10.1
  delta: '0:00:00.002583'
  end: '2026-04-28 13:25:31.472497'
  msg: non-zero return code
  rc: 2
  start: '2026-04-28 13:25:31.469914'
  stderr: 'Error: Nexthop has invalid gateway.'
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>

PLAY RECAP *********************************************************************
localhost                  : ok=414  changed=148  unreachable=0    failed=1    skipped=451  rescued=0    ignored=0   

Tuesday 28 April 2026  13:25:31 +0000 (0:00:00.178)       0:02:51.865 ********* 
=============================================================================== 
bootstrap/persist-config : Saving config in sysinv database ------------ 28.42s
bootstrap/apply-manifest : Applying puppet bootstrap manifest ---------- 27.12s
bootstrap/bringup-essential-services : Add loopback interface via system --- 7.81s
bootstrap/persist-config : Wait for sysinv inventory -------------------- 7.31s
bootstrap/apply-manifest : Execute sysinv-dbsync ------------------------ 5.89s
bootstrap/apply-manifest : Exec keystone-manage db_sync ----------------- 5.28s
bootstrap/apply-manifest : Create sysinv endpoints ---------------------- 4.26s
bootstrap/apply-manifest : Configure keystone services, roles and users --- 3.67s
bootstrap/apply-manifest : Create barbican endpoints -------------------- 3.46s
bootstrap/apply-manifest : Exec keystone boostrap ----------------------- 3.08s
bootstrap/persist-config : Restart sysinv services to pick up sysinv.conf update --- 3.05s
bootstrap/apply-manifest : Generating static config data ---------------- 2.76s
bootstrap/apply-manifest : Exec keystone-manage fernet_setup ------------ 2.44s
common/wipe-ceph-osds : Wipe ceph osds ---------------------------------- 2.10s
bootstrap/apply-manifest : Run fm-db-sync ------------------------------- 1.80s
bootstrap/apply-manifest : Exec barbican-manage upgrade ----------------- 1.77s
common/create-etcd-certs : Generate private key for etcd server and client --- 1.59s
bootstrap/apply-manifest : Exec barbican-db-manage sync secret stores --- 1.49s
bootstrap/apply-manifest : Write filesystem settings to runtime hieradata --- 1.36s
common/create-etcd-certs : Generate certs signed with etcd CA certificate --- 1.23s
sysadmin@localhost:~$ 
```

---

--> Debugging the Interface Address
```
sysadmin@localhost:~$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet 192.168.204.4/24 brd 192.168.204.255 scope host lo:1
       valid_lft forever preferred_lft forever
    inet 169.254.202.1/24 scope host lo
       valid_lft forever preferred_lft forever
    inet 192.168.206.1/24 scope host lo
       valid_lft forever preferred_lft forever
    inet 192.168.204.3/24 scope host secondary lo
       valid_lft forever preferred_lft forever
    inet 192.168.206.2/24 brd 192.168.206.255 scope host secondary lo:5
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:8f:dd:89 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:fe8f:dd89/64 scope link 
       valid_lft forever preferred_lft forever
3: enp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:79:d4:17 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:fe79:d417/64 scope link 
       valid_lft forever preferred_lft forever
4: enp2s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:ac:d5:95 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:feac:d595/64 scope link 
       valid_lft forever preferred_lft forever
5: enp2s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:a9:df:20 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:fea9:df20/64 scope link 
       valid_lft forever preferred_lft forever
6: ip6tnl0@NONE: <NOARP,UP,LOWER_UP> mtu 1452 qdisc noqueue state UNKNOWN group default qlen 1000
    link/tunnel6 :: brd :: permaddr 2222:113e:29ef::
    inet6 fe80::2022:11ff:fe3e:29ef/64 scope link 
       valid_lft forever preferred_lft forever
7: tunl0@NONE: <NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ipip 0.0.0.0 brd 0.0.0.0
```

```
sysadmin@localhost:~$ sudo ip address add 10.10.10.3/24 dev enp3s0
sudo ip link set up dev enp3s0
sudo ip route add default via 10.10.10.1 dev enp3s0
sysadmin@localhost:~$ ping -c 4 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
From 10.10.10.3 icmp_seq=1 Destination Host Unreachable
From 10.10.10.3 icmp_seq=2 Destination Host Unreachable
From 10.10.10.3 icmp_seq=3 Destination Host Unreachable
From 10.10.10.3 icmp_seq=4 Destination Host Unreachable
```

```
jdavidp@jdavidp-B650M-PG-Lightning-WiFi:/tmp/virtual-deployment/libvirt$ virsh domiflist controllerstorage-controller-0
 Interface   Type     Source   Model    MAC
-----------------------------------------------------------
 vnet0       bridge   stxbr1   e1000    52:54:00:ac:d5:95
 vnet1       bridge   stxbr2   e1000    52:54:00:a9:df:20
 vnet2       bridge   stxbr3   virtio   52:54:00:8f:dd:89
 vnet3       bridge   stxbr4   virtio   52:54:00:79:d4:17

jdavidp@jdavidp-B650M-PG-Lightning-WiFi:/tmp/virtual-deployment/libvirt$ sysadmin@localhost:~$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet 192.168.204.4/24 brd 192.168.204.255 scope host lo:1
       valid_lft forever preferred_lft forever
    inet 169.254.202.1/24 scope host lo
       valid_lft forever preferred_lft forever
    inet 192.168.206.1/24 scope host lo
       valid_lft forever preferred_lft forever
    inet 192.168.204.3/24 scope host secondary lo
       valid_lft forever preferred_lft forever
    inet 192.168.206.2/24 brd 192.168.206.255 scope host secondary lo:5
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:8f:dd:89 brd ff:ff:ff:ff:ff:ff
    inet 10.10.10.3/24 scope global enp3s0
       valid_lft forever preferred_lft forever
    inet6 fe80::5054:ff:fe8f:dd89/64 scope link 
       valid_lft forever preferred_lft forever
3: enp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:79:d4:17 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:fe79:d417/64 scope link 
       valid_lft forever preferred_lft forever
4: enp2s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:ac:d5:95 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:feac:d595/64 scope link 
       valid_lft forever preferred_lft forever
5: enp2s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:a9:df:20 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::5054:ff:fea9:df20/64 scope link 
       valid_lft forever preferred_lft forever
6: ip6tnl0@NONE: <NOARP,UP,LOWER_UP> mtu 1452 qdisc noqueue state UNKNOWN group default qlen 1000
    link/tunnel6 :: brd :: permaddr 2222:113e:29ef::
    inet6 fe80::2022:11ff:fe3e:29ef/64 scope link 
       valid_lft forever preferred_lft forever
7: tunl0@NONE: <NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ipip 0.0.0.0 brd 0.0.0.0
```

--> Adjust Interface Address
```
sudo ip addr flush dev enp3s0
sudo ip link set down dev enp3s0
```

```
# Hotwire enp2s1
sudo ip address add 10.10.10.3/24 dev enp2s1
sudo ip link set up dev enp2s1
sudo ip route add default via 10.10.10.1 dev enp2s1
```
---
### i. Final Ansible Results
```
...oh yeah TASK [common/push-docker-images : set_fact] ************************************
Tuesday 28 April 2026  13:37:40 +0000 (0:00:00.011)       0:01:34.632 ********* 
ok: [localhost] => changed=false 
  ansible_facts:
    download_images: registry.k8s.io/kube-apiserver:v1.34.1,registry.k8s.io/kube-controller-manager:v1.34.1,registry.k8s.io/kube-scheduler:v1.34.1,registry.k8s.io/kube-proxy:v1.34.1,registry.k8s.io/coredns/coredns:v1.12.1,registry.k8s.io/pause:3.10.1,registry.k8s.io/etcd:3.6.4-0,quay.io/calico/cni:v3.31.2,quay.io/calico/node:v3.31.2,quay.io/calico/kube-controllers:v3.31.2,ghcr.io/k8snetworkplumbingwg/multus-cni:v4.2.3-debug,ghcr.io/k8snetworkplumbingwg/sriov-cni:v2.10.0,ghcr.io/k8snetworkplumbingwg/sriov-network-device-plugin:v3.10.0,docker.io/starlingx/n3000-opae:stx.8.0-v1.0.2,quay.io/stackanetes/kubernetes-entrypoint:v0.3.1,registry.k8s.io/ingress-nginx/controller:v1.14.3,registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.6.7,registry.k8s.io/defaultbackend-amd64:1.5,docker.io/fluxcd/helm-controller:v1.4.5,docker.io/fluxcd/source-controller:v1.7.4,ghcr.io/fluxcd/notification-controller:v1.7.5,ghcr.io/fluxcd/kustomize-controller:v1.7.3,registry.k8s.io/sig-storage/snapshot-controller:v8.1.0,quay.io/jetstack/cert-manager-acmesolver:v1.18.5,quay.io/jetstack/cert-manager-cainjector:v1.18.5,quay.io/jetstack/cert-manager-controller:v1.18.5,quay.io/jetstack/cert-manager-webhook:v1.18.5,quay.io/jetstack/cert-manager-startupapicheck:v1.18.5,docker.io/starlingx/stx-oidc-client:stx.12.0-v1.0.10,ghcr.io/dexidp/dex:v2.44.0,docker.io/curlimages/curl:8.17.0
    use_multiprocessing: false

TASK [common/push-docker-images : Download images and push to local registry - multiprocessing disabled] ***
Tuesday 28 April 2026  13:37:40 +0000 (0:00:00.013)       0:01:34.646 ********* 
 
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (10 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (9 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (8 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (7 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (6 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (5 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (4 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (3 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (2 retries left).
FAILED - RETRYING: Download images and push to local registry - multiprocessing disabled (1 retries left).
An exception occurred during task execution. To see the full traceback, use -vvv. The error was: NoneType: None
fatal: [localhost]: FAILED! => changed=true 
  attempts: 10
  failed_when_result: true
  msg: non-zero return code
  rc: 1
  stderr: |-
    Traceback (most recent call last):
      File "/tmp/.ansible-root/tmp/ansible-tmp-1777387043.798378-23850-115459986370957/download_images.py", line 491, in <module>
        raise Exception("Failed to download images %s" % failed_downloads)
    Exception: Failed to download images ['quay.io/stackanetes/kubernetes-entrypoint:v0.3.1']
  stderr_lines: <omitted>
  stdout: |-
    Image registry.k8s.io/kube-apiserver:v1.34.1 already exists in the containerd cache.
    Image registry.k8s.io/kube-controller-manager:v1.34.1 already exists in the containerd cache.
    Image registry.k8s.io/kube-scheduler:v1.34.1 already exists in the containerd cache.
    Image registry.k8s.io/kube-proxy:v1.34.1 already exists in the containerd cache.
    Image registry.k8s.io/coredns/coredns:v1.12.1 already exists in the containerd cache.
    Image registry.k8s.io/pause:3.10.1 already exists in the containerd cache.
    Image registry.k8s.io/etcd:3.6.4-0 already exists in the containerd cache.
    Image quay.io/calico/cni:v3.31.2 already exists in the containerd cache.
    Image quay.io/calico/node:v3.31.2 already exists in the containerd cache.
    Image quay.io/calico/kube-controllers:v3.31.2 already exists in the containerd cache.
    Image ghcr.io/k8snetworkplumbingwg/multus-cni:v4.2.3-debug already exists in the containerd cache.
    Image ghcr.io/k8snetworkplumbingwg/sriov-cni:v2.10.0 already exists in the containerd cache.
    Image ghcr.io/k8snetworkplumbingwg/sriov-network-device-plugin:v3.10.0 already exists in the containerd cache.
    Image docker.io/starlingx/n3000-opae:stx.8.0-v1.0.2 already exists in the containerd cache.
    Image quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 does not exist in the containerd cache.
    404 Client Error: Not Found ("manifest unknown: manifest unknown")
    Image quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 not found on local registry, attempt to download...
     Image download failed: quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 Error download image: {'message': 'Docker Image Format v1 and Docker Image manifest version 2, schema 1 support has been removed. Suggest the author of quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 to upgrade the image to the OCI Format or Docker Image manifest v2, schema 2. More information at https://docs.docker.com/go/deprecated-image-specs/'}
    Image registry.k8s.io/ingress-nginx/controller:v1.14.3 already exists in the containerd cache.
    Image registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.6.7 already exists in the containerd cache.
    Image registry.k8s.io/defaultbackend-amd64:1.5 already exists in the containerd cache.
    Image docker.io/fluxcd/helm-controller:v1.4.5 already exists in the containerd cache.
    Image docker.io/fluxcd/source-controller:v1.7.4 already exists in the containerd cache.
    Image ghcr.io/fluxcd/notification-controller:v1.7.5 already exists in the containerd cache.
    Image ghcr.io/fluxcd/kustomize-controller:v1.7.3 already exists in the containerd cache.
    Image registry.k8s.io/sig-storage/snapshot-controller:v8.1.0 already exists in the containerd cache.
    Image quay.io/jetstack/cert-manager-acmesolver:v1.18.5 already exists in the containerd cache.
    Image quay.io/jetstack/cert-manager-cainjector:v1.18.5 already exists in the containerd cache.
    Image quay.io/jetstack/cert-manager-controller:v1.18.5 already exists in the containerd cache.
    Image quay.io/jetstack/cert-manager-webhook:v1.18.5 already exists in the containerd cache.
    Image quay.io/jetstack/cert-manager-startupapicheck:v1.18.5 already exists in the containerd cache.
    Image docker.io/starlingx/stx-oidc-client:stx.12.0-v1.0.10 already exists in the containerd cache.
    Image ghcr.io/dexidp/dex:v2.44.0 already exists in the containerd cache.
    Image docker.io/curlimages/curl:8.17.0 already exists in the containerd cache.
  stdout_lines: <omitted>

PLAY RECAP *********************************************************************
localhost                  : ok=363  changed=91   unreachable=0    failed=1    skipped=486  rescued=0    ignored=0   

Tuesday 28 April 2026  14:37:29 +0000 (0:59:49.043)       1:01:23.689 ********* 
=============================================================================== 
common/push-docker-images : Download images and push to local registry - multiprocessing disabled  3589.04s
bootstrap/persist-config : Find old registry secrets in Barbican ------- 20.03s
bootstrap/bringup-essential-services : Add loopback interface via system --- 7.18s
bootstrap/persist-config : Saving config in sysinv database ------------- 6.90s
bootstrap/persist-config : Wait for sysinv inventory -------------------- 6.30s
bootstrap/persist-config : Restart sysinv services to pick up sysinv.conf update --- 3.06s
bootstrap/persist-config : Check for existing ssl_ca certificates ------- 2.59s
bootstrap/validate-config : Retrieve list of applications from sysinv --- 2.15s
common/wipe-ceph-osds : Wipe ceph osds ---------------------------------- 2.10s
bootstrap/persist-config : Copy etcd certificates to etcd certs directory --- 1.11s
bootstrap/validate-config : Check if external CA files exist ------------ 1.06s
bootstrap/bringup-essential-services : Update local registry config files --- 1.04s
bootstrap/validate-config : Retrieve openrc region_name ----------------- 0.99s
common/configure-containerd : Get guest local registry credentials ------ 0.98s
common/configure-containerd : Get local registry credentials ------------ 0.97s
common/prepare-env : stat ----------------------------------------------- 0.80s
bootstrap/bringup-essential-services : Populate /etc/hosts -------------- 0.70s
bootstrap/bringup-essential-services : Add loopback interface address --- 0.53s
bootstrap/bringup-essential-services : Set certificate file and key permissions to root read-only --- 0.53s
bootstrap/bringup-essential-services : Copy certificate and keys to shared filesystem for mate --- 0.53s

```

(1 task failed: Image download failed: quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 Error download image: {'message': 'Docker Image Format v1 and Docker Image manifest version 2, schema 1 support has been removed. Suggest the author of quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 to upgrade the image to the OCI Format or Docker Image manifest v2, schema 2. More information at https://docs.docker.com/go/deprecated-image-specs/'})

---

### Issues Found

### 1. Topology Block: CPU Architecture Emulation
**Location:** Step 5 (`setup_configuration.sh`)
**The Issue:** The `virtual-deployment` script automatically generates KVM XML templates that hardcode the virtual motherboard to emulate a 2008 Intel **Nehalem** CPU (`<model fallback='forbid'>Nehalem</model>`). Modern StarlingX Debian 11 kernels require modern CPU instruction sets. When the kernel attempts to boot on the virtual Nehalem architecture, it throws an illegal instruction fault and permanently freezes at the `Booting from Hard Disk...` BIOS handoff.

- Users need to be instructed to patch the generated `.xml` templates in the `vms/` directory to use `host-passthrough` before booting the VMs. This can also be done via Virtual Manager's VM CPU Config (checkbox)

![Screenshot from 2026-04-28 20-08-28](https://hackmd.io/_uploads/H12XGHR6bl.png)

### 2. Network Block: Subnet Configuration Mismatch
**Location:** Step 3 and Step 7
**The Issue:** The guide is contradictory regarding the OAM network space. In Step 3, the `set_defaults.sh` variables build the host's virtual bridge (`stxbr1`) on the `192.168.1.0/24` subnet. However, in Step 7, the `localhost.yml` Ansible configuration instructs the VM to look for its external OAM gateway at `10.10.10.1`. The VM is completely isolated from the host.
**The Fix:** Unify the subnets. Either update Step 3 to build the host bridges on the `10.10.10.x` network, or update Step 7 so the Ansible playbook expects a `192.168.1.x` gateway.

Commands I personally ran (connect enp2s1 with the proper IP):
```
sudo ip addr flush dev enp3s0
sudo ip link set down dev enp3s0

sudo ip address add 10.10.10.3/24 dev enp2s1
sudo ip link set up dev enp2s1
sudo ip route add default via 10.10.10.1 dev enp2s1
```

### 3. Execution Block: Premature Ansible Routing Failure
**Location:** Step 7
**The Issue:** The guide instructs the user to run the Ansible bootstrap playbook in Step 7. The playbook immediately crashes with a `Nexthop has invalid gateway` error. This occurs because Ansible attempts to set a default route, but the OAM interface has not been powered on or assigned an IP address yet (the guide delays this until Step 8).
**The Fix:** The guide must include a "Network Hotwiring" step *before* running the Ansible playbook. The user must manually bring the interface UP and bind the `10.10.10.3` IP to it so Ansible can validate the routing path.

### 4. Configuration Block: Legacy Interface Naming
**Location:** Step 8
**The Issue:** The guide instructs the user to assign network classes using legacy interface names: `eth1`, `eth2`, and `eth3`. Modern StarlingX (Debian) utilizes Predictable Network Interface Names. During our test, KVM and Debian mapped the interfaces to `enp2s1`, `enp2s2`, `enp3s0`, and `enp4s0`. Attempting to configure `eth1` fails entirely.
**The Fix:** Update the documentation to reflect modern Debian naming conventions, and instruct the user to verify the correct interface using MAC address matching (`virsh domiflist` on the host mapped to `ip a` on the VM).

### 5. Fatal Block: Upstream Registry Manifest Deprecation
**Location:** Step 7 (Ansible Playbook - `push-docker-images` task)
**The Issue:** The bootstrap playbook attempts to download `quay.io/stackanetes/kubernetes-entrypoint:v0.3.1`. This image utilizes a deprecated Docker manifest (v1 / v2 schema 1). Modern container runtimes (containerd/Docker) have entirely dropped support for this legacy specification. Consequently, the image cannot be pulled, resulting in a fatal playbook crash after approximately 1 hour of runtime. 
**The Fix:** The author must provide a system override flag in the `localhost.yml` file to redirect the `kubernetes-entrypoint` dependency to a modernized, OCI-compliant fork or mirror of the image. The deployment cannot proceed without it.
