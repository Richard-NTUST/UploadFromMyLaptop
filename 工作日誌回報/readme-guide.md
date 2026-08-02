<h1 align="center">Project README.md — Guideline</h1>

---

> [!NOTE]
> **What a project `README.md` is:** the entry point of every project repository — how to get from zero to *using* the system. It contains exactly three sections:
>
> 1. **Prerequisites** — what must exist before setup
> 2. **Setup** — a link to [`implementation.md`](./implementation.md) to bring up the testbed
> 3. **User Guide** — how to use the project, following the workflow defined in [`research.md`](./research.md)
>
> Everything else lives in its dedicated file — see the documentation map in [README Section 3](./README.md#3-documentation-requirements).

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Setup](#2-setup)
- [3. User Guide](#3-user-guide)
- [Template Skeleton](#template-skeleton)
- [Key Differences: User Guide vs Implementation Guide](#key-differences-user-guide-vs-implementation-guide)

## 1. Prerequisites

List everything a new user needs **before** touching the system — the same table style as implementation.md's one-touch deployment inputs. Keep secret *values* out of Git; list only names and where they live (Vault path).

| Input | What it is | Example |
| --- | --- | --- |
| Hardware | testbed machines, SDRs, UEs required | USRP B210, Quectel RM500Q-GL |
| Access | accounts, VPN, SSH reachability | `user@<ip>` via lab VPN |
| Software | OS / runtime versions | Ubuntu 22.04, Docker 24.x |
| Credentials | secret **pointers** only — never values | `secret/lab/<project>/db` (Vault) |

## 2. Setup

One short paragraph plus the link — do **not** duplicate installation steps here:

- Link to [`implementation.md`](./implementation.md) for per-component installation and end-to-end integration.
- Give the single quick-verify command that proves the testbed is up (from implementation.md's Post-Installation Verification).
- If `.gitmodules` exists, show the `git clone --recursive` line here (see [programming.md Section 11.2](./programming.md#112-git-submodules)).

## 3. User Guide

How to **use** the running system. The structure follows the workflow defined in `research.md` — one subsection per use case in the [Use Case Diagram](./research.md#use-case-diagram), so the User Guide, the MSCs, and the flowcharts all describe the same flows.

**Must-have content:**

1. **Quick Start** — the shortest path to a first successful result (numbered steps, expected output shown)
2. **Per-use-case instructions** — for each use case `UC<n>` in research.md: purpose, when to use it, step-by-step commands or UI actions, and **expected results** (example inputs/outputs)
3. **Simplified workflow diagram** — a user-level Mermaid flowchart per main workflow; the full technical versions stay in `research.md`
4. **API usage** — only if users call APIs directly: request + example response in one block
5. **Troubleshooting for users** — symptom → cause → solution, for *user* errors (system/configuration errors belong in implementation.md)
6. **Limitations** — what the system cannot do

**Example (per-use-case section):**

```markdown
### UC2: Handover UEs to Neighbor Cell

**Purpose:** move all UEs off a low-traffic cell before shutdown.
**When to use:** triggered automatically by the ES rApp; run manually to test.

1. Check connected UEs:

    ```shell
    ./scripts/list-ues.sh --cell cell-1

    # UE  IMSI             RSRP
    # 1   001010000000001  -85 dBm
    ```

2. Trigger the handover and confirm:

    ```shell
    curl -X POST http://<rapp>:9090/api/handover -d '{"cell": "cell-1"}'

    # {"status": "OK", "moved_ues": 1}
    ```

**Expected result:** cell-1 reports 0 active UEs (see the flowchart in research.md, UC2).
```

## Template Skeleton

```markdown
# <Project Name>

<One-paragraph description: what the system does and who uses it.
 Research description: [research.md](./research.md)>

## 1. Prerequisites

| Input | What it is | Example |
| --- | --- | --- |
| ... | ... | ... |

## 2. Setup

Follow [implementation.md](./implementation.md) to bring up the testbed.
Verify it is up:

    <one quick-verify command>
    # <expected output>

## 3. User Guide

### Quick Start
1. ...

### UC1: <Use case name>
...

### Troubleshooting
| Symptom | Cause | Solution |
| --- | --- | --- |
```

## Key Differences: User Guide vs Implementation Guide

| Aspect | Implementation Guide (`implementation.md`) | User Guide (README section 3) |
| --- | --- | --- |
| **Focus** | System setup, configuration & integration | Feature usage & workflows |
| **Audience** | The next student bringing up the testbed | Anyone operating the running system |
| **Architecture** | Detailed technical diagrams | Simplified user-flow diagrams |
| **Content** | IP addresses, ports, dependencies | Steps per use case, example I/O |
| **Troubleshooting** | System errors, configuration issues | User errors, feature problems |
| **Source of structure** | Startup order of components | Use cases in `research.md` |
