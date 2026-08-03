# srsRAN NR MAC Scheduler Code Map (DL/UL RB Allocation)  
*Focus: PRB/VRB placement, per-slot loop, slice/policy interaction, and places to bias burst vs. spread scheduling.*

## Top-Level Slot Entry
- **[lib/scheduler/scheduler_impl.cpp](files/lib/scheduler/scheduler_impl.cpp)**  
  - `scheduler_impl::slot_indication`: DU entrypoint each TTI. Forwards to per-cell scheduler and returns `sched_result`.

- **[lib/scheduler/cell_scheduler.cpp](files/lib/scheduler/cell_scheduler.cpp)**  
  - `cell_scheduler::run_slot`: Per-cell slot loop. Clears grids, schedules SSB/CSI/SI/PRACH/RA/Paging, then hands the slot to the UE scheduler. Publishes metrics/logs.

- **[lib/scheduler/ue_scheduling/ue_scheduler_impl.cpp](files/lib/scheduler/ue_scheduling/ue_scheduler_impl.cpp)**  
  - `ue_scheduler_impl::run_slot_impl`: Per cell-group slot pipeline. Processes UE events, HARQ timeouts, UCI/SRS periodic, fallback SRB0, slice priorities, intra-slice DL then UL, post-process, PUCCH counters.
  - `run_sched_strategy`: Schedules DL slice candidates first, then UL, invoking intra-slice schedulers.

## Inter-Slice Selection (which slice can consume RBs)
- **[lib/scheduler/slicing/inter_slice_scheduler.cpp](files/lib/scheduler/slicing/inter_slice_scheduler.cpp)**  
  - Builds DL/UL slice candidates per slot based on min/max RBs, TDD/FDD availability, PUSCH TD resources, and dedicated/shared RB budgets. 
  - Priority queues per direction; `get_next_dl_candidate` / `get_next_ul_candidate` pop highest-prio slice candidate for intra-slice scheduling.

- **[lib/scheduler/slicing/inter_slice_scheduler.h](files/lib/scheduler/slicing/inter_slice_scheduler.h)**  
  - Declares slice context, priority computation hooks, and candidate queues.

## UE Priority Policies (ordering of UEs inside a slice)
- **[lib/scheduler/policy/scheduler_policy.h](files/lib/scheduler/policy/scheduler_policy.h)**  
  - Abstract interface for computing DL/UL priorities, saving allocations.

- **[lib/scheduler/policy/scheduler_time_rr.cpp](files/lib/scheduler/policy/scheduler_time_rr.cpp)** / **.h**  
  - Time RR: priority = slots since last alloc (DL/UL separately). Encourages temporal fairness.

- **[lib/scheduler/policy/scheduler_time_qos.cpp](files/lib/scheduler/policy/scheduler_time_qos.cpp)** / **.h**  
  - QoS/PF policy: combines PF metric, GBR shortfall, HOL delay, QoS/ARP priority. Tracks per-UE exponential avg DL/UL rates and updates on grants.

## Intra-Slice Scheduler (core DL/UL grant selection)
- **[lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp](files/lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp)** / **.h**  
  - Slot prep: `slot_indication` sets PDCCH slot context; resets attempt counters. 
  - DL path `dl_sched`: compute allowed PDSCHs (`max_pdschs_to_alloc`), schedule HARQ retx then newTx. 
  - UL path `ul_sched`: symmetric for PUSCH. 
  - NewTx DL two-stage flow (`schedule_dl_newtx_candidates`): 
    1) Stage 1 reserves PDCCH/PUCCH for top-priority UEs, accumulating target `rbs_to_alloc`. 
    2) Stage 2 assigns VRBs/CRBs via grant builders, updates `used_dl_vrbs`, and stores grants. 
  - HARQ retx flows: allocate PDCCH+data with existing sizes; stop on skip-slot signals. 
  - Slot limits encouraging time spreading: `expected_pdschs_per_slot`, `max_pdschs_to_alloc`, `max_pdcch_alloc_attempts_per_slot` caps. 
  - VRB occupancy tracking per slot (`used_dl_vrbs`, `used_ul_vrbs`) and recomputation when slot changes.

## Grant Building and RB Placement
- **[lib/scheduler/ue_scheduling/ue_cell_grid_allocator.h](files/lib/scheduler/ue_scheduling/ue_cell_grid_allocator.h)** / **.cpp**  
  - Provides builders for DL/UL grants. Handles PDCCH reservation, UCI (PUCCH/PUSCH), HARQ state, and final DCI/PDSCH/PUSCH population. 
  - DL newTx: `allocate_dl_grant` → returns builder; final params set via `set_pdsch_params`. 
  - UL newTx: `allocate_ul_grant` → builder; final params set via `set_pusch_params`. 
  - Post-process cleans cancelled grants and updates PUCCH power control.

- **[lib/scheduler/ue_scheduling/grant_params_selector.h](files/lib/scheduler/ue_scheduling/grant_params_selector.h)** / **.cpp**  
  - Computes sched contexts (search space, TD resource, MCS, expected RBs) for DL/UL newTx and retx. 
  - VRB selection functions: `compute_newtx_dl_vrbs`, `compute_retx_dl_vrbs`, `compute_newtx_ul_vrbs`, `compute_retx_ul_vrbs` — all call the shared first-fit hole finder.

