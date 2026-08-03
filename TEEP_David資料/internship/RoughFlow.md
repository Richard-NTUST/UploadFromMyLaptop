- Modify OAI repo for scheduling
- Build the image via jenkins.bmw.lab (Quay creds, bmw.ntust.edu.tw)
- From the HPE server, pull the image using Quay
- Build it using Helm in the CRAN -> templates directory
- OAI config tweaks (outside source code) can be done after building
- Check pod using K9s
- Connect to UE using Anydesk -> Turn off airplane mode to connect to 5G -> Note the IP using PingTest
- Iperf from server -> Start Magic Iperf from UE to enable the Iperf connections -> Note the numbers

---

Codex Context Here:

## Current Codex Context - 2026/06/30

### Current Goal

The main research direction is now back on WINLAB / Pegatron O-RU power saving:

1. Reproduce the existing E2E throughput-vs-RU-power baseline using the original OAI scheduler.
2. Confirm the measurement path through CortexDC / PDU.
3. Only after the baseline works, compare OAI scheduler variants such as original, time-domain, frequency-domain, or PRB-capped modes.

Do **not** start with scheduler source-code changes first. The immediate blocker is making the lab workflow runnable.

### Practical Next Step

Access first, baseline second, scheduler changes third.

Immediate checklist:

1. Fix or document AnyDesk access to the two UE machines.
2. Confirm which rApp/test case is the Pegatron RU baseline.
3. Confirm whether the baseline runs on Joule or Kepler.
4. Confirm the OAI image/config currently used for the known-good run.
5. Confirm the actual Pegatron RU power source in CortexDC/PDU.
6. Run a small baseline test and record throughput + power timestamps.

### UE Access Context

Someone showed AnyDesk access into two UE machines, but it was bugged yesterday.

Need to ask/record:

```text
UE1 AnyDesk ID:
UE2 AnyDesk ID:
Password / approval method:
VPN required before AnyDesk?:
Are UE machines powered on?:
OS / tool used on UE:
Expected UE IP after 5G attach:
How to start Magic iPerf / PingTest:
```

Suggested message:

```text
Yesterday the AnyDesk connection to the two UE machines was still bugged on my side.

Could you please confirm:
1. the AnyDesk IDs for UE1 and UE2,
2. whether I need VPN before connecting,
3. the correct access password / approval method,
4. whether the UE machines are currently powered on,
5. what command or app I should check after login?
```

### Direction Notes Already Created

Important files:

```text
docs/StudyNotes/2026-06-29_WINLAB_ORU_Power_Saving_Direction.md
docs/StudyNotes/2026-06-29_WINLAB_ORU_Experiment_Plan_and_OAI_Scheduler_Modes.md
docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md
docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md
```

What they contain:

- `2026-06-29_WINLAB_ORU_Power_Saving_Direction.md`: professor direction, milestones, collaborator questions for Ming and Chynna.
- `2026-06-29_WINLAB_ORU_Experiment_Plan_and_OAI_Scheduler_Modes.md`: baseline experiment matrix, OAI scheduler modes, CSV templates, logging fields.
- `2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md`: VPN, BMW account, Jenkins credentials, OAI image build/push workflow.
- `2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md`: HPE server, Helm deployment, `values.yaml`, `configmap.yaml`, OAI frequency/TDD theory.

### CortexDC / PDU Context

New files:

```text
Conversation.md
CortexDC_Data_Inventory_Workbook.xlsx
```

Their importance:

- `Conversation.md` says Chen/Chynna shared a completed CortexDC report/workbook.
- Ray asked for the data to be organized into Word tables.
- PDU is Raritan `PX4-5256CR-C8E8A0`.
- PDU has 12 outlets, 8 currently occupied: outlets 4, 5, 6, 8, 9, 10, 11, 12.
- CortexDC currently tracks 13 servers, 1 PDU, and 1 network device.
- About 9 servers provide usable Redfish telemetry.
- **Important caveat:** there is currently no RU information recorded in CortexDC Assets.

Relevant workbook findings:

```text
Joule:
- Dell PowerEdge R750
- IP: 192.168.8.222
- Online
- Redfish data: Yes
- Redfish server-level power: Yes
- PDU mapped: Yes
- PDU outlet: Outlet 12
- Research usability: High

Kepler:
- Dell PowerEdge R750
- IP: 192.168.10.123
- Online
- Redfish data: Yes
- Redfish server-level power: Yes
- Node Exporter data: Yes
- PDU mapped: Yes
- PDU outlet: Outlet 6
- Research usability: High
```

Meaning:

- The workbook helps identify server-side telemetry and PDU outlet mapping.
- It does **not** yet identify the Pegatron O-RU power outlet/source.
- Need to ask which CortexDC asset or PDU outlet corresponds to the Pegatron O-RU.

Suggested CortexDC question:

```text
For the Pegatron O-RU power experiment, which CortexDC asset or PDU outlet corresponds to the O-RU itself?
Can CortexDC export timestamped active power for that outlet?
What file format should I use for the export?
```

### July 6 Update - Ravi / Chynna PDU Mapping

