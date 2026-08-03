---
title: WiFi & O-RAN Integration Study Notes

---

# WiFi & O-RAN Integration Study Notes

## Table of Contents

- [WiFi \& O-RAN Integration Study Notes](#wifi--o-ran-integration-study-notes)
  - [Table of Contents](#table-of-contents)
  - [1. WiFi Architecture Foundation](#1-wifi-architecture-foundation)
    - [1.1 WiFi Design Overview](#11-wifi-design-overview)
    - [1.2 WiFi Network Components](#12-wifi-network-components)
      - [Access Points (APs)](#access-points-aps)
      - [Wireless Controllers (WLC)](#wireless-controllers-wlc)
      - [Authentication Systems](#authentication-systems)
    - [1.3 WiFi Protocol Stack \& Operations](#13-wifi-protocol-stack--operations)
      - [Physical Layer (PHY)](#physical-layer-phy)
      - [MAC Layer Operations](#mac-layer-operations)
      - [Association and Authentication Process](#association-and-authentication-process)
      - [Quality of Service (QoS) - WMM](#quality-of-service-qos---wmm)
      - [Roaming and Handoff Mechanisms](#roaming-and-handoff-mechanisms)
  - [2. O-RAN \& 3GPP Fundamentals](#2-o-ran--3gpp-fundamentals)
    - [2.1 Overview](#21-overview)
    - [2.2 3GPP Standards Overview](#22-3gpp-standards-overview)
    - [2.3 O-RAN Architecture Components](#23-o-ran-architecture-components)
  - [3. Component Mapping \& Comparison](#3-component-mapping--comparison)
    - [3.1 Access Layer Comparison](#31-access-layer-comparison)
    - [3.2 Control and Management Layer](#32-control-and-management-layer)
    - [3.3 Core Functions Mapping](#33-core-functions-mapping)
  - [4. WiFi-O-RAN Integration Scenarios](#4-wifi-o-ran-integration-scenarios)
    - [4.1 Convergence Architectures](#41-convergence-architectures)
    - [4.2 Interworking Standards](#42-interworking-standards)
    - [4.3 Network Slicing Integration](#43-network-slicing-integration)
  - [5. Technical Deep Dives](#5-technical-deep-dives)
    - [5.1 Authentication Flow Comparison](#51-authentication-flow-comparison)
    - [5.2 Mobility Procedures](#52-mobility-procedures)
    - [5.3 QoS and Traffic Management](#53-qos-and-traffic-management)
  - [6. Practical Implementation](#6-practical-implementation)
    - [6.1 Common Integration Use Cases](#61-common-integration-use-cases)
    - [6.2 Challenges and Solutions](#62-challenges-and-solutions)

---

## 1. WiFi Architecture Foundation

![Architecture of a WiFi Network](https://hackmd.io/_uploads/ryU00pxtlx.png)

### 1.1 WiFi Design Overview

**Definition**

WiFi (Wireless Fidelity) is a family of wireless network protocols based on the IEEE 802.11 formula that enables devices to connect and communicate over wireless local area networks (WLANs). WiFi was originally developed in the late 1990s to provide wireless connectivity in local environments, later evolving into a fundamental technology that powers internet connectivity for various general purposes.

The core use of WiFi is to eliminate the need for physical cables while maintaining reliable, high-speed data transmission. It operates in unlicensed spectrum bands, primarily 2.4 GHz, 5 GHz, and more recently expanding to 6 GHz, making it accessible for widespread deployment without requiring authorized spectrum licenses.

**Historical Evolution**

![WiFi Standards Evolution](https://hackmd.io/_uploads/B1euJRgYle.png)

The improvement from 802.11 legacy to modern WiFi 7 represents a significant advancement in wireless technology. The original 802.11 standard from 1997 provided just 2 Mbps throughput, which became insufficient as internet usage grew.

802.11a and 802.11g in the early 2000s brought speeds up to 54 Mbps and introduced concepts like OFDM (Orthogonal Frequency Division Multiplexing) that remain fundamental today. The breakthrough came with 802.11n (WiFi 4) in 2009, which introduced MIMO (Multiple-Input Multiple-Output) technology, enabling speeds up to 600 Mbps and significantly improving coverage.

WiFi 5 (802.11ac) focused on the 5 GHz band with wider channels and more spatial streams, reaching multi-gigabit speeds. WiFi 6 (802.11ax) brought revolutionary efficiency improvements through OFDMA and improved handling of dense environments. WiFi 6E extended into the 6 GHz band, providing much-needed spectrum relief. The upcoming WiFi 7 promises even higher speeds and lower latency through advanced features like multi-link operation.

**WiFi in Modern Networks**

![wifi-ecosystem-diagram](https://hackmd.io/_uploads/Bk5zygbKee.png)

In today's connectivity landscape, WiFi serves as the critical access technology for most daily environments. It handles the majority of smartphone data traffic, even in areas with great cellular coverage, because of its superior speed and lack of data caps. Enterprise networks rely on WiFi for employee mobility, visitor access, and increasingly for IoT device connectivity.

WiFi is essential for digital transformation initiatives, enabling flexible work arrangements and supporting new applications like augmented reality, real-time collaboration tools, and cloud-based services that demand high bandwidth and low latency. WiFi remains irreplacable even today for providing high-capacity access in dense indoor environments where cellular signals struggle to penetrate.

### 1.2 WiFi Network Components

#### Access Points (APs)

Access Points act as the bridge between wireless devices and the wired network infrastructure. They function as both radio transceivers and network switches, managing the complex task of coordinating multiple wireless devices while maintaining connections to the broader network.

**Functionality and Role**

An AP continuously broadcasts beacon frames that advertise the network's presence and capabilities. When devices want to connect, the AP manages the association process, authenticates users, and assigns network resources. It handles the translation between the wireless 802.11 protocol and standard Ethernet frames, which enables communication between wireless and wired devices.

Modern APs also perform sophisticated radio management functions, automatically adjusting transmit power and channel selection to optimize coverage and minimize interference. They maintain detailed statistics about connected devices, signal quality, and traffic patterns, providing valuable data for network optimization.

**Types of Access Points**

![csg29-01-access-point](https://hackmd.io/_uploads/Sk8obgWFlg.png)

**Standalone APs** operate independently with all intelligence built into each unit. They're more suitable for small deployments but become difficult to manage at scale because each AP requires individual configuration and monitoring.

**Controller-based APs** (or lightweight APs) depend on wireless controllers for most intelligence. The controller handles configuration, security policies, and advanced features while APs focus primarily on radio functions. This centralized approach simplifies management of large deployments and enables advanced features like seamless roaming and load balancing.

**Cloud-managed APs** represent the modern evolution, combining local intelligence with cloud-based management. They can operate independently if needed but receive configuration, updates, and monitoring through cloud services, offering the scalability benefits of centralized management with better resilience.

#### Wireless Controllers (WLC)

Wireless Controllers serve as the brains of enterprise WiFi networks, able in centralized management and advanced functionality that individual APs cannot deliver on their own.

**Centralized Management**

Controllers aggregate management of hundreds or thousands of APs through a single interface. Administrators can configure network policies, security settings, and operational parameters across the entire wireless infrastructure from one location. This centralization dramatically reduces the complexity of managing large wireless deployments and ensures consistent configuration across all sites.

Controllers also provide unified monitoring and troubleshooting capabilities, collecting performance data from all connected APs and presenting it through comprehensive dashboards and reporting tools.

**Policy Enforcement**

WLCs can implement and enforce security policies consistently across the wireless network. They handle tasks like user authentication, authorization, and accounting (AAA), ensuring that security policies apply uniformly regardless of which AP a user connects through. Controllers can implement role-based access controls, bandwidth limitations, and application-specific policies.

Traffic filtering and quality of service (QoS) policies are also enforced at the controller level, enabling sophisticated traffic management that considers both user requirements and overall network capacity.

**Load Balancing**

Controllers continuously monitor the load on individual APs and can implement various load balancing strategies. They might direct new clients to less congested APs or adjust transmit power to influence client roaming decisions (less populated streaming bands and such).

Advanced controllers can also coordinate between multiple sites, sharing load information and user context to optimize performance across distributed deployments.

#### Authentication Systems

![Auth Flow](https://hackmd.io/_uploads/HkJ6fe-Kxg.png)

**802.1X/EAP Frameworks**

The 802.1X standard provides port-based network access control for WiFi networks, creating a framework where devices must authenticate before gaining network access. The Extensible Authentication Protocol (EAP) works within this framework to support various authentication methods.

EAP enables different authentication mechanisms including certificate-based authentication (EAP-TLS), username/password with protected tunnels (EAP-TTLS, PEAP), and newer methods like EAP-PWD for password-based authentication without certificates.

This framework ensures that only authorized users and devices can access the network while providing flexibility in authentication methods to match organizational security policies and user device capabilities.

**RADIUS/AAA Servers**

RADIUS (Remote Authentication Dial-In User Service) servers provide the authentication, authorization, and accounting services that make enterprise WiFi security possible. When a device attempts to connect, the access point forwards authentication requests to the RADIUS server, which verifies credentials and returns authorization information.

AAA servers maintain user databases, apply security policies, and log access attempts for auditing purposes. They can integrate with existing directory services like Active Directory, LDAP, or cloud identity providers, enabling single sign-on capabilities and centralized user management.

### 1.3 WiFi Protocol Stack & Operations

![Protocol Stack](https://hackmd.io/_uploads/Hkvwmlbtge.png)


#### Physical Layer (PHY)

The Physical Layer handles the actual radio transmission and reception, converting digital data into radio waves and back. Modern WiFi uses sophisticated modulation techniques like QAM (Quadrature Amplitude Modulation) to pack more data into each transmission.

Key PHY features include MIMO technology that uses multiple antennas to increase capacity and improve reliability, channel bonding that combines adjacent frequency channels for higher speeds, and beamforming that focuses radio energy toward specific devices to improve signal quality and reduce interference.

The PHY layer also implements automatic rate adaptation, constantly adjusting modulation schemes and coding rates based on current channel conditions to maintain the best possible performance.

#### MAC Layer Operations

The Media Access Control layer coordinates how multiple devices share the wireless medium. WiFi uses CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance) as its fundamental access method, where devices listen before transmitting and use random backoff timers to avoid collisions.

Modern WiFi has evolved beyond basic CSMA/CA with features like OFDMA (Orthogonal Frequency Division Multiple Access) in WiFi 6, which allows multiple devices to transmit simultaneously on different frequency sub-carriers, dramatically improving efficiency in dense environments.

#### Association and Authentication Process

The connection process involves several distinct phases: scanning (where devices discover available networks), authentication (proving identity), association (establishing a connection), and finally key exchange for secure communication.

This process must balance security requirements with user experience, ensuring robust authentication while minimizing connection time. Modern enhancements like 802.11r enable fast roaming between access points without repeating the full authentication process.

#### Quality of Service (QoS) - WMM

WiFi Multimedia (WMM) implements quality of service by categorizing traffic into different access categories with varying priorities. Voice traffic gets the highest priority with minimal delay, video receives high bandwidth allocation, best effort handles normal data, and background traffic gets lowest priority.

These priorities affect how devices contend for channel access, with higher priority traffic using shorter wait times and more aggressive retry mechanisms to ensure timely delivery.

#### Roaming and Handoff Mechanisms

WiFi roaming enables seamless connectivity as users move between access points. The process involves continuous signal monitoring, handoff decision making based on signal strength and load conditions, and rapid reassociation with new access points.

Standards like 802.11k (neighbor reporting), 802.11v (network management), and 802.11r (fast roaming) work together to optimize roaming performance, reducing connection interruptions and improving user experience in mobile scenarios.

## 2. O-RAN & 3GPP Fundamentals

![O-RAN-components-of-mobile-network-R2](https://hackmd.io/_uploads/BJhb4gZYge.jpg)
### 2.1 Overview

**Open Radio Access Network Concept**

O-RAN is a paradigm shift toward open, interoperable, and intelligent radio access networks. Unlike traditional proprietary RAN solutions where hardware and software are tightly integrated from single vendors, O-RAN disaggregates network functions and introduces standardized interfaces between components.

**Key Principles**

The foundation rests on three core principles: **Openness** through standardized interfaces enabling multi-vendor interoperability, **Intelligence** via AI/ML-driven optimization and automation, and **Virtualization** allowing software-defined network functions to run on commercial off-the-shelf hardware.

### 2.2 3GPP Standards Overview

**3GPP Organization and Role**

The 3rd Generation Partnership Project defines global standards for mobile telecommunications, evolving from 2G GSM through current 5G New Radio specifications. 3GPP Release 15/16/17 specifications form the technical foundation for 5G networks worldwide.

**5G NR (New Radio) Architecture**

5G New Radio introduces flexible numerology, massive MIMO, and millimeter wave support. The architecture separates user plane and control plane functions, enabling distributed deployment models and network slicing capabilities.

**Core Network Evolution (4G EPC → 5G Core)**

![5G Core](https://hackmd.io/_uploads/Skr14lbKgx.png)

The evolution from 4G's Evolved Packet Core to 5G's Service-Based Architecture is a shift toward cloud-native, microservices-based network functions. Key improvements include network slicing support, enhanced mobile broadband capabilities, and ultra-low latency services.

### 2.3 O-RAN Architecture Components

![o-ran-architecture](https://hackmd.io/_uploads/BJ2qmxbKxx.png)

**Radio Unit (RU)**

The RU handles radio frequency functions including digital signal processing, beamforming, and antenna interface. It connects to Distributed Units via fronthaul interfaces with strict latency requirements.

**Distributed Unit (DU)**

DUs process real-time Layer 1/2 functions including physical layer processing and MAC scheduling. They require low-latency connections to RUs and handle time-critical radio operations.

**Centralized Unit (CU)**

CUs manage non-real-time Layer 2/3 protocols including RRC, PDCP, and SDAP functions. This functional split enables flexible deployment models from fully centralized to fully distributed configurations.

**RAN Intelligent Controller (RIC)**

The RIC provides AI/ML-driven optimization through two components: Near-Real-Time RIC for sub-second control loops and Non-Real-Time RIC for longer-term policy and analytics. xApps and rApps implement specific optimization algorithms.

**Service Management and Orchestration (SMO)**

SMO orchestrates the entire O-RAN ecosystem, managing lifecycle operations, configuration, and integration with broader network management systems. It provides the northbound interface for OSS/BSS integration.

## 3. Component Mapping & Comparison

### 3.1 Access Layer Comparison

| WiFi Component | O-RAN/3GPP Equivalent | Key Similarities | Key Differences |
|---|---|---|---|
| Access Point (AP) | gNB/eNB (Base Station) | Radio access provision, device connectivity | Licensed vs unlicensed spectrum, mobility scope, protocol complexity |
| WiFi Radio | Radio Unit (RU) | RF transmission, antenna interface | Frequency bands (2.4/5/6 GHz vs sub-6/mmWave), power levels, beamforming sophistication |

**Access Point vs gNB/Base Station**

Both WiFi Access Points and 5G base stations serve as core equipment providing wireless coverage and signal transmission between wired networks and wireless terminals. However, access points create wireless local area networks (WLANs) usually in offices or buildings, connecting via Ethernet to wired infrastructure, while gNB base stations provide wide-area coverage with licensed spectrum and sophisticated mobility management.

WiFi APs typically serve dozens of devices within a building, while base stations can serve thousands of devices across several kilometers. The complexity differs significantly - WiFi uses simple association procedures while 5G involves complex registration, authentication, and session management processes.

**WiFi Radio vs Radio Unit**

Both handle the fundamental RF transmission tasks, but gNodeB systems enhance speed and capacity with features like massive MIMO and ultra-low latency that exceed typical WiFi capabilities. WiFi radios operate in unlicensed bands with relatively simple antenna configurations, while O-RAN RUs support advanced beamforming, carrier aggregation, and millimeter wave frequencies requiring sophisticated RF processing.

### 3.2 Control and Management Layer

| WiFi Component | O-RAN/3GPP Equivalent | Comparison Notes |
|---|---|---|
| Wireless Controller | RAN Intelligent Controller (RIC) | Both provide centralized network optimization, but RIC adds AI/ML capabilities |
| Captive Portal | UPF + AMF functions | Authentication gateways with different complexity levels |
| RADIUS/AAA | 5G AAA/AUSF | Network access authentication with varying security frameworks |

**Wireless Controller vs RIC**

Traditional WiFi controllers focus on configuration management, policy enforcement, and basic load balancing across access points. The RAN Intelligent Controller (RIC) is a software-defined component responsible for controlling and optimizing RAN functions through cloud software managing baseband communication.

The RIC provides functions via xApps that enable increased optimizations through policy-driven, closed loop automation. While WiFi controllers operate with predefined rules and manual optimization, RIC systems incorporate deep AI/ML knowledge and cloud-native, software-defined networking capabilities for autonomous network optimization.

**Captive Portal vs UPF + AMF**

WiFi captive portals provide simple web-based authentication and terms acceptance before internet access. The 5G equivalent involves User Plane Functions (UPF) handling traffic routing combined with Access and Mobility Management Functions (AMF) managing authentication and access control - a more distributed but sophisticated approach.

**RADIUS/AAA vs 5G AAA/AUSF**

WiFi networks typically use RADIUS servers for centralized authentication, authorization, and accounting. 5G networks employ Authentication Server Functions (AUSF) with more advanced security protocols, supporting network slicing, enhanced privacy protection, and integration with cloud identity systems.

### 3.3 Core Functions Mapping

**Authentication & Authorization**

WiFi employs 802.1X/EAP frameworks directing authentication requests to RADIUS servers, supporting various EAP methods from simple passwords to certificate-based security. This approach works well for enterprise environments with existing directory services.

O-RAN networks use 5G-AKA (Authentication and Key Agreement) protocols with AUSF (Authentication Server Function) and UDM (Unified Data Management) providing more sophisticated security. The 5G approach includes mutual authentication, enhanced privacy features, and support for different authentication vectors depending on device capabilities and network policies.

**Mobility Management**

WiFi roaming relies on 802.11r (fast roaming), 802.11k (neighbor reporting), and 802.11v (network management) standards to enable seamless handoffs between access points. The process is relatively simple but limited to same-network transitions.

O-RAN handover procedures are significantly more complex, supporting intra-frequency, inter-frequency, and inter-RAT handovers. The system maintains detailed user context, manages bearer continuity, and coordinates with core network functions to ensure service continuity across different cell types and coverage areas.

**Quality of Service**

WiFi QoS through WMM (WiFi Multimedia) and 802.11e provides four access categories with different priority levels for traffic differentiation. This approach works well for basic prioritization but lacks fine-grained control.

O-RAN implements QoS through network slicing combined with QoS flows, enabling much more sophisticated service differentiation. Different network slices can provide completely isolated service levels, while QoS flows allow per-application or per-user quality guarantees with guaranteed bit rates, maximum latency limits, and error rate requirements.

## 4. WiFi-O-RAN Integration Scenarios

![A-typical-example-of-5G-wireless-network-architecture](https://hackmd.io/_uploads/SJhfrxWtxe.png)

### 4.1 Convergence Architectures

**WiFi Offloading in 5G**

WiFi offloading has been around for many years, but becomes even more effective in 5G-driven networks. The strategy involves automatically switching data traffic from cellular networks to WiFi when available, reducing congestion on licensed spectrum while providing users with high-speed connectivity.

With 200 MHz of WiFi spectrum allocation in the 6 GHz band, surpassing what individual carriers possess for 4G or 5G - the indoor wireless capacity provided by cellular technologies falls notably short compared to 6 GHz WiFi potential. Modern offloading systems use intelligent algorithms that consider network congestion, signal quality, and application requirements to make optimal handoff decisions.

Enhanced congestion-aware WiFi offloading systems can obtain network status information and systematically consider network congestion rather than simply offloading as much traffic as possible to WiFi, improving overall network efficiency and user experience.

**Converged Access Points**

Converged access points bring forth the next evolution in wireless infrastructure, combining WiFi and cellular capabilities in single devices. These systems can simultaneously provide WiFi services and act as small cells for 5G networks, offering seamless connectivity experiences.

The convergence enables operators to deploy unified infrastructure that serves both licensed and unlicensed spectrum needs. Users benefit from automatic network selection, load balancing between technologies, and consistent service policies regardless of the access method.

**Unified Policy Management**

Integration scenarios require unified policy management systems that can coordinate between WiFi and cellular domains. These systems ensure consistent user experiences, security policies, and quality of service regardless of which network the device is currently using.

Policy engines can dynamically adjust bandwidth allocation, application priorities, and security parameters based on network conditions, user profiles, and service level agreements across both WiFi and cellular access methods.

### 4.2 Interworking Standards

**3GPP TS 23.402 (Non-3GPP Access)**

3GPP TS 23.402 specifies the stage 2 service description for providing IP connectivity using non-3GPP accesses to the Evolved 3GPP Packet Switched domain. This standard defines how WiFi and other non-cellular technologies can integrate with 3GPP core networks.

The specification covers interworking of untrusted non-3GPP networks with 5G core networks, including the required interfaces, protocols, and procedures. It enables seamless authentication, billing, and policy enforcement across different access technologies.

The standard supports both trusted and untrusted non-3GPP access scenarios. Trusted access allows direct connection to the operator's core network, while untrusted access requires additional security measures like IPSec tunneling through evolved packet data gateways.

**WiFi-Cellular Aggregation**

Advanced integration scenarios support simultaneous use of WiFi and cellular connections for increased bandwidth and reliability. Link aggregation protocols can bond multiple connections, providing higher throughput than either technology alone.

Multi-path TCP and similar technologies enable applications to use both connections simultaneously, with intelligent load balancing based on current network conditions, latency requirements, and available bandwidth on each path.

**Seamless Authentication**

Modern interworking implementations support seamless authentication between WiFi and cellular networks. Smart phones and handheld devices equipped with multiple radio access technologies capabilities require advanced connection managers for interworking between 3GPP and non-3GPP networks.

Single sign-on mechanisms allow users to authenticate once and automatically gain access to both WiFi and cellular services. This reduces complexity for users while maintaining security through centralized identity management systems.

### 4.3 Network Slicing Integration

![5G-Network-Slicing](https://hackmd.io/_uploads/r1SWAeWYgx.jpg)

**WiFi as a Slice Access**

Network slicing extends beyond cellular networks to include WiFi as an access method for specific network slices. Different WiFi SSIDs can map to different network slices, enabling service differentiation at the access layer.

For example, an IoT slice might use dedicated WiFi infrastructure with optimized parameters for sensor traffic, while an enhanced mobile broadband slice provides high-speed access for multimedia applications. This approach ensures that WiFi access aligns with end-to-end service requirements.

**QoS Mapping Between Domains**

Integration requires sophisticated QoS mapping between WiFi and cellular domains. WiFi's WMM access categories must translate to appropriate 5G QoS flows and network slice parameters to maintain service quality across handoffs.

The mapping process considers application requirements, user profiles, and current network conditions to ensure consistent quality of service. Dynamic QoS adaptation can adjust parameters in real-time as users move between WiFi and cellular coverage areas.

Advanced implementations use machine learning algorithms to optimize QoS mapping based on historical performance data, user behavior patterns, and network utilization trends, continuously improving the integration effectiveness.

## 5. Technical Deep Dives

### 5.1 Authentication Flow Comparison

**WiFi 802.1X Flow**

![Untitled](https://hackmd.io/_uploads/SyqFClbFle.png)

IEEE 802.1X provides an authentication mechanism to devices wishing to attach to a LAN or WLAN, operating as a port-based network access control system. The authentication process involves three key entities: the supplicant (client device), authenticator (access point), and authentication server (RADIUS).

The flow begins when a client associates with an access point, which immediately places the port in an unauthorized state, blocking all traffic except 802.1X authentication frames. The supplicant sends an EAP-Start message, prompting the authenticator to request identity credentials. The authenticator forwards these credentials to the RADIUS server via EAP-over-RADIUS protocols.

802.1x EAP-TLS provides rapid, passwordless, certificate-based authentication for secure network access, while other methods like PEAP-MSCHAPv2 support password-based authentication within protected TLS tunnels. Upon successful authentication, the RADIUS server sends an Access-Accept message with configuration parameters, and the authenticator opens the port for normal traffic flow.

**5G Registration Procedure**

![5631.1712488788](https://hackmd.io/_uploads/S1ZsAebYeg.png)

The 5G registration procedure is significantly more complex, involving multiple network functions and sophisticated security protocols. The process starts with the UE performing cell search and system information acquisition, followed by RRC connection establishment with the gNodeB.

Initial registration involves mutual authentication using 5G-AKA (Authentication and Key Agreement) protocols. The UE sends a Registration Request via the Access and Mobility Management Function (AMF), which coordinates with the Authentication Server Function (AUSF) and Unified Data Management (UDM) for subscriber verification and security context establishment.

The procedure includes network slice selection, PDU session establishment, and policy enforcement through the Policy Control Function (PCF). Unlike WiFi's relatively simple credential exchange, 5G registration involves complex subscriber profile management, service authorization, and network slice configuration.

**Unified Authentication**

Integration scenarios require bridging these different authentication approaches. Modern implementations use identity federation protocols to enable single sign-on across WiFi and cellular domains. The Extensible Authentication Protocol (EAP) framework provides a common foundation, allowing both systems to support similar authentication methods.

Unified authentication systems typically maintain synchronized user databases and policy engines that can translate between 802.1X and 5G authentication contexts, ensuring consistent security postures regardless of access method.

### 5.2 Mobility Procedures

**WiFi Roaming Process**

WiFi roaming relies on client-driven decision making supported by network information provided through 802.11k (neighbor reporting), 802.11v (BSS transition management), and 802.11r (fast BSS transition) standards.

The process begins with continuous signal monitoring by the client device. When signal quality degrades below acceptable thresholds, the device initiates active scanning to discover alternative access points. 802.11k provides neighbor reports that help clients identify candidate APs without extensive scanning, reducing roaming latency.

802.11r enables fast roaming by pre-authenticating with target access points and establishing security associations before the actual handoff occurs. This reduces interruption time from hundreds of milliseconds to just a few milliseconds, supporting real-time applications like voice calls.

**5G Handover Process**

5G-NR cellular networks face serious challenges in mobility management due to dynamicity of user equipments, particularly with dense small cell deployments. 3GPP specification has defined different Intra system handovers, e.g. Xn Based Handover, N2 or NGAP Based Handover.

The 5G handover process is network-controlled, with the serving gNodeB making handover decisions based on measurement reports from the UE. The process involves measurement configuration, where the network instructs the UE which neighboring cells to monitor and report signal quality.

When handover criteria are met, the source gNodeB initiates the handover preparation phase, establishing resources at the target gNodeB and coordinating with core network functions to maintain service continuity. The UE then performs synchronization with the target cell and completes the handover by updating its location with the AMF.

**Inter-system Mobility**

Inter-system handovers between WiFi and 5G involve complex procedures where HSS provides SMF+PGW-C FQDN after authentication, and ePDG initiates GTPv2 create session request indicating handover toward PGW after IPSec tunnel establishment.

These procedures require coordination between different protocol stacks and network management systems. The handover process must maintain IP address continuity, transfer security contexts, and ensure quality of service parameters are properly mapped between domains.

### 5.3 QoS and Traffic Management

**WiFi QoS Mechanisms**

WiFi QoS implementation centers on the WiFi Multimedia (WMM) specification, which defines four Access Categories (ACs): Voice (AC_VO), Video (AC_VI), Best Effort (AC_BE), and Background (AC_BK). Each category uses different Enhanced Distributed Channel Access (EDCA) parameters including Arbitration Inter-Frame Space (AIFS), Contention Window sizes, and Transmission Opportunity (TXOP) limits.

Voice traffic receives the highest priority with shortest AIFS values and smallest contention windows, ensuring minimal delay for real-time communications. Video traffic gets moderate priority balancing latency and throughput requirements, while background traffic uses longer wait times and larger contention windows to avoid interfering with higher priority flows.

802.11e extends these capabilities with additional features like Automatic Power Save Delivery (APSD) for battery-powered devices and admission control mechanisms that can reject new traffic flows when network capacity is insufficient.

**5G QoS Framework**

The 5G QoS framework operates on a flow-based model where individual applications or services receive specific QoS treatment through QoS flows and network slices. Each QoS flow has associated parameters including 5G QoS Identifier (5QI), Guaranteed Flow Bit Rate (GFBR), Maximum Flow Bit Rate (MFBR), and packet delay budget.

Network slicing provides end-to-end service differentiation, creating isolated virtual networks with dedicated resources and optimized configurations for specific use cases. Enhanced Mobile Broadband (eMBB) slices prioritize throughput, Ultra-Reliable Low-Latency Communication (URLLC) slices minimize delay and maximize reliability, and Massive Machine-Type Communication (mMTC) slices optimize for device density and energy efficiency.

**End-to-end QoS Mapping**

Integration scenarios require sophisticated mapping between WiFi's access category model and 5G's flow-based QoS framework. This mapping process must consider application requirements, user service level agreements, and current network conditions to maintain consistent quality of service across technology boundaries.

Dynamic QoS adaptation mechanisms monitor network performance and automatically adjust mapping parameters to optimize user experience. Machine learning algorithms can analyze historical performance data to predict optimal QoS configurations for different traffic patterns and network conditions, continuously improving the effectiveness of cross-domain quality of service management.

## 6. Practical Implementation

### 6.1 Common Integration Use Cases

**Enterprise / College Networks**
Large enterprise deployments can benefit significantly from WiFi-5G integration, providing connectivity between buildings, outdoor areas, and remote locations. Unified policy management ensures consistent security and access controls across both technologies.

**Stadium/Venue Deployments**
High-density venues require both technologies to handle peak capacity demands. WiFi serves stationary users with high bandwidth needs while 5G handles mobile users and provides coverage in areas where WiFi deployment is impractical.

**Industrial IoT Scenarios**
Manufacturing environments use WiFi for high-bandwidth applications like video monitoring while 5G private networks handle mission-critical control systems requiring very low latency and high reliability.

### 6.2 Challenges and Solutions

**Spectrum Coordination**
Managing interference between WiFi and 5G in shared spectrum requires sophisticated coordination mechanisms and dynamic spectrum access protocols.

**Authentication Complexity**
Integrating different authentication frameworks increases complexity but can be addressed through identity federation and unified AAA systems.

**Performance Optimization**
Load balancing and intelligent traffic steering algorithms help optimize performance across both access methods based on real-time network conditions.

**Management Overhead**
Unified network management platforms reduce operational complexity by providing single-pane-of-glass visibility and control across both WiFi and cellular domains.