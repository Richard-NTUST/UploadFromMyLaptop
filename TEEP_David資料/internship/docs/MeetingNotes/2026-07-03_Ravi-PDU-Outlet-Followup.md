# Meeting Notes

## Meeting Information

| Item | Description |
| ---- | ----------- |
| Date | 2026/07/03 |
| Participants | David, Ravi / Chynna / Ming follow-up |
| Topic | Pegatron O-RU PDU outlet confirmation for WINLAB OCloud throughput-vs-power experiment |

---

## 1. Purpose

Confirm the physical and data-source mapping for the Pegatron O-RU power trace used by the current WINLAB OAI nFAPI / OCloud E2E workflow.

This is the remaining blocker before any throughput-vs-power plot can be treated as final baseline evidence.

Update after Ravi reply:

```text
CortexDC cannot show RU data yet.
Outlet 1 = Pegatron RU [N], OC/DU testing.
Outlet 2 = Pegatron RU [O], OCloud testing.
Outlet 11 = Lavoisier, [O-Cloud] OAI NFAPI (PNF), OAI Split 7.2 gNB + Commercial RU.
```

Therefore, for the current OCloud E2E throughput-vs-power workflow, use Outlet 2 as the Pegatron O-RU power outlet. Outlet 11 is not RU-only power.

---

## 2. Current Technical State

The HPE-side OCloud workflow is ready to produce timestamped traffic windows.

Verified on HPE:

| Item | Evidence |
| ---- | -------- |
| rApp API health | `{"status":"ok","version":"0.1.0","exec_mode":"local","ssh_target":null}` |
| OCloud VNF/PNF Helm releases | `vnf` and `pnf` deployed in `ming-ns` |
| OCloud pods | `oai-vnf` and `oai-pnf-pegatron` both `1/1 Running` on `lavoisier` |
| NetworkAttachmentDefinitions | `oai-pnf-pegatron-nfapi`, `oai-pnf-pegatron-ru-cplane`, `oai-pnf-pegatron-ru-uplane`, `oai-vnf-n2`, `oai-vnf-nfapi` present |
| Safe dry workflow artifact | `/home/hpe/winlab_e2e_rapp/runs/workflow-ocloud-dry-20260703-073208/` |
| CortexDC workbook clue | `CortexDC_Data_Inventory_Workbook.xlsx`, sheet `Sever 基本資料`, maps `Lavoisier` to `Outlet 11` |
| Ravi outlet confirmation | Outlet 2 is Pegatron RU `[O]`, OCloud testing; CortexDC cannot show RU data yet |

The verified dry workflow created:

```text
workflow_summary.json
status_snapshot/run_report.md
probe/run_report.md
```

The dry workflow is safe by default and does not start traffic unless `--live` is explicitly added.

---

## 3. Candidate PDU Outlets

Confirmed outlet mapping from Ravi:

| Candidate Outlet | Label / Meaning | Current Interpretation |
| ---------------- | --------------- | ---------------------- |
| Outlet 1 | Pegatron RU [N], OC/DU testing | Not the current OCloud E2E path |
| Outlet 2 | Pegatron RU [O], OCloud testing | Correct outlet for current OCloud Pegatron O-RU power |
| Outlet 11 | Lavoisier, [O-Cloud] OAI NFAPI (PNF), OAI Split 7.2 gNB + Commercial RU | Host/PNF-side power, not RU-only power |

Additional workbook evidence:

```text
CortexDC_Data_Inventory_Workbook.xlsx
Sheet: Sever 基本資料
Row: Lavoisier
PDU Name: PDU [Raritan] PX4-5256CR-C8E8A0
PDU Relationship: Yes
PDU Outlet: Outlet 11
```

The same workbook's server table shows mapped server outlets as `4`, `5`, `6`, `8`, `9`, `10`, `11`, and `12`. It does not resolve Outlet 1 or Outlet 2 in the server mapping table. Ravi's reply resolves that physical mapping for the current OCloud test: use Outlet 2.

---

## 4. What We Need Confirmed

