---
title: WINLAB InfluxDB Outlet 2 Power Access
date: 2026-07-09
---

# WINLAB InfluxDB Outlet 2 Power Access

**Date:** 2026-07-09  
**Purpose:** Record the confirmed data access path for Pegatron RU `[O]` power measurement and how it connects to the OAI nFAPI / OCloud E2E experiment artifacts.

---

## 1. Current Status

We now have the data access needed for the throughput-vs-power experiment.

Confirmed:

```text
E2E experiment path: Pegatron RU [O]
Power source: PDU Outlet 2 active_power
InfluxDB bucket: cortexdc_pdu
Measurement: pdu_outlet
Field: active_power
PDU IP: 192.168.10.72
Sensor: Outlet 2
CSV export path: InfluxDB HTTP API /api/v2/query
```

This resolves the earlier blocker where Chynna could see Outlet 2 data in InfluxDB but could not export it from the UI.

---

## 2. Why Outlet 2

Ming confirmed that the E2E tests use the Pegatron RU `[O]` path.

Ravi's outlet schedule maps:

| Outlet | Device | Usage |
|---|---|---|
| Outlet 1 | Pegatron RU `[N]` | OC/DU testing |
| Outlet 2 | Pegatron RU `[O]` | OCloud testing |
| Outlet 11 | Lavoisier | `[O-Cloud]` OAI NFAPI PNF / OAI Split 7.2 gNB + Commercial RU |

Therefore, for the current OAI nFAPI / OCloud E2E experiment, use:

```text
Outlet 2 active_power
```

Do not use Outlet 11 as RU-only power. Outlet 11 is associated with Lavoisier/server-side equipment, not the standalone Pegatron RU `[O]` power source.

---

## 3. InfluxDB Fields

The exported rows confirmed this schema:

```text
_start
_stop
_time
_value
_field
_measurement
asset_id
asset_tag
category
pdu_ip
sensor_id
sensor_name
```

Important values:

| Column | Required Value |
|---|---|
| `_measurement` | `pdu_outlet` |
| `_field` | `active_power` |
| `asset_id` | `17` |
| `category` | `outlet` |
| `pdu_ip` | `192.168.10.72` |
| `sensor_id` | `16` |
| `sensor_name` | `Outlet 2` |

The main analysis columns are:

```text
_time   -> UTC timestamp
_value  -> active power in watts
```

---

## 4. Flux Query

Use raw rows for analysis. Avoid `aggregateWindow()` for the final data export because we want to align power samples to the rApp/iPerf test windows ourselves.

Template:

```flux
from(bucket: "cortexdc_pdu")
  |> range(start: 2026-07-08T04:05:00Z, stop: 2026-07-08T07:30:00Z)
  |> filter(fn: (r) => r["_measurement"] == "pdu_outlet")
  |> filter(fn: (r) => r["_field"] == "active_power")
  |> filter(fn: (r) => r["asset_id"] == "17")
  |> filter(fn: (r) => r["category"] == "outlet")
  |> filter(fn: (r) => r["pdu_ip"] == "192.168.10.72")
  |> filter(fn: (r) => r["sensor_id"] == "16")
  |> filter(fn: (r) => r["sensor_name"] == "Outlet 2")
```

For UI inspection, an aggregated graph is fine:

```flux
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

For CSV export and final plotting, prefer raw rows without `aggregateWindow()`.

---

## 5. HTTP CSV Export

Use the InfluxDB query API with a token stored in an environment variable. Do not hard-code or commit the token.

```bash
export INFLUX_TOKEN='REPLACE_WITH_LOCAL_TOKEN'

curl --request POST \
  "http://192.168.8.48:8086/api/v2/query?orgID=d346b4cdcce3e360" \
  --header "Authorization: Token $INFLUX_TOKEN" \
  --header "Accept: application/csv" \
  --header "Content-Type: application/vnd.flux" \
  --data 'from(bucket: "cortexdc_pdu")
    |> range(start: 2026-07-08T04:05:00Z, stop: 2026-07-08T07:30:00Z)
    |> filter(fn: (r) => r["_measurement"] == "pdu_outlet")
    |> filter(fn: (r) => r["_field"] == "active_power")
    |> filter(fn: (r) => r["asset_id"] == "17")
    |> filter(fn: (r) => r["category"] == "outlet")
    |> filter(fn: (r) => r["pdu_ip"] == "192.168.10.72")
    |> filter(fn: (r) => r["sensor_id"] == "16")
    |> filter(fn: (r) => r["sensor_name"] == "Outlet 2")' \
  > pdu_data.csv
