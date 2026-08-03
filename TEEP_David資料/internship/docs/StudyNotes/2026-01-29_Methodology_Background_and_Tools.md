# Study Note: Measurement Methodology Deep Dive

## 1. Background: Why measure "Software Power"?

In Traditional RAN (Radio Access Network), the Baseband Unit (BBU) and Radio Unit (RU) are proprietary "Black Boxes". Measuring their power was simple but coarse: put a clamp meter on the power cord.

In **O-RAN (Open RAN)**, these components are disaggregated. The BBU becomes software (O-DU/O-CU) running on standard Commercial Off-The-Shelf (COTS) servers (like Dell/HPE servers with Intel x86 CPUs). This introduces a new problem: **Dynamic Software Energy**.

Unlike a dedicated hardware appliance that draws constant power, an O-RAN server's power fluctuates wildly based on:
1.  **Traffic Load:** How many packets are we processing?
2.  **CPU C-States:** Is the processor sleeping between packets?
3.  **Instruction Set:** Are we using AVX-512 for signal processing?

Therefore, we cannot just look at the wall plug. We need to inspect **internal energy counters** to see *which process* or *which core* is burning energy.

## 2. Tools & Concepts Explained

### A. RAPL (Running Average Power Limit) - The "Sensor"
*   **What it is:** A feature built into Intel and AMD CPUs.
*   **How it works:** The CPU doesn't have a tiny analog power meter inside. Instead, it uses a **model**. It counts events (voltage changes, capacitor discharges, instruction counts) and calculates: "Based on this activity, I must have consumed X Joules."
*   **Accuracy:** Surprisingly high for digital domains (CPU cores, DRAM). Less accurate for total system power (fans, PSU inefficiencies).
*   **Why we use it:** It is available on almost every Linux laptop/server without buying external hardware.

### B. Scaphandre - The "Aggregator"
*   **What it is:** An open-source energy monitoring agent (written in Rust).
*   **Role:** Linux exposes RAPL data in raw, hard-to-read files (`/sys/class/powercap/...`). Scaphandre reads these thousands of times a second, aggregates them, and calculates power (Joules $\div$ Seconds = Watts).
*   **Why not just read the file?** RAPL counters roll over (reset to zero) very quickly. Scaphandre handles the math, the rollovers, and attributes power to specific **Process IDs (PIDs)** (e.g., telling you "Python used 5W" vs "Docker used 2W").

### C. The "Proxy" Methodology
*   **The Problem:** We don't have a physical O-RU (Radio Unit) with Power Amplifiers yet.
*   **The Limit:** Software (Scaphandre) can ONLY measure Digital Power. It cannot measure the power of an antenna it isn't connected to.
*   **The "Gap":** This is why our measurements (~25W) are so much lower than real RU papers (~200W). Real RUs spend 80% of their energy on **RF Amplification** (Analog).
*   **The Value:** By measuring the "Digital Floor", we establish the absolute minimum energy required to run the O-RAN protocol stack. This is critical for "Green RAN" research because the Digital part is the only part we can optimize with software code.