| Question | Needed Answer |
| -------- | ------------- |
| Which physical PDU outlet powers the Pegatron O-RU used by the current OAI nFAPI / OCloud test? | Confirmed: Outlet 2 |
| Is the right trace `outlet2`, `outlet11`, or another outlet? | Use `outlet2` if Influx labels match outlet numbers |
| Is Outlet 11 Lavoisier/PNF host power rather than RU-only power? | Confirmed by Ravi's schedule and CortexDC workbook evidence |
| Can we export timestamped `active_power` for Outlet 2? | Still needed; CortexDC cannot show RU data yet, so use Influx/PDU/manual export if available |
| What timestamp basis should be used? | UTC preferred; otherwise Asia/Taipei with UTC+8 conversion noted |
| What is the sampling interval? | Seconds per sample or query cadence |

---

## 5. Commands Ready for a Marked Test Window

Safe dry workflow:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_power_workflow.py \
  --mode ocloud \
  --bandwidth 100 \
  --period 30 \
  --gap-time 2 \
  --ue-model samsung \
  --settle-time 45 \
  --attach-timeout 240
```

Live marked OCloud workflow, only when lab state and outlet collection are ready:

```bash
cd /home/hpe/winlab_e2e_rapp
python3 scripts/run_winlab_power_workflow.py \
  --mode ocloud \
  --bandwidth 100 \
  --period 300 \
  --gap-time 2 \
  --ue-model samsung \
  --settle-time 45 \
  --attach-timeout 240 \
  --live
```

If InfluxDB or direct PDU access is available, set the export variables before the live run:

```bash
export INFLUX_URL="http://<host>:8086"
export INFLUX_TOKEN="<token>"
export INFLUX_ORG="<org>"
export INFLUX_BUCKET="<bucket>"
export INFLUX_FIELD="active_power"
export INFLUX_OUTLET_COLUMN="outlet"
```

If measurements are stored as measurement names like `outlet1`, `outlet2`, etc.:

```bash
export INFLUX_OUTLET_COLUMN="_measurement"
```

---

## 6. Evidence Workflow

The HPE helper chain is now:

| Step | Script | Purpose |
| ---- | ------ | ------- |
| 1 | `collect_winlab_status_snapshot.py` | Read-only pre-test health snapshot |
| 2 | `run_winlab_ocloud_power_probe.py` | Marked rApp test window and optional Influx export |
| 3 | `summarize_winlab_outlet_power.py` | Candidate outlet power summary from exported CSVs |
| 4 | `build_winlab_evidence_report.py` | Compact Markdown evidence report |
| 5 | `run_winlab_power_workflow.py` | Safe one-command wrapper for the sequence |

Expected final evidence folder after a live run:

```text
runs/workflow-ocloud-live-YYYYMMDD-HHMMSS/
```

Expected report files:

```text
workflow_summary.json
status_snapshot/run_report.md
probe/run_report.md
probe/candidate_outlet_power_summary.csv
probe/candidate_outlet_power_summary.json
```

---

## 7. Suggested Follow-Up Message

```text
Hello Mr. Ravi,

We now have the HPE/OCloud rApp workflow ready to produce timestamped traffic windows and evidence reports. The remaining blocker is the physical PDU outlet mapping for the Pegatron O-RU.

Thank you for confirming the outlet mapping. I will use Outlet 2 for the current OAI nFAPI / OCloud Pegatron O-RU test, and I will treat Outlet 11 as Lavoisier/PNF host-side power rather than RU-only power.

Since CortexDC cannot show RU data yet, could you confirm whether Outlet 2 active_power is available through InfluxDB, direct PDU export, or another method? I mainly need timestamped power samples for the same UTC/Taipei window as the rApp/iPerf run.

Thank you!
```

---

## 8. Decision Rule

Use Outlet 2 for the current OCloud Pegatron O-RU power trace. The remaining blocker is no longer physical outlet identity; it is timestamped Outlet 2 `active_power` export, since CortexDC cannot show RU data yet.
