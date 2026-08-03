# 2026-07-28 PNF Runtime Bundle Rollback and PRACH Investigation

## Question

Why did the PNF begin to crash or stop at `PRACH segmentation is not
supported` even though the VNF image and normal RU settings appeared valid?

## Short Answer

The PNF does not run only the container image. Its Helm chart mounts
`/home/oai72_su` from Lavoisier and starts a host-built `nr-softmodem` with
host DPDK and FHI/xRAN libraries. The active host OAI/FHI runtime had drifted
from the known-good July 24 bundle.

Rebuilding only part of that active runtime fixed one ABI crash, but then
exposed a deterministic PRACH packetisation assertion. Pointing PNF at the
preserved July 24 **matched OAI and FHI bundle** removed both the crash and
the PRACH assertion during xRAN startup. The VNF image was not changed by this
test.

## What Runs Where

| Component | Source of executable/runtime | Relevance |
| --- | --- | --- |
| VNF | Container image from Quay | Contains the scheduler change under test. |
| PNF `nr-softmodem` | Host path mounted into the PNF pod | Must match the FHI/xRAN libraries used at runtime. |
| DPDK plugins | Host DPDK build | Remained unchanged in this rollback. |
| RU | Pegatron fronthaul device | Was reachable and its 100 MHz M-plane readback matched the expected profile. |

The PNF entrypoint derives its executable and library paths from the Helm
values below:

```yaml
config:
  oaiBuildRoot: /home/oai72_su/oai_mp_f_ming
  dpdkLibDir: /home/oai72_su/dpdk-stable-22.11.11/build/lib
  dpdkDriverDir: /home/oai72_su/dpdk-stable-22.11.11/build/drivers
  fhiLibDir: /home/oai72_su/oai_mp_f_ming/phy_k/fhi_lib/lib/build
```

Therefore changing a Quay tag alone does not guarantee a different PNF radio
runtime. The PNF can load a different host build while its Kubernetes image
name remains unchanged.

## Failure Sequence

### 1. Partial runtime mismatch

The active `nr-softmodem` was newer than the worker-mounted
`liboran_fhlib_5g.so`. It crashed in FHI transport initialisation with a
segmentation fault. The API had changed between the two builds, including the
`transport_init` interface.

Rebuilding active `oran_fhlib_5g` and `nr-softmodem` made the pair internally
consistent, but did not restore compatibility with the live RU path.

### 2. PRACH packetisation assertion

The rebuilt active runtime then reached xRAN startup and failed at:

```text
Assertion (pRbMap->sFrontHaulRxPacketCtrl[sym_id].nRxPkt <= 1) failed!
PRACH segmentation is not supported
```

This is an FHI limitation: more than one fronthaul packet was observed for a
PRACH antenna/symbol where the active code accepts only one. It is below the
VNF scheduler, rApp, and iPerf layers.

The RU NETCONF readback did not show an obvious 40 MHz or IQ-compression
profile drift: it reported 100 MHz, 3.75 GHz centre frequency, 9-bit static
block-floating-point compression, and PRACH eAxC IDs 4-7. That did not rule
out a host-runtime/RU packetisation incompatibility.

## Controlled Rollback

The preserved runtime is located at:

```text
/home/oai72_su/oai_mp_f_ming/experiments/k-pristine-20260724
```

The PNF-only Helm rollback kept the current values and replaced only the two
matched runtime roots:

```bash
K=/home/hpe/CRAN/kubectl
C=/home/hpe/CRAN/ming-kubeconfig.yaml
N=ming-ns
PRISTINE=/home/oai72_su/oai_mp_f_ming/experiments/k-pristine-20260724
FHI="$PRISTINE/xran-package-shim/fhi_lib/lib/build"

$K --kubeconfig="$C" scale deploy oai-pnf-pegatron -n "$N" --replicas=0

helm upgrade pnf /home/hpe/CRAN/ocloud-helm-templates/oai-pnf \
  -n "$N" --kubeconfig="$C" --reuse-values \
  --set-string config.oaiBuildRoot="$PRISTINE" \
  --set-string config.fhiLibDir="$FHI"
```

The deployment was upgraded to Helm revision `3`. PNF then completed P5/P7
setup and reached:

```text
PNF P7 bind succeeded
XRAN Start! RU0 [1]
```

It remained `1/1 Running` without the previous SIGSEGV or PRACH-segmentation
assertion. VNF was restarted once afterwards to clear the stale nFAPI session;
the PNF and VNF both returned to `1/1 Running`.

## Interpretation

This is a strong PNF-runtime result, not yet an E2E result:

- The matched July 24 bundle is a viable PNF baseline for the current RU path.
- The active July 28 host runtime should not be used for scheduler testing
  until its FHI/xRAN changes are reconciled with the known-good bundle.
- The custom scheduler image is a **VNF** concern. It should be tested only
  after the rollback PNF has stayed stable and the UE has a confirmed
  `10.45.x.x` address.
- No E2E test was submitted after this rollback because the shared server was
  handed to another user.

## Next Test Window

1. Confirm no one else is using Lavoisier, the RU, or `ming-ns`.
2. Verify `lavoisier` is `Ready` and both PNF/VNF pods are `1/1 Running`.
3. Confirm the Samsung UE has its mobile data address before invoking the
   preserve-UE E2E endpoint.
4. Deploy the uniquely tagged modified **VNF** image while leaving the PNF
   rollback overrides in place.
5. Run a five-minute test first, then the matched 20-minute run if it produces
   valid UE iPerf samples.

