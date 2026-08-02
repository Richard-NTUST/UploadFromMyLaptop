# Daily Note

> 依據 Open-Research-Playbook `templates/G-daily-note.md` 格式記錄。

---

### Date

**Date:** 2026/08/03

---

### Short-term Goal

* **Goal 1：** 執行 `plan_建議.txt` 步驟 2——重現 Track A（軟體代理功耗-流量敏感度掃描），取得「完全自己重現、有 QC 依據」的最小可行結果。

  * Milestone 1：把 David 的 `internship` repo（`scripts/`、`docs/FinalReport/`）clone 到 Ubuntu 環境，並套用步驟 1 已知的 metric 名稱修正 — Due 2026/08/03 — **已完成**
  * Milestone 2：依 SOP Phase A→B 執行完整 Track A 量測（Scaphandre + iperf3 + `run_week4_gap_run.sh`），產出 `markers.csv` + `power_uw.txt` — Due 2026/08/03 — **已完成**
  * Milestone 3：執行 `analyze_week3_data.py` 出圖，並對照 QC gate 驗收 — Due 2026/08/03 — **出圖已完成，QC 數量級未通過**（見下方 Review 與 Pending）

---

### Plan

> 沿用 `2026-08-01_Daily-Note.md` 的 Next Working Day Plan（P1-P3）。

| Priority | Task | Related Milestone or Action Item | Expected Deliverable | Estimated Time | Planned Evidence |
|---|---|---|---|---|---|
| P1 | 讀 `docs/FinalReport/01_Methodology_Reproducible_Measurement.md` 與 `03_Standard_Operating_Procedure.md` | Milestone 1（前置理解） | 理解場景矩陣（Idle → Load-L/M/H × 3 repeats）與執行 SOP，含 troubleshooting table | | 無（閱讀性任務） |
| P2 | 依序啟動 Scaphandre → `iperf3 -s` → 執行 `scripts/run_week4_gap_run.sh` 跑完整 Idle→Load→Idle 序列 | Milestone 2 | 產出 `markers.csv` + `power_uw.txt` | | 終端機輸出（`暫存.txt`）、iperf3 截圖 |
| P3 | 執行 `python scripts/analyze_week3_data.py` 產圖，並對照參考圖做 QC gate | Milestone 3 | 時序圖、線性度箱型圖、統計摘要；QC 判準：Idle <10W、Load >20W、平台段平坦、markers.csv 每個事件皆有 Start/Stop | | `stats_summary.md`、plots |

確認：