New corrected study note:

```text
docs/StudyNotes/2026-07-06_Pegatron_RU_CortexDC_Power_Mapping.md
```

Ravi confirmed the PDU schedule labels:

```text
Outlet 1: Pegatron RU [N], OC/DU testing
Outlet 2: Pegatron RU [O], OCloud testing
Outlet 11: Lavoisier, [O-Cloud] OAI NFAPI (PNF), OAI Split 7.2 gNB + Commercial RU
```

Ravi also said:

```text
CortexDC can't show RU data yet.
Do you use New Pegatron RU? -> Pegatron RU 1450.
Check if Pegatron RU supports Redfish.
```

Updated interpretation:

- Outlet 2 is a candidate only if the current OCloud/nFAPI run uses Pegatron RU [O].
- Outlet 11 is mapped to Lavoisier in Chynna's workbook, so treat it as server-side power unless physical wiring proves it is RU-only.
- CortexDC does not currently expose RU assets.
- InfluxDB likely has `outlet1` through `outlet12`, but mapping/export must be verified.
- Near-term path: use PDU/InfluxDB `active_power`, not CortexDC RU telemetry.

Chynna-related files checked:

```text
CortexConversation.md (currently deleted in worktree, read from git)
CortexDC_Data_Inventory_Workbook.xlsx
docs/MeetingNotes/2026-07-01_CortexDC-Pegatron-ORU-Power-Mapping.md
```

Do not claim final baseline power until this tuple is known:

```text
active RU identity
PDU outlet number
InfluxDB/CortexDC measurement name
power field, e.g. active_power
timestamp basis
sampling interval
iperf/rApp start and end time
```

### OAI Configuration Theory Summary

Clean mental model:

```text
Jenkins decides the code/image.
Helm decides what Kubernetes deploys.
OAI config decides what cell the gNB creates.
TDD/frequency/bandwidth decide radio behavior.
Scheduler decides how PRBs are used.
RU power depends on when the RU must transmit or receive.
```

Key OAI config concepts:

- `values.yaml`: deployment-level settings such as image tag, resources, node placement, AMF/core address, and sometimes chart variables.
- `templates/configmap.yaml`: renders the actual OAI `.conf` file mounted into the pod.
- `dl_frequencyBand = 78`: NR band n78.
- `absoluteFrequencySSB`: SSB/sync beacon ARFCN. UE needs this to find the cell.
- `dl_absoluteFrequencyPointA`: Point A / common resource block grid anchor.
- `3D1S1U`: TDD pattern: 3 downlink slots, 1 special slot, 1 uplink slot.

Raw values seen:

```text
TDD Pattern: 3D1S1U
absoluteFrequencySSB: 649920
dl_frequencyBand: 78
dl_absoluteFrequencyPointA: 646724
```

Approximate frequency conversion:

```text
absoluteFrequencySSB 649920 -> about 3748.8 MHz
dl_absoluteFrequencyPointA 646724 -> about 3700.86 MHz
```

### MIB / SIB and O-RAN Planes Summary

MIB/SIB:

```text
UE searches SSB
-> decodes PBCH
-> gets MIB
-> MIB points UE to SIB1
-> SIB1 tells UE how to access the cell
-> UE performs random access and registration
```

MIB = minimal cell info needed to find SIB1.

SIB1 = access/network information such as PLMN, TAC, cell access rules, random access config, and initial BWP.

C/U/S/M planes:

```text
M-plane = configure/manage RU
S-plane = synchronize RU/DU timing
C-plane = tell RU what radio resources to use
U-plane = actual IQ sample data
```

Scheduler changes affect RU power through C-plane allocation patterns and U-plane IQ activity.

### Logging Context

New format file:

```text
Log_Template.md
```

New log file started:

```text
New-Daily-Logs.md
```

Recommendation:

- Keep one growing `New-Daily-Logs.md`.
- Append one new Daily Note section per working day.
- Do not make a separate daily file unless professor explicitly asks.

### Current Working Tree Context

Most recent known untracked/new files:

```text
Conversation.md
CortexDC_Data_Inventory_Workbook.xlsx
Log_Template.md
New-Daily-Logs.md
RawDualNote.md
RoughFlow.md
docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md
docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md
image.png
```

Before committing, inspect `image.png` to decide whether it belongs in the repo.

Possible checkpoint commit later:

```bash
git add Conversation.md CortexDC_Data_Inventory_Workbook.xlsx Log_Template.md New-Daily-Logs.md RawDualNote.md RoughFlow.md \
  docs/StudyNotes/2026-06-30_BMW-Jenkins-OAI-Image-Build-Workflow.md \
  docs/StudyNotes/2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md

git commit -m "Add WINLAB workflow notes and CortexDC context"
```

### If Resuming Later

Start by running:

```bash
git status --short
sed -n '1,260p' RoughFlow.md
sed -n '1,220p' New-Daily-Logs.md
```

Then continue from:

```text
Fix UE AnyDesk access -> confirm baseline rApp/test path -> confirm Pegatron RU PDU/CortexDC power source.
```
