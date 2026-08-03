# Sideloader API Test Report (2026-03-20, overhauled)

- Base URL: `http://127.0.0.1:8080`
- Tested endpoints: `32`
- Successful: `18` | Expected fail: `13` | Code fail: `1` | Needs review: `0`

## Successful endpoints

- GET /health -> 200
- GET /cpu/governor -> 200
- GET /cpu/idle_states -> 200
- GET /memory/oom_check -> 200
- GET /disk/usage?mount=/ -> 200
- GET /irq/affinity?pattern=ens -> 200
- GET /stress/status -> 200
- GET /ptp/comprehensive -> 200
- POST /cpu/monitor -> 200
- POST /cpu/context_switches -> 200
- POST /memory/monitor -> 200
- POST /hugepages/monitor -> 200
- POST /disk/monitor -> 200
- POST /perf/context_switches -> 200
- POST /power/monitor -> 200
- POST /network/monitor -> 200
- POST /network/link_down -> 200
- POST /stress/kill -> 200

## Expected fail endpoints (Requires O-RAN host context)

- GET /dpdk/status -> 404 :: {   "message": "no DPDK devices found",   "status": "[ERROR]" }
- GET /ptp/time_properties -> 200 :: {   "message": "pmc command failed",   "status": "[ERROR]" }
- GET /ptp/current_data -> 200 :: {   "message": "pmc command failed",   "status": "[ERROR]" }
- GET /ptp/parent_data -> 200 :: {   "message": "pmc command failed",   "status": "[ERROR]" }
- GET /ptp/port_state -> 200 :: {   "message": "pmc command failed",   "status": "[ERROR]" }
- POST /ptp/monitor -> 200 :: {   "error": "no samples collected" }
- POST /ptp/status -> 200 :: {   "error": "pmc failed" }
- POST /process/threads -> 200 :: {   "error": "no samples collected" }
- POST /process/affinity -> 404 :: {   "message": "no process matching 'nr-softmodem'",   "status": "[ERROR]" }
- POST /perf/sched_latency -> 200 :: {   "error": "failed to collect latency data" }
- POST /network/vlan_fault -> 400 :: {   "message": "interface required",   "status": "[ERROR]" }
- POST /stress/memory -> 400 :: {   "message": "unknown stress type: invalid",   "status": "[ERROR]" }
- POST /stress/cpu -> 400 :: {   "message": "unknown stress type: invalid",   "status": "[ERROR]" }

## What each endpoint needs

- GET /dpdk/status -> DPDK NICs bound to vfio-pci (otherwise it correctly returns no devices).
- POST /ptp/monitor, POST /ptp/status -> linuxptp tools (pmc), running ptp4l/phc2sys, and a valid PTP-capable interface.
- POST /process/threads, POST /process/affinity -> running nr-softmodem process (or pass a real PID), plus pidstat from sysstat.
- POST /perf/sched_latency -> perf installed, kernel permissions for perf events, and enough privileges (CAP_PERFMON/SYS_ADMIN).
- POST /network/vlan_fault -> valid interface in payload and permission to change links/VLAN (ip link privileges).
- POST /stress/memory, POST /stress/cpu -> valid type values (not invalid) and stress-ng installed.

## Code fail endpoints

- POST /power/ipmi -> 500 :: <!doctype html> <html lang=en>   <head>     <title>ImportError: cannot import name &#39;IPMIPowerCollector&#39; from &#39;collectors.power&#39; (/home/noobplatinum/Videos/TEEP/External/sideloaderService/nino-sideloader-s
