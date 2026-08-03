# iperf Summary (Server Log)

This file summarizes `iperf.txt` by extracting per-test `[SUM]` throughput lines from the server output and mapping tests 1..9 to the 9 load segments (L/M/H x 3) in chronological order.

Important note: the sweep script uses `-P 4`. If `-b` applies per stream in your `iperf3` mode, the aggregate throughput will be ~4× the `-b` target.

| Segment | State | Round | iperf test | Mean (Gbps) | Min (Gbps) | Max (Gbps) | Samples |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Load_L_Run1 | Load-L | 1 | 1 | 120.00 | 120.00 | 120.00 | 100 |
| Load_M_Run1 | Load-M | 1 | 2 | 238.28 | 172.00 | 285.00 | 100 |
| Load_H_Run1 | Load-H | 1 | 3 | 267.23 | 132.00 | 350.00 | 101 |
| Load_L_Run2 | Load-L | 2 | 4 | 120.00 | 120.00 | 120.00 | 100 |
| Load_M_Run2 | Load-M | 2 | 5 | 238.66 | 180.00 | 265.00 | 100 |
| Load_H_Run2 | Load-H | 2 | 6 | 263.41 | 53.50 | 408.00 | 113 |
| Load_L_Run3 | Load-L | 3 | 7 | 120.00 | 120.00 | 120.00 | 100 |
| Load_M_Run3 | Load-M | 3 | 8 | 235.58 | 116.00 | 302.00 | 100 |
| Load_H_Run3 | Load-H | 3 | 9 | 266.14 | 172.00 | 366.00 | 100 |