- **[lib/scheduler/support/rb_helper.h](files/lib/scheduler/support/rb_helper.h)**  
  - Core contiguous-hole search: `find_empty_interval_of_length` (first-fit, low-RB to high-RB, returns longest if not enough). This is the main frequency-packing heuristic for DL/UL grants and also used in fallback/RA/paging paths.

## Resource Grids and Bitmaps (collision/usage tracking)
- **[lib/scheduler/cell/resource_grid.h](files/lib/scheduler/cell/resource_grid.h)** / **.cpp**  
  - `carrier_subslot_resource_grid`: symbol×CRB occupancy; `fill/collides/used_crbs/used_prbs`. 
  - `cell_slot_resource_grid`: per-slot DL/UL grids per numerology. 
  - `cell_resource_allocator`: ring buffer of per-slot allocators (`slots[slot_delay]`), with history access; used by schedulers to query present/future slots (k0/k2 offsets). 
  - `cell_slot_resource_allocator`: holds DL/UL result containers and resource grids; `slot_indication` resets per-slot state.

- **[lib/scheduler/cell/scheduler_prb.h](files/lib/scheduler/cell/scheduler_prb.h)** / **.cpp** and **[lib/scheduler/cell/vrb_alloc.cpp](files/lib/scheduler/cell/vrb_alloc.cpp)**  
  - PRB/RBG bitmap helpers for type0/type1 VRB allocs; conversions between RBGs and PRBs. Used when building DCI/PDSCH/PUSCH.

## Fallback / SRB paths that also allocate RBs
- **[lib/scheduler/ue_scheduling/ue_fallback_scheduler.cpp](files/lib/scheduler/ue_scheduling/ue_fallback_scheduler.cpp)**  
  - SRB0/1 and contention-res sources use the same `rb_helper::find_empty_interval_of_length` to grab contiguous RB holes for control/data when UE is not fully configured.

## UL Symmetry
- UL grant selection mirrors DL in the same files: intra-slice UL stages, grant builders, VRB finders, and resource grid marking all live in the components above.

## How to bias “burst vs. spread”
- **Time dimension knobs**: `expected_pdschs_per_slot`, `max_pdschs_to_alloc`, `max_pdcch_alloc_attempts_per_slot` in intra-slice scheduler; slice candidate RB limits in inter-slice scheduler. Relax to pack more UEs per slot.
- **Frequency dimension knobs**: change `find_empty_interval_of_length` (best-fit vs first-fit) or modify `compute_newtx_dl_vrbs`/`compute_newtx_ul_vrbs` to pick largest holes or extend existing allocations. 
- **Policy knobs**: adjust scheduler policy (RR/QoS) to prefer reusing the same UE within a slot or to deprioritize spreading across TTIs.

## File Index (quick links)
- Slot entry: [lib/scheduler/scheduler_impl.cpp](files/lib/scheduler/scheduler_impl.cpp) 
- Cell slot loop: [lib/scheduler/cell_scheduler.cpp](files/lib/scheduler/cell_scheduler.cpp) 
- UE slot loop: [lib/scheduler/ue_scheduling/ue_scheduler_impl.cpp](files/lib/scheduler/ue_scheduling/ue_scheduler_impl.cpp) 
- Inter-slice: [lib/scheduler/slicing/inter_slice_scheduler.cpp](files/lib/scheduler/slicing/inter_slice_scheduler.cpp) | [.h](files/lib/scheduler/slicing/inter_slice_scheduler.h) 
- Policies: [lib/scheduler/policy/scheduler_time_rr.cpp](files/lib/scheduler/policy/scheduler_time_rr.cpp), [lib/scheduler/policy/scheduler_time_qos.cpp](files/lib/scheduler/policy/scheduler_time_qos.cpp), [lib/scheduler/policy/scheduler_policy.h](files/lib/scheduler/policy/scheduler_policy.h) 
- Intra-slice core: [lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp](files/lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp) | [.h](files/lib/scheduler/ue_scheduling/intra_slice_scheduler.h) 
- Grant builders: [lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp](files/lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp) | [.h](files/lib/scheduler/ue_scheduling/ue_cell_grid_allocator.h) 
- Grant param selector: [lib/scheduler/ue_scheduling/grant_params_selector.cpp](files/lib/scheduler/ue_scheduling/grant_params_selector.cpp) | [.h](files/lib/scheduler/ue_scheduling/grant_params_selector.h) 
- RB helper (hole finder): [lib/scheduler/support/rb_helper.h](files/lib/scheduler/support/rb_helper.h) 
- Resource grids/ring: [lib/scheduler/cell/resource_grid.cpp](files/lib/scheduler/cell/resource_grid.cpp) | [.h](files/lib/scheduler/cell/resource_grid.h) 
- PRB/RBG helpers: [lib/scheduler/cell/scheduler_prb.cpp](files/lib/scheduler/cell/scheduler_prb.cpp) | [.h](files/lib/scheduler/cell/scheduler_prb.h) | [lib/scheduler/cell/vrb_alloc.cpp](files/lib/scheduler/cell/vrb_alloc.cpp) 
- Fallback SRB scheduler: [lib/scheduler/ue_scheduling/ue_fallback_scheduler.cpp](files/lib/scheduler/ue_scheduling/ue_fallback_scheduler.cpp)
