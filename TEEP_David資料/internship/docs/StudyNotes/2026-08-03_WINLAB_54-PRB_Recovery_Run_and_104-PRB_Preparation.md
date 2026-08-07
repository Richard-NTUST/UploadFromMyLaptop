# WINLAB 54-PRB Recovery Run and 104-PRB Preparation

**Date:** 2026-08-03  
**Workspace:** WINLAB OAI scheduler-versus-O-RU-power experiment  
**Status:** 54-PRB run complete but partial; 104-PRB source prepared for a later reserved slot

## Objective and Scope

Today's active experiment was the immutable 54-PRB condition at a 500 Mbps offered load for 20 minutes. The next condition was changed from the previously planned 106 PRBs to 104 PRBs. A later 900 Mbps run on OAI `latest` remains planned after the capped-condition sweep.

The scientific observables remain delivered UE throughput, scheduler telemetry, Outlet 2 power, energy per delivered bit, and run completeness. The user chose pragmatic progression rather than requiring 100% completion as a gate; partial completion must therefore be reported transparently and must not be represented as a complete 20-minute result.

## Infrastructure Interruption

Approximately two hours of the afternoon gap were used by David to debug and restore the computers providing Jenkins and Quay. Those machines had remained down following maintenance on 2026-08-02. This was experiment-enabling infrastructure recovery, not idle experiment time. After restoration, Jenkins and the registry were reachable again and the 54-PRB image could be built and retrieved.

## 54-PRB Image

| Item | Value |
|---|---|
| Source branch | `david/oai-prb-cap-54-20260731` |
| Source commit | `e72a03d91949d706059ac2b4a1379e646592083c` |
| Jenkins build | `#90`, successful |
| Image | `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-prb-cap-54-20260731` |
| Registry manifest digest | `sha256:538ef4d014ad9ce7ff56a7a771bb19c4312b41ed4a866e833b75240a103002aa` |
| Runtime image ID | `sha256:307d0e269a4187df719e0d48928ce639c8084f843411bdebb121fd3b9ee983ea` |

## Radio Recovery

The first VNF deployment did not establish a usable cell. An ordered restart restored continuous nFAPI P7 exchange, but the RU VF still showed no receive traffic and the UE could not attach. David then uninstalled the releases, ran the established `rrr` and `pegam` recovery procedures, and reinstalled PNF/VNF.

The reinstall reverted the VNF to `latest`; preflight caught this before the measurement. The VNF was upgraded back to the exact 54-PRB image and restarted in the required order. Continuous P7, RU timing traffic, increasing PRACH counters, and successful RRC/PDU attachment were then observed. Both pods were Ready with stable restart counts before the run.

## 500 Mbps 54-PRB Run

| Item | Result |
|---|---|
| Job ID | `72eb416c-062b-4c0e-b04c-a3e2f9a98240` |
| Artifact directory | `/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260803-080851` |
| Requested load/duration | 500 Mbps / 1200 seconds |
| UE samples | 940 |
| UE-measured duration | 940.000805 seconds |
| UE completion | 78.3334% |
| Server-reported duration/completion | 1060 seconds / 88.3% |
| Mean UE delivered throughput | 191.297 Mbps |
| Minimum / maximum | 61.959 / 197.461 Mbps |
| Positive-traffic UTC window | `2026-08-03T08:09:29Z` to `2026-08-03T08:25:09.000805Z` |
| Outlet 2 power samples | 16 |
| Outlet 2 mean / minimum / maximum | 40.18625 / 39.53 / 40.99 W |
| Outlet 2 sample SD / CV | 0.453841 W / 1.129% |
| O-RU energy per delivered bit | 210.072 nJ/bit |
| Pod state during run | PNF and VNF 1/1, zero restarts |
| Final rApp state | Failed on idle timeout after partial collection |

The UE JSON is authoritative for delivered-throughput duration and completeness. The server-side duration is retained as a secondary diagnostic. Because the UE completion is below the former 80% diagnostic minimum and below the requested duration, this result is usable for diagnosis and partial-condition comparison only; it is not a complete 20-minute replicate.

## Scheduler Validation

The copied scheduler log contained 3,983 grants labeled `oai_prb_cap_54`:

- 3,974 grants with `rbSize=54`
- 4 retransmissions with `rbSize=60`
- 5 retransmissions with `rbSize=149`

Every grant above 54 PRBs had `is_retx=1`. No new-data grant exceeded the configured 54-PRB cap, so the scheduler cap behavior was validated for the captured interval. Retransmissions remain intentionally exempt.

## Power Alignment and Energy Metric

Outlet 2 `active_power` was exported from InfluxDB for the padded interval `2026-08-03T08:08:00Z` to `2026-08-03T08:27:30Z` and saved as `pdu_data_20260803_080800_082730.csv`. The established merge script clipped it to the UE JSON's actual positive-throughput interval, `08:09:29Z` to `08:25:09.000805Z`, and wrote `power_throughput_summary_20260803_080851.csv`.

Sixteen approximately one-minute PDU samples overlap the 940.000805-second traffic window. Their mean active power is 40.18625 W, with a 39.53-40.99 W range, 0.453841 W sample standard deviation, and 1.129% coefficient of variation.

Using delivered UE throughput rather than offered load:

`energy per delivered bit = 40.18625 W / (191.29727389701 × 10^6 bit/s) = 2.10072 × 10^-7 J/bit = 210.072 nJ/bit`.

Multiplying mean power by the observed duration gives an estimated 37.775 kJ (10.493 Wh) for approximately 179.820 Gbit (22.477 GB) delivered during the captured interval. This estimate assumes the sample mean represents the intervals between the PDU's coarse one-minute observations.

The power alignment is complete and scientifically usable for this partial interval. It does not turn the run into a complete 20-minute replicate, and it does not establish an energy-saving claim without a directly comparable controlled condition.

## 104-PRB Preparation

A clean 104-PRB variant was derived from the immutable 27-PRB parent `d7c850098ac96f89a04695e6342ceca8ec757555`. Only the new-data PRB cap and telemetry condition label were changed.

| Item | Value |
|---|---|
| Branch | `david/oai-prb-cap-104-20260803` |
| Commit | `d01a1b79ae57def67b8734428f2447f20dafe855` |
| Telemetry mode | `oai_prb_cap_104` |
| Intended image tag | `david-oai-prb-cap-104-20260803` |
| Diff validation | Two files, two insertions, two deletions; `git diff --check` clean |
| State | Pushed; Jenkins build not triggered; cluster unchanged |

The 104-PRB run is deferred until after 19:00 because of the reservation. Before it starts, repeat the full reservation, Lavoisier, SR-IOV, exact-image, restart-count, Nemo-cell, UE-attachment, and rApp-health preflight. After the capped-condition work, run the separately controlled 900 Mbps condition using a newly resolved immutable digest for OAI `latest`.
