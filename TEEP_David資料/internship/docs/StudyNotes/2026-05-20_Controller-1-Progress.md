---
title: Short Update - Bypassing the Controller-1 Bootup Failure
---

# Short Update - Bypassing the Controller-1 Bootup Failure
**Date:** 23 May 2026
**OS Base:** Ubuntu 22.04 LTS

Last note, the deployment got stuck on 
### Phase 1: Unblock the PXE Server (On `controller-0`)

Before `controller-1` can even ask for an IP, the DHCP/PXE server on the active controller must be running. The legacy deployment has a path bug that prevents this.

1. SSH into `controller-0`.
2. Create the missing configuration file to satisfy the double-slash path bug:
```bash
sudo touch /opt/platform/config/24.09/dnsmasq.addn_conf

```


3. Inject the modern UEFI bootloader payload:
```bash
echo "dhcp-boot=grubx64.efi" | sudo tee /opt/platform/config/24.09/dnsmasq.addn_conf

```


4. Wipe the Service Manager penalty box to force the daemon to restart:
```bash
sudo sm-unmanage service dnsmasq
sudo sm-manage service dnsmasq

```


*(Wait 30 seconds to run `sudo sm-dump | grep dnsmasq` and ensure it stays `enabled-active`)*

### Phase 2: The Clean VM Spawn (On the Hypervisor)

Do **not** use `setup_configuration.sh` for the second controller. It hardcodes a legacy BIOS and a 2008 Nehalem CPU architecture, which causes the PXE boot loop and disk hang. Use this surgical command to enforce UEFI and host-passthrough:

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

### Phase 3: The Topology Fix

The Debian 11 installer will crash if the virtual CPU topology is fragmented (e.g., 4 independent sockets with 1 core).

1. Open **Virt-Manager** (Virtual Machine Manager) on your desktop.
2. Open `controllerstorage-controller-1` and go to its hardware details.
3. Select **CPUs**.
4. Check the box to "Manually set CPU topology".
5. Set it strictly to: **Sockets: 1, Cores: 4, Threads: 1**.
6. Apply changes.

Once Phase 3 is done, power on `controller-1`. Because of the UEFI firmware (`--boot firmware=efi`), it will correctly process the PXE payload, download the StarlingX installer from `controller-0`, and drop straight into the "Waiting for Configuration" state without crashing.
