# srsRAN Scheduler Deep Dive: Architecture & Power Analysis (2026-02-03)

Status: Complete
Deadline: 2026-02-03

This note documents the internal architecture of the `srsRAN_Project` MAC scheduler, specifically focusing on how Resource Blocks (RBs) are allocated and how this impacts O-RU power consumption. It identifies specific code sections that enforce Frequency Domain Multiplexing (FDM) and proposes changes to enable Time Domain Multiplexing (TDM) for energy efficiency.

## Table of Contents
- [srsRAN Scheduler Deep Dive: Architecture \& Power Analysis (2026-02-03)](#srsran-scheduler-deep-dive-architecture--power-analysis-2026-02-03)
  - [Table of Contents](#table-of-contents)
  - [Objective](#objective)
  - [Scheduler Architecture Hierarchy](#scheduler-architecture-hierarchy)
    - [1. The Gateway: `scheduler_impl`](#1-the-gateway-scheduler_impl)
    - [2. The Cell Manager: `cell_scheduler`](#2-the-cell-manager-cell_scheduler)
    - [3. The UE Manager: `ue_scheduler_impl`](#3-the-ue-manager-ue_scheduler_impl)
  - [The Scheduling Loop (TTI flow)](#the-scheduling-loop-tti-flow)
  - [Deep Dive: Resource Allocation Logic](#deep-dive-resource-allocation-logic)
    - [The "Equal Share" Heuristic](#the-equal-share-heuristic)
    - [Policy Interaction: `scheduler_time_rr.cpp`](#policy-interaction-scheduler_time_rrcpp)
  - [Power Management Implications](#power-management-implications)
    - [The Problem: Constant ON Time](#the-problem-constant-on-time)
    - [The Missing Piece: "Micro-Sleep" Scheduler](#the-missing-piece-micro-sleep-scheduler)
  - [Proposed Experiment: Enabling TDM Bursting](#proposed-experiment-enabling-tdm-bursting)
    - [Modification Target](#modification-target)
    - [Expected Result](#expected-result)
  - [Key Takeaways](#key-takeaways)

## Objective

To bridge the gap between "Theory" (burst transmission saves power) and "Implementation" (how srsRAN actually behaves). The goal is to locate the exact C++ logic that determines **how** resources are split among UEs and identify where to intervene to create "empty time slots" for RU micro-sleep.

## Scheduler Architecture Hierarchy

srsRAN uses a hierarchical scheduler design to separate concerns (Cell management vs UE logic vs QoS policies).

```mermaid
graph TD
    A[scheduler_impl] -->|Slot Indication| B[cell_scheduler]
    B -->|Grants Grid| C[ue_scheduler_impl]
    C -->|Slice Selection| D[inter_slice_scheduler]
    D -->|RB Allocation| E[intra_slice_scheduler]
    E -->|Priority Calc| F[scheduler_policy (RR/QoS)]
```

### 1. The Gateway: `scheduler_impl`
*   **File:** `lib/scheduler/scheduler_impl.cpp`
*   **Role:** The entry point for the DU.
*   **Key Function:** `slot_indication`. It receives the "tick" from the PHY layer every slot (0.5ms or 1ms) and triggers the chain.

### 2. The Cell Manager: `cell_scheduler`
*   **File:** `lib/scheduler/cell_scheduler.cpp`
*   **Role:** Manages fixed cell resources.
*   **Responsibilities:**
    *   Resets the Resource Grid (Clear the slate).
    *   Schedules "Common" channels (SSB, SIB, PRACH, Paging) first. These are non-negotiable power consumers.
    *   Hands the remaining RBs to the UE scheduler.

### 3. The UE Manager: `ue_scheduler_impl`
*   **File:** `lib/scheduler/ue_scheduling/ue_scheduler_impl.cpp`
*   **Role:** Orchestrates user traffic.
*   **Logic:**
    1.  Calls `slice_sched.get_next_dl_candidate()` to see which Slice (Standard vs VIP) needs RBs.
    2.  Invokes `intra_slice_sched.dl_sched()` to fill that slice's quote.

## The Scheduling Loop (TTI flow)

Every Transmission Time Interval (TTI), the following sequence prevents the RU from sleeping:

1.  **Slot N Trigger**: `scheduler_impl` wakes up.
2.  **Overhead check**: `cell_scheduler` reserves RBs for Signal Block (SSB) or Reference Signals (CSI-RS).
3.  **Slice Arbitration**: `inter_slice_scheduler` decides "Slice A gets 50 RBs, Slice B gets 50 RBs".
4.  **Grant Calculation**: `intra_slice_scheduler` looks at UEs in Slice A.
    *   *Critical Step:* It sees 4 UEs with data.
    *   *Default Behavior:* It splits the 50 RBs into 4 chunks of 12 RBs.
    *   *Result:* All 4 UEs transmit **now** (Frequency Division).
5.  **Grid Population**: The Resource Grid is filled.
6.  **PHY Transmission**: The DU sends I/Q data to the RU. The RU Power Amplifier (PA) stays ON for the whole symbol duration.

## Deep Dive: Resource Allocation Logic

The "smoking gun" for power behavior is located in `intra_slice_scheduler.cpp`. This class decides whether to "Burst" (TDM) or "Spread" (FDM).

### The "Equal Share" Heuristic

The function `get_max_grants_and_rb_grant_size` (template function inside `intra_slice_scheduler.cpp`) contains logic meant for fairness and latency, which inadvertently hurts power efficiency.

**Code Logic (Simplified):**

```cpp
// intra_slice_scheduler.cpp

// 1. Determine how many UEs we *could* schedule
unsigned ues_to_alloc = std::min(candidates.size() / 4, 8); // Heuristic: Schedule 1/4 of active users, max 8

// 2. Count available RBs
unsigned max_nof_rbs = slice.remaining_rbs();

// 3. Divide RBs equally (FDM)
return std::max(max_nof_rbs / ues_to_alloc, MIN_RB_PER_GRANT);
```

**Consequence:**
If you have 100MHz (273 RBs) and 4 users:
*   **Current FDM:** Each user gets ~68 RBs *in the same slot*.
    *   Slot 1: 100% Bandwidth Occupied.
    *   Slot 2: 100% Bandwidth Occupied.
*   **Power Impact:** PA operates at lower power spectral density but is **ON** for 14/14 symbols in every slot. No opportunity to turn off.

### Policy Interaction: `scheduler_time_rr.cpp`

The policy classes only determine **Order**, not **Quantity**.
*   `scheduler_time_rr` sorts UEs based on `slots_since_last_alloc`.
*   It does **not** tell the allocator "Give this user ALL the RBs".
*   Therefore, changing the policy to Round Robin doesn't force TDM; it just rotates who gets the small slices of FDM.

## Power Management Implications

### The Problem: Constant ON Time

For an O-RU to enter a power-saving mode (Micro-sleep or Symbol-shutoff), there must be **time periods** with zero transmission.

*   **FDM (Current srsRAN):** Spreads data across frequency. Time utilization is high. Sleep opportunity = Low.
*   **TDM (Desired):** Clumps data into bursts.
    *   Slot 1: UE A use 273 RBs (Full Power).
    *   Slot 2: UE B uses 273 RBs (Full Power).
    *   Slot 3: Idle (Zero Power -> Sleep).
    *   Slot 4: Idle (Zero Power -> Sleep).

### The Missing Piece: "Micro-Sleep" Scheduler

srsRAN does not currently have a "Green" scheduler mode. The default logic prioritizes:
1.  **Latency:** Serve as many UEs as possible per slot.
2.  **Fairness:** Don't let one UE hog the bandwidth.

To optimize for power, we must sacrifice strict latency for burstiness.

## Proposed Experiment: Enabling TDM Bursting

We can modify `intra_slice_scheduler.cpp` to force TDM behavior.

### Modification Target

In `intra_slice_scheduler.cpp`, modify the `get_max_grants_and_rb_grant_size` function (or the call site in `schedule_dl_newtx_candidates`).

**Concept Change:**

```cpp
// OLD (FDM):
unsigned ues_to_alloc = candidates.size(); // Or heuristic
unsigned rbs_per_ue = total_rbs / ues_to_alloc;

// NEW (TDM / Power Saver):
unsigned ues_to_alloc = 1; // Force single user per slot
unsigned rbs_per_ue = total_rbs; // Give them everything
```

### Expected Result

If we effectively constrain `ues_to_alloc` to 1:
1.  **Metric:** Throughput should remain roughly similar (sum of bits / time).
2.  **Metric:** Latency will increase (UE #2 has to wait for Slot #2).
3.  **Physical:** The O-RU will see "Pulse-Pulse-Idle-Idle" instead of "Constant-Constant-Constant-Constant".
4.  **Power:** If the O-RU has symbol-level sleep enabled, power consumption should drop during the idle slots.

## Key Takeaways

1.  **FDM is Hardcoded:** The preference for Frequency Domain Multiplexing is baked into the grant size calculation heuristic in `intra_slice_scheduler.cpp`.
2.  **Policies are Weak:** Changing `scheduler_policy` (RR vs QoS) is insufficient for power saving because it doesn't control Grant Size/Bandwidth occupancy.
3.  **Code Entry Point:** The function `intra_slice_scheduler::schedule_dl_newtx_candidates` using `get_max_grants_and_rb_grant_size` control the knobs we need to turn.
4.  **Verification:** We can verify this hypothesis by modifying the code to `max_ue_grants = 1`, running the traffic generator, and observing the Scaphandre/Power Analyzer metrics for reduced baseline or increased "idle" indications.

---
**Next Step:** Isolate the srsRAN container/build, apply this patch, and run the "Gap Analysis" workload again to see if we can shift the 70W-vs-100W curve.
