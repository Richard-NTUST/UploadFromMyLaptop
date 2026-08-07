# 執行步驟：Session Handoff §16 實驗矩陣（4 條件 × 2 輪，500Mbps × 20min）

> [!NOTE]
> 產出日期：2026-08-08。這份步驟是把 [`internship/docs/StudyNotes/2026-08-03_WINLAB_OAI_Scheduler_Experiment_Session_Handoff.md`](../internship/docs/StudyNotes/2026-08-03_WINLAB_OAI_Scheduler_Experiment_Session_Handoff.md) 的 §8–§18 整理成「照順序執行」的清單，對應 [`plan_建議.txt`](../../plan_建議.txt) 步驟 6「①先重現」階段。具體指令內容故意沒有寫死在這裡——請把這份清單連同 Session Handoff 原文一起交給執行端的 LLM，讓它依照原文精確語法補指令，避免憑空編造造成落差。

---

## 步驟 0：事前確認（每次進場前都要做，不只第一次）
- 確認自己有預約到這套 UE/RU 時段，沒人同時在用（§18）。
- SSH 進 HPE，定義好變數 `K`（kubectl 路徑）、`C`（kubeconfig）、`N=ming-ns`（§8）。

## 步驟 1：Preflight 健康檢查（§8，對應 §2「Always re-check live state before acting」）— 每次動手前自己做，不能只看歷史紀錄

### 1a. 叢集健康狀態（§8 原文指令，直接照跑）

```bash
ssh hpe@192.168.8.26

K=/home/hpe/CRAN/kubectl
C=/home/hpe/CRAN/ming-kubeconfig.yaml
N=ming-ns

$K --kubeconfig="$C" get node lavoisier -o wide

$K --kubeconfig="$C" get node lavoisier \
  -o jsonpath='cp={.status.allocatable.openshift\.io/fh_sriov_cp_lao} up={.status.allocatable.openshift\.io/fh_sriov_up_lao}{"\n"}'

$K --kubeconfig="$C" get pods -n "$N" -o wide \
  | grep -E 'oai-pnf|oai-vnf'

$K --kubeconfig="$C" get deploy -n "$N" \
  -o jsonpath='{range .items[?(@.metadata.name=="oai-pnf-pegatron")]}PNF={.spec.template.spec.containers[0].image}{"\n"}{end}{range .items[?(@.metadata.name=="oai-vnf")]}VNF={.spec.template.spec.containers[0].image}{"\n"}{end}'

curl -fsS http://127.0.0.1:9090/health
```

逐項確認，沒有全部通過就不要開跑：
1. `lavoisier` node 為 `Ready`
2. SR-IOV CP、UP allocatable 皆為 `1`
3. `ming-ns` 裡剛好一個 PNF pod + 一個 VNF pod，且都是 `1/1 Running`
4. 重啟計數（restart count）已持續穩定數分鐘沒跳動
5. PNF／VNF 目前的 image 符合你要跑的條件
6. 沒有其他人在用同一套 RU/UE（見下方 1b，Handoff 原文對這項沒有給指令）
7. Nemo Handy 顯示預期 cell（ARFCN `649920`、PCI `0`、PLMN `001-01`）
8. Samsung UE 已取得 `10.45.x.x` 位址（若要用 preserve-state 模式）
9. `curl http://127.0.0.1:9090/health` 正常

### 1b. 是否現在正有人在跑 job（Handoff 原文沒有給明確指令，以下是根據既有素材推出的判斷方式，非官方寫死做法）

Handoff §12 的 `curl http://127.0.0.1:9090/jobs/JOB_ID` 要先知道 JOB_ID 才能查，沒有「列出所有進行中 job」的 API；`get pods` 顯示 `1/1 Running` 不管有沒有人在跑都會是這樣，不能單獨當作判斷依據。建議疊加看以下三項：

- **Pod AGE**：上面 1a 指令 `get pods -o wide` 輸出裡的 `AGE` 欄位。剛重啟沒多久，可能代表剛好有人動過 image 或重跑。
- **Log 時間戳是否持續在跳**：
  ```bash
  $K --kubeconfig="$C" logs -n "$N" <pod-name> --tail=50
  ```
  找 `[WINLAB_SCHED_LOG]` 紀錄，如果時間戳持續在增加，代表現在真的有流量在跑，不要動。
- **當下 PDU 功耗讀數**：用 §14 的 InfluxDB 查詢方式，把時間範圍改成最近幾分鐘，看 Outlet 2 `active_power` 是否明顯高於 idle 水準——高於 idle 代表 RU 現在正在傳輸。

若判斷「現在有人在跑」→ 不要碰 Kubernetes，等對方跑完再重新檢查一次。

若任一項不過 → 跳去對應的「步驟 6：異常排除」。

## 步驟 2：決定本輪要跑的排程器條件，切換 VNF image（§11）
四個條件依序（建議照這個順序跑，一次一個條件跑滿 2 輪再換下一個，避免中途切換造成混淆）：
1. **Immutable baseline / 273-PRB（無 cap）** — 控制組
2. **27-PRB cap** — 已功能驗證過
3. **54-PRB cap** — 中間點
4. **106-PRB cap** — 較高中間點

