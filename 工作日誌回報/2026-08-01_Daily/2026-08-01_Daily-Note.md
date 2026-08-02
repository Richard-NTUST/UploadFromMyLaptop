# Daily Note

> 依據 Open-Research-Playbook `templates/G-daily-note.md` 格式記錄。

---

### Date

**Date:** 2026/08/01

---

### Short-term Goal

* **Goal 1：** 完成 Track A（軟體代理功耗量測）重現實驗的環境建置，作為 `claude_plan_建議.txt` 步驟 2（Track A 重現）的前置條件。

  * Milestone 1：Ubuntu 雙系統安裝於 D: 硬碟（Disk 1），C: 系統碟（Disk 0）完全未動 — Due 2026/08/01 — **已完成**
  * Milestone 2：RAPL（Intel Running Average Power Limit）可讀性驗證通過 — Due 2026/08/01 — **已完成**
  * Milestone 3：Track A 軟體鏈（iperf3、Python 分析套件、Docker、Scaphandre）安裝並驗證可回傳真實功耗數據 — Due 2026/08/01 — **已完成**

---

### Plan

|Priority|Task|Related Milestone or Action Item|Expected Deliverable|Estimated Time|Planned Evidence|
|-|-|-|-|-|-|
|P1|在 D: 硬碟安裝 Ubuntu 雙系統，不動 C: 系統碟|Milestone 1|雙系統可開機，分割區配置確認|2hr|PowerShell `Get-Partition` 輸出、開機截圖|
|P2|驗證 RAPL 可讀性|Milestone 2|`/sys/class/powercap/` 節點存在且 `energy_uj` 可讀|1hr|終端機輸出（`ls`、`cat energy_uj`）|
|P3|安裝並驗證 Track A 軟體鏈|Milestone 3|Scaphandre 容器回傳非零功耗數據|1hr|`curl localhost:8080/metrics` 輸出|

確認：

* [x] 每項任務對應 Milestone（步驟 1 的三個完成細項）。
* [x] 每項預期產出可驗證（分割區配置 / RAPL 節點與數值 / metrics 輸出）。
* [x] 證據位置已規劃（見上表 + 下方 Review 證據欄）。

---

### Review

|Task|Status|Actual Time|Evidence|
|-|-|-|-|
|Ubuntu 雙系統安裝於 D: 硬碟|☒ Done|1.5hr|機型 ASUS TUF Gaming F15 (FX507ZV4)；Ubuntu 26.04 LTS 裝於 Disk 1（D:），Disk 0（C:）完全未動。<br>1. 備份資料：僅備份「遺失會哭」等級的重要資料；嘗試用傳統 1T HDD（需轉接線）備份，過程中拆機取出該硬碟（[圖片4](圖片4.webp)）；後改考慮雲端備份重要圖片；順便整理並刪除 D: 上不再使用的檔案（Vivado、LTSpice 等課用軟體）。<br>2. 嘗試備份 BitLocker 復原金鑰：至 Microsoft 帳號頁面查詢，因平時未登入 Microsoft 帳號，確認未啟用需要金鑰的加密（[圖片1](圖片1.png)），故無金鑰問題，繼續備份資料。過程中曾插入隨身碟，因隨身碟老化一度無法退出並卡在讀取狀態，強制拔除後確認資料無損，重插後恢復正常讀取。<br>3. 確定環境：`Confirm-SecureBootUEFI` → True；`Get-BitLockerVolume`（[圖片2](圖片2.png)）；`manage-bde -protectors -get C:` / `D:`（[圖片3](圖片3.png)）確認無金鑰問題；分割 D: 硬碟給 Ubuntu 使用（[圖片6](圖片6.png)）。PowerShell `Get-Partition` 確認 Disk 1 Partition 3 = EFI ~1GB、Partition 4 = ext4 root ~159GB。<br>4. 用 Rufus 製作 Ubuntu 安裝隨身碟（[圖片7](圖片7.png)），過程中排除彈窗問題（[圖片8](圖片8.png)）。<br>5. 確認 Ubuntu 安裝位置（[圖片5](圖片5.png)）；依指引安裝，過程較快未逐步截圖（代表順利無異常），後續改用 Ubuntu Terminal 確認環境正確。<br>6. 確保雙系統可自由切換：BIOS(F2) 手動切換開機順序，兩邊皆可正常進入（[圖片9](圖片9.jpg)）。|
|RAPL 可讀性驗證|☒ Done|2hr|`ls /sys/class/powercap/` 輸出 `intel-rapl`, `intel-rapl-mmio`, `intel-rapl-mmio:0`, `intel-rapl:0`, `intel-rapl:0:0`, `intel-rapl:0:1`, `intel-rapl:1`（不需 modprobe）；`sudo cat /sys/class/powercap/intel-rapl:0/energy_uj` 讀到 `8950256567`|
|Track A 軟體鏈安裝與驗證|☒ Done|2hr|1. iperf3 安裝，啟動時彈窗詢問是否背景執行，選擇「否」（[圖片10](圖片10.webp)）。<br>2. `pip3 install pandas matplotlib seaborn --break-system-packages`（因 Ubuntu 26.04 PEP668 限制）；另用 `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc` 消除 PATH warning。<br>3. Docker：`sudo apt install -y docker.io`、`sudo usermod -aG docker $USER`；`docker --version` 確認為 `Docker version 29.1.3, build 29.1.3-0ubuntu4.1`。<br>4. 啟動 Scaphandre 容器：`docker run -d --name scaphandre --privileged -v /sys/class/powercap:/sys/class/powercap -p 8080:8080 hubblo/scaphandre prometheus`。<br>5. `curl localhost:8080/metrics \| grep scaph_host_power` 確認此版本沒有 `scaph_host_power` metric（已知落差，見下）。<br>6. `curl localhost:8080/metrics \| head -50` 取得正確結果，含 `scaph_domain_power_microwatts`（core ≈1.7W, uncore ≈0.12W）、`scaph_socket_rapl_mmio_energy_microjoules`（[圖片11](圖片11.webp)）— RAPL → Scaphandre → Prometheus HTTP 全鏈路打通。|

