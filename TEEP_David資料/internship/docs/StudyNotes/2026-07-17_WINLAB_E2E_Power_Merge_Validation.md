# WINLAB E2E Power Merge Validation

**Date:** 2026-07-17

## Goal

Validate that one successful OCloud E2E run can be joined with PDU Outlet 2 active-power data into one throughput-power summary row.

## Successful E2E Run

The Dockerized rApp endpoint on HPE was used:

```text
http://127.0.0.1:19090
```

Successful job:

```text
ce4d30b0-abb6-409e-96b0-74a55c1c7c79
```

Remote artifact directory:

```text
/home/hpe/winlab_e2e_rapp/runs/winlab_e2e_rapp/e2e-ocloud-20260717-083449
```

Run summary:

| Field | Value |
|---|---|
| Mode | `ocloud` |
| Target | `hpe-pegatron-ru-o` |
| UE serial | `R5CN30TMBYR` |
| UE IP | `10.45.0.3` |
| Offered load | `100 Mbps` |
| Duration | `60 s` |
| Direction | Downlink / reverse-mode iPerf |
| Result | Succeeded |
| Packet loss | `0%` |

The actual iPerf interval used by the merge script was:

```text
2026-07-17T08:35:33Z to 2026-07-17T08:36:33Z
```

## Power Data Source

The correct power source for the Pegatron RU `[O]` path is PDU Outlet 2:

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

The useful padded export file in this workspace is:

```text
pdu_data_20260717_083250_083840.csv
```

The exact run-window export only had one sample because CortexDC/InfluxDB currently records Outlet 2 at roughly one-minute cadence. A padded export is useful for QA, but the merge script only counts samples inside the actual iPerf step window.

## Merge Script

Local script:

```text
scripts/merge_winlab_e2e_power.py
```

Inputs:

- `summary.json`
- `iperf-UE-RX.log`
- `offered_load_throughput.csv`
- `pdu_data_*.csv`

Output:

```text
power_throughput_summary_20260717_083449.csv
```

The script now handles InfluxDB nanosecond timestamps by truncating fractional seconds to Python-compatible microseconds before parsing.

## Validation Result

Merged output:

```csv
run_id,mode,target_identity,offered_load_mbps,rx_throughput_mbps,start_utc,end_utc,avg_power_w,min_power_w,max_power_w,sample_count
e2e-ocloud-20260717-083449,ocloud,hpe-pegatron-ru-o,100.0,99.9959612864077,2026-07-17T08:35:33Z,2026-07-17T08:36:33Z,40.04,40.04,40.04,1
```

Interpretation:

- the rApp/E2E side produced a valid 100 Mbps throughput run;
- the PDU export contained one Outlet 2 `active_power` sample inside the iPerf window;
- the merge script successfully produced the final summary schema;
- `sample_count=1` is expected for a short 60 s run with about one-minute PDU sampling.

## Remaining Improvement

For stronger reporting, future tests should use either:

- longer iPerf periods, for example 180-300 s per offered-load level; or
- repeated runs at the same offered load.

This will produce more PDU samples per traffic window and make the average power value more defensible.
