# Daily Note

## Date

**Date:** 2026/07/28

---

## Short-term Goal

Restore a trustworthy PNF radio baseline, distinguish host-runtime failures
from the scheduler-image experiment, and prepare a controlled custom-image
E2E run.

### Goals and milestones

1. **Make PNF startup reproducible**
   - Identify the actual executable and FHI/xRAN libraries used by PNF.
   - Restore a matched runtime bundle that starts xRAN without crashing.

2. **Protect the scheduler A/B test**
   - Keep the PNF rollback independent of the VNF scheduler image.
   - Run custom-image E2E only after radio and UE preflight passes.

## Plan

| Priority | Task | Expected result |
| --- | --- | --- |
| P1 | Diagnose PNF crash and PRACH startup assertion | Clear failure boundary below VNF scheduler/rApp |
| P1 | Roll PNF back to a matched host runtime | PNF starts xRAN with no assertion or crash |
| P2 | Reconnect VNF and prepare modified-image test | Both pods stable and UE-ready baseline |
| P1 | Pause for shared-lab handoff | No disruptive changes while another user is active |

## Review

| Task | Status | Evidence / Result |
| --- | --- | --- |
| Identify PNF runtime ownership | Complete | Confirmed PNF loads worker-mounted `nr-softmodem`, FHI/xRAN, and DPDK libraries through Helm values; the Quay image is not the complete PNF runtime. |
| Diagnose active-runtime failure | Complete | The active build first showed a softmodem/FHI ABI mismatch and SIGSEGV. Rebuilding the pair removed that crash but exposed `PRACH segmentation is not supported`. |
| Validate matched PNF rollback | Complete | Helm release `pnf` revision `3` now uses the preserved July 24 OAI/FHI bundle. PNF reached `XRAN Start! RU0 [1]` and remained running without the earlier crash/assertion. |
| Re-establish VNF session | Complete | Restarted VNF after PNF rollback to remove its stale nFAPI connection. Both workloads returned to `1/1 Running`. |
| Run modified-image 20-minute E2E | Deferred | The UE had a valid address, but another user began using the shared environment before a safe test window was available. |

### Progress Summary

The primary discovery is that PNF behavior cannot be attributed to the VNF
container tag alone. The PNF Helm chart mounts host-built OAI/FHI artifacts
from Lavoisier. The active worker build had diverged from the preserved July 24
bundle and failed either during FHI transport initialisation or at a PRACH
packetisation assertion. The matched rollback bundle starts xRAN correctly.

This preserves a valid scheduler experiment: keep PNF on the rollback runtime,
then change only the uniquely tagged VNF image. Do not claim an E2E result for
today, because no traffic test was run after the rollback and the shared lab
was handed to another user.

Detailed evidence and commands are in [PNF Runtime Bundle Rollback and PRACH
Investigation](../StudyNotes/2026-07-28_PNF_Runtime_Bundle_Rollback_and_PRACH_Investigation.md).

## Next Working Session

| Priority | Task | Success condition |
| --- | --- | --- |
| P1 | Confirm exclusive use of the shared RU/Lavoisier path | No other OAI workloads or RU changes are active |
| P1 | Preflight the rollback PNF and UE | Node Ready, PNF/VNF `1/1`, intended cell visible, UE has `10.45.x.x` |
| P1 | Deploy the modified VNF tag only | PNF keeps the July 24 runtime overrides; image digest is recorded |
| P2 | Run 5-minute then 20-minute E2E | Valid iPerf samples and artifacts for the modified image |

