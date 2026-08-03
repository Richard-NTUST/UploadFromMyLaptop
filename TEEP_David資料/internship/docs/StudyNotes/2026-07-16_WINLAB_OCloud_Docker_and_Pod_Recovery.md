# WINLAB OCloud Docker and Pod Recovery Notes

**Date:** 2026-07-16

## Context

The WINLAB E2E rApp now has two service paths:

| Path | Port | Purpose |
|---|---:|---|
| Host rApp | `127.0.0.1:9090` | Existing working service, kept intact |
| Dockerized rApp | `127.0.0.1:19090` | Containerized service for side-by-side validation |

The key rule was to avoid deleting or replacing the working host rApp while validating the Dockerized version.

## Dockerized rApp Target

The Dockerized rApp should expose the same operational flow as the host version:

1. receive `POST /gnb/run`;
2. start an async job;
3. execute `run_e2e_with_artifacts.py`;
4. run Bare Metal or OCloud E2E based on request parameters;
5. preserve request, command, stdout, summary, throughput data, plots, and pod logs.

Important configurable fields:

| Field | Meaning |
|---|---|
| `server` | Main runner identity, currently HPE |
| `target_identity` | Experiment target label, currently `hpe-pegatron-ru-o` |
| `ue_serial` | Android UE serial, currently `R5CN30TMBYR` |
| `iapc_host` | UE-control server, currently `sshuser@140.118.162.81` |
| `iapc_port` | UE-control SSH port, currently `24` |

This matters because the flow has two server-side identities:

- Server 1: HPE runner / OCloud host side.
- Server 2: IAPC / UE-control side.

Both must remain configurable so the rApp is usable across the lab, not tied to one workstation layout.

## OCloud Pod Recovery

The OCloud path depends on healthy VNF/PNF pods in `ming-ns`:

- `oai-vnf`
- `oai-pnf-pegatron`

The main failure mode seen this week was PNF pod creation loops caused by SR-IOV allocation/state problems. Symptoms included:

- pods stuck in `Terminating`;
- pods entering `UnexpectedAdmissionError`;
- pods reporting missing SR-IOV resources such as `openshift.io/fh_sriov_up_lao`;
- repeated PNF pod creation until the namespace became noisy.

The safe recovery pattern is:

1. scale the failing deployment to zero;
2. force-delete failed or terminating pods;
3. verify node SR-IOV capacity/allocatable state;
4. clear stale CNI/SR-IOV allocation state only when needed;
5. scale or reinstall VNF/PNF after resources are healthy.

## Cleanup Script

Ming's recovery script on HPE:

```text
/home/hpe/force_cleanup_pods.sh
```

The script:

- uses `/home/hpe/CRAN/kubectl`;
- uses `/home/hpe/CRAN/ming-kubeconfig.yaml`;
- scans for terminating pods;
- strips finalizers when force deletion is not enough;
- detects `Failed` and `OutOf...` pods;
- prints node capacity/allocatable values for missing resources;
- scales the owning Deployment, ReplicaSet, or StatefulSet to zero to stop spawn loops;
- deletes failed pods after stopping the owner.

## Practical Lesson

The cleanup script is not the root-cause fix. It is a control tool to stop namespace churn. The actual fix is making sure the RT worker advertises the required SR-IOV resource and that stale allocation state does not reserve the same PCI address after failed pod deletion.

## Current Validation Target

Once VNF and PNF are both `Running` and `Ready`, the Dockerized endpoint should be tested through:

```text
POST http://127.0.0.1:19090/gnb/run
```

The minimum smoke test is a 100 Mbps downlink OCloud run for 60 seconds using the Samsung UE.
