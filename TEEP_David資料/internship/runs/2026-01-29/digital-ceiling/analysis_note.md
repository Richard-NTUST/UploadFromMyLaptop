# Digital Ceiling Analysis (Stress Test)

## Run Details
- **Date**: 2026-01-29
- **Goal**: Establish the absolute maximum power consumption of the proxy platform (Digital Ceiling) to compare against the "Gap".
- **Tool**: `stress-ng` (CPU stress).

## Observations
- **Peak Power**: ~59.05 W (Observed at `08:50:30Z`).
- **Throttling**: A distinct drop occurred around `08:51:30Z` (down to ~21 W), identified by the operator as "Low Battery Mode" activation.
- **Comparison**: 
    - This **59 W** peak is >2x the typical active load seen in iperf sweeps (~25-27 W).
    - However, it is still **~138 W lower** than the *minimum* Idle power of a theoretical Macro O-RU (197 W).

## Conclusion for Gap Analysis
Even if the digital hardware runs at absolute thermal limits (Stress), it cannot account for the "Gap". The missing hundreds of watts are physically attributable to the RF Front End / Power Amplifier bias currents, which are absent in this specific hardware but present in real RUs.
