# 5G Stack Deployment Master Report: Jan 30, 2026

**Project:** srsRAN 5G SA (Standalone) with ZeroMQ (ZMQ) Virtual Radio

**Objective:** Measure "Compute Power" baseline for containerized 5G PHY/MAC processing using **Scaphandre**.

---

## I. Detailed Progression Timeline

We transitioned from an unstable, generic setup to a strictly accurate, 5G-native architecture. Below are the key milestones achieved today:

### 1. Environment Sanitization & Architecture Selection

* **The Shift:** We abandoned a broken srsRAN-docker setup and adopted a modern, split-architecture: **srsRAN_Project** (gNB) + **srsRAN_4G** (UE).
* **Rationale:** This combination is the industry standard for 5G SA ZeroMQ simulations in 2026.
* **Networking:** Established a dedicated Docker Bridge network (`10.53.1.0/24`) to provide fixed IP addressing for the N2 (Control Plane) and N3 (User Plane) interfaces.

### 2. Core Network (Open5GS) Remediation

* **Binding Fix:** Identified that the AMF was bound to a loopback address (`127.0.0.5`), which is inaccessible across container boundaries.
* **Action:** Reconfigured `open5gs-5gc.yml` to bind the NGAP server to `0.0.0.0`, allowing it to "hear" the gNB on the container's ethernet interface.
* **Result:** The AMF successfully moved to a "Ready to Listen" state on `10.53.1.2`.

### 3. Transport Layer Hardening (SCTP)

* **Discovery:** Confirmed that Ubuntu 24.04 (Kernel 6.8) requires explicit loading of SCTP modules to allow the N2 handshake to pass through the Docker bridge.
* **Action:** Loaded `sctp` and `nf_conntrack_sctp` on the host machine.
* **Result:** Verified that the host kernel can now track stateful SCTP associations for 5G signaling.

### 4. UE Compilation & ZMQ Integration

* **Build:** Successfully compiled a ZMQ-enabled binary of `srsue` inside a temporary container.
* **Verification:** Confirmed that the UE now recognizes the `zmq` radio driver, a critical step for our virtualized power experiment.

---

## II. The "Deadlock" Roadblock: A Technical Deep-Dive

We are currently facing an **Indefinite gNB Hang**. Our deep research identified the following mechanisms at play:

### 1. The Virtual Clock Dependency

* **Mechanism:** In a ZMQ simulation, the gNB does not have a hardware oscillator. It derives its system clock from incoming I/Q samples.
* **The Problem:** Because the UE is currently failing to launch, the gNB is receiving **zero samples**. Consequently, the gNB's internal clock is "frozen" at , preventing it from ever reaching the code block that initiates the SCTP handshake with the Core.

### 2. The UE "Syntax Boss"

* **Symptom:** The UE fails with `[zmq] Error: Neither Tx port nor Rx port specified`.
* **Root Cause:** The `srsRAN_4G` ZMQ driver defaults to a 2-channel (MIMO) configuration. When provided with a single set of ports, it panics because it cannot initialize the second channel.
* **Current State:** Our last attempt failed because the `ue_zmq.conf` was accidentally corrupted with bash command syntax (`cat <<EOF`), which the `srsue` parser rejected.

---

## III. Resolution & Strategy for Tomorrow

To reach the goal of measuring 5G Compute Power, we must execute these specific, evolved steps:

### Step 1: Sanitize the Configuration

* We will re-create a "Pure" `ue_zmq.conf` on the host, ensuring it contains strictly cellular parameters with no shell artifacts.
* We will explicitly set `nof_antennas = 1` inside the file to force a SISO (Single-Input Single-Output) mode.

### Step 2: Breaking the Deadlock

* **Launch Order:** We must start the UE **before** the gNB is fully initialized.
* **The Trigger:** As soon as the UE begins "Searching for cell," it starts streaming virtual noise (samples) to the gNB. This provides the "tick" the gNB needs to finish its boot and connect to the Core.

### Step 3: Power Capture Baseline

* Once the `NG connection established` log appears, we will start **Scaphandre** to capture the baseline wattage of the 5G stack.
* We will then run `iperf3 -c 10.45.1.1 -b 100M` through the UE to simulate a heavy user load, observing the jump in CPU power consumption.

---

**Summary Checklist for Next Session:**

* [ ] Verify `open5gs/open5gs-5gc.yml` is still set to `0.0.0.0` for NGAP.
* [ ] Clean `ue_zmq.conf` of any `cat` or `EOF` text.
* [ ] Use the `--rf.nof_antennas=1` flag to bypass the 2-channel ZMQ panic.