#### Pending Tasks and Blockers

步驟 1 本身三項皆已完成，無 Pending/Blocked 項目。以下為 2026/08/02 補記的流程性待辦（非步驟 1 範疇，Richard 要求記在此處統一追蹤）：

|Task|Reason|Required Action or Support|
|-|-|-|
|補齊 `會議記錄\2026-07-30_meeting\2026-07-30_Meeting-Notes.md` 底部 Where 區塊的 Related Documents / Related Templates 連結|目前 `工作日誌回報\Open-Research-Playbook`（template_cloned）等相關檔案都還在本機、尚未上傳 Git，指向本機相對路徑的連結沒有意義，故先留空。**優先度低**——單純是連結/流程完整性問題，不影響會議紀錄本身的內容產出|待 Richard 把 `工作日誌回報` 資料夾（含 Open-Research-Playbook clone）整理並上傳到 Git 後，回頭補上正確連結。Richard 預計在下次教授檢查前完成，無明確 due date，不急|

已知落差（非 blocker，記錄供步驟 2 使用）：此版本 Scaphandre 沒有 `scaph_host_power_microwatts` 這個 metric（改為逐 domain 回報，`grep scaph_host_power` 查無結果），步驟 2 寫分析腳本時要改用 `scaph_domain_power_microwatts` 加總，不要照搬原 guide 的 metric 名稱。

小插曲（已自行排除，無需追蹤）：

* 隨身碟（金鑰備份時使用）老化一度無法退出、卡在讀取狀態，強制拔除後確認資料無損，重插後恢復正常讀取。
* Windows/Ubuntu 時間不同步：`sudo timedatectl set-ntp true`、`sudo systemctl restart systemd-timesyncd`、`timedatectl` 檢查後仍有落差（Local time 顯示 `2026-08-01 02:52:21 CST`），改用 `sudo date -s "2026-08-01 HH:MM:SS"` 手動校正後重新登入解決，下載問題排除。
* Ubuntu 中文輸入法：安裝 `ibus-chewing`（`sudo apt update && sudo apt install -y ibus-chewing`），但無法用 `Ctrl+Space` 切換、無法打逗號，最後放棄，改用全英文介面規避，不強求解決。
* 安裝完 Ubuntu 後，Windows 端 PowerShell 寬度判斷失效：未真正解決（全英文介面/調整 PowerShell JSON 皆非理想解），改用命令提示字元 `cmd` 取代 PowerShell 繞過此問題。

#### 附帶記錄（與今日 Goal/Milestone 無直接對應，僅供之後查閱）

今天過程中順便摸熟的工具操作，跟 Track A 環境建置本身無關，不算在任一 Milestone 內，僅記錄供未來查閱：

* Claude Code CLI 操作：在不同 Terminal 呼叫前先確認路徑，再輸入 `claude`；用方向鍵 + `Ctrl+X` 刪除不需要的對話紀錄；用 `/compact`、`/model` 管理與切換模型；可改為在筆記本中編輯生成內容。
* Claude Code CLI 中文輸入問題：可改輸出 JSON 檔處理（今日未採用）；改用黑色圖示的「命令提示字元」（cmd，需以系統管理員身分執行）取代藍色圖示的 PowerShell 呼叫 claude，解決中文輸入問題。
* Ubuntu 操作快捷鍵：`Ctrl+Alt+T` 開啟 Terminal；`Ctrl+Shift+C` 為 Copy（非 Windows 慣用的 `Ctrl+C`）。

