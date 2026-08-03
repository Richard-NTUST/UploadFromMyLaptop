# O-RAN Power Measurement: Pilot Run 01

## Executive Summary
This run validates the *Scaphandre-on-Ubuntu* pipeline for RU power estimation. We successfully isolated the software "static tax" from the "dynamic workload" power.

## Key Findings
- *Platform Idle Power* (pure idle mean): 1.023 W
- *O-RAN Software Overhead* (active-idle − idle): +0.851 W
- *Workload Dynamic Power* (load − active-idle): +33.405 W
- *Load Throughput* (iperf3 TCP): 97.464 Gbps
- *Efficiency* (throughput / mean load power): 2.763 Gbps/W

## Conclusion
The high sensitivity (≈34× from pure idle to load mean power) confirms this setup can measure large power/efficiency shifts across workload states. Results should be reported as **platform power under RU-like workload** until RU input power is measured with hardware.