---
title: HPE Server, OAI Helm Deployment, and WINLAB Configuration Guide
---

# HPE Server, OAI Helm Deployment, and WINLAB Configuration Guide

**Date:** 2026-06-30  
**Scope:** Access the HPE server through the BMW VPN, understand the `ocloud-helm-templates` deployment directory, identify where OAI runtime configuration lives, and interpret the key OAI NR configuration fields needed for WINLAB / Pegatron O-RU replication.
---

## 1. Relationship to the Jenkins Build Workflow

The full experiment pipeline has two halves:

| Stage | Main Tool | Output |
|---|---|---|
| Build and publish OAI image | Jenkins + Podman | Registry image such as `bmw.ece.ntust.edu.tw/<user>/oai-gnb:<tag>` |
| Deploy and configure OAI runtime | HPE server + Helm | Running gNB/VNF pod with selected image and OAI config |

This note covers the second half. The image build side is documented in [2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md](./2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md).

---

## 2. HPE Server Access

First, connect to the BMW WireGuard VPN. After the VPN is active, the HPE server is reachable on the lab subnet.

```bash
ssh hpe@192.168.8.26
```

Use the lab-provided password or SSH key. Do not store the password in this repository.

After login, the important project directory from the raw note is:

```text
CRAN/ocloud-helm-templates
```

Screenshot:

![HPE project directory](https://hackmd.io/_uploads/SJKi12gmMe.png)

---

## 3. What the Helm Directory Does

The `ocloud-helm-templates` directory contains Helm charts or chart templates used to deploy the CN/gNB/RU-related workloads onto the lab Kubernetes/O-Cloud environment.

The raw note says the Helm install command can pull/install the image created by Jenkins. More precisely:

1. Jenkins pushes the image to the BMW registry.
2. The Helm chart has values that define the image repository and tag.
3. `helm install` or `helm upgrade` renders the chart into Kubernetes manifests.
4. Kubernetes pulls the configured image and starts the pod.

Screenshot:

![Helm install context](https://hackmd.io/_uploads/BkYi13gQzg.png)

The exact command depends on the chart name, namespace, and values file. The general form is:

```bash
cd ~/CRAN/ocloud-helm-templates/<chart-directory>

helm upgrade --install <release-name> . \
  --namespace <namespace> \
  --create-namespace \
  -f values.yaml
```

If changing only the image reference, the command may use `--set`:

```bash
helm upgrade --install <release-name> . \
  --namespace <namespace> \
  -f values.yaml \
  --set image.repository=bmw.ece.ntust.edu.tw/<user>/oai-gnb \
  --set image.tag=<tag>
```

Use the chart's actual key names. Some charts use `image.repository`; others use names such as `vnf.image.repository`, `oai.image`, or a custom field.

---

## 4. Important Chart Area: `oai-vnf`

The raw note identifies an `oai-vnf` directory. In that chart, two files are especially important:

```text
oai-vnf/
+-- templates/
|   +-- configmap.yaml
+-- values.yaml
```

| File | Role |
|---|---|
| `templates/configmap.yaml` | Helm template that renders the OAI configuration file into a Kubernetes ConfigMap |
| `values.yaml` | Input values for the Helm chart: image, resources, node placement, addresses, OAI parameters, and other runtime settings |

### `templates/configmap.yaml`

This file usually contains the OAI `.conf` text or renders it from Helm values. It is responsible for producing the final gNB/VNF runtime configuration that the pod reads at startup.

Screenshots:

![OAI configmap.yaml location](https://hackmd.io/_uploads/rJKiyhe7Mg.png)

![OAI ConfigMap content](https://hackmd.io/_uploads/rkSFMnxmfe.png)

Typical things controlled by this file:

- PLMN and tracking area settings;
- AMF / core-network endpoint references;
- radio band and ARFCN values;
- TDD pattern;
- SSB and Point A frequency anchors;
- RF or fronthaul driver settings;
- command-line flags or mounted config paths.

### `values.yaml`

This file is the first place to check for deployment-level parameters.

Screenshots:

![values.yaml resource area](https://hackmd.io/_uploads/rkKjJnxQMx.png)

![values.yaml network/config area](https://hackmd.io/_uploads/HyFsknl7fx.png)

Common categories:

| Category | Example |
|---|---|
| Image | repository, tag, pull policy, image pull secret |
| Kubernetes resources | CPU request/limit, memory request/limit, hugepages |
| Node placement | node selector, affinity, tolerations |
| Core network | AMF address, MCC/MNC, TAC, slice/DNN |
| OAI radio config | band, ARFCN, TDD pattern, SSB position |
| Runtime flags | logging level, FHI/nFAPI mode, extra command options |

For WINLAB experiments, `values.yaml` should record the exact image tag and resource allocation. `configmap.yaml` should record the exact OAI radio configuration.

---

## 5. Helm Deployment Flow for a Jenkins-Built Image

After Jenkins pushes:

```text
bmw.ece.ntust.edu.tw/<user>/oai-gnb:<tag>
```

the Helm chart must be pointed to the same image.

Recommended workflow:

1. Choose an explicit image tag, not `latest`.
2. Update `values.yaml` or pass `--set` values for repository/tag.
3. Run `helm template` first if possible, to inspect the rendered manifests.
4. Deploy with `helm upgrade --install`.
5. Confirm the pod image matches the expected tag.
6. Save the rendered config or `helm get values` output as experiment evidence.

Useful commands:

```bash
helm template <release-name> . -f values.yaml > rendered.yaml

helm upgrade --install <release-name> . \
  --namespace <namespace> \
  -f values.yaml

kubectl get pods -n <namespace> -o wide

kubectl describe pod -n <namespace> <pod-name> | grep -i "Image:"

helm get values -n <namespace> <release-name> --all

kubectl get configmap -n <namespace> <configmap-name> -o yaml
```

Evidence to keep for each run:

```text
release_name=
namespace=
image_repository=
image_tag=
oai_commit=
helm_chart_commit_or_directory=
values_file_snapshot=
rendered_configmap_snapshot=
kubectl_pod_image=
```

---

## 6. Why OAI Configuration Matters for WINLAB Replication

The professor's target is not just "run OAI." The target is to reproduce or compare a specific O-RU throughput-power behavior. That means the radio configuration must be traceable.

For a throughput-vs-power experiment, these fields affect the result:

| Field Group | Why It Matters |
|---|---|
| Band and ARFCN | Determines the RF carrier location and whether it matches the Pegatron O-RU / UE setup |
| Channel bandwidth and SCS | Determines PRB count and slot duration |
| TDD pattern | Determines how many slots/symbols are DL, UL, or guard/flexible |
| SSB position | Determines synchronization signal placement and UE cell acquisition |
| Point A | Defines the common resource block grid anchor |
| Core network endpoint | Determines whether gNB can register and accept UE sessions |
| Resource allocation | CPU pinning/limits can change scheduler timing and throughput stability |

If any of these differ from the WINLAB baseline, throughput and RU power may not be comparable.

---

## 7. Current OAI TDD Pattern: `3D1S1U`

The raw note records:

```text
TDD Pattern (OAI conf): 3D1S1U
3 Downlink slots
1 Uplink slot
6 Downlink symbols
4 Uplink symbols
4 Mixed/flexible/guard symbols
```

This means the repeating TDD period has:

```text
Slot 0: D D D D D D D D D D D D D D
Slot 1: D D D D D D D D D D D D D D
Slot 2: D D D D D D D D D D D D D D
Slot 3: D D D D D D F F F F U U U U
Slot 4: U U U U U U U U U U U U U U
```

At 30 kHz SCS, each slot is 0.5 ms, so a 5-slot pattern repeats every:

```text
5 slots * 0.5 ms/slot = 2.5 ms
```

Symbol accounting over one 5-slot period:

| Symbol Type | Count | Fraction |
|---|---:|---:|
| Full DL slots | `3 * 14 = 42` symbols | |
| DL symbols in special slot | `6` symbols | |
| Total DL | `48 / 70` symbols | `68.6%` |
| Full UL slots | `1 * 14 = 14` symbols | |
| UL symbols in special slot | `4` symbols | |
| Total UL | `18 / 70` symbols | `25.7%` |
| Flexible/guard | `4 / 70` symbols | `5.7%` |

The 3GPP name for this structure is carried in `DL-UL-ConfigCommon`. Keysight's Signal Studio documentation gives a closely related DDDSU example for FR1 100 MHz and 30 kHz SCS with a 2.5 ms repetition period, `nrofDownlinkSlots = 3`, `nrofUplinkSlots = 1`, and special-slot DL/UL symbol fields. The exact special-slot split can differ by deployment; this note uses the values observed in the raw OAI configuration. Source: [Keysight, Configuring a Downlink Signal Under TDD Frame Structure](https://helpfiles.keysight.com/csg/n7631/Content/Main/Config%20DL%20Under%20TDD.htm).

### Why the TDD Pattern Matters for Throughput

The raw PHY capacity must be multiplied by the DL duty cycle. If a cell has about 68.6% DL symbols, its maximum DL throughput is lower than the same bandwidth in FDD or all-DL test mode.

For example:

```text
effective DL capacity ~= raw DL capacity * 0.686
```

Additional overhead then reduces it further:

- PDCCH control symbols;
- DMRS inside PDSCH grants;
- SSB and CSI-RS;
- HARQ retransmissions;
- MAC/RLC/IP overhead;
- scheduler behavior and UE channel quality.

This is why a WINLAB throughput target such as 65 Mbps or 84 Mbps cannot be interpreted from PRB count alone. The TDD pattern and scheduler logs are required.

### Why the TDD Pattern Matters for Power

For RU power, DL symbols are especially important because the RU transmit chain and PA are active. UL symbols keep receive chains active. Flexible or guard symbols may create partial sleep opportunity only if the RU is not transmitting or receiving other required signals.

For power-saving experiments:

- FDM/burst scheduling tries to concentrate traffic into fewer DL slots.
- TDM/spread scheduling keeps traffic present across more slots.
- A TDD pattern with frequent mandatory DL symbols reduces sleep opportunities.
- SSB/CSI-RS can keep the RU active even when no user data is scheduled.

---

## 8. OAI Frequency Fields in the Raw Note

The raw note records these OAI configuration fields:

```text
absoluteFrequencySSB 649920
dl_frequencyBand 78
dl_absoluteFrequencyPointA 646724
```

These are NR frequency-grid parameters.

| Field | Meaning |
|---|---|
| `dl_frequencyBand` | NR operating band. `78` means n78, a TDD FR1 band around 3.3-3.8 GHz. |
| `absoluteFrequencySSB` | NR-ARFCN for the SSB center/reference frequency used by UE synchronization. |
| `dl_absoluteFrequencyPointA` | NR-ARFCN for Point A, the common resource block grid reference. |

### ARFCN to Frequency Check

For FR1 frequencies between 3 GHz and 24.25 GHz, the NR-ARFCN raster uses:

```text
F_ref_MHz = 3000 + 0.015 * (N_REF - 600000)
```

Using the raw values:

```text
absoluteFrequencySSB = 649920
F_SSB = 3000 + 0.015 * (649920 - 600000)
      = 3000 + 748.8
      = 3748.8 MHz

dl_absoluteFrequencyPointA = 646724
F_PointA = 3000 + 0.015 * (646724 - 600000)
         = 3000 + 700.86
         = 3700.86 MHz
```

So the observed configuration places:

```text
SSB reference near 3748.8 MHz
Point A near 3700.86 MHz
Band: n78
```

Point A is not simply "the center frequency." It anchors the common resource block grid. The SSB frequency must be valid relative to that grid, the selected bandwidth, and the band's synchronization raster.

### Practical Validation

When reviewing or changing these values, check:

| Check | Why |
|---|---|
| Band is correct for the RU | Pegatron O-RU and UE must support n78 |
| ARFCNs map to the expected RF range | Prevents silent mismatch between gNB, RU, and UE |
| SSB position is valid | UE must find and decode SSB/PBCH |
| Point A matches bandwidth/SCS assumptions | Scheduler PRB indices depend on the CRB grid |
| Values match rApp or thesis baseline | Required for fair comparison to existing WINLAB results |

---

## 9. Relationship Between Bandwidth, SCS, PRBs, and WINLAB Metrics

The project notes often use the 100 MHz / 30 kHz SCS case because it gives the maximum FR1 PRB count:

```text
100 MHz channel bandwidth
30 kHz SCS
273 PRBs
0.5 ms slot duration
```

This matters because WINLAB-style metrics often report:

- offered traffic rate;
- measured E2E throughput;
- PRB utilization;
- RU power.

The scheduler consumes PRBs, but throughput depends on:

```text
throughput ~= PRBs * symbols * modulation * code_rate * layers * DL_duty_cycle - overhead
```

For example, using the project TBS notes:

- 273 PRBs in one DL slot gives a large instantaneous transport block;
- 27 PRBs over 10 slots gives almost the same PRB-slot volume;
- the actual measured throughput is lower after TDD duty cycle, PDCCH, DMRS, SSB/CSI-RS, HARQ, and protocol overhead.

Reference project notes:

- [5G NR Resource Grid and Scheduling Fundamentals](./2026-02-12_5G-NR-Resource-Grid-and-Scheduling-Fundamentals.md)
- [TBS Determination Worked Examples](./2026-02-26_TBS-Determination-Worked-Examples-273-vs-27-PRBs.md)
- [OAI and srsRAN MAC Scheduler PRB Scheduling](./2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md)

---

## 10. OAI Config Fields to Record for Every Experiment

For each WINLAB replication run, record at minimum:

| Category | Fields |
|---|---|
| Image | repository, tag, OAI commit, Jenkins build URL |
| Helm | chart path, release name, namespace, values snapshot |
| Core | AMF address, PLMN, TAC, NSSAI, DNN |
| Radio | `dl_frequencyBand`, `absoluteFrequencySSB`, `dl_absoluteFrequencyPointA`, bandwidth, SCS |
| TDD | periodicity, DL slots, DL symbols, UL slots, UL symbols |
| RU/FH | FHI/nFAPI mode, RU endpoint, PTP/sync status if exposed |
| Scheduler | original/modified mode, PRB cap if any, logging enabled |
| Resources | CPU limit/request, memory, hugepages, node placement |

Suggested run metadata block:

```text
run_id:
date_utc:
oai_image:
oai_commit:
helm_release:
namespace:
node:
oru:
band:
absoluteFrequencySSB:
dl_absoluteFrequencyPointA:
bandwidth_MHz:
scs_kHz:
tdd_pattern:
scheduler_mode:
offered_rate_mbps:
power_source:
```

---

## 11. Safe Configuration-Change Procedure

Use this sequence when modifying the OAI runtime config:

1. Save the current deployed values:

```bash
helm get values -n <namespace> <release-name> --all > before-values.yaml
kubectl get configmap -n <namespace> <configmap-name> -o yaml > before-configmap.yaml
```

2. Edit `values.yaml` or the relevant Helm value file.

3. Render locally:

```bash
helm template <release-name> . -f values.yaml > rendered.yaml
```

4. Inspect the rendered ConfigMap:

```bash
grep -n "absoluteFrequencySSB\\|dl_frequencyBand\\|dl_absoluteFrequencyPointA\\|nrofDownlinkSlots\\|nrofUplinkSlots" rendered.yaml
```

5. Deploy:

```bash
helm upgrade --install <release-name> . -n <namespace> -f values.yaml
```

6. Verify:

```bash
kubectl rollout status -n <namespace> deployment/<deployment-name>
kubectl logs -n <namespace> <pod-name> --tail=200
kubectl describe pod -n <namespace> <pod-name> | grep -i "Image:"
```

7. Save the after state:

```bash
helm get values -n <namespace> <release-name> --all > after-values.yaml
kubectl get configmap -n <namespace> <configmap-name> -o yaml > after-configmap.yaml
```

This gives enough evidence to prove which OAI image and configuration were active during a run.

---

## 12. Experiment Readiness Checklist

Before running a throughput-power test:

| Check | Expected Evidence |
|---|---|
| VPN active | HPE server reachable over SSH |
| Kubernetes context valid | `kubectl get nodes` works |
| Helm release identified | `helm list -n <namespace>` shows target release |
| Image tag updated | Pod description shows expected Jenkins-built image |
| ConfigMap rendered correctly | OAI config contains expected band, SSB, Point A, and TDD fields |
| gNB registered | Logs show successful connection to AMF / core |
| UE attached | UE gets PDU session / data path is established |
| Traffic generator ready | iPerf or rApp test case can run target offered rate |
| Power source ready | CortexDC/PDU export path known and timestamp-aligned |
| Scheduler logs ready | PRB allocation/MCS/TBS fields can be captured or inferred |

---

## 13. Common Mistakes

| Mistake | Impact | Prevention |
|---|---|---|
| Updating Jenkins image but not Helm values | Old pod image is redeployed | Verify pod `Image:` field |
| Reusing `latest` | Cannot trace which code was measured | Use run-specific image tags |
| Editing `templates/configmap.yaml` but deploying a different chart | No runtime effect | Use `helm template` and inspect rendered output |
| Changing ARFCN without validating SSB/Point A relationship | UE cannot find or attach to cell | Convert ARFCNs to MHz and compare against known-good baseline |
| Ignoring TDD pattern | Throughput estimates do not match measured DL throughput | Record DL/UL/flexible symbol fractions |
| Comparing scheduler modes with different resources | CPU scheduling noise contaminates result | Keep `values.yaml` resource requests/limits fixed |
| Power data not timestamp-aligned | Throughput-power plot is not defensible | Use UTC markers and a run summary table |

---

## 14. Immediate Next Questions for Lab Continuation

1. Which Helm release and namespace correspond to the Pegatron O-RU E2E test?
2. Which `oai-vnf` values keys set the image repository and tag?
3. Which OAI config file is currently used for the known-good WINLAB/Pegatron run?
4. Are the raw values `absoluteFrequencySSB=649920`, `dl_frequencyBand=78`, and `dl_absoluteFrequencyPointA=646724` the current baseline?
5. Is the active special-slot split truly `6 DL / 4 flexible / 4 UL`, or should it match the common `10 DL / 2 guard / 2 UL` DDDSU example?
6. How does CortexDC export RU power data, and what timestamp format does it use?

These answers determine whether the current config is already the baseline, or whether the chart must be adjusted before running the first throughput-power sweep.