#### Today's Biggest Lesson

```text
第一次建立雙系統，要先備份資料，前準備(不在這分清單上)比我想得還要久，我還有順便整理我的環境，刪除之前上課用到、但未來不會用的Vivado、LTSpice等等的。此外，確認哪些檔按要備份，以及利用雲端硬碟備份，所需上傳時間比我想得還要多。接著是建立雙系統後，出現的意外比我想得還多，先是 F8 失敗要用 F2，因為我自己電腦的問題。再來是 Ubunto 介面不熟悉，我習慣Windows下的 Ctrl+C 作為 Copy，諸如此類的還有 Ubuntu 下想用中文輸入但很不方便 + 額外處理輸入法、調整安裝後系統時間、確認路徑等等都是意外的事情。還有，Scaphandre 那裡的意外，也是沒想到的。
```

---

### AI Daily Self-review

依 [E-ai-daily-self-review-prompt.md](Open-Research-Playbook/templates/E-ai-daily-self-review-prompt.md) 執行：

## Overall Assessment

Ready for next-day planning. 三項任務都對應到 Milestone，證據已從文字描述改為指向實際圖片檔的超連結（11張圖全數對應到具體步驟），Review 表與 Today's Biggest Lesson 內容一致。

## Missing or Unverified Evidence

None identified — 11 張圖片皆已對應到 Review 表中的具體步驟並以超連結呈現，link 本身可在同資料夾內直接開啟；文字類證據（終端機指令與輸出值）皆為 Richard 逐條打字記錄，非籠統帶過。

## Daily Review Issues

None identified — Plan 表的三項任務都出現在 Review 表，狀態/實際時數/證據齊全；Today's Biggest Lesson 具體且與 Pending Tasks and Blockers 段落記錄的插曲（隨身碟老化、時間校正、中文輸入法、PowerShell 寬度問題）一致。

## Deliverable and Planning Issues

None identified — 三項產出（分割區配置確認、RAPL 節點與數值、Scaphandre 真實 metrics 回傳）皆為可驗證的具體結果，非模糊活動。「附帶記錄」段落（Claude Code CLI 操作、Ubuntu 快捷鍵）已明確標註與今日 Goal/Milestone 無直接對應，屬揭露性質而非強行掛在 Milestone 上，符合 goal alignment 原則。

## Required Revisions

None — 前次要求的「補上證據超連結」已於本次修訂完成。

## Recommendations for the Next Working Day Plan

沿用已排定的步驟 2 三項任務（讀 Methodology/SOP → 執行重現腳本 → QC gate），這些皆有 `claude_plan_建議.txt` 步驟 2 段落支持，暫無需新增建議。

## Questions for the Researcher

None required — 若之後每篇日誌都比照這次的「資料夾 + 超連結」方式呈現證據，此格式可視為固定慣例，不需每次重新確認。

**Researcher Confirmation**（待 Richard 自行勾選）：

* [ ] 已對照原始證據逐條檢查 AI 評論
* [ ] 已修正遺漏或誤導的資訊
* [ ] 未將 AI 生成內容當作研究證據
* [ ] 已更新 Next Working Day Plan

---

### Next Working Day Plan

|Priority|Task|Related Milestone or Action Item|Expected Deliverable|
|-|-|-|-|
|P1|讀 `docs/FinalReport/01_Methodology_Reproducible_Measurement.md` 與 `03_Standard_Operating_Procedure.md`|`claude_plan_建議.txt` 步驟 2|理解場景矩陣（Idle → Load-L/M/H × 3 repeats）與執行 SOP，含 troubleshooting table|
|P2|依序啟動 Scaphandre → `iperf3 -s` → 執行 `scripts/run_week4_gap_run.sh` 跑完整 Idle→Load→Idle 序列|`claude_plan_建議.txt` 步驟 2|產出 `markers.csv` + `power_uw.txt`（注意套用 `scaph_domain_power_microwatts` 取代 guide 原文 metric 名）|
|P3|執行 `python scripts/analyze_week3_data.py` 產圖，並對照參考圖 `assets/2026-01-28/plots/gap_analysis_sensitivity.png` 做 QC gate|`claude_plan_建議.txt` 步驟 2|時序圖、線性度箱型圖、統計摘要；QC 判準：Idle <10W、Load >20W、平台段平坦、markers.csv 每個事件皆有 Start/Stop|

---

## Where?

### Related Documents

* [claude_plan_建議.txt](../claude_plan_建議.txt)
* [Research Playbook](Open-Research-Playbook/docs/02-research-playbook.md)

### Related Templates

* [Meeting Notes](Open-Research-Playbook/templates/F-meeting-notes.md)
* [AI Daily Self-review Prompt](Open-Research-Playbook/templates/E-ai-daily-self-review-prompt.md)