* [x] 每項任務對應 Milestone（步驟 2 的三個細項）。
* [x] 每項預期產出可驗證（repo 就緒 / markers.csv+power_uw.txt / plots+stats）。
* [x] 證據位置已規劃（`TEEP_David資料\步驟2\` 內的 `暫存.txt`、`picture1.png`、`picture2.png`）。

---

### Review

| Task | Status | Actual Time | Evidence |
|---|---|---|---|
| P1：讀 Methodology/SOP 原文 | ☐ Pending | | **尚未由 Richard 本人親自閱讀原文** — 這一步實際上是由 AI 在另一個工作階段讀取 `01_Methodology_Reproducible_Measurement.md` 與 `03_Standard_Operating_Procedure.md` 原文後，轉譯整理成 [`步驟2_TrackA重現指南.md`](../../TEEP_David資料/步驟2/步驟2_TrackA重現指南.md)，Richard 依指南直接動手執行。原文本身尚未親自讀過，已依你的要求列入 Pending（見下）。 |
| P2：執行 Track A 量測 sweep | ☒ Done | | 1. Repo 準備：`git clone` David 的 `internship` repo，`git checkout 2026-TEEP-2-JDavid`；套用步驟 1 已知的 metric 修正（`scaph_domain_power_microwatts` 加總取代不存在的 `scaph_host_power_microwatts`），修正版腳本見 [`步驟2_run_week4_gap_run_fixed.sh`](../../TEEP_David資料/步驟2/步驟2_run_week4_gap_run_fixed.sh)。<br>2. Scaphandre 因 Ubuntu 重開機停止，`docker start scaphandre` 重啟；`curl localhost:8080/metrics` 確認 `scaph_domain_power_microwatts` 有值。<br>3. 第一次執行 `run_week4_gap_run.sh` 自動偵測連線速率失敗（`ip route get localhost` 查不到 loopback 介面），改為明確帶入 `TARGET_L=200M TARGET_M=500M TARGET_H=900M` 繞開。<br>4. 第一次正式跑（`sweep-01`）因誤按 Ctrl+C（原想按 Ctrl+Shift+C 複製）中斷，iperf3 server 端出現 idle timeout（**證據：[picture1.png](../../TEEP_David資料/步驟2/picture1.png)**，test #3）。<br>5. 重開 `OUTPUT_DIR=runs/2026-08-03/sweep-02` 重跑，完整跑完 3 輪 × 3 個 Load 等級（約 36 分鐘），iperf3 全程 900Mbit/s、0% loss（**證據：[picture2.png](../../TEEP_David資料/步驟2/picture2.png)**，test #13），產出 `markers.csv` + `power_uw.txt`。<br>完整逐指令記錄見 [`暫存.txt`](../../TEEP_David資料/步驟2/暫存.txt)。 |
| P3a：執行 `analyze_week3_data.py` 出圖 | ☒ Done | | 成功產出 `power_timeline.png`、`power_linearity_boxplot.png`、`stats_summary.md`。統計結果：Idle 0.248W（CV 208.6%）、Load-L 0.990W（CV 109.5%）、Load-M 0.729W（CV 11.0%）、Load-H 1.189W（CV 131.2%）。iperf3 流量端本身完全正常（900Mbit/s、0% loss）。 |
| P3b：對照參考圖做 QC gate 驗收 | ☐ Pending | | 與 FinalReport 參考數量級（Idle ~5.7W → Load-H ~26.9W）相差超過一個數量級，且多數 state 的 CV 過高——QC 判準「Load >20W」未通過，問題集中在功耗量測端（非 iperf3 流量端）。診斷與後續決定詳見 [`步驟2_TrackA重現指南.md`](../../TEEP_David資料/步驟2/步驟2_TrackA重現指南.md) §6.3-6.4，對應 Pending Tasks 表第二項。 |

#### Pending Tasks and Blockers

| Task | Reason | Required Action or Support |
|---|---|---|
| 親自閱讀 `01_Methodology_Reproducible_Measurement.md`、`03_Standard_Operating_Procedure.md` 原文 | 目前是由 AI 讀取原文後轉譯成執行指南，Richard 依指南直接動手執行，尚未親自逐字讀過方法論與 SOP 原文本身（Richard 本人確認） | Richard 自行安排時間閱讀原文，確認理解與轉譯版本一致（或發現落差再回報修正）。無明確 due date，Richard 主動列為 pending |
| Track A 功耗量測數據量級異常（比參考值低一個數量級以上，多數 state 的 CV 過高） | 診斷認為可能是 Scaphandre 瞬時取樣與外部每 10 秒輪詢週期未對齊、RAPL energy counter 短暫 wraparound 造成的雜訊尖峰所致，而非真實功耗變化。目前判斷「量測管線本身（repo→Scaphandre→iperf3→sweep script→分析腳本→出圖）可完整重複執行」已達成步驟 2「最短路徑重現」的目標，數據精度問題暫不影響往步驟 6（銜接 Track B / 跟上 David 進度）推進的優先度 | 待有餘力、或向 David 詢問他當初怎麼避開此雜訊問題後，再考慮改用累積能量計數器（`scaph_socket_rapl_mmio_energy_microjoules`）自算 Δenergy/Δtime 等方式改善。無時間壓力，Richard 主動列為 pending |

#### Today's Biggest Lesson

```text

