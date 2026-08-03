# Sideloader API Test Report (2026-03-21, overhauled quick suite)

- Base URL: `http://127.0.0.1:8080`
- Tested endpoints: `16`
- Successful: `13` | Expected fail: `2` | Code fail: `1` | Needs review: `0`

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
- POST /memory/monitor -> 200
- POST /disk/monitor -> 200
- POST /network/monitor -> 200
- POST /power/monitor -> 200

## Expected fail endpoints

- GET /dpdk/status -> 404 :: {   "message": "no DPDK devices found",   "status": "[ERROR]" }
- POST /process/affinity -> 404 :: {   "message": "no process matching 'nr-softmodem'",   "status": "[ERROR]" }

## Code fail endpoints

- POST /power/ipmi -> 500 :: <!doctype html> <html lang=en>   <head>     <title>ImportError: cannot import name &#39;IPMIPowerCollector&#39; from &#39;collectors.power&#39; (/home/noobplatinum/Videos/TEEP/External/sideloaderService/nino-sideloader-s
