# NVIDIA cuMAC & cuMAC-CP: GPU-Accelerated MAC Scheduling for 5G/6G (2026-05-01)

Status: Complete
Deadline: 2026-05-01

This note analyses NVIDIA's **Aerial cuMAC** library and **cuMAC-CP** (Control Plane) integration guide — two components of NVIDIA's CUDA-accelerated RAN stack. It examines how GPU-offloaded scheduling differs from the CPU-based schedulers in OAI and srsRAN that we have studied extensively, and maps the implications to our power scheduling research.

## Table of Contents
- [NVIDIA cuMAC \& cuMAC-CP: GPU-Accelerated MAC Scheduling for 5G/6G (2026-05-01)](#nvidia-cumac--cumac-cp-gpu-accelerated-mac-scheduling-for-5g6g-2026-05-01)
  - [Table of Contents](#table-of-contents)
  - [Objective](#objective)
  - [Source Material](#source-material)
  - [1. What is cuMAC-CP?](#1-what-is-cumac-cp)
  - [2. cuMAC-CP Architecture — Thread Model \& Data Flow](#2-cumac-cp-architecture--thread-model--data-flow)
    - [2.1 Receiver Thread (Task Creator)](#21-receiver-thread-task-creator)
    - [2.2 MPMC Lock-Free Task Queue](#22-mpmc-lock-free-task-queue)
    - [2.3 Worker Threads (GPU Dispatchers)](#23-worker-threads-gpu-dispatchers)
    - [2.4 Semaphore-Based Notification](#24-semaphore-based-notification)
    - [2.5 Program Flow](#25-program-flow)
  - [3. Multi-Cell Scheduling — 1:N Architecture](#3-multi-cell-scheduling--1n-architecture)
  - [4. CUDA Scheduling Algorithms](#4-cuda-scheduling-algorithms)
    - [4.1 PF UE Down-Selection](#41-pf-ue-down-selection)
    - [4.2 PF PRB Allocation (Type 0 \& Type 1)](#42-pf-prb-allocation-type-0--type-1)
    - [4.3 Layer Selection](#43-layer-selection)
    - [4.4 MCS Selection with OLLA](#44-mcs-selection-with-olla)
    - [4.5 64T64R MU-MIMO Scheduling](#45-64t64r-mu-mimo-scheduling)
  - [5. Comparison: cuMAC vs OAI/srsRAN CPU Schedulers](#5-comparison-cumac-vs-oaisrsran-cpu-schedulers)
  - [6. Connection to Our Power Scheduling Research](#6-connection-to-our-power-scheduling-research)
    - [6.1 What cuMAC Validates from Our Study](#61-what-cumac-validates-from-our-study)
    - [6.2 New Capabilities Relevant to Power Saving](#62-new-capabilities-relevant-to-power-saving)
    - [6.3 Where cuMAC Fits in Our Architecture](#63-where-cumac-fits-in-our-architecture)
    - [6.4 Implications for Cell DTX/DRX and TDM Bursting](#64-implications-for-cell-dtxdrx-and-tdm-bursting)
  - [7. Key Differences: GPU vs CPU Scheduling Architectures](#7-key-differences-gpu-vs-cpu-scheduling-architectures)
  - [Key Takeaways](#key-takeaways)
  - [References](#references)

---

## Objective

After reading this note, the reader should be able to:
1. **Describe** the cuMAC-CP architecture and how it interfaces between L2/MAC and the GPU-accelerated cuMAC library.
2. **List** the CUDA-accelerated scheduling algorithms and compare them to the CPU implementations in OAI and srsRAN.
3. **Explain** how multi-cell scheduling enables joint optimization across cells, and why this is relevant to power efficiency.
4. **Map** the cuMAC capabilities to our existing scheduler studies and identify what changes for our FDM/TDM power analysis.

---

## Source Material

| Page | Content | Image Files |
|------|---------|-------------|
| **Page 1** — cuMAC-CP Integration Guide | Architecture diagram, thread model, MPMC task queue, receiver/worker thread program flow | ![image](https://hackmd.io/_uploads/B19ylm7RWe.png) </br> ![image](https://hackmd.io/_uploads/r1rGxmX0-x.png) </br> ![image](https://hackmd.io/_uploads/BknQGmXRbe.png)|
| **Page 2** — Implementation Details | Multi-cell vs single-cell scheduling, CUDA algorithm descriptions (PF UE selection, PRB allocation, layer selection, MCS selection, 64T64R MU-MIMO) | ![image](https://hackmd.io/_uploads/rkQuM7Q0-x.png)
 |

**Source URL:** NVIDIA Aerial cuMAC documentation ([Implementation](https://docs.nvidia.com/aerial/cuda-accelerated-ran/latest/cubb/cumac/implementation.html) and [Integration](https://docs.nvidia.com/aerial/cuda-accelerated-ran/latest/cubb/cumac/cumac-cp/index.html))

---

## 1. What is cuMAC-CP?

**cuMAC-CP** (CUDA RAN MAC Scheduler Control Plane) is a process that acts as the **interface between 5G/6G L2 (MAC Scheduler Functions) and NVIDIA's Aerial cuMAC library**, with scheduler functions accelerated on GPU.

Its operational cycle per slot:
1. Accepts **L2/MAC scheduling requests per cell** from the partner L2 stack
2. Translates requests to **cuMAC tasks**
3. Calls **cuMAC library APIs** to process on GPU
4. Returns **scheduling results to L2/MAC** via response messages per cell

> **Key distinction from OAI/srsRAN:** In OAI and srsRAN, the scheduler runs entirely on CPU cores. cuMAC-CP offloads the computationally intensive scheduling algorithms (PF, PRB allocation, MCS selection) to the GPU while keeping the control plane orchestration on CPU.

---

## 2. cuMAC-CP Architecture — Thread Model & Data Flow

### 2.1 Receiver Thread (Task Creator)

- **Count:** Exactly 1 receiver thread per cuMAC-CP instance
- **CPU Binding:** Bound to a dedicated CPU core (configurable via YAML)
- **Responsibilities:**
  1. Receives scheduling request messages from L2/MAC for **all cells** via **nvIPC** (NVIDIA's inter-process communication)
  2. Assembles requests from all cells in the group into a **cell group**
  3. Allocates a `cumac_task` object and necessary data buffers for each slot
  4. Populates the `cumac_task` and pushes it into the lock-free task queue
  5. Increases the semaphore to notify worker threads

### 2.2 MPMC Lock-Free Task Queue

The central data structure is a **Multi-Producer Multi-Consumer (MPMC) lock-free ring queue**:

```
Receiver thread     Task ring-queue          Worker threads
(task creator) --> [|█|█|█|█|█|█|] --> dequeue --> Worker on CPU core 1
                    MPMC lock-free           --> Worker on CPU core 2
                                             --> Worker on CPU core 3
```

- **Lock-free:** No mutex contention — critical for meeting the 0.5 ms slot deadline at µ=1 (30 kHz SCS)
- **Ring buffer:** Fixed-size, pre-allocated to avoid dynamic allocation jitter
- **Memory pool:** `cuMAC-Task Memory Pool Manager` pre-allocates GPU-side buffers; tasks allocate from and release back to this pool

### 2.3 Worker Threads (GPU Dispatchers)

- **Count:** Multiple worker threads, each bound to a dedicated CPU core
- **Role:** Dequeue tasks, call cuMAC library APIs (GPU kernel launches), and construct per-cell response messages
- **Key property:** Each worker thread independently processes a complete scheduling task for a cell group, enabling pipelined execution

### 2.4 Semaphore-Based Notification

```
Receiver thread ──notify──> Notifier (Semaphore) ──wake──> idle worker thread
```

- All worker threads wait on the **same semaphore** after initialisation
- For every notification, **only one idle thread** wakes up (semaphore semantics)
- This naturally load-balances across worker threads without explicit scheduling

### 2.5 Program Flow

**Receiver thread:**
```
init, core binding
  └─> loop:
       ├─> waiting for nvIPC event...
       ├─> dequeue and handle messages
       ├─> all cells ended? 
       │    ├─ N: continue collecting
       │    └─ Y: build and enqueue cuMAC task
       │         └─> notify worker threads
       └─> More FAPI? → loop back
```

**Worker thread (×N):**
```
init, core binding
  └─> loop:
       ├─> waiting for cuMAC task event...
       ├─> dequeue cuMAC task
       ├─> task = null?
       │    ├─ Y: loop back (spurious wake)
       │    └─ N: cuMAC task setup
       │         └─> cuMAC task run (GPU kernels)
       │              └─> cuMAC task callback (send response to L2)
       └─> loop back
```

> **Comparison to srsRAN:** srsRAN's `scheduler_impl::slot_indication()` runs the **entire** scheduling pipeline (overhead channels, inter-slice, intra-slice, grant building) within a single function call on the same CPU thread. cuMAC-CP separates the task creation from execution, enabling GPU-pipelined processing.

---

## 3. Multi-Cell Scheduling — 1:N Architecture

cuMAC supports two scheduling approaches:

| Approach | Architecture | PRB Optimization | Inter-Cell Interference |
|----------|-------------|------------------|------------------------|
| **Single-Cell** | 1:1 mapping (MAC ↔ PHY per cell) | Per-cell only | Not considered |
| **Multi-Cell** | 1:N mapping (one scheduler ↔ N PHY instances) | Joint across cell group | **Explicitly modelled** from SRS estimates |

```
Single Cell Scheduling Approach        Multi-Cell Scheduler Approach
1:1 mapping                            1:N mapping

┌─────────────────┐                    ┌──────────────────────┐
│ Cell N           │                    │  Multi-cell          │──> Cell N (PHY N)
│ MAC N ──── PHY N │                    │  MAC                 │
├─────────────────┤                    │  Multi-cell          │──> Cell 3 (PHY 3)
│ Cell 3           │                    │  Scheduler           │
│ MAC 3 ──── PHY 3 │     ────>         │                      │──> Cell 2 (PHY 2)
├─────────────────┤                    │                      │
│ Cell 2           │                    │                      │──> Cell 1 (PHY 1)
│ MAC 2 ──── PHY 2 │                    └──────────────────────┘
├─────────────────┤
│ Cell 1           │
│ MAC 1 ──── PHY 1 │
└─────────────────┘
```

**Why multi-cell matters for power:**
- Joint scheduling across cells enables **coordinated cell sleep**. If cells in a group can consolidate UEs onto fewer cells, the vacated cells can enter SM2/SM3 sleep — exactly UC1 (Carrier Switch Off) from O-RAN WG1.
- Inter-cell interference-aware PRB allocation can reduce required transmit power per cell by avoiding frequency collisions between neighbouring cells.

> **Our project context:** Our study notes on [O-RAN Energy Saving (2026-02-10)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md) and [Cell DTX/DRX (2026-02-27)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md) discuss sleep modes and cell switch-off. cuMAC's multi-cell scheduler provides the **computational engine** to make these decisions jointly and in real time.

---

## 4. CUDA Scheduling Algorithms

All algorithms are implemented as **CUDA kernels** running on GPU. They jointly process **all cells in a cell group simultaneously**.

### 4.1 PF UE Down-Selection

**Purpose:** Select which UEs to schedule in each TTI from the pool of all active UEs.

**Algorithm:**
1. Assign a priority weight to each active UE per cell
2. Sort all UEs in descending priority order
3. Select the top-N UEs (configurable input parameter)

**Priority weights:**
- **HARQ retransmissions** → highest priority (always selected first)
- **New transmissions** → PF metric = `instantaneous_rate / long_term_average_throughput`

> **Comparison to OAI:** OAI's `pf_dl()` uses `coeff_ue = tbs / dl_thr_ue` — functionally the same PF metric but computed sequentially on CPU. cuMAC does this in parallel across all cells and all UEs simultaneously on GPU.

> **Comparison to srsRAN:** srsRAN's `scheduler_time_qos.cpp` uses `compute_pf_metric()` with 4 sub-weights (PF + GBR + QoS priority + delay budget). cuMAC's PF is simpler (pure PF) but processed across multiple cells in parallel.

### 4.2 PF PRB Allocation (Type 0 & Type 1)

**Purpose:** Allocate PRBs to selected UEs based on channel quality.

**Inputs:**
- Narrow-band SRS channel estimates (MIMO channel matrices) per cell-UE link
- Cell-UE association solutions
- UE status and cell group parameters

**Output formats:**
- **Type 0:** Per-UE binary bitmap indicating allocated PRBs
- **Type 1:** Per-UE (startPRB, endPRB) — contiguous allocation

**Two versions:**
| Version | Inter-Cell Interference | Input Scope | Optimality |
|---------|------------------------|-------------|------------|
| Single-cell | Not considered | Per-cell only | Cell-local optimum |
| Multi-cell | **Derived from SRS** | All cells in group | **Globally optimized** |

> **This is a critical advancement over OAI/srsRAN:** Both OAI and srsRAN are inherently single-cell schedulers. They use a first-fit contiguous hole-finder (`rb_helper::find_empty_interval_of_length()` in srsRAN, linear scan in OAI's `pf_dl()`). cuMAC can jointly optimize PRB placement across cells, avoiding inter-cell frequency-domain collisions.

> **Power implication:** Multi-cell PRB allocation that accounts for inter-cell interference can achieve the same SINR with **lower transmit power** per cell, or achieve higher spectral efficiency at the same power — directly reducing $\Delta_p \cdot P_{max} \cdot x$ in the EARTH model.

### 4.3 Layer Selection

**Purpose:** Choose the optimal number of MIMO layers per UE.

**Algorithm:**
1. Compute singular values across all allocated subbands per UE
2. Apply a threshold to determine how many layers each subband can support
3. Take the **minimum layer count** across all subbands → this is the optimal layer selection

> **Power insight:** Fewer layers = fewer RF chains active = lower power. Adaptive layer selection can trade throughput for power savings during low-load periods.

### 4.4 MCS Selection with OLLA

**Purpose:** Choose the highest feasible MCS that meets a given BLER target.

**Key feature:** Integrates an **Outer-Loop Link Adaptation (OLLA)** algorithm that offsets SINR estimates based on previous transport block decoding results. This is a closed-loop mechanism — successful decodes push towards higher MCS, failed decodes pull back.

> **Comparison to OAI:** OAI's `nr_find_nb_rb()` is given MCS externally (from PHY feedback + CQI). srsRAN's `tbs_calculator` similarly takes MCS as input. cuMAC integrates the MCS selection *into* the scheduling decision on GPU.

> **Power relevance:** Higher MCS means **more bits per PRB**, which means fewer PRBs needed for the same data volume. Fewer active PRBs → lower PA power (reduces the load fraction $x$ in $P = P_0 + \Delta_p P_{max} x$). Accurate MCS selection via OLLA directly improves energy efficiency.

### 4.5 64T64R MU-MIMO Scheduling

**Purpose:** Schedule multiple UEs on the same time-frequency resources using spatial multiplexing with 64 antenna elements.

**Three components:**
1. **UE Sorting** — PF metric + SRS wideband SNR threshold + HARQ status
2. **MU-MIMO UE Grouping** — Channel semi-orthogonality algorithm using SRS channel estimates to find UE pairs/groups that can share PRBs
3. **MCS Selection** — Per-UE MCS with beamforming gains and OLLA

> **This is entirely absent from OAI/srsRAN.** Neither stack supports MU-MIMO scheduling. cuMAC can schedule multiple UEs on the **same PRBs** using beamforming, effectively multiplying capacity without additional bandwidth.

> **Power relevance for massive MIMO:** With 64T64R, the PA array is inherently active across all antenna elements. However, MU-MIMO enables serving more UEs per slot, which means the same data volume can be delivered in fewer slots → enabling longer sleep periods (Cell DTX opportunity).

---

## 5. Comparison: cuMAC vs OAI/srsRAN CPU Schedulers

| Aspect | cuMAC (GPU) | OAI (CPU) | srsRAN (CPU) |
|--------|-------------|-----------|--------------|
| **Execution target** | NVIDIA GPU (CUDA kernels) | CPU (single-thread in `pf_dl()`) | CPU (`intra_slice_scheduler.cpp`) |
| **Multi-cell** | ✅ Joint optimization across cell group | ❌ Single-cell only | ❌ Single-cell only |
| **PF algorithm** | GPU-parallel across all UEs + cells | Sequential loop over UEs | Two-pass: reserve PDCCH → fill VRBs |
| **PRB allocation** | Channel-aware, frequency-selective, CUDA | First-fit contiguous (`nr_find_nb_rb()`) | First-fit contiguous (`find_empty_interval_of_length()`) |
| **RA Type** | Type 0 (bitmap) + Type 1 (contiguous) | Type 1 only (enforced by `AssertFatal`) | Type 0 + Type 1 |
| **MCS selection** | Integrated with OLLA on GPU | Separate (PHY feedback) | Separate (`tbs_calculator`) |
| **Layer selection** | ✅ SVD-based per UE | ❌ Fixed layers | ❌ Fixed layers |
| **MU-MIMO** | ✅ 64T64R with grouping | ❌ | ❌ |
| **FDM/TDM control** | Implicit in multi-cell joint optimisation | `max_rbSize` cap (source mod) | `max_prb_policy_ratio` (YAML config) |
| **Thread model** | 1 receiver + N workers + GPU | Single scheduler thread | Single scheduler thread |
| **Latency target** | Sub-0.5 ms for 30 kHz SCS | Same (must complete per slot) | Same |
| **Open source** | ❌ (proprietary NVIDIA Aerial SDK) | ✅ (GitLab) | ✅ (GitHub) |

---

## 6. Connection to Our Power Scheduling Research

### 6.1 What cuMAC Validates from Our Study

| Our Finding | cuMAC Confirmation |
|------------|-------------------|
| **PF is the standard scheduling algorithm** (OAI `pf_dl()`, srsRAN `scheduler_time_qos`) | cuMAC also uses PF as the primary UE selection metric, confirming it as the industry-standard approach |
| **PRB allocation is the key scheduler output** that determines power (our EARTH model: $P = P_0 + \Delta_p P_{max} x$) | cuMAC's PRB allocation is explicitly the core CUDA algorithm, confirming PRBs as the critical scheduling decision |
| **Type 1 contiguous allocation** is sufficient for basic scheduling | cuMAC supports both Type 0 and Type 1, but the same RIV encoding applies (our TBS equivalence proof remains valid) |
| **HARQ retransmissions take priority** over new data | cuMAC explicitly assigns HARQ retransmissions the highest priority weight, matching OAI/srsRAN behavior |

### 6.2 New Capabilities Relevant to Power Saving

1. **Multi-cell joint scheduling → Coordinated sleep**
   - cuMAC can consolidate UEs across cells in real time, enabling empty cells to enter SM2/SM3 sleep
   - This is the **computational prerequisite** for O-RAN UC1 (Carrier Switch Off) at slot-level granularity
  - Our study's [Cell DTX analysis (2026-02-27)](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md) assumed per-cell scheduling; multi-cell coordination adds an inter-cell dimension

2. **SRS-based interference-aware PRB allocation → Lower transmit power**
   - By modelling inter-cell interference in the PRB assignment, cuMAC can reduce required Tx power
   - This reduces the $\Delta_p \cdot P_{max} \cdot x$ term without reducing the load fraction $x$ — a power saving invisible to load-based metrics

3. **Adaptive layer selection → RF chain power scaling**
   - Dynamically reducing MIMO layers during low-load periods can power down corresponding RF chains
   - Analogous to O-RAN UC2 (RF Channel Reconfiguration) but at sub-slot granularity

4. **MU-MIMO → Denser packing enables longer sleep windows**
   - Serving multiple UEs on the same PRBs via spatial multiplexing means the same aggregate data volume fits in fewer slot-PRB resources
   - The freed slots become available for Cell DTX sleep

### 6.3 Where cuMAC Fits in Our Architecture

```
Our Current Architecture:
┌──────────────┐     ┌───────────┐     ┌──────────┐
│  Near-RT RIC │─E2─>│  O-DU     │─FH─>│  O-RU    │
│  (xApp)      │     │  MAC Sched│     │  PA/RF   │
│              │     │  (CPU)    │     │          │
└──────────────┘     └───────────┘     └──────────┘
         │                 │                │
     A1 Policy        Scheduler          Sleep Mode
     (SM guidance)   (FDM/TDM knob)    (SM0-SM3)

With cuMAC:
┌──────────────┐     ┌───────────────────────┐     ┌──────────┐
│  Near-RT RIC │─E2─>│  O-DU                 │─FH─>│  O-RU    │
│  (xApp)      │     │  ┌─────────────────┐  │     │  PA/RF   │
│              │     │  │ cuMAC-CP (CPU)  │  │     │          │
│              │     │  │   └─> cuMAC(GPU)│  │     │          │
│              │     │  └─────────────────┘  │     │          │
└──────────────┘     └───────────────────────┘     └──────────┘
         │                 │                           │
     A1 Policy       GPU-accelerated             Sleep Mode
                     joint scheduling             (SM0-SM3)
                     + multi-cell opt.
```

### 6.4 Implications for Cell DTX/DRX and TDM Bursting

Our TDM bursting work (burst experiment Feb 4, Cell DTX analysis Feb 27, scheduler intervention study Mar 4) identified that the scheduler must **concentrate grants into fewer slots** to create sleep windows. cuMAC adds relevant dimensions:

| Our TDM Approach | cuMAC Enhancement |
|-----------------|------------------|
| Cap `max_rbSize` to 273 → burst 1 slot | cuMAC could jointly schedule **all cells' bursts** to align sleep windows across the cell group |
| Single-cell sleep (9/10 slots idle) | Multi-cell: consolidate traffic → entire cell sleep (all slots) |
| SM2 sleep during empty slots (4.5 ms window) | MU-MIMO packing can create **longer** contiguous idle windows → SM3 eligibility |
| CPU C-state during idle → 48% savings | GPU idle power + O-RU SM2 → estimated 73%+ savings |

---

## 7. Key Differences: GPU vs CPU Scheduling Architectures

| Dimension | CPU-Based (OAI/srsRAN) | GPU-Based (cuMAC) |
|-----------|----------------------|-------------------|
| **Parallelism** | Sequential per-UE loop | Thousands of GPU threads process all UEs simultaneously |
| **Scalability** | Performance degrades with UE count | GPU naturally scales — designed for massive parallelism |
| **Multi-cell** | Would require inter-process coordination | Native — single kernel processes all cells |
| **Latency** | Tight but sequential | Kernel launch overhead, but massively parallel execution |
| **Power model** | CPU + RAPL measurable | GPU power (nvidia-smi) + CPU power (RAPL) — dual measurement needed |
| **Flexibility** | Open source, easily modified | Proprietary kernels, configurable via API |
| **Memory model** | Shared memory / stack | GPU global memory + shared memory, explicit data transfer |
| **Suitability for Cell DTX** | Modify scheduler loop (our approach) | Would require task-level idle detection + GPU power gating |

---

## Key Takeaways

1. **cuMAC-CP is the GPU-accelerated counterpart to the CPU schedulers we studied in OAI and srsRAN.** The same PF algorithm and PRB allocation logic are used, but parallelised across thousands of GPU threads and extended to multi-cell joint optimisation.

2. **The multi-cell 1:N architecture is the major advancement.** Single-cell schedulers (OAI/srsRAN) cannot coordinate sleep across cells. cuMAC's joint optimisation is the computational engine needed for O-RAN UC1 (cell switch-off) at real-time granularity.

3. **PRB allocation with inter-cell interference awareness can reduce transmit power.** This is a power saving dimension absent from our current EARTH model analysis, which assumes per-cell load-proportional power.

4. **MU-MIMO scheduling enables denser temporal packing.** By serving multiple UEs on the same PRBs via spatial multiplexing, cuMAC can deliver the same aggregate data volume in fewer slot-PRB resources, creating longer Cell DTX sleep windows.

5. **Our FDM/TDM analysis and TBS equivalence proof remain valid.** cuMAC uses the same 3GPP resource allocation types (Type 0/1) and the same TBS determination procedure. The fundamental physics — PRBs determine power — is unchanged.

6. **GPU scheduling introduces new power measurement complexity.** Instead of measuring only CPU package power (RAPL), a cuMAC deployment requires **dual measurement**: GPU power (`nvidia-smi`) + CPU power (RAPL). The power model would be: $P_{total} = P_{CPU} + P_{GPU} + P_{O-RU}$.

7. **cuMAC's CPU reference code confirms algorithm correctness.** NVIDIA provides CPU C++ implementations of all CUDA algorithms for verification, suggesting that the algorithmic logic (PF, PRB allocation, MCS, layer selection) is identical — only the execution platform differs.

---

## References

1. NVIDIA, "cuMAC-CP Integration Guide," NVIDIA Aerial SDK Documentation. *[Page 1 screenshots: architecture, thread model, program flow]*
2. NVIDIA, "cuMAC Implementation Details," NVIDIA Aerial SDK Documentation. *[Page 2 screenshots: multi-cell scheduling, CUDA algorithm descriptions]*
3. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-24_OAI-srsRAN-MAC-Scheduler-PRB-Scheduling.md) (CPU scheduler comparison)
4. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-03_srsRAN-Scheduler-Source-Code-Verified.md) (srsRAN source code deep dive)
5. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_OAI-Scheduler-Source-Code-Verified.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_OAI-Scheduler-Source-Code-Verified.md) (OAI source code deep dive)
6. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_Enabling-Time-Frequency-Domain-Scheduling.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-03-04_Enabling-Time-Frequency-Domain-Scheduling.md) (FDM/TDM configuration)
7. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-10_O-RAN-Energy-Saving-Deep-Dive.md) (Sleep modes SM0–SM3)
8. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-27_Cell-DTX-DRX-Rel18-Standardized-Burst.md) (Cell DTX/DRX analysis)
9. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-23_EARTH-Power-Model-and-BS-Power-Modelling.md) (EARTH power model)
10. Our project: [https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md](https://github.com/bmw-ntust-internship/internship/blob/2026-TEEP-2-JDavid/docs/StudyNotes/2026-02-26_TBS-Calculator-Results-273-vs-27-Equivalence.md) (TBS equivalence proof)
