---
title: WINLAB nFAPI Baseline Clarifications and Next Learning Target
---

# WINLAB nFAPI Baseline Clarifications and Next Learning Target

**Date:** 2026-06-30  
**Purpose:** Capture the clarified baseline assumptions after the HPE end-to-end walkthrough, and define the next learning target.

---

## 1. Current Baseline Understanding

The first official reproduction target should use Ming's nFAPI path.

```text
Architecture: nFAPI
Scheduler mode: OAI original scheduler
Deployment target: HPE server
Traffic path: 2 UE E2E iPerf / Magic iPerf
Throughput evidence: iPerf output
Power evidence: CortexDC / PDU export, still pending exact RU source
```

This replaces the earlier ambiguity between:

- F1 split,
- monolithic gNB,
- nFAPI split.

For the current project direction, treat the baseline label as:

```text
nfapi_pegatron_original_oai
```

---

## 2. What We No Longer Need From Ming

Ming already showed the practical end-to-end line:

```text
Modify/select OAI image
-> build image with Jenkins
-> deploy through Helm on the HPE server
-> check pod with k9s/kubectl
-> connect to UEs by AnyDesk
-> disable airplane mode / attach to 5G
-> use PingTest to note UE IP
-> start Magic iPerf on UE
-> run iPerf from server side
-> record throughput result
```

So we do not need another full E2E architecture walkthrough.

We also do not need Ming to define all sweep parameters if we standardize them ourselves and keep them fixed across scheduler modes.

---

## 3. What We May Still Need From Ming

Only narrow confirmations remain.

| Topic | Why It Still Matters |
|---|---|
| Known-good HPE Helm release / namespace | Needed to avoid deploying to the wrong chart or namespace |
| Exact nFAPI baseline chart/config path | Needed to make the baseline reproducible |
| Whether the current OAI config is the thesis/lab baseline | Needed before calling results "replicated" |
| How image variants should be selected later | Needed for scheduler comparison runs |

The important distinction:

```text
Ming is no longer the main blocker for understanding the flow.
Ming is only needed for lab-specific baseline confirmation.
```

---

## 4. Parameters We Can Standardize Ourselves

Sweep settings can be defined by us, as long as they are documented and reused consistently.

Recommended two-level plan:

### Smoke Test

Use this for debugging access, pod health, UE attach, and iPerf path.

```text
Bitrate: 100 Mbps
Stabilization: 30 s
Traffic duration: 60 s
Repeats: 1
Power use: optional / sanity only
```

### Final Baseline Sweep

Use this for the first defensible original-OAI result.

```text
Bitrates: 100, 400, 700 Mbps
Stabilization: 30-120 s
Traffic duration: 300 s
Repeats: 3 per bitrate
Power source: CortexDC / PDU
Clock basis: UTC timestamps
```

If CortexDC/PDU sampling is slow or noisy, use the longer stabilization target:

```text
Stabilization: 120 s
Traffic duration: 300 s
```

The key rule:

```text
Original OAI, time-domain OAI, and frequency-domain OAI must use the same sweep settings.
```

---

## 5. Throughput Evidence

Throughput can be taken directly from the iPerf call.

For each run, record:

```text
run_id:
architecture: nFAPI
scheduler_mode:
target_bitrate_mbps:
traffic_duration_s:
stabilization_s:
ue1_ip:
ue2_ip:
server_ip:
iperf_command:
iperf_start_utc:
iperf_end_utc:
measured_throughput_mbps:
packet_loss_or_retransmits:
jitter_if_udp:
```

Prefer saving machine-readable output when possible:

```bash
iperf3 -c <UE_IP> -u -b 100M -t 300 --json
```

If Magic iPerf only gives GUI output, record:

- screenshot,
- UTC start/end time,
- target bitrate,
- measured throughput,
- UE IP,
- server command.

---

## 6. Run ID Convention

Use run IDs that encode the architecture, scheduler mode, bitrate, and repeat.

Baseline:

```text
nfapi_original_100m_run01
nfapi_original_400m_run01
nfapi_original_700m_run01
```

Later scheduler variants:

```text
nfapi_timedomain_100m_run01
nfapi_frequencydomain_100m_run01
nfapi_prbcap27_100m_run01
```

This keeps the final plot traceable.

---

## 7. Remaining Main Blocker: Power Measurement

The largest remaining unknown is no longer the E2E line. It is the RU power source.

The direction note says the required plot is:

```text
X-axis: E2E throughput
Y-axis: Pegatron RU power consumption
Curve: OAI original scheduler
```

The CortexDC workbook helps with server inventory and PDU mapping, but it does not yet identify the Pegatron O-RU power outlet/source.

Known from the current CortexDC context:

```text
PDU: Raritan PX4-5256CR-C8E8A0
PDU outlets: 12 total
Occupied outlets: 4, 5, 6, 8, 9, 10, 11, 12
CortexDC assets: 13 servers, 1 PDU, 1 network device
RU asset info: not currently recorded in CortexDC Assets
```

Therefore, the next learning target is:

```text
Ms. Chynna - CortexDC / PDU power measurement path
```

---

## 8. What To Learn From Ms. Chynna

Ask specifically about measurement mechanics, not general project direction.

Questions:

```text
1. Which CortexDC asset or PDU outlet corresponds to the Pegatron O-RU?
2. Can CortexDC export timestamped active power for that outlet?
3. What is the export format: CSV, Excel, screenshot, API, or database query?
4. What are the fields and units? W, kW, Wh, current, voltage?
5. What is the sampling interval?
6. Does CortexDC use local time or UTC?
7. Can we select a time window matching the iPerf run?
8. Is there existing Pegatron RU power data from previous nFAPI tests?
```

The required output from this learning session should be:

```text
CortexDC export procedure
PDU outlet / RU source mapping
power CSV schema
timestamp alignment method
sample baseline export file
```

---

## 9. Updated Next Action

Immediate next action:

```text
Learn the CortexDC/PDU export path from Ms. Chynna.
```

After that:

```text
1. Run one nFAPI original-OAI smoke test.
2. Save iPerf throughput output.
3. Export matching CortexDC/PDU power window.
4. Build the first throughput-power data row.
5. Repeat for 100 / 400 / 700 Mbps once the pipeline works.
```

Clean decision:

```text
Ming = baseline nFAPI / sweep workflow reference.
Chynna = next required learning target for power measurement.
```
