# Scaphandre on Ubuntu (Dual Boot) — Working Setup + Evidence (2026-01-19)

Status: Done
Deadline: 2026-01-19

## Purpose
This note is the "turning point" from WSL2 limitations to a runnable power estimator. The goal is to produce a **reproducible proof** that Scaphandre reports power/energy on your Ubuntu dual-boot environment.

Outcome: Scaphandre metrics were successfully scraped on Ubuntu, and a pilot run produced a power signal that clearly separates idle vs active-idle vs load.

## What to capture (bring back into the repo)
Minimum evidence bundle (copy/paste + screenshots if helpful):
- `uname -a`
- `ls -la /sys/class/powercap/` output (should show `intel-rapl:*` on Intel)
- `lscpu | head` output (CPU model)
- Docker version (if using Docker): `docker version`
- Scaphandre version / image digest (record the exact image tag)
- A saved `/metrics` snapshot (or stdout log) showing power/energy counters

What is already in the repo (run artifacts):
- Power samples: `runs/2026-01-20/power_uw.txt`
- Cleaned power subsets: `runs/2026-01-20/cleaned_power_uw.md`
- State markers: `runs/2026-01-20/markers.md`
- Traffic: `runs/2026-01-20/iperf_tcp_loadm_300s.json`
- Summary: `runs/2026-01-20/summary.md`

What we can already prove about the environment (from `iperf_tcp_loadm_300s.json`):
- iperf version: 3.16
- OS/kernel string: `Linux noobplatinum-IdeaPad-Pro-5-14IAH10 6.14.0-37-generic #37~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC ... x86_64`

## Step 1 — Verify energy counters exist
Run:
- `ls -la /sys/class/powercap/`

Expected success:
- one or more `intel-rapl:*` directories.

If missing:
- note it here and switch to alternative estimator (Kepler) or log CPU/NIC counters as fallback.

## Step 2 — Run Scaphandre (fast sanity)
Option A (stdout):
- `sudo docker run --rm --privileged --pid=host -v /proc:/proc:ro -v /sys:/sys:ro hubblo/scaphandre stdout | tee scaphandre_stdout.log`

What "success" looks like:
- repeated lines with power/energy values (not all zeros).

## Step 3 — Run Scaphandre Prometheus exporter (recommended)
- `sudo docker run --rm --privileged --pid=host -p 8080:8080 -v /proc:/proc:ro -v /sys:/sys:ro hubblo/scaphandre prometheus --address 0.0.0.0 --port 8080`

Then (same machine):
- `curl -s http://localhost:8080/metrics | head -n 50`

Save a full snapshot:
- `curl -s http://localhost:8080/metrics > scaphandre_metrics_snapshot.prom`

## Step 4 — Minimal logging for the pilot run
If you don’t set up Prometheus yet, you can still log by periodic curl:

- `while true; do date -u +"%Y-%m-%dT%H:%M:%SZ"; curl -s http://localhost:8080/metrics | grep -E "scaph_host_power_microwatts|scaph_host_energy_microjoules" | head -n 20; echo "---"; sleep 10; done | tee scaphandre_metrics_log.txt`

Note: this is crude but good enough to prove the method works; later you can parse into CSV.

## Results (from the Jan 19/20 pilot artifacts)
Power signal (from `runs/2026-01-20/cleaned_power_uw.md`, values in µW converted to W):
- Pure Idle mean power: 1.023 W (n=10; min 0.859 W; max 1.138 W)
- Active-idle mean power: 1.874 W (n=6; min 1.576 W; max 2.157 W)
- Load-M mean power: 35.279 W (n=6; min 19.816 W; max 39.078 W)

How power was logged:
- We scraped the first matching `scaph_host_power_microwatts` value from `http://localhost:8080/metrics` every ~10s.
- The raw capture is `runs/2026-01-20/power_uw.txt` (µW).
- The usable stage segments are extracted in `runs/2026-01-20/cleaned_power_uw.md`.

Interpretation:
- O-RAN software “static tax” (active-idle − idle): +0.851 W
- Workload dynamic power (load − active-idle): +33.405 W

Important scoping note:
- This is **platform power under RU-like workload** (software-estimated). It is not RU wall/input power.

## What we can claim now
- We can produce **platform power under RU-like workload** with timestamps on Ubuntu.

## What we still cannot claim
- RU wall/input power (needs RU + meter).

## Missing items (needed to fully close the “evidence bundle”)
These are not blockers for analysis, but they are required for a perfect record:
- Paste the outputs for `uname -a`, `lscpu | head`, and `ls -la /sys/class/powercap/` into the run folder (suggest: add `runs/2026-01-20/env.md`).
- Record the exact Scaphandre image tag/digest used and Docker version (same `env.md`).
- Save one `curl http://localhost:8080/metrics > scaphandre_metrics_snapshot.prom` snapshot into the run folder.
