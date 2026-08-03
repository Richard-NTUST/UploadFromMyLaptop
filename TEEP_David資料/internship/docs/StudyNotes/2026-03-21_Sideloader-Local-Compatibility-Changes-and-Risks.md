# Sideloader Local Compatibility Changes (Unpushed External Repo) + Risk Review

**Date:** 2026-03-21  
**Scope:** `External/sideloaderService/nino-sideloader-service/`  
**Reason:** External repo is not pushed to internship GitHub branch, so this note tracks local patches and review findings.

---

## 1) Code changes made (in order)

### Change 1 — `utils/nsenter.py`: nsenter fallback execution
**What changed**
- Added `NSENTER_PREFIX` constant.
- In `run_cmd()`, if an `nsenter ...` command fails, retry the same command without `nsenter`.

**Why**
- In local/non-privileged runs, `nsenter` can fail and cause blanket `None` returns, which propagated as `no samples collected` across many endpoints.

**Functional impact**
- Local testing can still collect metrics when direct host namespace entry is unavailable.

---

### Change 2 — `utils/nsenter.py`: PATH hardening for subprocesses
**What changed**
- `run_cmd()` now appends `/usr/sbin:/sbin` to subprocess `PATH`.

**Why**
- Some commands (notably `ip`) were available in interactive shells but missing in subprocess PATH.

**Functional impact**
- Network interface discovery and related collectors now work in local runs.

---

### Change 3 — `collectors/disk.py`: block-device auto-detection
**What changed**
- Added `_auto_detect_device()` to choose available non-loop block device (`sd*`, `nvme*`, `vd*`, `xvd*`).
- Added `effective_device` and fallback from requested/default device when missing.
- Aggregation now reports effective device used.

**Why**
- Default `sda` does not exist on many laptops/VMs (e.g., NVMe-only hosts).

**Functional impact**
- `POST /disk/monitor` returns real output on hosts without `sda`.

---

### Change 4 — `app.py`: disk monitor API default behavior
**What changed**
- `/disk/monitor` no longer hard-defaults request device to `sda`; lets collector auto-detect when `device` is omitted.

**Why**
- Align API behavior with new auto-detect logic.

**Functional impact**
- Safer out-of-the-box disk monitor behavior in heterogeneous environments.

---

### Change 5 — `collectors/network.py`: robust interface discovery
**What changed**
- Replaced shell pipeline discovery with parsing of `ip -o link show` output.
- Uses `nsenter()` first, then local `run_cmd()` fallback.

**Why**
- Pipeline behavior under fallback and quoting/path differences produced empty interface lists in local testing.

**Functional impact**
- `POST /network/monitor` now returns interface-level stats in local mode.

---

### Change 6 — `collectors/power.py`: structured unavailable result
**What changed**
- `collect_sample()` now returns a sample with status marker (`rapl_unavailable`) when no RAPL/iDRAC data is available, instead of returning `None`.

**Why**
- Prevent `no samples collected` for power monitor in environments with no accessible RAPL counters.

**Functional impact**
- `POST /power/monitor` returns structured response (`samples`, `duration`, `rapl_domains`) even when power counters are unavailable.

---

## 2) Potential issues / trade-offs introduced

1. **nsenter fallback may mask privilege errors**
   - Some commands intended to run in host namespace may silently run in container/local namespace instead.
   - Mitigation: Keep this behavior for local-dev only, or gate by env flag (e.g., `ALLOW_NSENTER_FALLBACK=true`).

2. **PATH injection broadens command resolution**
   - Adding `/usr/sbin:/sbin` can change command resolution order relative to strict production environments.
   - Mitigation: Keep deterministic pathing in production container images.

3. **Disk auto-detection may pick non-target disk**
   - Auto-selected block device might not be the RU-target disk in multi-disk systems.
   - Mitigation: Pass explicit `device` in production test plans.

4. **Power monitor now favors availability over strictness**
   - Returning structured empty/zero-like power data can be interpreted as valid measurements by consumers if not checked.
   - Mitigation: downstream should check `rapl_domains` non-empty or explicit status fields before using as valid power signal.

5. **Network discovery now parses `ip -o` format assumptions**
   - Unusual interface naming or format changes can affect parsing.
   - Mitigation: add unit tests for interface parsing patterns.

---

## 3) Current validated state after patches

From overhauled reports:
- `runs/current_sweep/sideloader_api_test_report_2026-03-20.md` (full suite)
- `runs/current_sweep/sideloader_api_test_report_2026-03-21_after_fixes.md` (quick suite)

Highlights:
- CPU, memory, disk, network, and baseline power monitor endpoints now return structured outputs locally.
- Remaining code-level defect: `POST /power/ipmi` -> 500 due to missing `IPMIPowerCollector` symbol.
- Remaining expected-fail endpoints are mostly environment/service/payload dependent (PTP/DPDK/process/perf/validation paths).
