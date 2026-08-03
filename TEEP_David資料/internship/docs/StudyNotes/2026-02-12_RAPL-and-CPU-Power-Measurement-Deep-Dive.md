# Intel RAPL & CPU Power Measurement Deep Dive (2026-02-12)

Status: Complete
Deadline: 2026-02-12

This note provides a foundational deep dive into Intel Running Average Power Limit (RAPL) — the hardware mechanism behind every power measurement in this project. Understanding RAPL at the register level is essential for interpreting our Scaphandre data, defending methodology claims in the final report, and planning the transition to hardware-grade RU measurement.

## Table of Contents
- [Objective](#objective)
- [1. What Is RAPL?](#1-what-is-rapl)
- [2. RAPL Domains (What It Measures)](#2-rapl-domains-what-it-measures)
  - [Domain Hierarchy Diagram](#domain-hierarchy-diagram)
  - [Package (PKG)](#package-pkg)
  - [PP0 / Cores](#pp0--cores)
  - [PP1 / Uncore (Client Only)](#pp1--uncore-client-only)
  - [DRAM](#dram)
  - [PSys / Platform (Skylake+)](#psys--platform-skylake)
- [3. How RAPL Works Internally](#3-how-rapl-works-internally)
  - [Model-Specific Registers (MSRs)](#model-specific-registers-msrs)
  - [Energy Counter Mechanics](#energy-counter-mechanics)
  - [Measurement vs Estimation](#measurement-vs-estimation)
- [4. Accuracy and Validation](#4-accuracy-and-validation)
  - [Published Validation Results](#published-validation-results)
  - [Known Accuracy Characteristics](#known-accuracy-characteristics)
- [5. Reading RAPL on Linux](#5-reading-rapl-on-linux)
  - [Method 1: powercap sysfs (What Scaphandre Uses)](#method-1-powercap-sysfs-what-scaphandre-uses)
  - [Method 2: perf_event](#method-2-perf_event)
  - [Method 3: Raw MSR Access](#method-3-raw-msr-access)
  - [Comparison of Methods](#comparison-of-methods)
- [6. Practical Concerns for Our Project](#6-practical-concerns-for-our-project)
  - [Counter Overflow](#counter-overflow)
  - [Sampling Cadence](#sampling-cadence)
  - [WSL2 Limitation (Why We Needed Ubuntu)](#wsl2-limitation-why-we-needed-ubuntu)
  - [Security (Linux 5.10+)](#security-linux-510)
- [7. What RAPL Does NOT Capture](#7-what-rapl-does-not-capture)
- [8. How Scaphandre Uses RAPL](#8-how-scaphandre-uses-rapl)
- [9. Comparison to Other Power Measurement Approaches](#9-comparison-to-other-power-measurement-approaches)
- [10. Connection to Our Project](#10-connection-to-our-project)
  - [Why Our Methodology Is Sound](#why-our-methodology-is-sound)
  - [Why the "Gap" Exists](#why-the-gap-exists)
  - [Implications for Stage 2 (Hardware RU)](#implications-for-stage-2-hardware-ru)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Objective

To build a hardware-level understanding of Intel RAPL so that:
1. We can **defend** the accuracy claims in our final report to reviewers.
2. We understand **exactly** what `scaph_host_power_microwatts` represents physically.
3. We can articulate **why** platform power ≠ RU power (the "gap") at the component level.
4. We can plan the **measurement transition** from RAPL to PDU/power analyzer for Stage 2.

---

## 1. What Is RAPL?

**RAPL (Running Average Power Limit)** is an Intel technology, introduced with Sandy Bridge (2011), that provides:

1. **Energy counters** — cumulative energy consumed (in microjoules) by different power domains of the processor.
2. **Power capping** — the ability to set power limits that the CPU firmware enforces by throttling frequency/voltage.

For our project, we use RAPL exclusively as a **measurement tool** (energy counters), not as a power-capping mechanism.

**Key insight:** RAPL is not a simple current-sense resistor. On most processors, it is a **software power model** running inside the CPU's Power Control Unit (PCU) firmware. The PCU reads internal analog sensors (voltage regulators, temperature, activity counters) and computes an energy estimate using a proprietary model trained against physical measurements at the factory.

**Exception:** Some server processors (notably Haswell-EP/Broadwell-EP) use integrated voltage regulators (FIVR — Fully Integrated Voltage Regulator), which allow **actual current measurement** rather than model-based estimation. This was discontinued on later server chips.

---

## 2. RAPL Domains (What It Measures)

RAPL exposes energy counters for several **power domains**, each covering a different part of the processor/platform. Not all domains are available on all processors.

### Domain Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────┐
│  PSys / Platform (Skylake+ client only)                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Package (PKG) = one CPU socket                   │  │
│  │  ┌──────────────┐  ┌───────────────────────────┐  │  │
│  │  │  PP0 / Cores │  │  PP1 / Uncore (iGPU etc.) │  │  │
│  │  │  (all cores  │  │  (integrated GPU, memory   │  │  │
│  │  │   in socket) │  │   controller, ring bus)    │  │  │
│  │  └──────────────┘  └───────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────┐                                  │
│  │  DRAM              │                                  │
│  │  (memory DIMMs)    │                                  │
│  └───────────────────┘                                  │
│  + Platform I/O (PCH, USB, NIC, chipset — PSys only)    │
└─────────────────────────────────────────────────────────┘
```

### Package (PKG)

- **What it covers:** The entire CPU socket — all cores, uncore (ring bus, LLC, memory controller), and integrated graphics.
- **MSR:** `MSR_PKG_ENERGY_STATUS` (0x611)
- **Availability:** All RAPL-capable processors (Sandy Bridge+)
- **This is what Scaphandre reads as `scaph_host_power_microwatts`.**

### PP0 / Cores

- **What it covers:** All CPU cores within the package (execution units, L1/L2 caches).
- **MSR:** `MSR_PP0_ENERGY_STATUS` (0x639)
- **Availability:** Most Intel processors.
- **Note:** You cannot break this down to individual cores. It is the aggregate of all cores in the socket.

### PP1 / Uncore (Client Only)

- **What it covers:** On client (desktop/laptop) chips, this typically measures the integrated GPU (iGPU) power. On server chips, PP1 is usually not available (there is no iGPU).
- **MSR:** `MSR_PP1_ENERGY_STATUS` (0x641)
- **Availability:** Client processors only (desktop/laptop/NUC).

### DRAM

- **What it covers:** Energy consumed by the DRAM DIMMs connected to the memory controller.
- **MSR:** `MSR_DRAM_ENERGY_STATUS` (0x619)
- **Availability:** Server processors (Sandy Bridge-EP+), and some client chips (Haswell+).
- **Accuracy caveat:** On desktop Haswell, DRAM RAPL has been shown to be offset from actual measurements. On Haswell-EP (with FIVR), DRAM RAPL is based on actual measurement and is much more accurate (see Weaver et al. validation below).

### PSys / Platform (Skylake+)

- **What it covers:** The entire SoC platform — CPU package + chipset (PCH) + other on-SoC components. This is the broadest domain and the closest to "total system power" that RAPL can provide (though it still excludes discrete GPUs, storage, fans, display, etc.).
- **MSR:** `MSR_PLATFORM_ENERGY_STATUS` (0x64D)
- **Availability:** Skylake mobile/desktop and newer client chips. **Not available on server chips.**
- **Relevance:** On our Intel Core Ultra 7 (Meteor Lake) test platform, PSys would be valuable because it captures more of the SoC than PKG alone.

---

## 3. How RAPL Works Internally

### Model-Specific Registers (MSRs)

RAPL data lives in **MSRs** — special CPU registers accessible via the `rdmsr` instruction (privileged). The key MSRs are:

| MSR Address | Name | Description |
|---|---|---|
| 0x606 | `MSR_RAPL_POWER_UNIT` | Unit multipliers (power, energy, time) |
| 0x610 | `MSR_PKG_POWER_LIMIT` | Power limit configuration (PL1/PL2) |
| 0x611 | `MSR_PKG_ENERGY_STATUS` | Cumulative package energy (J) |
| 0x614 | `MSR_PKG_POWER_INFO` | Thermal spec / min / max power |
| 0x619 | `MSR_DRAM_ENERGY_STATUS` | Cumulative DRAM energy (J) |
| 0x639 | `MSR_PP0_ENERGY_STATUS` | Cumulative core energy (J) |
| 0x641 | `MSR_PP1_ENERGY_STATUS` | Cumulative uncore/GPU energy (J) |
| 0x64D | `MSR_PLATFORM_ENERGY_STATUS` | Cumulative platform energy (J) |

### Energy Counter Mechanics

The energy counters work as follows:

1. **Unit resolution:** Read `MSR_RAPL_POWER_UNIT` to get the energy unit. For most Intel CPUs, the energy unit is $2^{-14}$ joules ≈ 61 µJ. Example output: `Energy units = 0.00001526 J`.

2. **Accumulation:** The counter increments by the number of energy units consumed since the last reset (or boot). The counter is 32 bits wide.

3. **Deriving power:** RAPL does **not** provide instantaneous power. To get power, you must:
   - Read the energy counter at time $t_1$ → $E_1$
   - Read the energy counter at time $t_2$ → $E_2$
   - Compute: $P_{avg} = \frac{E_2 - E_1}{t_2 - t_1}$

   This is exactly what Scaphandre does every ~10 seconds.

4. **Overflow:** The 32-bit counter with ~61 µJ resolution overflows at approximately:
$$E_{max} = 2^{32} \times 61 \times 10^{-6} \text{ J} \approx 262{,}144 \text{ J}$$

   At 100 W continuous draw: $\frac{262{,}144}{100} \approx 2{,}621 \text{ s} \approx 43.7 \text{ min}$

   At a more typical server load of 300 W, overflow happens in ~14.5 minutes. **This is why sampling more often than every ~60 seconds is important.**

### Measurement vs Estimation

| Generation | Method | Accuracy Claim |
|---|---|---|
| Sandy Bridge – Ivy Bridge | Pure software model (activity counters + voltage/temp) | ±5–10 % vs wall power |
| Haswell (client) | Software model, improved training | ±5 % |
| Haswell-EP (server, FIVR) | **Actual current measurement** via integrated VR | ±1–2 % |
| Broadwell-EP | Actual measurement (FIVR, last gen) | ±1–2 % |
| Skylake+ (server) | Software model (FIVR removed) | ±5 % |
| Meteor Lake (client, our DUT) | Software model (hybrid architecture) | Expected ±5–10 % |

**Key point:** Even on model-based processors, the model is trained against physical measurements at the fab. Intel considers the accuracy sufficient for power management decisions. For our purposes (trend detection, state separation, relative comparison), this accuracy is more than adequate.

---

## 4. Accuracy and Validation

### Published Validation Results

**Weaver et al., University of Maine (2016, MEMSYS)**

The most comprehensive independent RAPL validation study. Key findings:

1. **Package (PKG) domain:** Tracks wall-power measurements closely across workloads. Correlation coefficients > 0.95 on Haswell client and Haswell-EP.

2. **DRAM domain (Haswell desktop/DDR3):** Overall pattern correct, but readings are **offset** from actual in a way that varies between individual systems. Better accuracy under load than at idle. The offset suggests the internal model was trained on a specific DIMM type.

3. **DRAM domain (Haswell-EP/DDR4):** Much better accuracy due to integrated voltage regulator providing real current measurement. "Mode 1" RAPL gives very good results.

4. **Idle accuracy:** Worse than under load. The model struggles when power draw is very low and dominated by leakage current rather than dynamic switching.

5. **iGPU interaction:** When the integrated GPU is active, some energy may not be correctly attributed across PP0/PP1 domains. The Package total remains correct.

### Known Accuracy Characteristics

| Condition | RAPL Accuracy | Notes |
|---|---|---|
| Steady-state compute load | Good (±5 %) | Model well-trained for this case |
| Idle / very low power | Fair (±10-15 %) | Low signal-to-noise; leakage dominates |
| Bursty / transient loads | Fair | RAPL averages over its internal update interval (~1 ms) |
| Mixed CPU+GPU workloads | Package total is good; sub-domain split may be approximate | |
| Multi-socket systems | Each socket has independent counters | Read both packages |
| Hybrid architectures (P-core + E-core) | Newer RAPL models account for this, but validation data is limited | Relevant to our Meteor Lake DUT |

---

## 5. Reading RAPL on Linux

There are four historical methods to access RAPL counters on Linux. As of 2026, **powercap sysfs** and **perf_event** are the recommended approaches.

### Method 1: powercap sysfs (What Scaphandre Uses)

The Linux powercap framework (introduced in kernel 3.13) exposes RAPL as a sysfs tree:

```
/sys/class/powercap/intel-rapl/
├── intel-rapl:0/              # Package 0
│   ├── name                   # "package-0"
│   ├── energy_uj              # Cumulative energy (µJ) ← THE KEY FILE
│   ├── max_energy_range_uj    # Counter wrap-around value
│   ├── intel-rapl:0:0/        # Sub-zone: PP0 (cores)
│   │   ├── name               # "core"
│   │   └── energy_uj
│   └── intel-rapl:0:1/        # Sub-zone: PP1 (uncore/GPU)
│       ├── name               # "uncore"
│       └── energy_uj
├── intel-rapl:1/              # Package 1 (if multi-socket)
│   └── ...
└── intel-rapl-mmio:0/         # PSys (if available)
    ├── name                   # "psys"
    └── energy_uj
```

**To read power manually:**
```bash
# Read energy at time t1
E1=$(cat /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj)
sleep 10
# Read energy at time t2
E2=$(cat /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj)

# Compute average power (µW)
POWER_UW=$(( (E2 - E1) / 10 ))
echo "Average power: $POWER_UW µW"
```

This is effectively what Scaphandre does internally when it exposes `scaph_host_power_microwatts`.

### Method 2: perf_event

Linux's `perf` tool (kernel 3.14+) can read RAPL as performance counters:

```bash
sudo perf stat -a -e "power/energy-pkg/,power/energy-cores/,power/energy-ram/" sleep 10
```

Output:
```
10.001234567 seconds time elapsed

    73.456789 Joules  power/energy-pkg/      ( +- 0.01% )
    51.234567 Joules  power/energy-cores/    ( +- 0.02% )
     6.789012 Joules  power/energy-ram/      ( +- 0.05% )
```

**Advantage:** `perf` handles multi-socket aggregation and overflow detection automatically.
**Disadvantage:** Requires `CAP_SYS_ADMIN` or `perf_event_paranoid < 1`.

### Method 3: Raw MSR Access

Direct register reads via `/dev/cpu/*/msr`. Requires root:

```bash
sudo rdmsr -p 0 0x611   # Read MSR_PKG_ENERGY_STATUS on CPU 0
```

**Not recommended** for production use. The kernel developers are moving toward deprecating raw MSR access for security reasons.

### Comparison of Methods

| Method | Kernel | Permissions | Overflow Handling | Multi-socket | Recommended |
|---|---|---|---|---|---|
| powercap sysfs | 3.13+ | Restricted since 5.10 | Manual | Read each package | **Yes** (Scaphandre uses this) |
| perf_event | 3.14+ | root or paranoid < 1 | Automatic | Aggregated | **Yes** |
| Raw MSR | Any | root | Manual | Manual per-core | No (deprecated path) |
| AMD hwmon | 5.8–5.13 | Unrestricted (removed) | N/A | N/A | Removed |

---

## 6. Practical Concerns for Our Project

### Counter Overflow

The 32-bit energy counter overflows approximately every **44 minutes at 100 W** or **15 minutes at 300 W**. Since Scaphandre polls every ~10 seconds, overflow is not a concern for us — we detect deltas between consecutive reads.

**However:** If you ever switch to a custom polling script and poll infrequently (e.g., every 5 minutes), you must handle the wrap-around:

```python
if E2 < E1:
    # Overflow occurred
    delta = (max_energy_range_uj - E1) + E2
else:
    delta = E2 - E1
```

### Sampling Cadence

Our Scaphandre Prometheus exporter polls at approximately **10-second intervals**. This means:

- We compute a **10-second average power** per sample.
- Transients shorter than 10 seconds are smoothed (averaged out).
- This is appropriate for our steady-state scoring windows (5-minute phases, 10-second trim).

For sub-second power analysis (e.g., observing individual scheduling decisions), you would need `perf` or direct MSR reads at µs/ms cadence. This is not needed for our current methodology.

### WSL2 Limitation (Why We Needed Ubuntu)

WSL2 runs Linux inside a lightweight Hyper-V virtual machine. The hypervisor does **not** expose the physical `/sys/class/powercap` directory to the guest because:

1. RAPL MSRs are privileged hardware registers. Hyper-V does not virtualize them.
2. The powercap sysfs tree is populated by the `intel_rapl_common` kernel driver, which requires access to physical MSRs.
3. Even if MSR access were available, the energy counters would reflect the **entire host**, not just the VM — misleading for per-VM accounting.

This is why all our power measurements were taken on **native Ubuntu (dual boot)** rather than WSL2. This limitation was documented in `docs/StudyNotes/2026-01-16_Scaphandre-Progress_Intel-Laptop.md`.

### Security (Linux 5.10+)

Starting with Linux kernel 5.10, the powercap sysfs `energy_uj` files were restricted to root-only access. This was a response to the **Platypus** side-channel attack (CVE-2020-8694/8695), which demonstrated that unprivileged RAPL readings could be used to infer cryptographic keys via power analysis.

**Impact on our setup:** Scaphandre runs as root (or in a privileged Docker container), so this restriction does not affect us.

---

## 7. What RAPL Does NOT Capture

Understanding RAPL's blind spots is critical for interpreting the "gap" between our proxy measurements and real RU power:

| Component | Captured by RAPL? | Notes |
|---|---|---|
| CPU cores (all cores aggregate) | **Yes** (PKG, PP0) | |
| Integrated GPU | **Yes** (PP1, included in PKG) | |
| Memory controller + ring bus | **Yes** (included in PKG) | |
| DRAM DIMMs | **Partially** (DRAM domain, model-based on most chips) | |
| Chipset / PCH | **Only with PSys** (Skylake+ client) | |
| Discrete GPU (NVIDIA/AMD) | **No** | Use nvidia-smi or amdgpu for these |
| NIC (network interface card) | **No** | Significant for network-heavy workloads |
| Storage (SSD/HDD) | **No** | |
| Fans / cooling | **No** | |
| Display / backlight | **No** | |
| USB devices | **No** | |
| Power supply losses (AC→DC) | **No** | Wall power = RAPL power / PSU efficiency |
| **O-RU Power Amplifier** | **No** | The dominant RU component (60–80% of RU power) |
| O-RU RF front end | **No** | |
| O-RU FPGA/ASIC (DFE) | **No** | |

**The "gap" in one sentence:** RAPL measures the CPU + memory of a general-purpose host; an O-RU's power is dominated by the Power Amplifier and RF front end, which are entirely outside RAPL's measurement boundary.

---

## 8. How Scaphandre Uses RAPL

Scaphandre is a lightweight power monitoring agent written in Rust. In its "PowercapRAPL" sensor mode (the default on Linux), it:

1. **Reads** `/sys/class/powercap/intel-rapl/intel-rapl:*/energy_uj` at each poll interval.
2. **Computes** the delta since the last read.
3. **Divides** by the elapsed time to produce instantaneous power in microwatts.
4. **Exposes** the result as:
   - `scaph_host_power_microwatts` — total platform power (PKG domain, or PSys if available).
   - `scaph_process_power_consumption_microwatts{pid="..."}` — per-process attribution (estimated proportionally from CPU time).

**Process-level attribution caveat:** Scaphandre estimates per-process power by distributing the total package power proportionally based on each process's CPU utilization. This is an approximation — it assumes power scales linearly with CPU time, which is not strictly true (memory-bound vs compute-bound workloads have different power-per-cycle characteristics).

For our project, we only use `scaph_host_power_microwatts` (total host power), so this caveat does not apply.

---

## 9. Comparison to Other Power Measurement Approaches

| Approach | What It Measures | Accuracy | Granularity | Cost | Our Use Case |
|---|---|---|---|---|---|
| **RAPL / Scaphandre** | CPU + memory (model-based) | ±5–10 % | ~1 ms (MSR), 10 s (our polling) | Free (software) | **Current methodology** |
| **Smart PDU** (e.g., Raritan) | AC input to the entire server/rack | ±1–2 % | ~1–10 s | $500–$2000 | Stage 2 (whole-server RU measurement) |
| **BMC/IPMI** (iLO, iDRAC) | Server-level DC power (from VR sensors) | ±5 % | ~1–5 s | Built-in (server hardware) | Alternative to RAPL on servers |
| **Power Analyzer** (Yokogawa, N6705C) | AC/DC at any measurement point | ±0.1 % | µs–ms | $5,000–$50,000 | Lab-grade RU measurement |
| **turbostat** (Intel) | Same RAPL MSRs, CLI tool | Same as RAPL | Per-sample | Free | Quick command-line checks |
| **powertop** (Intel) | RAPL + device-level estimates | RAPL + heuristic | Per-interval | Free | Battery optimization focus |
| **perf stat** | RAPL energy events | Same as RAPL | Per-benchmark | Free | One-shot benchmarking |

**Decision rationale for our project:** We chose RAPL/Scaphandre because (1) it is the only option available without dedicated hardware, (2) its accuracy is sufficient for trend detection and state separation, and (3) it runs continuously without disturbing the workload.

---

## 10. Connection to Our Project

### Why Our Methodology Is Sound

1. **We use Package (PKG) energy** — the most validated and stable RAPL domain.
2. **We compute power from energy deltas** — the correct derivation, not a "reported instantaneous" value.
3. **We apply trimmed steady-state windows** — mitigating RAPL's idle-state inaccuracy by focusing on stable phases.
4. **We achieve CV < 10 % across repeated runs** — demonstrating that RAPL is sufficiently repeatable for our purposes.
5. **We label measurements as "platform power"** — never claiming they represent RU AC/DC input power.

### Why the "Gap" Exists

Our proxy platform idle: **~3.4–5.7 W** (RAPL PKG)
Macro RU idle (P12 anchor): **197 W** (AC input)
Ratio: **~34×**

The ~190 W difference comes from components RAPL cannot see:
- **Power Amplifier bias current** (~50–150 W even at idle, ready-state)
- **RF front end** (LNAs, filters, synthesizers: ~10–30 W)
- **Digital Front End FPGA/ASIC** (~20–50 W)
- **Cooling system** (~10–20 W)
- **Power supply losses** (AC→DC efficiency ~85%, meaning ~15% overhead)

None of these exist on our laptop DUT. RAPL correctly reports the compute/memory portion; the "gap" is not a measurement error but a scope difference.

### Implications for Stage 2 (Hardware RU)

When real O-RU hardware becomes available, the measurement architecture should be:

```
                    ┌──────────────────────┐
   AC Mains ──────►│  Power Analyzer /    │
                    │  Smart PDU           │──► Total RU AC Power
                    └──────────────────────┘
                              │
                    ┌─────────▼────────────┐
                    │      O-RU            │
                    │  ┌──────────────┐    │
                    │  │ PA + RF FE   │    │──► (Dominant power consumer)
                    │  └──────────────┘    │
                    │  ┌──────────────┐    │
                    │  │ DFE (FPGA)   │    │──► (Fixed overhead)
                    │  └──────────────┘    │
                    │  ┌──────────────┐    │
                    │  │ Cooling      │    │──► (Proportional to total)
                    │  └──────────────┘    │
                    └──────────────────────┘
                              │
   Fronthaul ◄───────────────┘
                              │
                    ┌─────────▼────────────┐
                    │   O-DU Host          │
                    │   (RAPL/Scaphandre)  │──► Compute-side power (keep measuring)
                    └──────────────────────┘
```

**Key principle:** Keep the same scenario structure (states, markers, trimmed windows) and add the PDU/analyzer measurement in parallel. This allows direct comparison of compute-side vs total-RU power under identical workload conditions.

---

## Key Takeaways

1. **RAPL is a software power model** on most consumer processors — it estimates energy from internal activity counters and voltage/temperature sensors, trained against physical measurements at the factory. Accuracy is ±5–10 % for package-level readings.

2. **The energy counter is cumulative.** You derive power by computing $\Delta E / \Delta t$ between two reads. This is exactly what Scaphandre does.

3. **RAPL measures CPU + memory only.** It does not capture NIC, storage, GPU (discrete), fans, or any RF hardware. This is why our "platform power" is ~3–6 W while a Macro RU draws ~200–530 W.

4. **Counter overflow** happens approximately every 15–44 minutes depending on power draw. Our 10-second polling cadence avoids this issue entirely.

5. **WSL2 cannot access RAPL** because the hypervisor does not expose the physical MSRs. Native Linux (or bare-metal) is required.

6. **For Stage 2**, RAPL should be maintained on the O-DU host while a PDU/power analyzer is added at the O-RU AC input. The same scenario/marker methodology transfers directly.

7. **Security restriction (Linux 5.10+):** `energy_uj` files require root. Scaphandre's privileged Docker container handles this.

---

## References

1. Intel® 64 and IA-32 Architectures Software Developer's Manual, Volume 3, Chapter 15: "Power and Thermal Management" (RAPL MSR definitions).
2. V. Weaver et al., "Measuring Energy and Power with PAPI," IEEE ICPP Workshops, 2012.
3. V. Weaver, "RAPL Validation," University of Maine, https://web.eece.maine.edu/~vweaver/projects/rapl/rapl_validation.html (DRAM RAPL accuracy study, MEMSYS 2016).
4. V. Weaver, "Linux Support for Power Measurement Interfaces," https://web.eece.maine.edu/~vweaver/projects/rapl/rapl_support.html (comprehensive processor support table).
5. Linux Kernel Documentation, "Power Capping Framework," https://www.kernel.org/doc/html/latest/power/powercap/powercap.html.
6. Lipp et al., "PLATYPUS: Software-based Power Side-Channel Attacks on x86," IEEE S&P 2021 (CVE-2020-8694/8695, motivating Linux 5.10 permission changes).
7. Scaphandre Documentation, https://hubblo-org.github.io/scaphandre-documentation/ (sensor architecture and powercap mode).
8. 3GPP TS 28.552 v18.5.0, "Management and orchestration; 5G performance measurements" (PEE.AvgPower definition — the standards-level analog to what RAPL provides).
