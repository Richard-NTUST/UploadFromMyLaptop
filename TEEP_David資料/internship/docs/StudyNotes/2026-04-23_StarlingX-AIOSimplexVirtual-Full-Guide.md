---
title: StarlingX AIO Simplex - Complete Deployment Guide

---

# StarlingX AIO Simplex (Virtual) - Deployment & Troubleshooting Guide
**Date:** March 2026
**OS Base:** Debian 11 (StarlingX 8.0+)

## 1. Architecture Selection: Why AIO Simplex Virtual?
We selected the **All-in-One (AIO) Simplex Virtual** topology. 
![image](https://hackmd.io/_uploads/r1hjoM4iWe.png)

* **Why not Bare Metal?** A bare-metal deployment requires wiping a physical machine entirely. Using a VM on an Ubuntu dual-boot allows us to utilize the host OS for troubleshooting, downloading ISOs, and running Virt-Manager. 
* **Why not Multi-Node or AIO Duplex?** Multi-node setups require extensive physical networking (separate switches for OAM, Management, and Data networks). Simplex gives us the entire StarlingX edge cloud stack (Controller, Compute, and Storage) inside a single node. For telecom research or validating environments in a BMW lab setup, simulating the entire stack on a single robust workstation is far more practical than sourcing a rack of physical servers.
* **Resource Requirements:** Because it is nested, the host needs significant buffer space. Recommended: 32GB+ RAM and 600GB+ storage. The VM itself is allocated 28GB RAM and 500GB storage.

### Outdated Documentations
Do **NOT** use the official documentation links that reference `stx.5.0` (e.g., `.../deploy_install_guides/r4_release/...`). 
* StarlingX 5.0 was based on **CentOS**. 
* Modern StarlingX (8.0+) is built on **Debian**. 
* The old setup scripts will fail. For virtual deployments, always use the dedicated [virtual-deployment repository](https://opendev.org/starlingx/virtual-deployment).

---

## 2. Host OS Preparation
Before spinning up the VM, the Ubuntu host must be configured as a hypervisor.

```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager ovmf git curl
```
* **`qemu-kvm` & `libvirt-*`**: The core virtualization engine and management daemons.
* **`bridge-utils`**: Allows the creation of virtual network switches (bridges) for the VM to talk to the host.
* **`virt-manager`**: The GUI tool for viewing the VM console.
* **`ovmf`**: Provides UEFI firmware support for virtual machines (required by modern OS installations).

```bash
sudo ufw disable 
```
* **Why:** The Uncomplicated Firewall (UFW) aggressively blocks forwarded packets by default. This will silently break the virtual network bridges, preventing the VM from accessing the internet.

```bash
sudo adduser $USER libvirt
sudo adduser $USER kvm 
```
* **Why:** Grants your standard Linux user permission to manage virtual machines. Without this, you would have to run `virt-manager` as `root`, which breaks file permissions. *(Note: Requires a logout/login to take effect).*

---

## 3. Network Bridge Setup & The "Ghost Bridge" Fix
StarlingX requires four distinct network interfaces (OAM, Management, Data, and Infrastructure). We clone the official repository to generate these bridges automatically.

```bash
git clone https://opendev.org/starlingx/virtual-deployment.git
cd $HOME/virtual-deployment/libvirt/
```

### The Problem: Orphaned Bridges
When running `bash setup_network.sh`, it may throw errors like `stxbr1 exists, cowardly refusing to overwrite it` or `RTNETLINK answers: File exists`. This happens if a previous run crashed, leaving "ghost" interfaces (`stxbr1` through `stxbr4`) stuck in the host's networking stack.

### The Solution: Manually Nuke the Bridges
To fix this, we must hunt down the stuck interfaces, force them offline, and delete them from the bridge controller:

```bash
# 1. Identify the stuck bridges
ip link | grep stx

# 2. Force the bridges offline and delete them (Loop through stxbr0 to stxbr4)
for br in $(ip -o link show | awk -F': ' '{print $2}' | grep '^stxbr'); do
  echo "Removing $br"
  sudo ip link set $br down
  sudo brctl delbr $br
done

# 3. Restart the virtualization daemon to clear its cache
sudo systemctl restart libvirtd

# 4. Run the script successfully
sudo bash setup_network.sh
```

---

## 4. VM Provisioning
With the host ready and network bridges active, we download the monolithic ISO and attach it to our new VM.

![Screenshot from 2026-03-27 12-07-17](https://hackmd.io/_uploads/HkRajMVjbx.png)
You can get this from this link:
https://mirror.starlingx.windriver.com/mirror/starlingx/release/11.0.0/debian/bullseye/amd64/monolithic/outputs/iso/

```bash
# Move the downloaded ISO to the default libvirt storage pool
sudo mv ~/Downloads/starlingx-intel-x86-64-20251029043716-cd.iso /var/lib/libvirt/images/
```

We use `virt-install` to build the VM from the command line, ensuring precise hardware mapping:

```bash
virt-install \
  --name stx-aio-simplex \
  --ram 28672 \
  --vcpus 4 \
  --cpu host-passthrough,cache.mode=passthrough \
  --disk path=/var/lib/libvirt/images/stx-aio.qcow2,size=500,bus=virtio,format=qcow2 \
  --os-variant=debian11 \
  --network bridge=stxbr1,model=virtio \
  --network bridge=stxbr2,model=virtio \
  --network bridge=stxbr3,model=virtio \
  --network bridge=stxbr4,model=virtio \
  --boot hd,cdrom,menu=on \
  --graphics vnc \
  --cdrom /var/lib/libvirt/images/starlingx-intel-x86-64-20251029043716-cd.iso
```

### Command Breakdown:
* **`--ram 28672`**: Allocates exactly 28GB of RAM. StarlingX is heavy; anything less risks Ansible timeouts during Kubernetes deployment.
* **`--cpu host-passthrough`**: *Critical.* Exposes the physical CPU's virtualization flags (VT-x/AMD-V) to the VM. Without this, the StarlingX hypervisor cannot run containers.
* **`--disk ... size=500,bus=virtio`**: Creates a 500GB dynamically allocated disk. `virtio` ensures high-speed I/O access, bypassing legacy IDE emulation.
* **`--os-variant=debian11`**: Optimizes QEMU's internal settings for the Debian 11 architecture.
* **`--network bridge=...`**: Attaches the 4 virtual network cables we created in Step 3 into the VM.

***

Good catch! You are absolutely right. I over-optimized the revision and accidentally chopped out the actual bridge between running the `virt-install` command and fixing the CPU. 

If we leave that out, the next person reading this will run the command, stare at a frozen terminal, and have no idea how to actually install the OS from the ISO. 

Let's stitch that crucial Virt-Manager sequence back into the beginning of **Part 2** so the timeline is perfectly linear. Here is the fully corrected flow:

***

# Part 2: Virt-Manager Installation & The Bulletproof Configuration

**Context:** You have just executed the `virt-install` command in Part 1. Your terminal will now appear to "freeze" as it waits for the installation to finish in the background. Leave that terminal alone. We are moving to the graphical interface.

## 1. Entering Virt-Manager & The Safety Valve
Open a new terminal tab and launch the GUI manager:
```bash
virt-manager
```
*(If the manager opens but is completely empty, close it and reopen with `sudo virt-manager`).*

![Screenshot from 2026-03-27 16-00-44](https://hackmd.io/_uploads/rJAhgQViWe.png)


> **The "Nuke and Pave" Safety Valve:**
> If you struggled to get Virt-Manager open, or if the VM sat at the boot screen for a long time while you were troubleshooting host issues, **kill it and start over.** StarlingX boot sequences are highly time-sensitive. 
> 1. Right-click the VM -> **Shut Down -> Force Off**.
> 2. Right-click -> **Delete** (CRITICAL: Check the box to delete the 500GB `.qcow2` storage file).
> 3. Re-run your `virt-install` command from Part 1. This prevents cascading ghost errors later.

## 2. Boot Options & OS Installation
Double-click the `stx-aio-simplex` VM to open the console viewer. You will be greeted by the StarlingX Debian installer menu.

1.  **Select OS Type:** Choose **Debian All in One Install**.
2.  **Select Console Type:** Choose **Graphical Console**. 
    * *Why:* Because we passed the `--graphics vnc` flag in our `virt-install` command earlier, Virt-Manager is perfectly equipped to intercept and display the graphical output during the OS installation.
3.  **Select Disk:** When prompted for installation media, select the 500GB `vda` drive (usually Option 0) and press `y` to confirm wiping it.

![Screenshot from 2026-03-27 16-18-07](https://hackmd.io/_uploads/rJCM-7VoWe.png)

The OS will now take a few minutes to extract and install itself. 

## 3. The Pre-Boot Intercept: CPU Topology
StarlingX requires a standard CPU layout to allocate its real-time kernel resources. KVM defaults to a fragmented virtual CPU layout that will cause the system to report 0MB of RAM later on. 

1. As soon as the initial Debian installation finishes and reboots to the `localhost login:` prompt, **do not log in.** 2. Go to your Virt-Manager window.
3. Right-click the VM -> **Shut Down -> Force Off**.
4. Click the **"i" (Show virtual hardware details)** icon at the top of Virt-Manager.
5. Navigate to **CPUs** in the left-hand panel.
6. Check the box for **"Manually set CPU topology"**.
7. Set the layout to match a standard workstation:
   * **Sockets: 1**
   * **Cores: 4**
   * **Threads: 1**

![Screenshot from 2026-03-27 22-05-50](https://hackmd.io/_uploads/HynpgXNi-g.png)

8. Click **Apply**, then turn the VM back on. 
*(Note: At the GRUB bootloader screen, press Enter on the standard `StarlingX ostree...` option, ignoring the Rollback option).*

![Screenshot from 2026-03-27 17-31-06](https://hackmd.io/_uploads/BJUnbQVsWx.png)

## 4. First Login & The LVM Intercept
Once the VM boots back to the `localhost login:` prompt:
1. Log in with `sysadmin` / `sysadmin`.
2. Update your password when prompted (requires uppercase, lowercase, number, and special character).

![Screenshot from 2026-03-27 16-24-41](https://hackmd.io/_uploads/rkvE-7Vi-g.png)

### The LVM Blindfold Fix
StarlingX applies a strict security filter to the Logical Volume Manager (LVM) to prevent accidental wipes of external drives. In a virtual environment, this accidentally "blindfolds" the OS from seeing its own `cgts-vg` hard drive partitions, which will cause the Ansible bootstrap to fail.

**Remove the blindfold immediately:**
1. Open the configuration file:
   ```bash
   sudo nano /etc/lvm/lvm.conf
   ```
2. Press `Ctrl+W` to search for `global_filter`.
3. Change the array to accept all devices:
   ```text
   global_filter = [ "a|.*|" ]
   ```
   
   ![Screenshot from 2026-03-27 16-48-22](https://hackmd.io/_uploads/B1AUbXVsbl.png)

   
4. Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).
5. Force LVM to rescan the unblindfolded drives:
   ```bash
   sudo vgscan --cache
   sudo vgs
   ```
*(You should now successfully see `cgts-vg` listed with ~468GB of free space).*

![Screenshot from 2026-03-27 16-49-57](https://hackmd.io/_uploads/Bk6uZmEiZg.png)

## 5. Network Hotwiring & The Ansible Roadmap
You are inside a raw StarlingX node with no internet. We must manually activate the virtual network cables so Ansible can download Kubernetes.

```bash
sudo ip address add 10.10.10.3/24 dev enp1s0
sudo ip link set up dev enp1s0
sudo ip route add default via 10.10.10.1 dev enp1s0
```
*(Verify with `ping -c 4 8.8.8.8`)*

![Screenshot from 2026-03-27 16-32-24](https://hackmd.io/_uploads/ByUrGmVj-g.png)

### Creating the Configuration File
Create `localhost.yml` in your home directory (`nano localhost.yml`). Ensure your spacing is exact. 

```yaml
system_mode: simplex
dns_servers:
  - 8.8.8.8
external_oam_subnet: 10.10.10.0/24
external_oam_gateway_address: 10.10.10.1
external_oam_floating_address: 10.10.10.2
admin_username: admin
admin_password: "your-password"
ansible_become_pass: "your-password"
```

## 6. Execution & The Golden Snapshot
Run the bootstrap playbook. Because you proactively fixed the CPU and LVM, this will run flawlessly.
```bash
ansible-playbook /usr/share/ansible/stx-ansible/playbooks/bootstrap.yml
```

![Screenshot from 2026-03-27 17-12-35](https://hackmd.io/_uploads/H1T9bXEjbe.png)

> **TIP: THE SNAPSHOT**
> When the Ansible playbook successfully finishes, **stop**. 
> Go to Virt-Manager, click the **Manage VM Snapshots** icon, and create a snapshot called `"Pre-Unlock Clean State"`. 
> The next step (Unlocking) is the most fragile part of the StarlingX deployment. If it fails, you can revert to this exact snapshot in 5 seconds instead of re-doing a 2-hour installation.


# Part 3: Activating the Controller & Verifying the Cloud

**Context:** The Ansible bootstrap playbook has finished. Your terminal prompt should now say `controller-0:~$`. The system is fully installed but resting in a **Locked** administrative state. Because we proactively fixed the CPU topology and LVM blindfold in Part 2, unlocking the node will be a smooth, linear process.

## 1. The OAM Network Prerequisite
Before unlocking the node, StarlingX requires you to explicitly assign a permanent physical network interface for the Operations, Administration, and Management (OAM) network. Even though we gave Ansible the IP address, we must snap the physical cable into place.

1. Load the OpenStack admin credentials into your terminal:
   ```bash
   source /etc/platform/openrc
   ```
2. Assign the `enp1s0` interface to the `platform` class:
   ```bash
   system host-if-modify controller-0 enp1s0 -c platform
   ```
3. Map the OAM network to that interface:
   ```bash
   system interface-network-assign controller-0 enp1s0 oam
   ```

## 2. The Final Unlock
With the hardware correctly mapped and the storage unblindfolded, command the system to unlock and bring the active compute and control services online:

```bash
system host-unlock controller-0
```

**What happens next:**
Your SSH/console session will abruptly drop, and the VM will immediately reboot itself. **This is fully expected.** It is tearing down the temporary bootstrap environment and booting into its final, real-time kernel state.

## 3. Verifying the Edge Cloud
Wait about 3 to 5 minutes for the VM to boot back to the `localhost login:` prompt and for the background Service Manager (`sm`) to initialize the databases.

1. Log in as `sysadmin` and load your credentials:
   ```bash
   source /etc/platform/openrc
   ```
2. Check the host status:
   ```bash
   system host-list
   ```
   *Success Condition:* The `administrative` state should say **unlocked** and the `availability` state should say **online**.

3. Verify the underlying Kubernetes cluster is alive:
   ```bash
   kubectl get nodes
   ```
   *Success Condition:* `controller-0` is listed with a `Ready` status.

You now have a fully functional StarlingX AIO-Simplex edge cloud running on your workstation!

***

# Part 4 (Appendix): The Debug Graveyard

**Notice to future researchers:** The installation flow in Parts 1-3 is highly specific. If you deviate from the order of operations—specifically, if you fail to set the CPU topology or remove the LVM blindfold *before* running the Ansible playbook—the StarlingX State Machine will permanently fracture. 

Below is an archive of the fatal errors encountered when hardware prerequisites are not met, documented here to aid in future troubleshooting.

### Landmine 1: The LVM Ghost (`unsupported operand type(s) for *: 'NoneType' and 'NoneType'`)
**The Scenario:** You run `system host-unlock`, but Python crashes with a math error.
**The Root Cause:** If the LVM blindfold (`/etc/lvm/lvm.conf`) is removed *after* the inventory agents (`sysinv`) have booted, the database still thinks the `cgts-vg` hard drive has a size of `None`. The unlock script tries to calculate Kubernetes partition percentages (e.g., `None * 0.8`) and crashes.
**The Band-Aid Fix:** Restart the inventory daemons to force a rescan:
```bash
sudo systemctl restart sysinv-agent sysinv-conductor sysinv-api
```

### Landmine 2: The Fatal CPU Topology (0MB RAM)
**The Scenario:** The `NoneType` crash persists. Running `system host-memory-list controller-0` shows `mem_total(MiB)` is `0` for every processor.
**The Root Cause:** KVM passed the `--vcpus 4` flag by building a virtual motherboard with 4 separate physical CPU sockets instead of 1 socket with 4 cores. The virtual BIOS cannot distribute the 28GB of RAM across 4 fake sockets, reporting 0MB total RAM to the inventory database.
**The Fix:** The VM must be powered off, and the topology manually set in Virt-Manager to **1 Socket, 4 Cores, 1 Thread**.

### The Point of No Return: Service Manager (SM) Deadlock
**The Scenario:** You applied the CPU fix and rebooted. Now, `source /etc/platform/openrc` fails with "credentials can only be loaded from the active controller," and `sm-query` reports `sm.db` is missing.
**The Root Cause:** When the VM rebooted in a "Locked" state, the background configuration manager (Puppet) woke up and re-applied its default templates, **putting the LVM blindfold back on**.
Because the storage was hidden during boot:
1. The Distributed Storage (DRBD) daemon crashed.
2. The Postgres database couldn't mount.
3. Keystone (Identity) and RabbitMQ failed to start.
4. The Service Manager deadlocked entirely.

While you can technically manually inject OpenStack credentials (`export OS_...`) and systematically restart every backend service, the internal database state is severely poisoned. Attempting an unlock here usually results in indefinite timeouts. 

**Conclusion:** If you reach this state, the fastest resolution is to delete the VM, wipe the `.qcow2` drive, and restart from Part 1.

# Part 5: Inside the StarlingX Machine - Deploying the OpenAirInterface (OAI) 5G Core

![image](https://hackmd.io/_uploads/HJT0D7ZTbl.png)

This is what I got after redoing step 3 with proper VM topology (before logging in the machine, turn it off and change the topology first before continuing).

**Context:** With the StarlingX Kubernetes cluster unlocked and active, the next step in establishing the e2e testbed is deploying the 5G Core Network. OAI has migrated to a cloud-native architecture, meaning the Core Network (AMF, SMF, NRF, UPF, MySQL) is deployed entirely via Helm charts.

## 1. Environment Preparation
First, create dedicated Kubernetes namespaces to isolate the Core Network from the Radio Access Network (RAN) that will be deployed later.

```bash
kubectl create namespace oai-core
kubectl create namespace oai-ran
```

![image](https://hackmd.io/_uploads/rJLZq7Zp-g.png)

### The Package Manager Limitation
StarlingX locks down standard Debian `apt` repositories to maintain its real-time edge stability. Attempting to run `sudo apt-get install git` will likely fail with no installation candidate. We bypass `git` entirely by pulling the deployment tarball directly using `wget`.

*(Note: Ensure you pull from the newer `oai/orchestration/charts` repository, as OAI completely removed Helm charts from the older `oai-cn5g-fed` repository in release v2.2.0).*

```bash
# Download the modern Orchestration Charts repository
wget https://gitlab.eurecom.fr/oai/orchestration/charts/-/archive/main/charts-main.tar.gz

# Extract and navigate to the basic 5G Core directory
tar -xzf charts-main.tar.gz
cd charts-main/oai-5g-core/oai-5g-basic
```

![Screenshot from 2026-04-14 00-17-40](https://hackmd.io/_uploads/Hy149QbaWg.png)

## 2. Helm Deployment
Before installing the Core, we must pull down the required sub-charts (like the MySQL database used for subscriber profiles). 

```bash
helm dependency update
helm install basic-core . -n oai-core
```
Monitor the pod initialization:
```bash
watch kubectl get pods -n oai-core
```
![Screenshot from 2026-04-14 01-21-10](https://hackmd.io/_uploads/By-Kc7WTZl.png)

---

## 3. The Debug Graveyard: OAI Core

Even on a perfectly clean StarlingX cluster, the OpenAirInterface deployment may hang due to internal K8s networking quirks or strict configuration parsers. Below is the path we took to identify and resolve the two major hurdles we encountered.

### Pitfall 1: Network Sandbox Failure (Calico "Unauthorized")

![Screenshot from 2026-04-14 01-03-54](https://hackmd.io/_uploads/B1kpcXWTWe.png)

> **The Encounter:** After launching the Helm chart, the pods sat in the `Init` and `ContainerCreating` states indefinitely. After waiting nearly 40 minutes, we ran a trace on a stuck pod (`kubectl describe pod -n oai-core -l app.kubernetes.io/name=oai-nrf`). The event log was flooded with Multus and Calico CNI errors stating: `error getting ClusterInformation: connection is unauthorized`. 

**The Root Cause:** This is a lingering side-effect of the "Ghost Bridge" issue from Part 3. Because the StarlingX VM was temporarily booted while the host's virtual network bridges were down, the internal Calico network controllers desynchronized from the main Kubernetes API server. They lost their active security tokens, completely locking them out from assigning IP addresses to new pods.

**The Fix:** We must force Kubernetes to reboot the network controllers to fetch fresh authentication tokens, then nuke the broken OAI pods so they can be rebuilt from scratch.

1. **Restart the Calico controllers:**
   ```bash
   kubectl delete pods -n kube-system -l k8s-app=calico-node
   kubectl delete pods -n kube-system -l k8s-app=calico-kube-controllers
   ```
2. **Verify the network is back online:**
   ```bash
   kubectl get pods -n kube-system | grep calico
   ```
   *(Wait until all Calico pods report a `Running 1/1` status).*
3. **Wipe the stuck OAI Core pods:**
   ```bash
   kubectl delete pods --all -n oai-core
   ```
   *(Helm will automatically detect the missing pods and spin up fresh ones, successfully assigning them IPs).*

---

### Pitfall 2: SMF `CrashLoopBackOff` (IPv6 Parser Panic)

![Screenshot from 2026-04-14 01-47-21](https://hackmd.io/_uploads/HybGi7WaZx.png)

> **The Encounter:** Once the network was fixed, all the core pods successfully initialized and hit `Running`—except for the SMF, which fell into a `CrashLoopBackOff`. We pulled the container logs (`kubectl logs -n oai-core -l app.kubernetes.io/name=oai-smf`). The log showed the SMF trying to parse the `ims` Data Network Name (DNN), hitting a blank `IPv6 prefix.......:`, and instantly throwing `Reading the configuration failed. Exiting.` 
> *Our initial attempt to fix this was changing the PDU session type from `IPv4v6` to `IPv4`, but the strict parser just crashed on the IPv6 DNS entry instead.*

**The Root Cause:** The default OAI Helm chart includes an IMS (IP Multimedia Subsystem) network configured for dual-stack (`IPv4v6`). However, the chart fails to pass a valid IPv6 prefix string to the SMF container. Because the newest OAI releases use a ruthlessly strict configuration parser, any malformed or missing variable causes a fatal crash.

**The Fix:** Since our primary goal is standard 5G data connectivity (not VoNR/Voice over 5G), the IMS network is entirely unnecessary. The cleanest fix is to amputate the broken IMS configuration completely.

**1. Scrub IMS from `config.yaml`:**
Open the configuration file:
```bash
nano config.yaml
```
* Delete the `- dnn: ims` item listed under `smfInfoList`.
* Scroll down to the `pdn` block and delete the entire `ims` array. Your configuration should only contain the `oai` IPv4 network:
    ```yaml
        pdn:
          - dnn: "oai"
            pdu_session_type: "IPv4"
            ipv4_subnet: "12.1.1.0/24"
    ```

**2. Disable IMS in `values.yaml`:**
Open the deployment values file:
```bash
nano values.yaml
```
Press `Ctrl+W` to search for `ims:`. Change its enabled flag to false:
```yaml
ims:
  enabled: false
```

**3. Push the Upgrade & Snipe the Pod:**
Force Helm to apply the cleaned configuration, then manually delete the crashing pod to break it out of its timeout loop.
```bash
helm upgrade basic-core . -n oai-core
kubectl delete pod -l app.kubernetes.io/name=oai-smf -n oai-core
```
   
![Screenshot from 2026-04-14 01-49-49](https://hackmd.io/_uploads/S1BmomWpWx.png)

***

# Part 6: Deploying the OAI 5G RAN & Establishing the Data Plane

**Context:** With the 5G Core Network functional, the final step for a complete end-to-end edge testbed is deploying the Radio Access Network (RAN) components: the gNodeB (Radio Tower) and the NR-UE (Simulated Phone). This phase establishes the RF simulator link and validates the UPF data plane by assigning a real IP address to the UE.

## 1. The Pre-Flight Configuration: Aligning 3GPP Network Logic
Before deploying the RAN, the Core Network must be explicitly configured to accept the specific network slice parameters requested by the UE. Failure to synchronize these definitions results in an immediate 403 `DNN_DENIED` rejection during the PDU Session establishment.

**The Goal:** Map Slice `SST: 1`, `SD: FFFFFF` (the default UE fallback) to the `oai` Data Network Name (DNN) instead of the default Voice-over-NR `ims` DNN.

Open the core configuration file (`charts-main/oai-5g-core/oai-5g-basic/config.yaml`) and make the following critical adjustments:
1. **Enable Local Subscriptions:** Set `use_local_subscription_info: yes` under the `smf` block to bypass external UDM lookups.
2. **Re-map the DNNs:** In `smf.smf_info.sNssaiSmfInfoList`, `smf.local_subscription_infos`, and `upf.upf_info.sNssaiUpfInfoList`, locate the `embb_slice2` definition (`sst: 1, sd: FFFFFF`) and change its authorized DNN from `"ims"` to `"oai"`.

Apply the core upgrade:
```bash
helm upgrade basic-core . -n oai-core
```

![Screenshot from 2026-04-21 12-12-55](https://hackmd.io/_uploads/ry-PZYvTWl.png)

## 2. Deploying the gNodeB (Radio Tower)
OpenAirInterface is an active research project; using bleeding-edge `develop` images guarantees instability. We must lock the deployment to a stable weekly build and configure it for the RF Simulator.

**1. Update the gNB Configuration (`charts-main/oai-5g-ran/oai-gnb/values.yaml`):**
* **Pin the Image:** Set `nfimage.version` strictly to `"2026.w15"`.
* **Remove Explicit SD:** Under `plmn_list.snssaiList`, delete the `sd: "0xffffff"` line to ensure the tower broadcasts a generic `sst: 1` slice.
* **Clean Startup Options:** Ensure `useAdditionalOptions` does **not** contain the `--sa` flag. Standalone mode is now the unchangeable default in modern OAI binaries.

**2. Deploy:**
```bash
cd $HOME/charts-main/oai-5g-ran/oai-gnb
helm install oai-gnb . -n oai-ran --set config.amfHost="oai-amf.oai-core.svc.cluster.local" --set config.radio="rfsim"
```

![image](https://hackmd.io/_uploads/SkQzDFwaZx.png)

## 3. Deploying the NR-UE (Simulated Phone)
The simulated phone acts as a TCP client connecting directly to the gNodeB's headless Kubernetes service.

**1. Update the UE Configuration (`charts-main/oai-5g-ran/oai-nr-ue/values.yaml`):**
* **Pin the Image:** Set `nfimage.version` to `"2026.w15"`.
* **Remove Explicit SD:** Under `pdu_sessions`, delete the `sd` parameter entirely so the UE utilizes its natural fallback behavior.

**2. Deploy with the strict FQDN:**
```bash
cd $HOME/charts-main/oai-5g-ran/oai-nr-ue
helm install oai-nr-ue . -n oai-ran --set config.rfSimServer="oai-ran.oai-ran.svc.cluster.local"
```

## 4. The Data Plane Verification
To verify the deployment is fully operational, check if the UPF successfully allocated a data pipe (virtual interface) to the UE.

```bash
export UE_POD=$(kubectl get pods -n oai-ran -l app.kubernetes.io/name=oai-nr-ue -o jsonpath="{.items[0].metadata.name}")
kubectl exec -n oai-ran -it $UE_POD -- ip a
```
**Success Condition:** You will see a `5: oaitun_ue1` interface with a valid subnet IP (e.g., `12.1.1.2`). 

You can cross-reference the success in the NAS logs:
```bash
kubectl logs -n oai-ran $UE_POD | grep -i "PDU Session Establishment Accept"
```

![image](https://hackmd.io/_uploads/HyCQwKDaZl.png)

***

# The Debug Pitfalls: RAN & Data Plane

### 1. The PDU Session Instant Rejection (403 DNN_DENIED)
* **Symptom:** The UE successfully registers and receives a GUTI, but the logs show `[NAS] E Received PDU Session Establishment reject`. The Core logs (SMF/AMF) are completely silent regarding the error.
* **Root Cause:** A 3GPP subscription mismatch between the Core and the RAN. The UE requests the `oai` DNN using the fallback slice `1.16777215` (SST 1, SD FFFFFF). By default, the core's static subscription database explicitly limits that specific slice to the `ims` DNN. 
* **Resolution:** Modified `oai-5g-basic/config.yaml` to map `embb_slice2` to `"oai"` instead of `"ims"` across the SMF and UPF info blocks.

### 2. The gNB Standalone Poison Pill (`unknown option: --sa`)
* **Symptom:** The `oai-gnb` pod falls into an immediate `CrashLoopBackOff`. Logs reveal `[CONFIG] unknown option: --sa`.
* **Root Cause:** Outdated documentation often suggests passing `--sa` to force 5G Standalone mode. In releases `2026.w15` and newer, the OpenAirInterface binary parsers have completely stripped this flag, as SA mode is now permanent.
* **Resolution:** Remove `--sa` from the `useAdditionalOptions` string in the gNB `values.yaml`.

### 3. The UE Ghost Domain (`Name or service not known`)
* **Symptom:** The `oai-nr-ue` pod runs, but logs are flooded with `E getaddrinfo: Name or service not known`. The UE never connects to the AMF.
* **Root Cause:** Passing a partial domain name (e.g., `oai-gnb.svc.cluster.local`) fails internal DNS resolution. Additionally, the headless service created by the gNB chart is named `oai-ran`, not `oai-gnb`.
* **Resolution:** Always provide the full Fully Qualified Domain Name (FQDN) including the target namespace during Helm installation: `oai-ran.oai-ran.svc.cluster.local`.

### 4. The Core Race Condition (Silent Routing Failure)
* **Symptom:** After a VM restart, the UE connects to the radio but gets no IP address. The SMF is healthy, but the AMF logs show timeouts.
* **Root Cause:** If Kubernetes boots the AMF, SMF, and UPF simultaneously (e.g., after fixing Calico ghost bridges), the AMF will cache an outdated SMF IP, or the SMF will fail to establish its N4 PFCP bind with the UPF. 
* **Resolution:** Perform a cascading chronological restart to force routing tables to sync:
    1. `kubectl delete pod -l app.kubernetes.io/name=oai-smf -n oai-core`
    2. Wait for SMF, then: `kubectl delete pod -l app.kubernetes.io/name=oai-gnb -n oai-ran`
    3. Wait for gNB N2 bind, then: `kubectl delete pod -l app.kubernetes.io/name=oai-nr-ue -n oai-ran`