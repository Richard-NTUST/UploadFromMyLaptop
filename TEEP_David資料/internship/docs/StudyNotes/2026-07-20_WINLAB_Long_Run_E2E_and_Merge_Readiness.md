# WINLAB Long-Run OCloud E2E and Power Merge Validation

**Date:** 2026-07-20

## Goal

Validate that the Dockerized WINLAB rApp can run a longer OCloud E2E throughput test and merge the resulting throughput artifact with CortexDC/InfluxDB Outlet 2 active-power data.

## Confirmed E2E Run

Dockerized rApp endpoint:

```text
http://127.0.0.1:19090
```

Successful job:

```text
3bb047b9-2b21-48b5-bc3b-d66f2a79dcba
```

Remote artifact directory:

```text
/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260720-061120
```

Local copied snapshot:

```text
runs/hpe_artifacts/e2e-ocloud-20260720-061120
```

Run summary:

| Field | Value |
|---|---|
| Mode | `ocloud` |
| Target | `hpe-pegatron-ru-o` |
| UE serial | `R5CN30TMBYR` |
| UE controller | `sshuser@140.118.162.81:24` |
| UE IP | `10.45.0.9` |
| Offered load | `200 Mbps` |
| Requested period | `3600 s` |
| Captured UE samples | `1676` |
| Average RX throughput | `199.892 Mbps` |
| Result | `succeeded` |

The run produced the expected artifact set:

```text
summary.json
request.json
command.txt
command.json
e2e_stdout.log
iperf_timeseries.csv
iperf_throughput.png
offered_load_throughput.csv
offered_load_throughput.png
ocloud_pod_logs/
```

The summary file reports:

```text
started_utc: 2026-07-20T06:11:20.657146Z
finished_utc: 2026-07-20T06:42:08.218506Z
ue_iperf_samples: 1676
```

## Long-Run Stability Finding

Earlier 20-minute attempts could continue sending traffic but leave the rApp job stuck because the UE-side Android iPerf process did not reliably exit for long `-t` values. The fix was to bound the long-running path in two places:

- `ue_driver.py` wraps Android `iperf3` with `/system/bin/timeout`.
- `cloud_e2e.py` adds a watchdog around the UE iPerf driver process.

The 2026-07-20 run completed and finalized artifacts instead of hanging indefinitely, so the watchdog direction is valid.

## Important Caveat

This was submitted as a one-hour request, but the captured evidence is about 1676 one-second UE samples, and the wrapper finished at 2026-07-20T06:42:08Z. Treat it as a successful long-run stability test, not as a full 3600-second power-baseline sample window.

For strict one-hour evidence, the next test should either:

- split the run into smaller repeated windows, for example three 20-minute runs; or
- further investigate why Android iPerf terminates early on the long request.

## Merge Script Update

The local merge script is:

```text
scripts/merge_winlab_e2e_power.py
```

It was updated so iPerf JSON step windows prefer the actual captured interval span when interval samples exist. This matters for long-run cases where `test_start.duration` still shows the requested duration, but the actual interval list is shorter.

Without this correction, power samples could be selected over the requested 3600-second window instead of the real captured traffic window.

## PDU Data Source

The correct power source remains CortexDC/InfluxDB PDU Outlet 2:

| Field | Value |
|---|---|
| Bucket | `cortexdc_pdu` |
| Measurement | `pdu_outlet` |
| Field | `active_power` |
| `asset_id` | `17` |
| `category` | `outlet` |
| `pdu_ip` | `192.168.10.72` |
| `sensor_id` | `16` |
| `sensor_name` | `Outlet 2` |

The matching export window for this run is:

```text
2026-07-20T06:11:20Z to 2026-07-20T06:42:08Z
```

Exported local filename:

```text
pdu_data_20260720_061120_064208.csv
```

Export command, after setting `INFLUX_TOKEN`:

```bash
curl --request POST \
  "http://192.168.8.48:8086/api/v2/query?orgID=d346b4cdcce3e360" \
  --header "Authorization: Token $INFLUX_TOKEN" \
  --header "Accept: application/csv" \
  --header "Content-Type: application/vnd.flux" \
  --data 'from(bucket: "cortexdc_pdu")
    |> range(start: 2026-07-20T06:11:20Z, stop: 2026-07-20T06:42:08Z)
    |> filter(fn: (r) => r["_measurement"] == "pdu_outlet")
    |> filter(fn: (r) => r["_field"] == "active_power")
    |> filter(fn: (r) => r["asset_id"] == "17")
    |> filter(fn: (r) => r["category"] == "outlet")
    |> filter(fn: (r) => r["pdu_ip"] == "192.168.10.72")
    |> filter(fn: (r) => r["sensor_id"] == "16")
    |> filter(fn: (r) => r["sensor_name"] == "Outlet 2")' \
  > pdu_data_20260720_061120_064208.csv
```

Merge command used:

```bash
python3 scripts/merge_winlab_e2e_power.py \
  runs/hpe_artifacts/e2e-ocloud-20260720-061120 \
  pdu_data_20260720_061120_064208.csv \
  -o power_throughput_summary_20260720_061120.csv
```

## Merge Result

Merged output:

```text
power_throughput_summary_20260720_061120.csv
```

Final row:

```csv
run_id,mode,target_identity,offered_load_mbps,rx_throughput_mbps,start_utc,end_utc,avg_power_w,min_power_w,max_power_w,sample_count
e2e-ocloud-20260720-061120,ocloud,hpe-pegatron-ru-o,200.0,199.89228792135998,2026-07-20T06:11:20.657146Z,2026-07-20T06:42:08.218506Z,40.096774193548384,38.03,41.58,31
```

Interpretation:

- OCloud E2E traffic reached `199.892 Mbps` average RX throughput for a `200 Mbps` offered load.
- Outlet 2 active-power data contributed `31` samples inside the selected run window.
- Average Outlet 2 active power was `40.097 W`.
- Power ranged from `38.03 W` to `41.58 W` during the selected window.

## Current Status

- E2E run: complete.
- Artifact snapshot: copied locally for the main CSV/plot/summary/log artifacts.
- Merge script: updated for actual interval windows.
- PDU export: complete in `pdu_data_20260720_061120_064208.csv`.
- Final merged power summary: complete in `power_throughput_summary_20260720_061120.csv`.
