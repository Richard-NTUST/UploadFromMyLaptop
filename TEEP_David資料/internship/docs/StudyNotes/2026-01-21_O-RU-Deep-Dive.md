# O-RAN Radio Unit (O-RU) Deep Dive: Architecture, Power, and Implementation (2026-01-21)

Status: Complete
Deadline: 2026-01-21

This note provides a detailed technical analysis of the O-RU physical implementation, power consumption characteristics, and hardware architecture. It builds on Part 1 (architecture fundamentals) and Part 2 (RIC/interfaces) to provide the hardware foundation needed for power measurement work.

Part 1 is in:
- `docs/StudyNotes/2026-01-16_O-RAN Principles.md`

Part 2 is in:
- `docs/StudyNotes/2026-01-16_O-RAN-Principles_Part-2_RIC-and-Interfaces.md`

## Table of contents
- [Why this matters for power measurement](#why-this-matters-for-power-measurement)
- [O-RU hardware architecture](#o-ru-hardware-architecture)
- [Power consumption breakdown](#power-consumption-breakdown)
- [The 7.2x split boundary in detail](#the-72x-split-boundary-in-detail)
- [O-RU categories and profiles](#o-ru-categories-and-profiles)
- [Fronthaul transport and timing](#fronthaul-transport-and-timing)
- [Power management and energy saving](#power-management-and-energy-saving)
- [Measurement implications](#measurement-implications)
- [Key takeaways](#key-takeaways)

## Why this matters for power measurement

Understanding O-RU internal architecture is critical because:
- **Different power domains**: RF analog power behaves fundamentally differently from digital processing power
- **Measurement point selection**: AC input captures everything; platform counters miss RF components entirely
- **Workload correlation**: Not all "throughput" translates equally to power—PA efficiency curves are non-linear
- **Baseline vs dynamic**: O-RU has significant static power even at 0% utilization (bias voltages, ready-state)

When we measure "RU power" we are measuring a specialized radio computer, not a general-purpose server.

## O-RU hardware architecture

### Physical form factors

O-RUs come in various physical configurations:
- **Macro RU**: High-power outdoor units (40W-300W typical), often IP65/IP67 rated
- **Small cell RU**: Indoor/outdoor, lower power (10W-60W typical)
- **Massive MIMO RU**: 64T64R or higher, can exceed 500W
- **mmWave RU**: 5G high-band units with integrated antenna arrays

![image](https://hackmd.io/_uploads/H12mCQCBWl.png)


### Major hardware subsystems

#### 1. RF Front End (Analog Domain)

**Components:**
- **Power Amplifier (PA)**: The primary power consumer
  - Class AB/Doherty/GaN technology common
  - Efficiency: 25-40% typical (meaning 60-75% becomes heat)
  - Output power: 20-63 dBm (100mW to 200W per antenna)
- **Low Noise Amplifier (LNA)**: First stage receiver amplification
- **Duplexer/Filters**: Frequency separation for TX/RX
- **RF switches**: Antenna routing, TDD timing
- **Circulators**: Isolate TX from RX in same frequency bands

**Power characteristics:**
- Dominates total RU power budget (60-80% of total)
- Non-linear relationship with output power
- Temperature-sensitive (efficiency degrades with heat)
- Always "on" with bias current even when idle

![image](https://hackmd.io/_uploads/r1zr0mCr-x.png)

#### 2. Digital Front End (DFE) / Low-PHY Processing

**Components:**
- **SoC/FPGA/ASIC**: Main digital processing engine
  - Commercial options: Xilinx RFSoC, Intel Agilex, custom ASICs
  - Functions: FFT/IFFT engines, beamforming matrix operations, PRACH detection
- **DAC (Digital-to-Analog Converter)**: Converts digital IQ to analog
  - Typical: 12-16 bit resolution, GSPS sample rates
- **ADC (Analog-to-Digital Converter)**: Converts received analog to digital
  - Typical: 12-14 bit resolution, matching sample rate to bandwidth

**Processing blocks implemented:**
- **FFT/IFFT engines**: Transform between time and frequency domain
  - Size: 512-4096 point FFTs depending on bandwidth
  - Operation: Continuous at subframe rate (1ms periods)
- **PRACH detection**: Physical Random Access Channel processing
  - Computationally intensive correlation operations
  - Must run in parallel with normal data processing
- **Digital Predistortion (DPD)**: Linearizes PA non-linearity
  - Adaptive algorithm running continuously
  - Reduces spectral regrowth and improves efficiency
- **Crest Factor Reduction (CFR)**: Reduces peak-to-average power ratio
  - Allows PA to operate more efficiently
  - Trade-off: slight signal quality degradation for power savings
- **Digital Beamforming**: Antenna weight application
  - Matrix operations per PRB per antenna
  - Scales with MIMO configuration (4T4R, 8T8R, 64T64R, etc.)

**Power characteristics:**
- Relatively constant baseline (processing is continuous)
- Modest scaling with bandwidth (40MHz vs 100MHz config)
- Scales with antenna count (more beamforming calculations)
- FPGA power: 10-50W typical depending on utilization

![image](https://hackmd.io/_uploads/HkuU0mRBbl.png)

#### 3. Fronthaul Interface & Transport

**Components:**
- **Ethernet PHY/MAC**: 10G/25G/100G Ethernet interfaces
- **SFP+/QSFP cages**: Optical or copper connectivity
- **eCPRI/RoE processing**: Fronthaul protocol handling
- **Timing circuitry**: PTP/IEEE 1588 clock distribution

**Functions:**
- **C-Plane (Control Plane)**: Beamforming weights, scheduling info
  - Low bandwidth (~100s Mbps typical)
  - Strict timing requirements (microsecond precision)
- **U-Plane (User Plane)**: IQ sample data transport
  - High bandwidth (10-25 Gbps typical for 100MHz carrier)
  - Formula: BW ≈ (IQ_size × layers × subcarriers × symbols) / time
  - Example: 16-bit IQ, 4 layers, 3276 subcarriers, 14 symbols/ms → ~23 Gbps
- **S-Plane (Synchronization)**: PTP messages for time/phase sync
  - Critical for TDD timing and beamforming coherence
  - Sub-microsecond accuracy required

**Power characteristics:**
- Optical transceivers: 2-5W per 25G interface
- Processing overhead: 5-15W depending on line rate
- Minimal variation with traffic (mostly static)

![image](https://hackmd.io/_uploads/By9Tb40B-g.png)


#### 4. Synchronization & Timing

**Components:**
- **PTP slave clock**: IEEE 1588v2 implementation
- **PLL (Phase-Locked Loop)**: Clock generation and distribution
- **GPS/GNSS receiver**: Optional external time reference
- **1PPS input**: Pulse-per-second for time alignment

**Requirements:**
- **Frequency accuracy**: ±0.05 ppm (parts per million)
- **Phase accuracy**: ±65 ns for TDD, ±260 ns for FDD
- **Time of Day**: ±1.5 μs accuracy

**Why this matters:**
- Beamforming requires phase-coherent transmission across antennas
- TDD requires precise TX/RX switching timing
- PRACH detection needs accurate time reference
- Multi-site coordination (CoMP, carrier aggregation) needs network-wide sync

**Power characteristics:**
- Clock distribution: 1-3W typical
- GPS receiver: 0.5-1W if present
- Always on, no dynamic scaling

#### 5. Power Supply & Thermal Management

**Components:**
- **DC-DC converters**: Multiple voltage rails
  - Typical rails: 48V input → 12V, 5V, 3.3V, 1.8V, 1.0V outputs
  - Conversion efficiency: 85-95% depending on load
- **Cooling system**: 
  - Passive: Heat sinks, thermal pads (small RUs)
  - Active: Fans, liquid cooling (high-power RUs)
  - Fan power: 5-20W depending on configuration
- **Temperature sensors**: Thermal monitoring and protection
- **Power monitoring**: Current/voltage sensors on key rails

**Thermal design considerations:**
- PA generates most heat (50-150W heat dissipation typical)
- Thermal throttling reduces output power if overheating
- Ambient temperature affects PA efficiency significantly
- IP-rated outdoor units must dissipate heat without active cooling in many cases

**Power characteristics:**
- Converter losses: 5-15% of total input power
- Cooling overhead: 5-25W depending on thermal design
- Non-productive power (doesn't contribute to radio function)

### Complete O-RU block diagram

Putting it all together, a typical O-RU contains:

```
┌─────────────────────────────────────────────────────────────┐
│                         O-RU Unit                           │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Fronthaul │───▶│    DFE       │───▶│   RF Front   │───│──▶ Antenna
│  │  (Ethernet) │    │  (FPGA/SoC)  │    │   End (PA)   │   │
│  │   + Timing  │◀───│  FFT/DPD/BF  │◀───│   (LNA/Filters)│◀─│──▶ Antenna
│  └─────────────┘    └──────────────┘    └──────────────┘   │
│         │                   │                    │           │
│         └───────────────────┴────────────────────┘           │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │  Power Supply   │                       │
│                    │   Management    │                       │
│                    └─────────────────┘                       │
│                             ▲                                │
│                             │                                │
└─────────────────────────────┼────────────────────────────────┘
                              │
                         AC Input
                      (Measurement Point)
```

## Power consumption breakdown

### Typical power distribution (100W macro RU example)

| Component | Power (W) | Percentage | Behavior |
|-----------|-----------|------------|----------|
| Power Amplifier | 50-70 | 50-70% | Highly dynamic with traffic |
| Digital Processing | 15-25 | 15-25% | Mostly static with slight scaling |
| Fronthaul Interface | 5-8 | 5-8% | Static |
| Timing/Sync | 2-3 | 2-3% | Static |
| Power Supply Loss | 10-15 | 10-15% | Scales with total load |
| Cooling (if active) | 5-10 | 5-10% | Temperature-dependent |

**Key insight:** Even at 0% network utilization (idle), the RU consumes 40-60% of its peak power due to:
- PA bias current (ready state)
- Digital processing baseline (continuous FFT operations)
- Fronthaul keepalive
- Cooling and power supply overhead

![image](https://hackmd.io/_uploads/r1x8AR7CSbg.png)


### Power Amplifier efficiency curves

- **Backoff operation**: Running PA at 50% max power wastes energy
- **Peak-to-average ratio**: OFDM signals have high PAR, forcing backoff
- **DPD/CFR trade-off**: These features improve efficiency but add processing cost

**Practical example:**
- PA rated for 40W output (46 dBm)
- Actual operation: 20W average output (to maintain linearity)
- Power consumption: 80W electrical input
- Efficiency: 20W / 80W = 25%
- Heat dissipated: 60W

### Bandwidth and configuration scaling

Power consumption varies with operational configuration:

| Configuration | FPGA Power | PA Power | Total RU Power |
|---------------|------------|----------|----------------|
| 1x 20MHz FDD, 2T2R | 12W | 30W | ~60W |
| 1x 100MHz FDD, 4T4R | 20W | 60W | ~120W |
| 2x 100MHz TDD, 8T8R | 35W | 100W | ~210W |
| 4x 100MHz TDD, 64T64R | 80W | 250W | ~500W+ |

**Scaling factors:**
- Bandwidth: Linear scaling in digital processing
- Antenna count: Near-linear in beamforming computation
- Carrier count: Additive (multi-carrier RUs)
- MIMO layers: Multiplicative effect on both digital and RF

### Traffic load vs power consumption

Measured behavior (typical macro RU):

| Network Load | Power Consumption | Notes |
|--------------|-------------------|-------|
| Idle (0% PRB) | 55W (55% of peak) | PA bias, processing baseline |
| 25% PRB utilization | 70W (70%) | Moderate PA activation |
| 50% PRB utilization | 85W (85%) | PA approaching efficient region |
| 100% PRB utilization | 100W (100%) | Full capacity |

**Key observation:** Power consumption is NOT proportional to throughput. The relationship is logarithmic due to:
- Static overhead dominance
- PA efficiency curves
- Processing already running at baseline

![image](https://hackmd.io/_uploads/ryAfyVCSbx.png)


## The 7.2x split boundary in detail

### Functional split definition

The 7.2x split (O-RAN Fronthaul specification) places the boundary between High-PHY and Low-PHY:

| Layer | Function | Implementation | Power Domain |
|-------|----------|----------------|--------------|
| **Upper Layers** | RRC, PDCP, RLC, MAC | O-CU / O-DU software | Platform power (CPU/RAM) |
| **High PHY** | FEC encode/decode, Rate matching, Scrambling, Modulation, Layer mapping | O-DU software/hardware | Platform power or accelerator |
| **⚡ SPLIT POINT** | **IQ samples on Fronthaul** | **eCPRI/UDP/IP over Ethernet** | **Interface transport** |
| **Low PHY** | Precoding, Resource mapping, IFFT/FFT, CP add/remove, PRACH detection | O-RU FPGA/ASIC | RU digital power |
| **RF** | DPD, CFR, DUC/DDC, DAC/ADC, Filtering, PA/LNA | O-RU analog/mixed-signal | RU RF power |

### Why this split matters for measurement

**When measuring platform power (Scaphandre/RAPL on O-DU host):**
- Captures: FEC, scrambling, modulation, scheduler CPU
- Misses: FFT operations, beamforming matrix math, PA consumption
- Result: Massive underestimate of total RAN power

**When measuring RU AC input power:**
- Captures: Everything from Fronthaul input to RF output
- Includes: Digital processing, PA, power supply losses, cooling
- Result: True radio unit energy consumption

**Implication for our project:**
- "Platform power under RU-like workload" ≠ "RU power"
- Platform measurements are useful for DU/CU optimization only
- Physical RU measurement requires hardware instrumentation (PDU/analyzer)

### Data flow across the split

**Downlink (DU → RU):**
1. O-DU generates frequency-domain IQ samples per PRB
2. Samples compressed (optional, BFP/block floating point)
3. Transported via eCPRI over Ethernet (U-plane)
4. O-RU receives, decompresses, applies beamforming weights
5. IFFT converts to time domain
6. CP added, DPD/CFR applied, DAC conversion
7. Upconversion, filtering, PA amplification
8. RF transmission

**Uplink (RU → DU):**
1. RF reception, LNA amplification, filtering, downconversion
2. ADC conversion, FFT to frequency domain
3. PRACH detection (done in RU), channel estimation
4. IQ samples compressed and transported to DU
5. O-DU performs demodulation, decoding, MAC processing

![image](https://hackmd.io/_uploads/SJtSJERr-g.png)


### Bandwidth calculation revisited

Fronthaul bandwidth for 7.2x split:

```
BW_fronthaul = (IQ_bits × antennas × subcarriers × symbols_per_subframe) / time_per_subframe

Example (100 MHz, 4T4R):
= (2 × 16 bits × 4 antennas × 3276 subcarriers × 14 symbols) / 1 ms
= ~23 Gbps uncompressed

With compression (typical 3:1):
= ~7.7 Gbps actual
```

**Compression trade-off:**
- Reduces bandwidth requirements (enables 10G/25G Ethernet)
- Adds processing overhead in RU (compression/decompression)
- Slight signal quality degradation (lossy compression)

## O-RU categories and profiles

### O-RAN Alliance RU categories

**Category A (Precoding in O-DU):**
- RU receives per-antenna IQ samples (already beamformed)
- Simpler RU, higher fronthaul bandwidth
- Used for small antenna counts (2T2R, 4T4R)

**Category B (Precoding in O-RU):**
- RU receives layer-mapped IQ samples + beamforming weights
- RU applies precoding matrix
- Lower fronthaul bandwidth, more complex RU
- Used for massive MIMO (64T64R, 256T256R)

![image](https://hackmd.io/_uploads/H1aUJEASbx.png)


### Transmit power classes

| Class | Max TX Power | Typical Use Case |
|-------|--------------|------------------|
| Wide Area | >38 dBm (6.3W) | Macro cells, rural coverage |
| Medium Range | 31-38 dBm (1.3-6.3W) | Urban microcells |
| Local Area | 24-31 dBm (250mW-1.3W) | Indoor small cells |
| Low Power | <24 dBm (<250mW) | Enterprise femtocells |

**Power consumption correlation:**
- Higher TX class → proportionally higher PA power → higher total RU power
- Wide area RU: 100-300W typical
- Low power RU: 10-30W typical

### Frequency bands

Different frequency bands have different hardware characteristics:

| Band Type | Frequency Range | PA Technology | Efficiency | Typical RU Power |
|-----------|-----------------|---------------|------------|------------------|
| Low-band | <1 GHz | LDMOS | 40-50% | 80-150W |
| Mid-band | 1-6 GHz | GaN HEMT | 30-40% | 100-250W |
| High-band (mmWave) | 24-71 GHz | GaN MMIC | 20-30% | 50-150W (smaller coverage) |

**Key insight:** Higher frequencies require more power per area covered due to:
- Higher path loss (physics)
- Lower PA efficiency
- Need for more sites (coverage holes)

## Fronthaul transport and timing

### eCPRI protocol stack

The Enhanced Common Public Radio Interface (eCPRI) transports IQ data:

```
┌────────────────────────┐
│    IQ Samples (User)   │
├────────────────────────┤
│    eCPRI Protocol      │  ← Message types, sequence numbers
├────────────────────────┤
│     UDP (optional)     │
├────────────────────────┤
│     IP (optional)      │
├────────────────────────┤
│      Ethernet          │  ← L2 transport
├────────────────────────┤
│   Physical (Fiber)     │
└────────────────────────┘
```

**eCPRI message types:**
- Type 0: IQ data (U-plane, most bandwidth)
- Type 1: Bit sequence
- Type 2: Real-time control data (C-plane)
- Type 5: Remote reset
- Type 6: Event indication

### PTP timing synchronization

IEEE 1588v2 (Precision Time Protocol) provides:
- **Frequency sync**: Clock rate alignment
- **Phase sync**: Carrier phase alignment (for beamforming)
- **Time of Day**: Absolute time reference (for frame timing)

**PTP message flow:**
1. Sync message: Master → Slave (timestamp T1)
2. Follow_Up: Contains precise T1 value
3. Delay_Req: Slave → Master (timestamp T2)
4. Delay_Resp: Master → Slave (timestamp T3)

**Calculation:**
- Offset = ((T2 - T1) - (T4 - T3)) / 2
- Delay = ((T2 - T1) + (T4 - T3)) / 2

![image](https://hackmd.io/_uploads/BkPdyV0SZe.png)

**Why microsecond precision matters:**
- TDD switching: TX/RX must be coordinated within 5μs across RUs
- Beamforming: Phase error of 10° = ~1.4μs at 2.4 GHz
- CoMP: Multi-site coordination requires network-wide time alignment

### Fronthaul latency budget

Total fronthaul latency breakdown (typical):

| Segment | Latency | Notes |
|---------|---------|-------|
| O-DU processing | 50-100 μs | Software scheduler, HARQ |
| Fronthaul transport | 50-200 μs | Fiber propagation + switching |
| O-RU processing | 100-200 μs | FFT, DPD, buffering |
| **Total** | **200-500 μs** | Must fit within 3GPP timing requirements |

**3GPP timing constraints:**
- N1 (DL data to HARQ ACK): 4-5 ms
- N2 (UL grant to UL data): 4-5 ms
- Fronthaul must not consume more than ~10% of available timing budget

## Power management and energy saving

### O-RAN M-Plane energy saving features

The Management Plane (M-Plane) defines standardized energy saving states:

#### 1. Cell Sleep States

**Deep Sleep:**
- All transmissions stopped
- PA powered down, bias removed
- Only management interfaces active
- Wake-up time: 10-100 seconds
- Power savings: 80-90%

**Light Sleep:**
- Synchronization signals still transmitted
- Reduced power on PA
- Fast wake-up capability
- Wake-up time: <1 second
- Power savings: 30-50%

**Micro Sleep (Symbol-Level DTX):**
- PA disabled between symbols if no data
- Nanosecond-level on/off switching
- No user-perceptible delay
- Power savings: 10-20% (highly traffic-dependent)

#### 2. Carrier Shutdown

For multi-carrier RUs:
- Deactivate secondary carriers during low traffic
- Keep primary carrier active for control
- Per-carrier PA chains can be powered down
- Power savings: 20-30% per carrier disabled

#### 3. MIMO Layer Reduction

**Antenna muting:**
- Reduce from 4T4R → 2T2R during low traffic
- Reduces beamforming computation and PA power
- Trade-off: Lower peak throughput capacity
- Power savings: 20-40% depending on configuration

**Adaptive MIMO:**
- Dynamic switching based on channel conditions and load
- SU-MIMO → Beamforming → Diversity
- Each mode has different power profile

#### 4. Dynamic Spectrum Sharing (DSS)

Not purely energy saving, but affects power profile:
- Share spectrum between 4G/5G dynamically
- Opportunistic carrier activation
- Avoids running full 5G carrier for few users

![image](https://hackmd.io/_uploads/By3jkECSZx.png)


### Practical energy saving strategies

**Time-of-day scheduling:**
```
06:00-22:00: Full capacity (all carriers, all antennas)
22:00-02:00: Reduced capacity (primary carrier only, 2T2R)
02:00-06:00: Deep sleep on selected cells
```

**Load-based adaptation:**
```
PRB utilization < 20%: Carrier shutdown, MIMO reduction
PRB utilization 20-70%: Normal operation
PRB utilization > 70%: Full capacity, all resources active
```

**Geographic optimization:**
- Indoor sites: Aggressive sleep during night hours
- Highway sites: Maintain coverage, reduce capacity
- Urban sites: Follow traffic patterns

### Power-performance trade-offs

| Feature | Power Savings | User Impact | Implementation Complexity |
|---------|---------------|-------------|---------------------------|
| Micro Sleep (DTX) | 10-20% | None (transparent) | Low (automatic) |
| Light Sleep | 30-50% | Slight (wake latency) | Medium (scheduling) |
| Deep Sleep | 80-90% | Significant (service interruption) | Low (off-peak only) |
| Carrier Shutdown | 20-30% | Reduced capacity | Medium (multi-carrier logic) |
| MIMO Reduction | 20-40% | Lower peak throughput | High (adaptive algorithm) |

**Key principle:** Energy savings must be balanced against QoS requirements and user experience.

## Measurement implications

### What different measurement approaches capture

**1. AC Input Power (PDU/Power Analyzer):**
```
✅ RF PA consumption
✅ Digital processing (FPGA/SoC)
✅ Fronthaul interface
✅ Timing/sync circuits
✅ Power supply losses
✅ Cooling system
✅ All overhead
━━━━━━━━━━━━━━━━━━━━━
= TOTAL RU POWER
```

**2. Platform Power (RAPL/Scaphandre on O-DU):**
```
✅ CPU for High-PHY/MAC/RLC
✅ Memory bandwidth
✅ Accelerator cards (if used)
❌ Low-PHY (FFT/beamforming in RU)
❌ PA consumption
❌ RF analog circuits
❌ Fronthaul transport
❌ RU power supply/cooling
━━━━━━━━━━━━━━━━━━━━━
= DU PLATFORM POWER ONLY
```

**3. Estimators (Scaphandre/Kepler):**
```
✅ Software-observable CPU/RAM
⚠️  Approximations based on HW counters
⚠️  Accuracy varies by platform
❌ No visibility into RU hardware
━━━━━━━━━━━━━━━━━━━━━
= PLATFORM ESTIMATE ONLY
```

### Our probation project measurement strategy

**Primary goal:** Validate platform power estimation accuracy

**Measurement points:**
1. **Reference (ground truth):** AC input to compute platform running O-DU workload
2. **Estimator (test):** Scaphandre/Kepler output on same platform
3. **Workload:** iperf throughput as proxy for DU High-PHY load

**Clear scope boundaries:**
- We are measuring O-DU platform power behavior
- We are NOT measuring actual O-RU power (no RF hardware)
- We validate if software estimators work for DU-class workloads
- We do NOT claim this represents base station total energy

**Labeling requirements in results:**
- Always specify: "Platform power under DU-like workload"
- Never say: "RU power" or "base station power"
- Separate: Measurement point (AC vs estimator) from workload (throughput level)

### Future work: True RU measurement

To measure real O-RU power consumption would require:

**Hardware:**
- Physical O-RU unit (e.g., Benetel 650, Foxconn RPQN-7800)
- High-precision power analyzer (Yokogawa WT310E or similar)
- Current clamps for per-rail monitoring
- Thermal camera for heat distribution analysis

**Software:**
- O-DU with Open Fronthaul interface implementation
- Traffic generator (OAI UE simulator or commercial equipment)
- M-Plane interface for sleep state control

**Measurement protocol:**
1. Baseline: Idle RU with synchronization only
2. Load steps: 0%, 25%, 50%, 75%, 100% PRB utilization
3. Configuration sweep: 20MHz → 100MHz, 2T2R → 4T4R
4. Sleep state validation: Trigger via M-Plane, measure power drop
5. Thermal profiling: Correlate temperature with power/efficiency

![image](https://hackmd.io/_uploads/SkXh-4RBZe.png)

## Key takeaways

### Architecture understanding
- O-RU is a specialized radio computer, not a general-purpose server
- Power Amplifier dominates consumption (60-80% of total)
- Digital processing has high static baseline, modest dynamic scaling
- 7.2x split boundary determines what measurements capture

### Power characteristics
- Static power: 40-60% of peak even at 0% utilization
- Non-linear PA efficiency: low utilization is energy-inefficient
- Configuration-dependent: bandwidth, MIMO, carrier count all affect baseline
- Thermal management adds 10-20% overhead in high-power RUs

### Measurement approach
- Platform power ≠ RU power (fundamentally different hardware)
- AC input is the only true measure of total RU energy
- Software estimators have no visibility into RF domain
- Clear labeling is critical to avoid misleading results

### Future optimization opportunities
- Energy saving features: Cell sleep, carrier shutdown, MIMO reduction
- Traffic-aware scheduling: Match capacity to demand
- Hardware efficiency: GaN PAs, advanced thermal design
- Architecture evolution: Centralization can amortize DU power across many RUs
