# Scaphandre Progress — Intel Laptop (WSL-first) (2026-01-16)

Status: Closed (Resolved via Ubuntu)
Deadline: 2026-01-16

## Goal
Get **Scaphandre** producing a usable power time series (stdout or `/metrics`) so we can run the same pilot structure as Day 4, but with actual platform power available.

Constraints we must respect:
- WSL2 often hides `/sys/class/powercap` (RAPL) completely.
- On AMD, Linux powercap/RAPL availability can be more finicky depending on kernel/driver support.

## Quick decision tree
### Step 1 — Check power counters in the environment you are actually using
Inside the target environment:
- `ls -la /sys/class/powercap/ 2>/dev/null`

Expected outcomes:
- If you see `intel-rapl:*` directories: proceed.
- If missing/empty: Scaphandre won’t have a sensor source here; switch environment.

### Step 2 — If on Linux and counters exist, load modules (per upstream docs)
- `sudo modprobe intel_rapl_common` (or `intel_rapl` on older kernels)

### Step 3 — If on Linux kernel >= 5.10 and you get permission errors
Upstream troubleshooting says the powercap files can be owned by root.
- Run upstream init script: `bash init.sh`

## Run commands (upstream-style)
### Fast sanity check: stdout
- Docker:
  - `docker run -v /sys/class/powercap:/sys/class/powercap -v /proc:/proc -ti hubblo/scaphandre stdout -t 15`
- Binary:
  - `scaphandre stdout -t 15`

### Prometheus exporter
- Docker:
  - `docker run -v /sys/class/powercap:/sys/class/powercap -v /proc:/proc -p 8080:8080 -ti hubblo/scaphandre prometheus`
- Validate:
  - `curl -s http://localhost:8080/metrics`

## If WSL2 fails again: Windows-native fallback
Upstream provides a Windows installer that includes a driver.

- Run:
  - `& 'C:\Program Files (x86)\scaphandre\scaphandre.exe' stdout`

If you see `Failed to open device : HANDLE(-1)`:
- Check driver state:
  - `driverquery /v | findstr capha`

## Logbook (fill as you test)
### Environment
- Machine: Intel laptop
- OS: Windows + WSL2
- Kernel (WSL): 5.15.167.4-microsoft-standard-WSL2

### Powercap probe
- `/sys/class/powercap` listing result: not present in WSL2 (RAPL counters not exposed)

### Scaphandre attempt
- Command used: Scaphandre via Docker (prometheus/stdout modes attempted)
- Result (success/error): blocked in WSL2; power estimation unavailable (no powercap + Docker/sysctl limitation)

### Outcome
- Today’s power status: Blocked in WSL2
- Next step if blocked: use a full Linux environment that exposes `/sys/class/powercap` (Ubuntu dual boot)

## Resolution (what actually worked)
On 2026-01-19, Scaphandre produced a usable power signal on Ubuntu dual boot, and we captured a complete pilot run artifact set (power + markers + iperf logs). See:
- `docs/StudyNotes/2026-01-19_Scaphandre-Ubuntu-Dualboot.md`
- `docs/StudyNotes/2026-01-19_Day-5_Pilot-Run-with-Power.md`
- `runs/2026-01-20/` (power-enabled run artifacts; UTC boundary)

## References (upstream)
- Getting started: https://hubblo-org.github.io/scaphandre-documentation/tutorials/getting_started.html
- Linux installation: https://hubblo-org.github.io/scaphandre-documentation/tutorials/installation-linux.html
- Windows installation: https://hubblo-org.github.io/scaphandre-documentation/tutorials/installation-windows.html
- Troubleshooting: https://hubblo-org.github.io/scaphandre-documentation/troubleshooting.html
