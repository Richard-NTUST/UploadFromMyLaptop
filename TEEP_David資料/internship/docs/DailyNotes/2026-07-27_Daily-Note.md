# Daily Note

## Date

**Date:** 2026/07/27

---

## Short-term Goal

Validate a known-good bare-metal O-Cloud E2E baseline after fronthaul recovery, document the recovery path, and return the shared lab to a clean state when other users need it.

### Goals and milestones

1. **Validate the baseline E2E path**
   - Complete a five-minute, 200 Mbps downlink test with saved artifacts.
   - Record the evidence needed to distinguish radio attachment from iPerf traffic.

2. **Make worker recovery repeatable**
   - Document the post-BMC-reboot fronthaul preparation and kubelet recovery sequence.
   - Separate conditional RU recovery from the normal per-test procedure.

3. **Bound the custom-image test**
   - Check the deployed VNF image identity and the effect of a VNF rollout on the UE.
   - Avoid treating a mutable `latest` tag as conclusive custom-image provenance.

4. **Hand over the shared namespace cleanly**
   - Remove temporary workloads before the server is used by others.

## Plan

| Priority | Task | Expected result |
| --- | --- | --- |
| P1 | Run a baseline bare-metal rApp test | Valid iPerf samples and pod-log artifacts |
| P1 | Record Lavoisier post-reboot recovery | Repeatable fronthaul and kubelet runbook |
| P2 | Assess the custom VNF image test | Clear deployment provenance and failure boundary |
| P1 | Clean `ming-ns` for handoff | No temporary OAI workloads left running |

## Review Table

| Task | Status | Evidence / Result |
| --- | --- | --- |
| Five-minute baseline E2E | Complete | Job `4b44c8e9-a03a-4ed2-b6ea-b67d7397ff83` completed at 200 Mbps for 300.06 s, transferred 6.99 GBytes, and reported 0 packet loss. |
| Bare-metal rApp preserve-UE mode | Complete | The port `9090` rApp now supports preserving UE state: it neither changes airplane mode nor retries attachment when no `10.45.x.x` address exists. |
| Post-BMC worker recovery runbook | Complete | Identified `/home/oai72_su/Script/setup_network.sh enp67s0f1` followed by kubelet recovery as the required worker/fronthaul preparation after a Lavoisier BMC reboot. |
| RU recovery boundary | Complete | `rrr` and `pegam` are conditional recovery actions after another user has moved, repurposed, or reconfigured the RU; they are not required before every E2E run. |
| Custom-image long-run validation | Blocked | The VNF chart used mutable `latest`; the observed digest could not prove which Jenkins build was deployed. A VNF rollout also reset UE user-plane state, so the preserve-UE run correctly exited before traffic began. |
| RF attachment investigation | In progress | During the no-attach state, pods and AMF/F1 control-plane setup were healthy but no UE RACH/RRC setup appeared. Nemo observations of n78 cells did not match the configured OAI cell, so the UE was not confirmed to be selecting the intended cell. |
| Shared-lab cleanup | Complete | Temporary `gnb` and `nrue` Helm releases were uninstalled from `ming-ns` with the correct kubeconfig before shared use began. |

### Progress Summary

The baseline path is reproducible when the worker and fronthaul are prepared correctly. The successful bare-metal job used port `9090`, a 200 Mbps offered load, and a five-minute traffic period. It produced 302 UE iPerf samples plus throughput plots, CSV files, and copied VNF/PNF logs under:

```text
/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260727-053805
```

The critical post-reboot discovery is that a Lavoisier BMC reboot leaves the network interfaces required by the fronthaul path unprepared. Before starting the PNF after such a reboot, keep the PNF scaled to zero, run `/home/oai72_su/Script/setup_network.sh enp67s0f1` on Lavoisier, start kubelet, and wait for the worker to report `Ready`. The detailed runbook is recorded in [Lavoisier Post-Reboot Fronthaul Recovery](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-07-27_Lavoisier_PostReboot_Fronthaul_Recovery_and_Stable_E2E.md).

The custom-image result is not yet a valid A/B comparison. Jenkins published the build through the mutable `latest` tag, so the deployed digest alone did not establish whether the running VNF contained the desired scheduler change. Rolling the VNF also reset the UE attachment state. The subsequent preserve-UE run failed safely because no UE `10.45.x.x` address existed; it did not cycle airplane mode or introduce an additional radio recovery attempt.

The later no-attach state was diagnosed as a radio-selection/RU-path problem rather than an iPerf or rApp problem. The worker, PNF, VNF, and core-side setup were available, but the UE showed no active interface and no RACH/RRC setup was observed in the VNF logs. Nemo saw nearby n78 cells whose ARFCN, PCI, and PLMN did not match the OAI configuration. This is a diagnostic discriminator, not a final root-cause claim: the next test must confirm the intended on-air cell before invoking E2E.

From 14:00 onward the server was passed between users. The temporary test workloads were removed and no further changes should be assumed after the handoff.

### Pending Tasks and Blockers

| Item | Blocking condition | Next action |
| --- | --- | --- |
| Confirm the intended OAI cell is on air | UE must see/select the configured PLMN, PCI, and SSB before attachment | Use Nemo and VNF logs to confirm the target cell and observe RACH/RRC setup before running E2E. |
| Obtain immutable image provenance | Jenkins currently publishes to mutable `latest` | Build/push a unique tag, set that tag in the Helm VNF values, and record the resulting digest. |
| Compare baseline and custom scheduler image | Requires stable RF attach and immutable tag | Run matched short tests first, then a longer test and merge PDU power data. |
| Coordinate use of Lavoisier/RU | Shared lab state may change outside this work | Reserve an exclusive window and confirm worker, RU, and UE state before deployment. |

---

## Next Working Day Plan

| Priority | Task | Success condition |
| --- | --- | --- |
| P1 | Reserve a test window and preflight the RF path | Lavoisier is `Ready`; PNF/VNF are healthy; Nemo confirms the intended cell; UE completes RACH/RRC. |
| P1 | Deploy a uniquely tagged scheduler image | Helm values and image digest identify the exact Jenkins build. |
| P1 | Run matched baseline/custom short tests | Both produce valid UE iPerf samples and comparable artifacts. |
| P2 | Run a longer validated workload and merge PDU data | Throughput/power summary is generated from the exact E2E time window. |
