# Power Estimator Setup (Recommended): Scaphandre (2026-01-14)

Status: Completed
Deadline: 2026-01-14

## Purpose
This note documents a **software-only power estimation approach** suitable for the probation phase: collecting **platform power under RU-like workload** on a compute host.

Scaphandre is recommended because it is relatively lightweight and is designed to expose energy/power consumption per host/process/container using Linux power interfaces (typically Intel RAPL).

## What Scaphandre provides (and what it does not)
### Provides
- Host-level energy/power estimates derived from CPU/package energy counters (when available)
- Process/container attribution (useful if you want to isolate workload components)
- Exporters (notably Prometheus) for time-series logging

### Does not provide
- RU wall power / RU AC input measurements
- A guarantee of correctness on hardware/OS combinations that lack energy counters

## Requirements (important)
Scaphandre typically relies on Linux powercap interfaces (commonly Intel RAPL).

You will need:
- A Linux environment (recommended on Windows: **WSL2 + Ubuntu**)
- A CPU/kernel exposing energy counters under Linux
- Sufficient privileges to read the relevant `/sys` interfaces

WSL note (important): depending on your Windows/WSL/kernel/hardware, **RAPL powercap counters may not be exposed inside WSL2**. If `/sys/class/powercap` is missing/empty, treat this as a normal outcome and use the fallback path described below.

## Outcome on 2026-01-15 (WSL2 pilot)
- `/sys/class/powercap` was not exposed inside WSL2 (no RAPL counters).
- Attempting to run Scaphandre in Docker hit a WSL2 sysctl limitation (`ip_unprivileged_port_start: read-only file system`).
- Therefore, power/energy is **unavailable** in this environment and the pilot run was executed in fallback mode (throughput + UTC markers + artifacts).

Evidence:
- Missing powercap: `assets/2026-01-15/screenshots/04_powercap_missing.png`
- Scaphandre sysctl error: `assets/2026-01-15/screenshots/05_scaphandre_sysctl_readonly.png`

## Ubuntu dual-boot (recommended when WSL2 blocks powercap)
If you have a dual-boot Ubuntu environment, use it as the primary platform for Scaphandre.

Evidence + exact commands are recorded here:
- `docs/StudyNotes/2026-01-19_Scaphandre-Ubuntu-Dualboot.md`

## Recommended setup on Windows (WSL2 + Docker)
### Step 0 — Confirm WSL2 is available
In PowerShell:
- `wsl --status`

If WSL is not installed:
- `wsl --install`

(You may need a restart.)

### Step 1 — Install an Ubuntu distribution
From PowerShell:
- `wsl --install -d Ubuntu`

Open Ubuntu once to complete user creation.

### Step 2 — Install Docker (recommended via Docker Desktop)
- Install Docker Desktop for Windows
- Enable: “Use WSL 2 based engine”
- Enable WSL integration for your Ubuntu distro

Then, inside Ubuntu:
- `docker version`

### Step 3 — Check if energy counters exist
Inside Ubuntu:
- `ls -la /sys/class/powercap/ 2>/dev/null`

Typical success signal (Intel): directories like `intel-rapl:0`.

If `/sys/class/powercap` is missing or empty, Scaphandre may not be able to report energy.

Also check kernel details (useful for debugging):
- `uname -a`

## Running Scaphandre
### Option A — Quick sanity run (stdout)
Inside Ubuntu:
- `docker run --rm --privileged --pid=host -v /proc:/proc:ro -v /sys:/sys:ro hubblo/scaphandre stdout`

Expected outcome:
- Continuous power/energy lines in stdout.

### Option B — Prometheus exporter (recommended for logging)
Inside Ubuntu:
- `docker run --rm --privileged --pid=host -p 8080:8080 -v /proc:/proc:ro -v /sys:/sys:ro hubblo/scaphandre prometheus --address 0.0.0.0 --port 8080`

Then browse (from Windows) to:
- `http://localhost:8080/metrics`

Expected outcome:
- A Prometheus metrics page with power/energy counters.

## How to use Scaphandre outputs in our analysis plan
Minimum for probation:
- Collect a time series of a power metric (W) with UTC timestamps.
- Run a step-test scenario (idle → active-idle → load) and compute steady-state means/energy.

Practical approaches:
- If you have Prometheus available: scrape `/metrics` at a fixed cadence and store it.
- If you do not: capture stdout and parse into a CSV (timestamp + power).

## Common failure modes (and what to do)
- No `/sys/class/powercap` / no RAPL-like counters:
  - Outcome: Scaphandre will not report meaningful energy.
  - Action: document that platform energy counters are unavailable in this environment (common in WSL2); fall back to collecting **proxy workload metrics** (throughput + CPU/NIC counters) and keep the pipeline ready for later validation on a Linux host that exposes counters.

- Permission issues reading `/sys`:
  - Outcome: errors or missing values.
  - Action: ensure container is run with `--privileged` and `/sys` is mounted read-only.

- Container fails to start on WSL2 with an error like:
  - `open /proc/sys/net/ipv4/ip_unprivileged_port_start: read-only file system`
  - Outcome: container init fails before Scaphandre runs.
  - Why it happens: some `/proc/sys` sysctls are read-only under WSL2, and certain container modes can trigger an attempted sysctl write.
  - Action:
    - First, confirm Docker can run a simple container: `docker run --rm hello-world`.
    - If Docker works but Scaphandre fails, treat Scaphandre as unavailable in this environment and use the fallback (throughput + CPU/NIC counters).
    - If Docker cannot run simple containers, restart Docker Desktop and run `wsl --shutdown`, then retry.

## How we will report results (software-only disclaimer)
If Scaphandre is used, all results are reported as:
- “platform power under RU-like workload (software-estimated)”

This is aligned with:
- `docs/StudyNotes/2026-01-13_Boundaries.md`

## Related notes
- Metrics primer: `docs/StudyNotes/2026-01-14_Energy-Metrics-Glossary.md`
- Analysis plan: `docs/StudyNotes/2026-01-14_Analysis-Plan.md`
