# O-RAN Principles — Part 1: Architecture Fundamentals (2026-01-16)

Status: Complete
Deadline: 2026-01-16

This note is a cleaned + repo-formatted version of my O-RAN study notes. It focuses on the architecture fundamentals we need for the internship scope (RU/DU/CU placement, control loops, and where measurements/telemetry “live”).

Part 2 (RIC/interfaces/work groups) is in:
- `docs/StudyNotes/2026-01-16_O-RAN-Principles_Part-2_RIC-and-Interfaces.md`

## Table of contents
- [Why this matters for our project](#why-this-matters-for-our-project)
- [Quick glossary (RAN generations + core terms)](#quick-glossary-ran-generations--core-terms)
- [What Open RAN / O-RAN means](#what-open-ran--o-ran-means)
- [Functional disaggregation (O-CU / O-DU / O-RU)](#functional-disaggregation-o-cu--o-du--o-ru)
- [Control loop hierarchy (SMO / RIC / CU-DU-RU)](#control-loop-hierarchy-smo--ric--cu-du-ru)
- [O-RU internal architecture (high level)](#o-ru-internal-architecture-high-level)
- [Key takeaways](#key-takeaways)

## Why this matters for our project
Our probation deliverable is framed as energy/power measurement replication with strict labeling (platform vs RU input). To avoid mixing scopes:
- O-RU is a physical unit with RF + low-PHY; measuring its input power is a hardware measurement task (PDU/analyzer).
- O-DU/O-CU can run on a compute platform; measuring their platform power can be software-estimated (Scaphandre/Kepler/etc) if counters exist.

## Quick glossary (RAN generations + core terms)
Radio Access Network (RAN) connects user devices (UEs) to the core network.

Common base station naming by generation:
- 2G: BTS + BSC
- 3G: NodeB + RNC
- 4G: eNodeB
- 5G: gNodeB

## What Open RAN / O-RAN means
Two related ideas are often mixed:

1) Open RAN (concept/movement)
- Disaggregate traditional base station components
- Use open/standardized interfaces
- Enable multi-vendor interoperability

2) O-RAN (Alliance + specific architecture/framework)
- Formal reference architecture + interface specs
- Adds RIC concepts (Near-RT / Non-RT) and management/orchestration (SMO)

## Functional disaggregation (O-CU / O-DU / O-RU)
At a high level, the monolithic base station becomes a split system:

- O-RU (Radio Unit)
  - RF + Low-PHY
  - Located near antenna/radio site
  - Open Fronthaul to O-DU

- O-DU (Distributed Unit)
  - High-PHY + MAC + RLC (real-time-ish functions)
  - Typically edge/distributed location

- O-CU (Central Unit)
  - 5G splits into CU-CP (control plane) and CU-UP (user plane)
  - More centralized; can run on cloud/COTS infrastructure

## Control loop hierarchy (SMO / RIC / CU-DU-RU)
The architecture is typically described by control loops/time scales:

1) Non-real-time control loop ( 1s)
- SMO / Non-RT RIC level

2) Near-real-time control loop ( 10ms and < 1s)
- Near-RT RIC level

3) Real-time (< 10ms)
- RAN stack execution in CU/DU/RU layers

This matters because what you can optimize and what you can measure depends on the layer and its time scale.

## O-RU internal architecture (high level)
Common internal functional blocks (conceptual):

- RF front end
  - filtering, PA (power amplifier), LNA, DAC/ADC

- Digital front end
  - DPD/CFR, DUC/DDC

- Low-PHY
  - FFT/IFFT, PRACH processing, cyclic prefix operations, beamforming/precoding

- Fronthaul / transport
  - eCPRI/UDP/IP + sync/1588/PTP (implementation dependent)

- Support systems
  - power supply, management ports, indicators

## Key takeaways
- Treat O-RU as the thing we eventually want to measure at AC input (hardware instrumentation).
- Treat O-DU/O-CU as candidates for platform power under RU-like workload (software-first, if counters exist).
- Dont mix RAN performance metrics (throughput/PRB/latency) with power measurement point in writing; always name both explicitly.

- Treat O-RU as the **thing we eventually want to measure at AC input** (hardware instrumentation).
- Treat O-DU/O-CU as candidates for **platform power under RU-like workload** (software-first, if counters exist).
- Don’t mix “RAN performance metrics” (throughput/PRB/latency) with “power measurement point” in writing; always name both explicitly.
*** End Patch
-> Radio Access Network
- BSC - Base Station Controller & BTS - Base Transceiver Station in 2G
- RNC - Radio Network Controller & NodeB in 3G
- eNodeB in 4G
- gNodeB in 5G

OpenRAN applies to all generations of RAN, including 2G, 3G, 4G, and 5G.

Open RAN - OpenRAN - oRAN - ORAN - O-RAN?

a. Open RAN : Movement to disaggregate the RAN components and use open interfaces to allow interoperability between different vendors' equipment.

b. OpenRAN : Either refers to the telecom industry movement or the specific implementations that follow the Open RAN principles.

### What is O-RAN?

XRAN Forum, which is a collaboration of telecom operators, vendors, and research institutions, collaborated with C-RAN Alliance, which was formed by China Mobile, to create the O-RAN Alliance in 2018. 

The O-RAN Alliance aims to drive the adoption of open and intelligent RAN solutions.
Founding Operators include AT&T, China Mobile, Deutsche Telekom, NTT DOCOMO, and Orange.

- When people write #O-RAN, they are typically referring to the O-RAN Alliance and its initiatives.

## Open RAN Concept

### Typical Architecture:

Services
-- -- -- --
Core Network
|
| <- Transport Network
|
Access Network
|
Air Interface
|
User Equipment (UE)

### Usual Mobile Tower Architecture:

- A cabinet of hardware and operating system on the bottom, and a tower to hold the antennas on top.
- Consists of Signal Processing Unit (SPU), RF Equipment, Network Access, and Long RF Cables.

(!) Primitive approach due to the distance between the cabinet and the antennas, which can lead to signal loss and latency.

- During late 3G to 4G, the architecture evolved to move the RRU (Remote Radio Unit) and RF Equipment closer to the antennas, reducing latency and improving signal quality.
- Now, the base station contains Signal Processing Unit, Network Access, and Fiber Optic Cables, with the RRU and RF Equipment on the tower.

### Traditional RAN Architecture:

![image](https://hackmd.io/_uploads/SJMQnWpLxe.png)

- RRU contains DAC/ADC and RF Equipment, while BBU is similar to the late 4G towers

### Virtual RAN Architecture:

![Screenshot 2025-07-22 200205](https://hackmd.io/_uploads/ByDb3ZTUeg.png)

- COTS Server + Proprietary software virtualized for BBU

### Open RAN Architecture:

![Screenshot 2025-07-22 200435](https://hackmd.io/_uploads/HJgp6Wa8ge.png)

- COTS based hardware (SDR)
- Interface is now open instead of being proprietary
- Due to flexibility on both ends, Open RAN enables free use from any ODM/OEM vendors without brand limitations

### Legacy Model

![image](https://hackmd.io/_uploads/SydN0bp8xl.png)

-> More stiff and less modification potential

### Open RAN Model

![image](https://hackmd.io/_uploads/rJQvC-T8lx.png)

-> Flexibility in hardware used thanks to OpenRAN software (COTS Server)

![image](https://hackmd.io/_uploads/SJ85Rb6Lxx.png)

-> System still works with different vendors for hardware, and when the software updates, the OpenRAN architecture doesn't block usage.

### Future Developments

![image](https://hackmd.io/_uploads/B15AxfaLgg.png)

#### Old Setup (Left Side)

- BBU = Baseband Unit
- RRU = Remote Radio Unit
- Fronthaul = Connection between BBU and RRU
- Backhaul = Connection from BBU to the core network (internet, voice, etc.)

In this setup, BBU does all the "thinking" (processing), and RRU does the "talking" (radio transmission).

#### New Setup (Right Side) — 5G OpenRAN with 3GPP Standard

- CU = Central Unit
- DU = Distributed Unit
- RRU stays the same

Now there are three types of links:

- Fronthaul: DU ↔ RRU
- Midhaul: CU ↔ DU (allows more flexibility)
- Backhaul: CU ↔ Core Network

This breaks the work into three parts:

- RRU: Radio interface
- DU: Handles real-time functions (close to the RRU)
- CU: Handles slower, non-time-sensitive tasks (can be centralized far away)

## Typical Mobile Network Architecture

![Screenshot 2025-07-23 154205](https://hackmd.io/_uploads/Skyz1jA8gl.png)

- 3GPP Standards Based Interface to connect end devices to Access Network and Access Network to Core Network, where all services are provided.

- The scope of O-RAN is on the Access Network.

### Basic O-RAN Architecture

![Screenshot 2025-07-23 154235](https://hackmd.io/_uploads/Byc4ys08ex.png)

Foundational O-RAN setup with minimal components:
- Near-RT RIC (Near Real-Time RAN Intelligent Controller) running VNFs (Virtual Network Functions)
- RU (Radio Unit) handling the radio transmission
- COTS Hardware providing the underlying compute platform
- Simple connection to core network services

### 4G LTE O-RAN Architecture

![Screenshot 2025-07-23 154249](https://hackmd.io/_uploads/SkZHkjAIge.png)

This adds 4G LTE-specific components and management layers:
- SMO Framework (Service Management and Orchestration) at the top for centralized management
- Non-RT RIC (Non-Real-Time RIC) for policy management and optimization
- BBU (Baseband Unit) added within the Near-RT RIC for signal processing
- Open Fronthaul M-Plane interfaces (A1, O1, O2) for standardized communication
- E2 interface connecting RIC components

### 5G NR O-RAN Architecture

![Screenshot 2025-07-23 160334](https://hackmd.io/_uploads/rJIr1i0Lxx.png)

This shows the full 5G implementation with functional disaggregation:
- DU (Distributed Unit) separated as a distinct black component
- CU-CP (Control Plane) and CU-UP (User Plane) split for 5G's control/user plane separation
- F1-C and F1-U interfaces connecting the disaggregated functions
- E1 interface between CU components
- More sophisticated VNF deployment

### Centralized Near-RT RIC Options

Type 1: Near-RT RIC Only Serving 5G
- Dedicated to 5G components only
- Manages O-CU-CP (Control Plane), O-CU-UP (User Plane), and O-DU (Distributed Unit)
- Pure 5G NR implementation

Type 2: Near-RT RIC Only Serving 4G and 5G
- Hybrid deployment managing both technologies
- Handles 5G components (O-CU-CP, O-CU-UP, O-DU) plus 4G eNodeB (O-eNB)
- Enables coordination between 4G and 5G networks

Type 3: Near-RT RIC Only Serving 4G
- Legacy-focused deployment
- Manages only O-eNB (4G base stations)
- Useful for operators with significant 4G infrastructure

### Distributed Near-RT RIC

![Screenshot 2025-07-23 160349](https://hackmd.io/_uploads/H10rkoR8lx.png)

This shows a distributed approach where:
- Single physical Near-RT RIC hosts multiple logical Near-RT RICs
- Each logical RIC can specialize in different network functions
- More flexible resource allocation and isolation
- Better scalability and fault tolerance
- Each logical RIC still maintains its own E2 connections to network elements

The distributed model allows operators to optimize resource usage while maintaining logical separation between different network domains or services, providing both efficiency and flexibility in RIC deployment.

## O-RAN Timeline and Releases

![Screenshot 2025-07-23 170001](https://hackmd.io/_uploads/Byu0ksCIge.png)

### The O-RAN Community

O-RAN Software Community (OSC) Summary
The O-RAN Software Community is a collaborative initiative between the O-RAN Alliance and Linux Foundation aimed at developing open-source software for Radio Access Networks.

Key Objectives:

- Create open-source software implementations of O-RAN components and systems
- Align software reference implementations with O-RAN Alliance's open architecture and specifications
- Unify and accelerate RAN evolution and deployment
- Address wireless technology support for essential patents

Organizational Structure:

- Exclusively sponsored by the O-RAN Alliance
- Technical Oversight Committee (TOC) provides technical oversight for all software community activities
- Operates under the Linux Foundation's open-source project framework

Project Portfolio:

- Infrastructure projects: OPNFV, ONAP, LF Networking Fund, Deep Learning Foundation
- AI/ML components: Acumos AI, Angel ML
- O-RAN specific components: Integration, Non-RT RIC, Near-RT RIC, O-CU, O-DU
- Development projects: Various O-CU and O-DU implementations

## Reference Architecture

![Screenshot 2025-07-23 170524](https://hackmd.io/_uploads/Byi1xiCUlg.png)

These three diagrams show the O-RAN Alliance Reference Architecture with its hierarchical control loops and functional decomposition.

## Control Loop Hierarchy

![Screenshot 2025-07-23 194057](https://hackmd.io/_uploads/HJweesRUxg.png)

The architecture operates on three distinct time scales:

1. Non-real-time control loop (≥ 1 second) - SMO Framework level
2. Near-real-time control loop (≥ 10ms < 1 second) - Near-RT RIC level  
3. O-DU real-time control loop (< 10ms) - Physical layer processing

![Screenshot 2025-07-23 194046](https://hackmd.io/_uploads/SJjmej0Ige.png)

### SMO Framework (Top Level)
- Service Management and Orchestration providing policy, inventory, configuration, and design functions
- Connects via A1 interface to Near-RT RIC
- Uses O1/O2 interfaces for management

### Near-RT RIC (Middle Level)
- Applications Layer with various xApps for:
- 3rd Party Apps, Radio Connection Management
- Mobility Management, QoS Management
- Interference Management, Trained Models
- Radio Network Information Base as the data foundation
- E2 interface connecting to CU/DU functions

### CU/DU Functions (Lower Level)
- Multi-RAT CU Protocol Stack split into:
- CU-CP (Control Plane) with RRC and PDCP-C
- CU-UP (User Plane) with SDAP and PDCP-U
- F1 interface between CU and DU
- E1 interface between CU-CP and CU-UP

### O-DU and O-RU (Physical Level)

![Screenshot 2025-07-23 200454](https://hackmd.io/_uploads/By-Bls0Lel.png)

- O-DU: Higher PHY functions (RLC/MAC/PHY-High)
- O-RU: Lower PHY and RF functions (PHY-Low/RF)
- Open Fronthaul interfaces (CUS-Plane and M-Plane)

## O-RAN Functional Disaggregation

This shows how traditional base station functions are disaggregated across three main units:

### O-RU (Radio Unit)
- RF: Radio Frequency processing
- Low-PHY: Lower physical layer functions

### O-DU (Distributed Unit)  
- High-PHY: Higher physical layer processing
- MAC: Media Access Control
- RLC: Radio Link Control

### O-CU (Centralized Unit)
- PDCP: Packet Data Convergence Protocol
- RRC/SDAP: Radio Resource Control/Service Data Adaptation Protocol

### O-Cloud Infrastructure
- AAL (Acceleration Abstraction Layer) provides hardware abstraction for each unit
- Cloud Stack includes containers/VMs, OS, and cloud management
- Hardware options: x86 processors, FPGA, GPU, ASIC
- Note: O-RU cloudification and O-RU AAL are identified as future study items

## O-RU Internal Architecture

![Screenshot 2025-07-23 200507](https://hackmd.io/_uploads/SyaDloRLgg.png)

### RF Front End
- Filter, PA (Power Amplifier), DAC (Digital-to-Analog Converter)
- LNA (Low Noise Amplifier), ADC (Analog-to-Digital Converter)

### Digital Front End
- DPD (Digital Pre-Distortion), CFR (Crest Factor Reduction), DUC (Digital Up Converter)
- PIMC (optional), DDC (Digital Down Converter)

### Low PHY (highlighted in orange)
- FFT/IFFT: Fast Fourier Transform processing
- PRACH: Physical Random Access Channel processing
- CP addition: Cyclic Prefix addition
- Digital BF: Digital Beamforming
- Precoding: Signal precoding functions

### Fronthaul/Transport
- eCPRI, UDP/IP, Synch: Protocol stack for fronthaul communication
- Ethernet Interfaces, IEEE 1588I: Network connectivity and timing

### Support Systems
- Power Supply, RJ-45, LED: Infrastructure and monitoring components

This architecture enables vendor interoperability while maintaining high-performance radio processing through standardized interfaces and modular design.

## Near-RT RIC Architecture

![Screenshot 2025-07-23 200527](https://hackmd.io/_uploads/B1qOxoCLgl.png)

## External Interfaces

### SMO Connection
- O1 Interface: Connects to SMO for configuration and management
- A1 Interface: Receives policies and enrichment information from Non-RT RIC
- Both terminate at dedicated O1 Termination and A1 Termination points

### E2 Connection
- E2 Interface: Connects to E2 Nodes (O-DU, O-CU functions)
- E2 Termination: Handles communication with RAN functions
- Enables real-time control and data collection from network elements

## Core Platform Components

### xApp Layer
- xApp 1, xApp 2, ... xApp N: Multiple intelligent applications
- These are the "brains" of the Near-RT RIC
- Each xApp can provide specific optimization functions (mobility management, interference coordination, QoS optimization, etc.)
- Near-RT RIC APIs for xApp: Standardized APIs enabling xApp development and deployment

### Platform Services
- Messaging Infrastructure: Enables communication between xApps and platform components
- Conflict Mitigation: Resolves conflicts when multiple xApps make contradictory decisions
- Subscription Management: Manages E2 subscriptions for data collection from RAN functions
- Management Services: Handles xApp lifecycle, configuration, and monitoring
- Security: Provides authentication, authorization, and secure communication

### Data Management
- Shared Data Layer: Provides common data access for all xApps
- Database: Stores RAN data, policies, and operational information
- Enables data sharing between xApps while maintaining consistency

## Key Architecture Principles

1. Modularity: xApps can be independently developed, deployed, and updated
2. API Enablement: Standardized APIs allow third-party xApp development
3. Data Sharing: Common data layer prevents data silos
4. Conflict Resolution: Built-in mechanisms handle competing xApp decisions
5. Real-time Processing: Sub-second control loop capabilities for RAN optimization

This architecture enables intelligent, automated network optimization through programmable applications while maintaining platform stability and vendor neutrality.

## Non-RT RIC Architecture

![Screenshot 2025-07-23 212431](https://hackmd.io/_uploads/B18tgsCLeg.png)

### Core Architecture

The Non-RT RIC (Non-Real-Time RAN Intelligent Controller) sits within the broader SMO Framework and serves as a platform for hosting rApps (RAN Applications) that can influence network behavior through standardized interfaces.

### Key Components

rApps Layer: Multiple applications (rApp 1, rApp 2, etc.) run on top of the Non-RT RIC framework. 

R1 Interface: The standardized "Open APIs for rApps" interface that allows applications to access framework services in a consistent manner.

Non-RT RIC Framework (orange section):
- rApp Service Exposure Functions: Provides the API layer that rApps use to access framework capabilities
- Inherent Non-RT RIC Framework Functionality: Core platform services that are always present
- A1 Functions: Handle the A1 interface communication protocol

### Critical Interface A1

The A1 interface is the key southbound interface that connects the Non-RT RIC to:
- Near-RT RIC: For more time-sensitive RAN control functions
- Other O-RAN xNF: Other network functions in the O-RAN ecosystem

This A1 interface enables the Non-RT RIC to send policies, configurations, and control information down to network elements that operate on faster timescales.

### Implementation Flexibility

The Implementation Variability indicates where vendors can customize functionality while maintaining standard interface compliance. This allows for competitive differentiation while ensuring interoperability.

#### Integration Points

- SMO Internal Interface: Connects upward to broader Service Management and Orchestration functions
- O2 Functions/O1 Functions: Connect to O-Cloud infrastructure for cloud-native deployment and management

This architecture enables a separation of concerns where rApps can focus on network intelligence and optimization logic, while the framework handles the complexities of interfacing with the underlying RAN infrastructure through standardized protocols like A1.

### Non-RT RIC Framework Architecture

Looking at these five images, I can now provide a comprehensive explanation of the Non-RT RIC functional architecture and its key aspects:

### Non-RT RIC Framework Architecture

The Non-RT RIC Framework serves as a hosting platform for rApps (RAN Applications) within the O-RAN ecosystem. The architecture demonstrates several key functional areas:

### Core Framework Components

Service Exposure Layer: 
- SMO Service Exposure Function: Provides northbound connectivity to the broader SMO ecosystem
- Non-RT RIC Framework Service Exposure Function: Internal service management
- rApp Service Exposure Functions: Direct API access for applications

A1 Interface Functions:
- A1 Policy Functions: Handle policy distribution southbound
- A1 EI Functions: Manage enrichment information exchange
- A1 ML Functions: Support machine learning model distribution
- A1 Termination: Protocol termination for A1 interface

Application Management: 
- App Management Functions: Lifecycle management of rApps
- Other Non-RT RIC Framework Functions: Additional platform services

### Key Interface Highlights

R1 Interface (Image 3): The "Open APIs for rApps" provides standardized northbound access, enabling rApps to consume framework services consistently regardless of implementation.

External Interfaces Termination (Image 4): Shows how external connectivity is managed:
- External EI Interface: For enrichment information from external sources  
- External A1/ML Interface: For machine learning model exchange
- Human-Machine Interface: For operator interaction and oversight

### Implementation Flexibility

The Implementation Variability sections (shown in gray with dotted borders) indicate where different vendors can provide custom implementations while maintaining interface compliance. This includes:
- External interface terminations
- Workflow functions  
- Human-machine interaction capabilities

### Operational Flow

The architecture enables a clear separation of concerns:
1. rApps focus on network intelligence and optimization logic
2. Framework handles service exposure, lifecycle management, and interface standardization
3. A1 Interface carries policies, models, and control information to Near-RT RIC and E2 Nodes
4. SMO Integration provides broader orchestration and management capabilities

## O-RAN Work Groups

![Screenshot 2025-07-23 215436](https://hackmd.io/_uploads/HkOJbjAUxe.png)

This diagram shows the 10 O-RAN Work Groups and their specific objectives, organized around a central O-RAN architecture diagram. Here's what each work group focuses on:

### Intelligence and Control Layer
WG1: Use Cases and Overall Architecture
- Identifies use cases and requirements for the entire O-RAN ecosystem
- Plans the overall architecture and manages Proof-of-Concepts
- Provides the foundational framework that other work groups build upon

WG2: RIC (Non-RT) and A1 Interface
- Develops AI-enabled Non-Real-Time RIC functionality
- Focuses on operational supervision and intelligent Radio Resource Management (RRM)
- Specifies the A1 interface for policy and model distribution

WG3: RIC (Near-RT) and E2 Interface
- Defines Near-Real-Time RIC architecture for faster control loops
- Enables control and optimization of RAN elements through the E2 interface
- Handles time-sensitive network optimization functions

### Interface Specifications
WG4: Open FH Interface
- Specifies the open fronthaul interface (NGFH) between Distributed Unit (DU) and Radio Unit (RU)
- Based on C-RAN and xRAN work from standards bodies (IEEE 1914, eCPRI, CPRI)

WG5: Open F1, W1, E1, X2, Xn Interfaces
- Designs Open Central Unit (CU) specifications
- Addresses RAN virtualization and splits
- Ensures interfaces intersect properly with 3GPP specifications

### Infrastructure and Platform
WG6: Cloudification and Orchestration
- Specifies virtualization layer and hardware requirements
- Focuses on decoupling Virtual Network Functions (VNF) and NFV Infrastructure (NFVI)
- Handles MANO (Management and Network Orchestration) enhancement

WG7: White-Box Hardware
- Develops complete reference designs for decoupled software and hardware platforms
- Promotes open hardware specifications to enable vendor interoperability

WG8: Stack Reference Design
- Creates software architecture, design, and release plans
- Focuses on O-RAN Central Unit (O-CU) and O-RAN Distributed Unit (O-DU)
- Based on O-RAN and 3GPP specifications

### Transport and Management
WG9: Open X-Haul Transport
- Addresses transport domain requirements including equipment, physical media, and protocols
- Covers fronthaul, mid-haul, and backhaul transport network interfaces
- Ensures underlying Ethernet interfaces support O-RAN functions

WG10: OAM and O1 Interface
- Creates detailed Operations, Administration, and Maintenance (OAM) architecture
- Has full responsibility for O1 interface specifications
- Handles network management and monitoring capabilities

## O-RAN Overview (Handbook)

### Core Definition & Purpose

O-RAN = Open Radio Access Network - A paradigm shift toward disaggregated, virtualized, and intelligent RAN architecture using open interfaces and standardized APIs.

#### Key Principles
- Disaggregation: Breaking monolithic base stations into modular components (CU, DU, RU)
- Virtualization: Software-based network functions running on COTS hardware
- Open Interfaces: Standardized APIs enabling multi-vendor interoperability
- Intelligence: AI/ML-driven optimization through RIC controllers

### O-RAN Alliance Structure

Founded: 2018 (merger of xRAN Forum + C-RAN Alliance)
Key Founding Members: AT&T, China Mobile, Deutsche Telekom, NTT DOCOMO, Orange

#### Software Community (OSC)
- Collaboration between O-RAN Alliance & Linux Foundation
- Develops open-source implementations of O-RAN specifications
- Technical Oversight Committee (TOC) provides governance

### Functional Architecture

#### Three-Layer Control Hierarchy

1. Non-RT RIC (≥1 second)
   - Policy management & orchestration
   - Hosts rApps for network optimization
   - A1 interface to Near-RT RIC

2. Near-RT RIC (10ms - 1 second)
   - Real-time RAN optimization
   - Hosts xApps for intelligent control
   - E2 interface to CU/DU functions

3. Real-Time Processing (<10ms)
   - Physical layer processing in O-DU/O-RU
   - Time-critical radio functions

#### Disaggregated Functions

| Component | Functions | Location |
|-----------|-----------|----------|
| O-RU | RF, Low-PHY, Digital beamforming | At antenna site |
| O-DU | High-PHY, MAC, RLC | Edge/distributed |
| O-CU-CP | RRC, PDCP-C (Control Plane) | Centralized |
| O-CU-UP | SDAP, PDCP-U (User Plane) | Centralized |

#### Key Interfaces

- Open Fronthaul: O-DU ↔ O-RU (7.2x split standard)
- F1: O-CU ↔ O-DU
- E1: O-CU-CP ↔ O-CU-UP
- E2: Near-RT RIC ↔ Network Functions
- A1: Non-RT RIC ↔ Near-RT RIC
- O1: Management interface to SMO

### Business Drivers & Benefits

#### Primary Motivations (Industry Survey)
1. Vendor diversity/reduce lock-in (49%)
2. Rural/marginal geography coverage (43%)
3. New service opportunities (37%)
4. CAPEX optimization (31%)
5. Feature development control (23%)

#### Strategic Advantages
- Multi-vendor ecosystem: Best-of-breed component selection
- Innovation acceleration: Competitive marketplace drives advancement
- Cost flexibility: COTS hardware reduces proprietary equipment costs
- Deployment agility: Software-defined functions enable rapid updates
- Rural enablement: Lower-cost solutions for underserved areas

### Current Challenges

#### Technical Limitations
- Performance gaps: Software solutions introduce latency vs. optimized hardware
- Advanced feature support: Massive MIMO, carrier aggregation still challenging
- Integration complexity: Multi-vendor testing and validation overhead

#### Economic Realities
- Early adoption costs: High-performance COTS equipment can exceed traditional costs
- Integration expenses: Third-party integration services add overhead
- Maturity timeline: Traditional RAN has decades of optimization advantage

#### Standards & Ecosystem
- Specification maturity: O-RAN specs evolving but not yet 3GPP-level stable
- Vendor alignment: Not all players fully committed to O-RAN standards
- Interoperability testing: Complex validation across vendor boundaries

### O-RAN Work Groups (WG1-WG10)

| WG | Focus Area | Key Deliverables |
|----|------------|------------------|
| WG1 | Use Cases & Architecture | Overall system design, PoCs |
| WG2 | Non-RT RIC & A1 | Policy management, AI/ML models |
| WG3 | Near-RT RIC & E2 | Real-time control, xApps |
| WG4 | Open Fronthaul | O-DU/O-RU interface specs |
| WG5 | Open CU Interfaces | F1, E1, X2, Xn specifications |
| WG6 | Cloudification | Virtualization, orchestration |
| WG7 | White-box Hardware | Open hardware reference designs |
| WG8 | Stack Reference | Software architecture, O-CU/O-DU |
| WG9 | Open X-haul Transport | Transport network interfaces |
| WG10 | OAM & O1 | Operations, management interface |

### Deployment Examples

#### Commercial Deployments
- Rakuten Mobile (Japan, 2019): First large-scale multi-vendor O-RAN
- DISH Network (US): Second major greenfield O-RAN deployment
- Vodafone (UK): 2,600-site commitment by 2023
- 1&1 (Germany): Fully virtualized network with Rakuten collaboration

#### Deployment Strategies
- Greenfield: New operators building O-RAN from scratch (Rakuten, DISH)
- Brownfield: Existing operators gradually migrating (Vodafone)
- Hybrid: Selective O-RAN deployment for specific use cases

### Future Outlook

#### Technology Maturation
- Performance gaps closing through optimized software/hardware co-design
- Standards consolidation around O-RAN Alliance specifications
- Growing ecosystem of specialized vendors and integrators

#### Market Evolution
- Increased government support (security, supply chain diversity)
- Cloud provider entry (AWS, Microsoft, Google offering O-RAN services)
- Private network applications driving demand for flexible, cost-effective solutions

#### Key Success Factors
1. Performance parity: Achieving traditional RAN performance levels
2. Cost competitiveness: Realizing promised economic benefits
3. Ecosystem maturity: Robust multi-vendor integration capabilities
4. Standards stability: Converging on stable, interoperable specifications


## Open-RAN Architecture

### Core Components and Functions

#### Network Function Units
- O-RU (Radio Unit): RF processing, Low-PHY functions, digital beamforming, handles radio transmission/reception
- O-DU (Distributed Unit): High-PHY, MAC, RLC processing at network edge for real-time functions
- O-CU (Central Unit): Split into two planes:
- O-CU-CP (Control Plane): RRC, PDCP-C, connection management
- O-CU-UP (User Plane): SDAP, PDCP-U, user data traffic routing
- O-eNB: O-RAN enabled evolved NodeB for 4G/5G integration

#### Intelligence Layer
- Near-RT RIC (Near Real-Time RIC): 
- Control loop: ≥10ms to <1s
- Hosts xApps for network optimization
- Functions: load balancing, interference management, QoS control
- Non-RT RIC (Non-Real-Time RIC):
- Control loop: ≥1 second
- Hosts rApps for policy management
- Functions: AI/ML model training, network analytics, strategic guidance

#### Management and Orchestration
- SMO Framework: Service Management and Orchestration for centralized network management
- O-Cloud: Cloud infrastructure providing compute resources and storage

### Key Interfaces

#### 3GPP Standard Interfaces
- X2-c/X2-u: Inter-base station communication (control/user plane)
- NG-c/NG-u: 5G gNB to core network connection
- Xn-c/Xn-u: 5G NR inter-gNB interfaces

#### O-RAN Specific Interfaces
- A1: Non-RT RIC ↔ Near-RT RIC (policy distribution)
- E1: O-CU-CP ↔ O-CU-UP (control/user plane coordination)
- E2: Near-RT RIC ↔ RAN functions (real-time control)
- F1: O-CU ↔ O-DU connection
- F1-c: Control plane (O-CU-CP to O-DU)
- F1-u: User plane (O-CU-UP to O-DU)
- Open Fronthaul (FH): O-DU ↔ O-RU interface
- CUS-Plane: Control, User, Synchronization
- M-Plane: Management plane
- O1: SMO Framework ↔ Network functions (management)
- O2: SMO Framework ↔ O-Cloud (orchestration)

### Architecture Evolution

#### Traditional RAN → Open RAN Transformation
1. Legacy Model: Monolithic, vendor-locked base stations
2. Virtual RAN: COTS hardware + proprietary software
3. Open RAN: COTS hardware + open interfaces + standardized software

#### Functional Split Options (3GPP 38.801)
- Option 1-8: Different protocol layer split points
- Most common: Option 7 (PHY split) and Option 2 (PDCP/RRC split)
- Option 7.2x: Enhanced fronthaul split variant

### Control Loop Hierarchy

#### Three-Tier Control Structure
1. SMO Level (≥1s): Policy, inventory, configuration management
2. Near-RT RIC (≥10ms, <1s): Real-time optimization, xApp execution
3. O-DU Level (<10ms): Physical layer real-time processing

### Deployment Models

#### Near-RT RIC Deployment Options
- Type 1: 5G only (O-CU-CP/UP, O-DU)
- Type 2: 4G+5G hybrid (O-eNB + 5G functions)
- Type 3: 4G only (O-eNB)
- Distributed: Multiple logical RICs on single physical platform

#### Cloud-Native Architecture
- Containerized Functions: VNFs/CNFs deployment
- Hardware Abstraction: AAL (Acceleration Abstraction Layer)
- Multi-vendor Support: x86, FPGA, GPU, ASIC compatibility

### Applications and Intelligence

#### xApps (Near-RT RIC Applications)
- Radio connection management
- Mobility management
- QoS optimization
- Interference coordination
- Real-time network optimization

#### rApps (Non-RT RIC Applications)
- Policy management
- Network analytics
- AI/ML model development
- Long-term optimization strategies

### Benefits and Capabilities

#### Technical Advantages
- Vendor Interoperability: Multi-vendor RAN deployments
- Flexibility: Software-defined network functions
- Intelligence: AI/ML-driven optimization
- Cost Reduction: COTS hardware utilization
- Innovation: Open ecosystem for development

#### Operational Benefits
- Automated network optimization
- Improved resource utilization
- Reduced operational complexity
- Enhanced network performance
- Future-proof architecture

## O-RAN Split

### Split Philosophy and Options

#### Core Concept
- Goal: Disaggregate monolithic RAN into modular building blocks with open interfaces
- Challenge: Balance between ideal granular splits vs. practical implementation complexity
- Industry Focus: Three major functional blocks (CU, DU, RU) instead of 8 possible layer splits

#### 3GPP Split Options (Options 1-8)
Protocol stack can be split at different layers:
- Option 1: Above PDCP (minimal split)
- Option 2: PDCP/RRC split (F1 interface)
- Option 3: High RLC split
- Option 4: Low RLC split
- Option 5: High MAC split
- Option 6: Low MAC split
- Option 7: High PHY split (most popular)
- Option 8: Low PHY split (maximum disaggregation)

#### Popular Split Variants
- Option 7.2x: Enhanced 3GPP-based split between High PHY and Low PHY
- eCPRI Splits: D, ID, HD, E, IU splits defined by eCPRI specification
- O-RAN FH: O-RAN Alliance specific fronthaul split

### Link Types and Latency Requirements

#### Transport Links
- Backhaul: CU to core network
- Midhaul: CU to DU connection
- Fronthaul: DU to RU connection

### Bandwidth Characteristics

#### Downlink/Uplink Bandwidth Impact
- Higher splits (1-3): Low bandwidth requirements
- Mid-level splits (4-6): Moderate bandwidth needs
- Lower splits (7-8): High bandwidth requirements
- Option 7.2x: Balanced bandwidth (~25 Gbps max)

### Benefits of Option 7.2x

#### Technical Advantages
- Optimal Balance: Between centralization and RU complexity
- Manageable Bandwidth: Fronthaul data rate ≤25 Gbps
- Relaxed Latency: Less stringent than Option 8 requirements
- Simple Interface: Open protocol enabling multi-vendor integration
- Bandwidth Formula: (IQsize × nLayers × nSubcarriers) / symTime

#### Implementation Benefits
- RU Simplification: Compared to higher splits (2, 6)
- Centralized Processing: Most L1/L2/L3 functions in DU
- Antenna Independence: Bandwidth doesn't scale with physical antennas
- Vendor Flexibility: Easy DU-RU vendor mixing

#### Functional Distribution in 7.2x
- RU Functions:
  - Low PHY: FFT/IFFT, PRACH, Cyclic Prefix
  - RF: DAC/ADC, filtering, amplification
  - Digital beamforming and precoding
- DU Functions:
  - High PHY: Coding, rate matching, scrambling, modulation
  - MAC: Resource allocation, HARQ
  - RLC: Segmentation, ARQ
- CU Functions:
  - PDCP: Compression, ciphering, header compression
  - RRC/SDAP: Connection management, QoS handling

### Trade-offs and Considerations

#### Cost Factors
- Development: Additional interfaces require extra development investment
- Hardware: More splits may need separate hardware components
- Testing: Interoperability verification costs increase with splits

#### Performance Impact
- Centralization vs. Latency: Higher splits enable centralization but increase latency
- Bandwidth vs. Flexibility: Lower splits need more bandwidth but offer greater flexibility
- COMP Effect: Coordinated Multi-Point benefits decrease with higher splits

#### Industry Consensus
- Option 7.2x: Emerging as the standard for DU-RU separation
- Multi-vendor Support: Widest ecosystem support and interoperability testing
- Future Evolution: Potential for dynamic split selection based on network conditions
