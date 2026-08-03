# 2026-07-27 Lavoisier Post-Reboot Fronthaul Recovery and Stable E2E

## Question

Why did otherwise Ready OCloud PNF/VNF pods repeatedly fail to attach the UE or
crash after Lavoisier was rebooted, and what recovery sequence returns the lab
to a known-good E2E state?

## Short Answer

Lavoisier needs an explicit post-BMC-reboot fronthaul setup step. A reboot does
not restore the SR-IOV virtual functions, VFIO/DPDK binding, RU-facing VLAN/IP
addresses, or performance settings needed by the PNF. Starting the Kubernetes
pods before this setup can produce severe xRAN and nFAPI timing failures.

The verified recovery is:

1. Restore Lavoisier fronthaul networking with `setup_network.sh`.
2. Start and verify the Lavoisier kubelet.
3. Verify the worker is `Ready` and PNF/VNF are stable.
4. Restore the RU with `rrr` then `pegam` only when its configuration was
   changed for another experiment.
5. Confirm the Samsung UE already has a `10.45.x.x` address, then run E2E in
   preserve-UE-state mode.

## Lab Components

| Component | Role | Operational fact |
| --- | --- | --- |
| HPE (`192.168.8.26`) | Open5GS, bare-metal rApp, E2E runner | E2E rApp listens on `127.0.0.1:9090`. |
| Lavoisier (`192.168.8.82`) | Kubernetes worker, OAI PNF/VNF, fronthaul NIC | The `super` SSH alias from HPE reaches this host. |
| Lavoisier BMC | Out-of-band recovery | `https://192.168.10.92/` is used when Lavoisier is unavailable. |
| Pegatron RU | Commercial O-RU | Its expected configuration is restored by `pegam` after external use. |
| Samsung UE | E2E traffic endpoint | Serial: `R5CN30TMBYR`; a valid cellular data attach uses `10.45.x.x`. |

## What the Network Setup Script Restores

Run on Lavoisier:

```bash
/home/oai72_su/Script/setup_network.sh enp67s0f1
```

The script is not a simple IP setup. It restores the PNF fronthaul host state:

1. Applies real-time-oriented performance settings when available.
2. Loads `sctp`, `iavf`, and `vfio_pci` kernel modules.
3. Sets `enp67s0f1` to MTU `9600` and requests larger NIC rings.
4. Removes existing SR-IOV VFs and creates two new VFs.
5. Configures the VFs for VLAN `103`, the expected RU-facing MAC, MTU `9600`,
   and disabled spoof checking.
6. Restores `192.168.109.10/24` on the physical interface and a route to
   `192.168.109.9`; restores VLAN `104` with `192.168.110.10/24` and a route
   to `192.168.110.9`.
7. Rebinds both VFs to `vfio-pci`, allowing the PNF's DPDK/xRAN path to use
   them.

### Important Safety Rule

The script destroys and recreates the PNF's SR-IOV devices. Do not run it while
PNF is active. Scale PNF to zero first, run the script, then restore PNF.

```bash
K=/home/hpe/CRAN/kubectl
C=/home/hpe/CRAN/ming-kubeconfig.yaml
N=ming-ns

$K --kubeconfig="$C" scale deploy oai-pnf-pegatron -n "$N" --replicas=0
ssh super '/home/oai72_su/Script/setup_network.sh enp67s0f1'
ssh super 'sudo systemctl start kubelet; systemctl is-active kubelet'
$K --kubeconfig="$C" get node lavoisier
$K --kubeconfig="$C" scale deploy oai-pnf-pegatron -n "$N" --replicas=1
```

If the node was rebooted, do not submit E2E until `lavoisier` reports `Ready`.

## Failure Signatures and Meaning

### Kubernetes node unavailable

```text
NodeStatusUnknown: Kubelet stopped posting node status.
```

This means the worker cannot safely run or replace OAI pods. Recover kubelet
through the Lavoisier console, then wait for `Ready` before changing deployments.

### PNF xRAN timing collapse

```text
xran_timingsource_poll_next_tick too long, delta: 885993165 ns
Assertion (xran_queue_length == 0) failed
```

The timing thread is designed around a 500 microsecond interval. An 886 ms
delay is a real-time/fronthaul failure, not a normal performance warning. It
causes frame/slot jumps and ends the PNF process before UE attach is possible.

### nFAPI P7 timing collapse

```text
check_nr_p7_timing: dl_tti_request too early by 381415 us (window:6500)
```

The accepted timing window is 6.5 ms, but the request was about 381 ms out of
time. This confirms the PNF/VNF/RU timing chain is invalid; it is not a UE or
iPerf issue.

### Misleading PNF `Completed` status

The PNF entrypoint pipes `nr-softmodem` output through `tee`. Without
`set -o pipefail`, an OAI assertion can appear to Kubernetes as a successful
exit from `tee`, even though the PNF crashed. Treat repeated `Completed` or
`CrashLoopBackOff` together with xRAN assertions as a PNF failure.

## RU Recovery Is Separate

Use `rrr` followed by `pegam` only when the RU has been used, moved, or
reconfigured for another experiment. `rrr` restarts the RU; `pegam` reapplies
the expected M-plane/U-plane configuration. They do not replace Lavoisier's
post-reboot fronthaul script.

```bash
ssh super
rrr
# wait for RU boot
pegam
```

## Stable E2E Procedure

1. Confirm Lavoisier is `Ready` and both pods are `1/1 Running` with no recent
   restarts.
2. Confirm the Samsung UE already has a `10.45.x.x` address.
3. Submit the bare-metal rApp on HPE using `preserve_ue_state: true`.

This option was added to prevent the rApp from toggling airplane mode when a
manual UE attach is already present. It fails promptly if there is no UE IP,
and it leaves airplane mode unchanged after success or failure.

```bash
curl -fsS -X POST http://127.0.0.1:9090/gnb/run \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ocloud",
    "server": "hpe",
    "target_identity": "hpe-pegatron-ru-o",
    "ue_serial": "R5CN30TMBYR",
    "iapc_host": "sshuser@140.118.162.81",
    "iapc_port": 24,
    "bandwidth": [200],
    "period": 300,
    "gap_time": 2,
    "ue_model": "samsung",
    "settle_time": 30,
    "attach_timeout": 120,
    "preserve_ue_state": true
  }'
```

The five-minute validation job submitted on 2026-07-27 was
`4b44c8e9-a03a-4ed2-b6ea-b67d7397ff83`.

## Operational Boundary

This sequence makes recovery repeatable, but it does not eliminate shared-lab
coordination. Before changing pods, resetting VFs, or restoring RU settings,
confirm that no other experiment is using the PNF/RU path.
