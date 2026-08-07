# OAI latest baseline sweep through 600 Mbps

This directory consolidates the 5 August 2026 OAI `latest` baseline load sweep.
Power is Raritan PDU Outlet 2 `active_power`, clipped by
`scripts/merge_winlab_e2e_power.py` to each iPerf object's actual traffic
window. The InfluxDB export covers the padded UTC interval
`2026-08-05T05:18:00Z`–`2026-08-05T07:14:00Z`.

| Offered (Mbps) | Delivered (Mbps) | Mean power (W) | Energy (nJ/bit) | Power samples | Completion | Use |
|---:|---:|---:|---:|---:|---:|---|
| 100 | 100.008 | 40.594 | 405.909 | 10 | 100% | Complete |
| 200 | 200.007 | 40.992 | 204.952 | 10 | 100% | Complete |
| 300 | 299.976 | 41.020 | 136.744 | 8 | 76.333% | Incomplete diagnostic |
| 400 | 399.498 | 41.326 | 103.445 | 10 | 100% | Complete |
| 500 | 495.066 | 42.015 | 84.867 | 10 | 100% | Complete |
| 600 | 549.112 | 41.953 | 76.402 | 6 | 65.333% | Incomplete diagnostic |

The selected 200 Mbps point is the full retry (`060051`), not the partial
duplicate in `051900`. The interrupted `065806` attempt has no finalized
throughput CSV and is excluded. The 300 and 600 Mbps points are retained only
as explicitly marked diagnostic evidence.

Per-step completion is the established positive-traffic window span divided
by the requested 600 seconds. The 300 Mbps window spans 458 seconds (76.333%)
but contains 429 finalized one-second throughput samples; this distinction is
another reason to keep it diagnostic rather than treat it as a complete run.

Across the complete 100–500 Mbps points, delivered throughput increased by
395.0% while mean Outlet 2 power increased by 3.50%. A descriptive least-
squares fit over those four points is
`P(W) = 40.2752 + 0.0032028 × throughput(Mbps)` (`R² = 0.9246`). This is not
yet a validated RU power model: it has only four complete single-run points,
no repetitions or confidence intervals, and roughly one-minute PDU sampling.
The 600 Mbps result additionally shows offered-load saturation and is partial.

`energy_per_bit_nj = avg_power_w × 1000 / rx_throughput_mbps`.
