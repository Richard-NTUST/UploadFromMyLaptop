# 2026-07-22 OAI Custom Image and UE Attach Investigation

## Question

Did the scheduler logging image break the OCloud E2E path, or did the shared
radio and UE environment independently fail to attach?

## Images Under Test

| Role | Image | Registry digest | Build evidence |
|---|---|---|---|
| Baseline | `bmw.ece.ntust.edu.tw/minghong/oai-gnb:latest` | `sha256:c227006518795bdb517db0db15be7c12850c9184297e4cb514ea3987a5108edc` | Jenkins build #87 checked out `9522317237738e3c4d1f4e006dc3b27faf5904b5` from `nfapi-DelayManagement`. |
| Scheduler log image | `bmw.ece.ntust.edu.tw/minghong/oai-gnb:david-oai-scheduler-logonly-20260721` | `sha256:a60a4a5796a9167ebd68aeeecb1699c020e32abc518966e96dda6c060f1e75cd` | Jenkins build #88 checked out `31c7aa0477586643a7acdae9c316c61c1ba0cdbf` from `david/oai-scheduler-logonly-20260721`. |

Build #88 is not a retag of `latest`. Jenkins recorded the custom commit and
the worker cached a separate 2026-07-21 image. The Stage View label `No
Changes` only means Jenkins did not generate a changelog for that build; it
does not mean that #88 used the #87 source revision.

The custom image is also directly verified to contain `WINLAB_SCHED_LOG` in
`/opt/oai-gnb/bin/nr-softmodem`. Its `nr-softmodem` SHA-256 is
`52e68ea2a779e75e0b52f2751b2dee77856fbf33a41e63fa164c07870872c730`.
The baseline binary checksum is
`3646dd12273dd930166799523562a877f0b0364c571912fbf7a25289e3e0250f`.

## Controlled Observations

### Valid baseline traffic

Job `17b89110-cd4d-4608-b450-0eb58abaf8d3` used `latest` with 200 Mbps for
300 seconds. The UE received `10.45.0.3`; the local iPerf server accepted the
connection and observed 200 Mbps with zero loss. The VNF log contained UE
RACH, RRC connection, LCID 4 traffic, and PDU-session activity.

This proves the baseline image and the end-to-end data path can work.

### Custom-image deployment

The custom image deployed with the same VNF Kubernetes template, configuration
map, n2 and nFAPI networks, CPU assignment, and PNF pod as `latest`. The image
registered the gNB with AMF, but its first deployment generated a Kubernetes
`BackOff` event before the pod eventually stayed Running. Its short persistent
VNF logs end after `Received NGSetupResponse from AMF`; they contain no UE
RACH, RRC, LCID, or scheduler marker lines.

That early restart is image-specific evidence worth investigating. It is not,
however, sufficient to attribute the later missing UE address to the scheduler
log statement: no UE scheduling happened in that session.

### Fresh baseline failure

After restoring `latest`, job `29ad5a6d-44ea-4408-9137-b47e9e773116` also
failed before iPerf. Both pods were Running and Ready, but the Samsung UE did
not receive a `10.45.x.x` address within the 120-second attach window. A
read-only ADB check afterwards showed only loopback IPv4 on the UE.

The current baseline VNF log likewise stops after AMF registration with no UE
RACH or RRC activity. The PNF continues to advance its hardware counters.

## Conclusion

There are two separate problems:

1. The custom image has a reproducible startup concern: it produced a
   container restart/BackOff event during rollout while the current baseline
   did not. This is an image or startup-interaction issue and needs source-level
   comparison against the exact #87 baseline.
2. The no-`10.45.x.x` symptom is not currently image-specific. It occurs with
   `latest` too, and in both failed sessions the gNB did not see any UE RACH.
   That places this symptom before the DL scheduler, at the UE/RU/radio attach
   boundary.

The custom image must therefore not be declared the root cause of the attach
failure yet. Conversely, it should not be accepted as scheduler-test-ready
until its initial restart is explained and it passes a valid baseline-qualified
attach test.

## Required Next Test

Use a paired trial only after a baseline preflight succeeds:

1. Deploy `latest`, run a 60-second 200 Mbps E2E check, and require all of:
   UE `10.45.x.x`, accepted local iPerf connection, interval samples, and no
   VNF restart.
2. Without changing PNF, RU, UE APN, ConfigMap, or rApp scripts, deploy the
   custom image and repeat the same check.
3. Repeat the pair at least three times. Treat any test lacking baseline UE
   attach as invalid rather than as an image failure.
4. Fetch the private Git branch with approved credentials and compare
   `31c7aa...` directly with `952231...` (or the exact parent) before making
   any further scheduler change.
