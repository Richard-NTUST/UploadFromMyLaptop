# WINLAB 900 Mbps PRB-Cap Sweep and Debug-UI Assessment

**Date:** 2026-08-04
**Status:** Four operating points power-aligned; debug-UI integration backlogged

## Scope and Controls

This sweep tested whether limiting OAI downlink new-data grants changes throughput and O-RU Outlet 2 power under a constant 900 Mbps offered load. Controls were the WINLAB UE and expected Nemo cell (ARFCN 649920, PCI 0, PLMN 001-01), O-RU, PNF worker runtime, core, rApp workflow, 20-minute request, outlet, and alignment method. The VNF image changed between 27-, 54-, and 104-PRB caps; digest-pinned OAI `latest` is a separate uncapped/high-throughput reference.

## Immutable Conditions

| Condition | Runtime image digest | Successful job / artifact |
|---|---|---|
| 27 | `david-oai-prb-cap-27-20260723@sha256:409690de1803d3705b3419f4a35cbe65e36efa1af2f832d5977b6db5fff9eadd` | `6c7e1a73-7e4a-4c66-b1e5-77d3c7df68ba` / `e2e-ocloud-20260804-061813` |
| 54 | `david-oai-prb-cap-54-20260731@sha256:307d0e269a4187df719e0d48928ce639c8084f843411bdebb121fd3b9ee983ea` | `24241728-e93a-4169-b001-6959de29421c` / `e2e-ocloud-20260804-065538` |
| 104 | `david-oai-prb-cap-104-20260803@sha256:1f1ffe2736e8e0ce91e90db586348d3bc8d42cbe669019a4154b8af58e239a8a` | `1e2e5c03-6943-46ae-abeb-b71de0f1df67` / `e2e-ocloud-20260804-071951` |
| `latest` | `latest@sha256:c227006518795bdb517db0db15be7c12850c9184297e4cb514ea3987a5108edc` | `5554c656-d8af-472c-a49c-66851814a393` / `e2e-ocloud-20260804-040735` |

The staged 54 digest `538ef4d014ad...` was not pullable and caused `ImagePullBackOff`; it was not measured. The verified CRI repository digest above was deployed after recovery. PNF exited once with code 141 during transition, then recovered before preflight.

## Aligned Results

| Condition | Throughput | Completion | Power | Energy / delivered bit |
|---|---:|---:|---:|---:|
| 27 | 95.601 Mbps | 93.25% | 40.952 W | 428.36 nJ/bit |
| 54 | 191.585 Mbps | 82.00% | 41.258 W | 215.35 nJ/bit |
| 104 | 362.052 Mbps | 93.08% | 41.536 W | 114.72 nJ/bit |
| `latest` | 760.715 Mbps | 93.00% | 41.988 W | 55.20 nJ/bit |

Power inputs/outputs were `pdu_data_20260804_061730_064100.csv` / `power_throughput_summary_20260804_061813.csv` (27; 19 samples), `pdu_data_20260804_065500_071530.csv` / `power_throughput_summary_20260804_065538.csv` (54; 16), `pdu_data_20260804_071900_074230.csv` / `power_throughput_summary_20260804_071951.csv` (104; 18), and `pdu_data_20260804_040700_043030.csv` / `power_throughput_summary_20260804_040735.csv` (`latest`; 18).

Throughput rose approximately with the cap while mean power changed by only about 1.04 W; energy per delivered bit therefore fell sharply. This suggests a large load-independent component in measured O-RU power, not a general causal scheduler-efficiency law.

## Run and Scheduler QC

The successful 27 repeat had nine buffer-full reports and no unknown-RB or RRC-reestablishment events. The 54 run had 113 buffer-full reports and no unknown-RB or reestablishment events; live telemetry showed `oai_prb_cap_54`, but rotated artifact logs lacked a complete grant distribution. The 104 run captured 26,998 `oai_prb_cap_104` grants: all 25,945 new-data grants were at or below 104; one retransmission used 115, consistent with a cap applying only to new data. `latest` had 16 unknown-RB messages during a successful RRC re-establishment, after which traffic continued. Measured pods did not restart.

The first 27 job, `18b18926-3d1c-4893-8a24-c5d002bc65ba` (`e2e-ocloud-20260804-060556`), produced only 125.001074 seconds of positive traffic (10.4168%) before unknown-RB and buffer-full errors wedged attachment. It is excluded. Recovery placed the UE in airplane mode, restarted PNF and verified stable RU/P7, restarted VNF and its image, then restored radio and verified cell, attachment, and user plane before the successful repeat.

## Scientific Boundary

These are sequential single runs in a shared lab without randomization, confidence intervals, or drift estimates. The builds have different source lineages, especially `latest`. Report throughput, power, energy/bit, completeness, and QC together; do not claim statistical significance or causality. The 54 result is only diagnostic-minimum quality at 82%. A stricter study needs randomized repeats on a common source base with a runtime-selectable cap.

## Ming Debug-UI Assessment and Decision

Read-only inspection of `/home/hpe/ming-oai-debug-rapp` found that it selects source trees with `oai_path`, SSHes to hosts, runs `sudo ninja`, launches host `nr-softmodem` in `screen`, restarts Open5GS, manages NIC/MTU and UE state, and collects host logs. It has no Kubernetes namespace, Helm release, image repository/version, digest verification, or pod-log controls; `start_container` is Docker over SSH.

Worktree profiles could test source-built host binaries, but not the immutable Jenkins/Quay images used here. Proper support requires a separate O-Cloud/Helm backend with tag/digest validation, ordered PNF/VNF rollouts, runtime `imageID` verification, and Kubernetes logs. This offers no immediate benefit over the rApp and native actions could interfere with the live split path, so integration is backlogged.

## Final State

The final successful condition was digest-pinned 104 PRB, with measured pods Ready and zero restarts. Documentation caused no cluster, RU, networking, image, rApp, or UE mutation. The temporary InfluxDB token file in `/tmp` was intentionally retained; its value is not recorded.