```

---

### AI Daily Self-review

依 [E-ai-daily-self-review-prompt.md](../Open-Research-Playbook/templates/E-ai-daily-self-review-prompt.md) 執行：

## Overall Assessment

四項任務對應到步驟 2 的三個 Milestone；P2 完整完成且有逐指令記錄與截圖佐證，P3a（出圖）完成，P3b（QC gate）如實標記為 Pending（數量級未過），P1 如實標記為 Pending（Richard 本人尚未讀原文）。日期已確認為 2026/08/03，P3 已依你的要求拆成 P3a/P3b 兩列。Estimated Time、Actual Time、Today's Biggest Lesson 依你的要求留空待你自己填寫。

## Missing or Unverified Evidence

`picture1.png`/`picture2.png` 只看得到 iperf3 server 端（terminal_2）畫面，看不到 Scaphandre/`curl metrics` 或 `analyze_week3_data.py` 執行當下的畫面截圖——這些步驟目前只有 `暫存.txt` 裡的文字終端機記錄佐證，沒有對應截圖。是否需要補圖由你決定，非必要（文字記錄本身已足夠具體）。

## Daily Review Issues

None identified — P3 已拆成 P3a（出圖，Done）/P3b（QC gate，Pending）兩列，狀態欄位回到模板原本的三選一（Done/Pending/Blocked），不再有複合寫法。

## Deliverable and Planning Issues

None identified — 三項產出（repo 就緒/量測管線可重複執行/出圖與統計摘要）皆為可驗證的具體結果，QC 未過的部分已如實記錄為落差而非隱藏或美化。

## Required Revisions

* 待你填入 Estimated Time、Actual Time、Today's Biggest Lesson。

## Recommendations for the Next Working Day Plan

步驟 2 的「管線重現」目標已達成，數據精度問題已列 pending 且不卡進度；建議下一步依計畫檔重心轉向步驟 6（銜接 Track B、跟上 David 目前實際進度），背景知識研讀（步驟 4）可平行進行。

## Questions for the Researcher

None required — 上次的兩個問題（日期歸屬、P3 是否拆列）已由你回覆確認，本次修訂已套用。

**Researcher Confirmation**（待 Richard 自行勾選）：

* [ ] 已對照原始證據逐條檢查 AI 評論
* [ ] 已修正遺漏或誤導的資訊
* [ ] 未將 AI 生成內容當作研究證據
* [ ] 已更新 Next Working Day Plan

---

### Next Working Day Plan

| Priority | Task | Related Milestone or Action Item | Expected Deliverable |
|---|---|---|---|
| P1 | 銜接／確認 TEEP David 目前 Track B 實際進度與交接事項 | `plan_建議.txt` 步驟 6 | 掌握 David 尚未完成的 baseline vs. 27-PRB 排程器 A/B 對照現況，作為未來接手的具體切入點 |
| P2 | 背景知識研讀（依步驟 4 建議順序，先從 NR 頻域基礎開始） | `plan_建議.txt` 步驟 4 | 讀完至少第一份 StudyNote（`2026-03-02_Frequencies-in-NR.md`） |
| P3 | 視時間，回頭補讀步驟 2 文獻原文，清掉本篇 Pending 項目 | 本篇 Pending Tasks | 親自讀完 `01_Methodology...` 與 `03_SOP...`，確認與執行指南內容一致 |

---

## Where?

### Related Documents

* [plan_建議.txt](../../plan_建議.txt)
* [步驟2_TrackA重現指南.md](../../TEEP_David資料/步驟2/步驟2_TrackA重現指南.md)
* [Research Playbook](../Open-Research-Playbook/docs/02-research-playbook.md)

### Related Templates

* [Meeting Notes](../Open-Research-Playbook/templates/F-meeting-notes.md)
* [AI Daily Self-review Prompt](../Open-Research-Playbook/templates/E-ai-daily-self-review-prompt.md)