```

Check the result:

```bash
wc -l pdu_data.csv
head -n 10 pdu_data.csv
```

Confirmed local export:

```text
pdu_data.csv
207 lines for 2026-07-08T04:05:00Z to 2026-07-08T07:30:00Z
```

Example rows:

```text
_time,_value,_field,_measurement,pdu_ip,sensor_id,sensor_name
2026-07-08T04:05:33.818938112Z,39.1,active_power,pdu_outlet,192.168.10.72,16,Outlet 2
2026-07-08T04:06:33.844582912Z,40.03,active_power,pdu_outlet,192.168.10.72,16,Outlet 2
2026-07-08T04:07:33.83839616Z,38.58,active_power,pdu_outlet,192.168.10.72,16,Outlet 2
```

---

## 6. Sampling Rate

The PDU data appears to be sampled about once per minute.

This matters because short rApp/iPerf tests will only have a few power samples.

Example short run:

```text
started_utc:  2026-07-08T04:05:34Z
finished_utc: 2026-07-08T04:06:52Z
```

Matching PDU samples:

```text
2026-07-08T04:05:33.818938112Z -> 39.10 W
2026-07-08T04:06:33.844582912Z -> 40.03 W
```

Approximate average:

```text
(39.10 + 40.03) / 2 = 39.565 W
```

For final experiments, use longer windows per offered-load step so that each step has enough PDU samples. A 20-second sanity test is valid for pipeline verification, but weak for power statistics.

---

## 7. Alignment With rApp Artifacts

Each rApp E2E run writes an artifact directory such as:

```text
/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-YYYYMMDD-HHMMSS/
```

Important files:

| File | Purpose |
|---|---|
| `summary.json` | Run metadata, start/end UTC, mode, target identity, output paths |
| `iperf_timeseries.csv` | Throughput time series |
| `offered_load_throughput.csv` | Offered-load vs RX-throughput summary |
| `iperf_throughput.png` | Throughput-over-time plot |
| `offered_load_throughput.png` | Offered-load vs RX-throughput plot |
| `iperf-UE-RX.log` | Pulled UE iPerf JSON/log source |
| `ocloud_pod_logs/` | VNF/PNF pod logs for OCloud runs |

Power alignment should use:

```text
summary.json started_utc / finished_utc
pdu_data.csv _time / _value
```

For each run or each offered-load step, filter PDU rows where:

```text
step_start_utc <= _time <= step_end_utc
```

Then compute:

```text
avg_power_w
min_power_w
max_power_w
sample_count
```

---

## 8. Desired Merged Output

The next analysis script should output a merged CSV like:

```text
run_id,mode,target_identity,offered_load_mbps,rx_throughput_mbps,start_utc,end_utc,avg_power_w,min_power_w,max_power_w,sample_count
```

This enables final plots:

```text
offered_load_mbps vs rx_throughput_mbps
offered_load_mbps vs avg_power_w
rx_throughput_mbps vs avg_power_w
energy_per_bit or watts_per_mbps if needed
```

---

## 9. Security Note

An InfluxDB token was used for API export. Treat tokens as local secrets:

```text
Do not paste tokens into notes.
Do not commit tokens.
Use INFLUX_TOKEN or a local .env file.
Rotate/revoke exposed tokens when needed.
```

The note records the API path and query shape, not the token value.

---

## 10. Final Current Answer

Yes, we now have access to the core data needed for the experiment:

```text
Throughput data: rApp/iPerf artifacts
Power data: InfluxDB Outlet 2 active_power CSV
Time base: UTC timestamps from summary.json and InfluxDB _time
Join key: test window start/end time
```

Remaining work is no longer access discovery. It is integration:

```text
1. Add automated PDU export or accept uploaded pdu_data.csv.
2. Merge power rows with rApp step windows.
3. Generate final throughput-vs-power plots.
4. Containerize the rApp once Docker is available on HPE.
```
