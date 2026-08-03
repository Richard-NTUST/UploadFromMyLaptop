# Daily Note

## Date

**Date:** 2026/07/23

---

## Short-term Goal

Restore a reproducible bare-metal OCloud E2E baseline, identify the current radio configuration failure domain, and publish the first narrowly scoped OAI scheduling experiment for image build.

### Goal 1: Restore a valid OCloud E2E baseline

* Milestone 1: Confirm HPE network connectivity after Docker removal and reboot, Due 2026/07/23
* Milestone 2: Reapply the Pegatron RU E2E configuration only when it has been changed for another use, Due 2026/07/23
* Milestone 3: Produce a valid 5-minute bare-metal rApp throughput artifact, Due 2026/07/23

### Goal 2: Locate the scheduler modification seam

* Milestone 1: Trace the active NR downlink scheduler policy pipeline, Due 2026/07/23
* Milestone 2: Preserve HARQ retransmission and control-only behavior, Due 2026/07/23
* Milestone 3: Publish one measurable new-data scheduling experiment, Due 2026/07/23

---

## Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Planned Evidence |
| -------- | ---- | -------------------------------- | -------------------- | ---------------- |
| P1 | Recover HPE and RU E2E readiness | Goal 1 | Usable HPE network and RU configuration | NIC/DHCP checks and `pegam` procedure |
| P1 | Run a bare-metal 5-minute validation | Goal 1 | Valid iPerf artifact | rApp job and iPerf server output |
| P2 | Compare Nemo Handy cell view with VNF configuration | Goal 1 | Radio mismatch diagnosis | Cell table and `gnb.conf` values |
| P2 | Trace OAI downlink scheduler code | Goal 2 | Safe policy seam | Scheduler discovery and learning notes |
| P1 | Create and push PRB-cap experiment branch | Goal 2 | Jenkins-buildable OAI commit | Git commit and remote branch |

---

## Review

| Task | Status | Evidence |
| ---- | ------ | -------- |
| Recover HPE and RU E2E readiness | Complete | `ens1f3` link was restored and DHCP obtained `192.168.8.26`; RU reset procedure identified as `ssh super` then `pegam` when another activity has changed the RU configuration. |
| Run a bare-metal 5-minute validation | Complete | Job `4a7915a3-9378-4afd-ab3e-28467736318b` on `127.0.0.1:9090` completed 300 seconds at 200 Mbps with 0% reported packet loss and 300 UE samples. |
| Compare Nemo Handy cell view with VNF configuration | Complete | Nemo Handy observed a different broadcast cell than the VNF configuration, supporting the conclusion that the RU had been changed for another purpose. |
| Trace OAI downlink scheduler code | Complete | Identified the policy flow and phase-3 new-data allocation seam in the OAI scheduler. |
| Create and push PRB-cap experiment branch | Complete | Branch `david/oai-prb-cap-27-20260723`, commit `d7c850098a`, built successfully by Jenkins #89 and published with tag `david-oai-prb-cap-27-20260723`. |
| Deploy the PRB-cap VNF and prepare an E2E test | Blocked | The custom VNF rolled out and registered with the AMF, but the PNF crashed while loading the worker-mounted xRAN library before an E2E run could start. |

### Progress Summary

After Docker removal and an HPE reboot, the host initially had no active production NIC state. The physical link on `ens1f3` was restored and DHCP assigned `192.168.8.26`. This repaired host reachability but did not itself prove the radio path.

The UE-side Nemo Handy evidence and the running VNF configuration did not describe the same cell. The VNF advertised PLMN `001/01`, PCI `0`, and SSB ARFCN `649920`, whereas the observed cell table showed n78 ARFCN `623328` and PCI `27`. This is consistent with the Pegatron RU having been reconfigured for a separate activity. The E2E RU reset is therefore an operational prerequisite only after such a change, not a step for every test run.

After the RU configuration was restored, the bare-metal rApp on `127.0.0.1:9090` completed a valid 300-second, 200 Mbps downlink test:

```text
Job: 4a7915a3-9378-4afd-ab3e-28467736318b
Artifact: /home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260723-050642
Transfer: 6.99 GBytes
Rate: 200 Mbps
Loss: 0%
UE samples: 300
```

This proves that the current OCloud, core, RU, UE, and bare-metal rApp path can produce valid traffic after recovery. It does not prove that Docker was the root cause of prior failures; Docker/nFAPI routing interference remains a hypothesis requiring a controlled comparison.

The first scheduler behavior experiment is intentionally narrow. In `nr_dl_proportional_fair()`, only phase-3 new-data scheduling is capped at 27 PRBs. HARQ retransmissions and no-data control grants retain the default behavior. The log marker was changed to `mode=oai_prb_cap_27` so the deployed image can be identified from pod logs.

Jenkins #89 completed successfully for commit `d7c850098a`, and `oai-vnf` was rolled out with `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-prb-cap-27-20260723`. Its VNF pod registered with AMF successfully. The PNF could not start, however: its mounted `/home/oai72_su/oai_mp_f_ming/phy_k/fhi_lib/lib/build/libxran.so` has an unresolved `MLogSetTaskCoreMap` symbol. The library declares no provider for that symbol and the paired `nr-softmodem` does not export it, indicating a worker-side FHI/xRAN build mismatch rather than a scheduler-image regression. The PNF deployment was scaled to zero to stop the crash loop.

### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
| ---- | ------ | -------------------------- |
| Restore compatible PNF FHI/xRAN runtime | PNF crashes before radio startup because `libxran.so` cannot resolve `MLogSetTaskCoreMap` | Restore or rebuild the matching worker-side FHI/xRAN bundle, then scale PNF back to one replica |
| Validate the custom image | VNF is deployed, but PNF is deliberately stopped until its runtime is repaired | Re-run the 5-minute 200 Mbps test after the PNF reaches Ready state |
| Compare energy effect | One modified run cannot establish an energy conclusion | Export matching Outlet 2 power data and merge it with baseline/custom artifacts |

---

## Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
| -------- | ---- | -------------------------------- | -------------------- |
| P1 | Restore the PNF FHI/xRAN runtime | OCloud radio dependency | PNF Ready without the `MLogSetTaskCoreMap` loader failure |
| P1 | Smoke-test the deployed PRB-cap VNF | Scheduler experiment | 5-minute 200 Mbps artifact with `mode=oai_prb_cap_27` logs |
| P2 | Export Outlet 2 power and run merge | Measurement comparison | Baseline/custom throughput-power summary |
| P3 | Escalate only reproducible Docker-vs-bare-metal differences | Environment stability | Controlled evidence for or against the Docker hypothesis |