切換時：
- 只換 VNF image，PNF 維持在相容 runtime 不動。
- baseline 不要用會漂移的 `latest` tag 當科學基準——要用固定 commit/digest 建出的 immutable image（handoff §11 特別強調，補指令時要注意）。
- 記錄：source repo/commit、Jenkins build number、完整 image reference + digest、Helm release revision/values、pod image ID。

## 步驟 3：（若剛換過 image 或叢集狀態有疑慮）依序重啟 Pod（§9）
順序固定：**先 scale PNF+VNF 都到 0 → 等 pod 刪除 → 先拉起 PNF → 等 rollout 完成 → sleep 15 秒 → 再拉起 VNF → 等 rollout 完成**。
不要一個一個手動刪 pod，要 scale 整個 deployment（§18 規則）。

## 步驟 4：跑 E2E 實驗（§12）
- 用 preserve-state 模式送出 job（避免 UE 重新 airplane mode 中斷已知良好的 attach）。
- 參數固定：`bandwidth=500`（Mbps）、`period=1200`（20 分鐘）、`ue_model=samsung`、`uplink=false`。
- 送出前先確認當前 `9090` API schema 還吃 `preserve_ue_state` 這個欄位（handoff 提醒這個 API 可能改版）。
- 需要才 poll job 狀態，不要無意義地一直輪詢。

## 步驟 5：驗收這一輪 run 是否有效（§13）— 不要只看「succeeded」就採信
八項都要確認：
1. 實際跑的是你要的 VNF image + PNF runtime
2. PNF/VNF 全程 Ready，重啟數穩定
3. 觀察到預期 cell 且 UE 有 attach
4. 本地 iPerf server 真的接到 UE 連線
5. 吞吐樣本覆蓋 ≥80% 請求時長（正式比較要盡量到 100%，80% 只是診斷用最低標準）
6. 排程器 log 出現預期的 mode/grant 行為
7. PDU 資料時間有蓋到實際正流量視窗
8. 沒有致命 PNF assertion／UE idle-timeout 截斷／client 中斷

沒過 → 這輪只能標記為「診斷用」，不能拿去做正式比較；視情況重跑。

## 步驟 6：異常排除（只有出狀況才進來，對照 §10 故障樹）
- Lavoisier `NotReady` → 走 A：重啟 kubelet，不行就用 BMC。
- 重開機後 fronthaul/VF 異常 → 走 B：**先把 PNF scale 到 0**，才能跑 `setup_network.sh`。
- SR-IOV UP allocatable 是 0 → 走 C：重啟 device plugin 的 CRI container。
- RU 被別人動過/搬過 → 走 D：`rrr` → 等重開機 → `pegam`（不要每次都跑這兩個指令，只有確定 RU 被動過才跑）。
- PNF 在 PRACH 後掛掉 → 走 E：先看 log 再判斷是哪種 signature（分組不相容／RU 相容性／timing 崩潰／worker binary 不match／外部干擾），對照 §10 表格分流，不要瞎猜。
- Cell 看得到但 UE 沒 IP → 走 F：先查 AMF/NGAP 證據，不要看到沒 IP 就重啟 Open5GS。

## 步驟 7：匯出功耗資料並合併（§14）
- 從 InfluxDB `cortexdc_pdu` bucket 匯出 Outlet 2 `active_power`，時間範圍對齊這輪 run 的 UTC 區間。
- Influx token 放在 shell 環境變數，不要寫進 script 或筆記檔（§18 規則：絕不能外流憑證）。
- 用 `merge_winlab_e2e_power.py` 把 iPerf artifact 跟 PDU CSV 合併，腳本會自動裁掉 traffic 結束後的 idle power，不會污染平均值。

## 步驟 8：（可選）重建排程器 playback 視覺化（§15）
用 `build_winlab_scheduler_playback.py` 重新產生 `assets/winlab_scheduler_playback/data/run-data.js`，本地開 `index.html` 看。注意：目前排程器 log 是製程相對時間，跟 iPerf/PDU 沒有真正共用時間戳，不要宣稱三者精確對齊。

## 步驟 9：每個條件都要記錄的欄位（§16）
不管哪個條件，每輪跑完都要留這些數字：
- 吞吐量均值與分布
- Outlet 2 功耗均值／最小／最大／變異
- 每 delivered-Gb 焦耳數（energy/bit）
- PRB 分配分布與 cap 違規次數
- MCS、TBS、HARQ、重傳率
- 正流量時長與完成率
- pod 重啟次數與相關故障訊號

## 步驟 10：重複步驟 2–9，跑完全部 4 條件 × 2 輪
跑完後才有足夠資料畫出「排程分配 vs 功耗」曲線的起點（這是教授要的東西，只有 27-PRB 一個點看不出功耗是平的、階梯的還是跟負載相關）。

## 步驟 11：全程遵守的紅線（§18，貫穿以上所有步驟，不是單獨一步）
不要：PNF 還在跑時執行 `setup_network.sh`／每輪都跑 `rrr`/`pegam`／只憑 IP 判斷 user-plane 健康／只憑 offered bandwidth 判斷排程器對不對／只憑 API 狀態判斷科學有效／拿固定 image 跟一直變動的 `latest` 比較／只換 `nr-softmodem` 不換配套 library／沒有 AMF/NGAP 證據就重啟 Open5GS／逐一手動刪 pod（要 scale deployment）／在任何輸出裡洩漏 Git 或 Influx 憑證。
