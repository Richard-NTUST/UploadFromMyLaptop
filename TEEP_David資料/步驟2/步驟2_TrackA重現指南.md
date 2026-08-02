# 步驟 2：重現 Track A —「軟體代理」功耗-流量敏感度掃描

> 對應計畫：`C:\Users\徐銘亨\.claude\plans\piped-seeking-fog.md` 步驟 2
> 對應方法論：`internship/docs/FinalReport/01_Methodology_Reproducible_Measurement.md`
> 對應 SOP：`internship/docs/FinalReport/03_Standard_Operating_Procedure.md`
> 產出日期：2026-08-02

> [!IMPORTANT]
> 這份指南是在 **Windows 這一側**寫的（AI 這次是在 Windows 背景工作階段執行，無法直接連進你的 Ubuntu 開機環境跑指令）。RAPL / Scaphandre 一定要在原生 Ubuntu 開機環境下才能讀到，所以以下每一步都需要你自己在 Ubuntu 裡貼指令執行。如果卡住，把終端機輸出貼給我，我可以繼續協助排查。

---

## 0. 先解決一件事：internship repo 怎麼弄到 Ubuntu

你確認目前**還沒決定**怎麼把 `internship/` repo（含 `scripts/`、`docs/FinalReport/`）弄到 Ubuntu 上。建議做法：

```bash
# 在 Ubuntu 終端機執行
git clone https://github.com/bmw-ntust-internship/internship.git
cd internship
git checkout 2026-TEEP-2-JDavid   # 這是 Windows 這邊本地 clone 目前所在的分支
```

理由：這個 repo 有遠端（`github.com/bmw-ntust-internship/internship`），直接 clone 最乾淨，不用處理 NTFS 掛載權限問題，且 `runs/`、`assets/` 這些量測產出資料夾天生就是這個 repo 的相對路徑，clone 下來馬上就能用。

> [!NOTE]
> 這是 David 的 internship repo，不是 Richard 自己的專案。**不要 push** 任何東西回這個遠端（沒有事先跟 lab admin / David 協調過）。你在 Ubuntu 本地跑實驗產生的 `runs/`、`assets/` 新資料夾，就留在本地 clone 裡當自己的重現紀錄即可，不用也不該推回 origin。

---

## 1. 套用已知的 metric 名稱修正

**已知落差**（步驟 1 驗證時發現，已記在計畫檔）：你裝的 Scaphandre 版本**沒有** `scaph_host_power_microwatts` 這個 metric，`scripts/run_week4_gap_run.sh` 原始版本抓的正是這個不存在的名稱，會導致 `power_uw.txt` 整份是空的。你的版本改成逐 domain 回報（`scaph_domain_power_microwatts{domain="core"}`、`domain="uncore"`），這兩個 domain 加總 = Package 功耗，正好對應方法論文件定義的「Platform Power = Package + DRAM」。

我已經在 Windows 這邊把修正版寫好了，路徑：
```
TEEP_David資料\步驟2_run_week4_gap_run_fixed.sh
```
修正只有一處（把 awk 過濾條件從抓 `scaph_host_power_microwatts` 改成加總所有 `scaph_domain_power_microwatts` 行），其餘完全跟原始腳本一致。

**在 Ubuntu 裡套用**（clone 完 repo 之後）：
```bash
# 方法：直接覆蓋掉 repo 裡的原始腳本
# 如果 Ubuntu 有掛載 Windows 的 D:/C: 槽，可以直接 cp；
# 如果沒有掛載，就把 步驟2_run_week4_gap_run_fixed.sh 的內容
# 貼到 Ubuntu 這邊新建一個檔案，存成 internship/scripts/run_week4_gap_run.sh
chmod +x scripts/run_week4_gap_run.sh
```

**套用前先自己驗證一次**（因為不同機器/版本可能 domain 標籤不完全一樣），避免照抄我的假設：
```bash
curl -s localhost:8080/metrics | grep scaph_domain_power_microwatts
```
確認每一行都是你預期的 domain（例如 `core`、`uncore`），沒有出現重複計算的風險（例如同時有 `package` 又有 `core`+`uncore`，那樣加總會偏高）。步驟 1 你已經看過 core≈1.7W、uncore≈0.12W 兩行，只要這次看到的還是同樣兩個 domain，加總就是安全的。

---

## 2. 執行順序（照 SOP Phase A → B → C）

### Phase A：啟動量測鏈路

```bash
# Terminal 1：啟動 Scaphandre（如果步驟1裝的 container 還在，先確認還活著；不在就重開）
docker run -d --name scaphandre --privileged \
  -v /sys/class/powercap:/sys/class/powercap \
  -p 8080:8080 \
  hubblo/scaphandre prometheus

curl -s localhost:8080/metrics | grep scaph_domain_power_microwatts
# 應該要看到非零數值，看不到就先別往下走

# Terminal 2：啟動 iperf3 server（本機單機測試，不需要另一台機器）
iperf3 -s
```

### Phase B：跑掃描

因為是單機 loopback 測試（SOP §2.1 允許：「Loopback interface (lo) is sufficient for single-host testing」），**一定要**把 `TARGET_HOST` 指向本機，否則腳本預設的 `192.168.1.15` 大概率連不到，會在 preflight 檢查就直接失敗退出。

```bash
# Terminal 3（repo 根目錄 internship/ 下執行）
cd internship

TARGET_HOST=localhost \
MODE=udp \
OUTPUT_DIR=runs/2026-08-02/sweep-01 \
./scripts/run_week4_gap_run.sh
```

- 沒指定 `TARGET_L/M/H`：腳本會自動偵測 `lo` 介面速率並給預設值，通常 loopback 會抓到很高的速率、給到 Wi-Fi 等級的保守預設（50M/150M/300M）；如果想要更貼近方法論裡的 30%/60%/100% link capacity 語意，也可以自己明確指定，例如：
  ```bash
  TARGET_HOST=localhost TARGET_L=200M TARGET_M=500M TARGET_H=900M \
  OUTPUT_DIR=runs/2026-08-02/sweep-01 \
  ./scripts/run_week4_gap_run.sh
  ```
- 預設 `DURATION=180`、`IDLE=60`、`ROUNDS=3`（腳本內建值），跑完整套約需 **9 個 Load segment × (180+60)s ≈ 36 分鐘**，加上初始 idle 就再多一點。方法論文件建議的是每段 300s，如果時間夠、想更貼近方法論規格，可以加上：
  ```bash
  DURATION=300 IDLE=300
  ```
  但這會讓總時長拉到 90 分鐘以上。**先用預設值跑第一輪**確認整條鏈路通、QC 過關就好，之後有餘裕再考慮拉長到 300s 做「更嚴謹」的一輪。
- 跑的過程中**不要用這台機器做其他重負載的事**（SOP 明確要求），跑完前不要關終端機。

跑完會在 `runs/2026-08-02/sweep-01/` 底下產生：
- `power_uw.txt`（功耗取樣，每 10 秒一筆，單位微瓦）
- `markers.csv`（每個 Start/Stop 事件的 UTC 時間戳）
- `iperf_Load_*_Run*.txt`（每段的 iperf3 client 輸出）

### Phase C：分析出圖

```bash
python3 scripts/analyze_week3_data.py runs/2026-08-02/sweep-01
```

會在 `assets/2026-08-02/plots/` 產生：
- `power_timeline.png`（時序圖，功耗 vs 時間，按狀態上色）
- `power_linearity_boxplot.png`（各 Load 等級的功耗箱型圖）
- `stats_summary.md`（trimmed mean/std/CV 統計表）

同時在 `runs/2026-08-02/sweep-01/` 底下也會產生 `iperf_summary.md`、`iperf_client_summary.md`、`repeatability_per_run.md`。

---

## 3. QC 驗收標準（照 SOP §4，逐項對照）

跟參考圖 `internship/assets/2026-01-28/plots/gap_analysis_sensitivity.png` 比對：

| 檢查項 | 標準 | 怎麼查 |
|---|---|---|
| 1. 狀態區隔 | Idle < 10W，Load > 20W，兩者要有清楚落差 | 看 `power_timeline.png`，或 `stats_summary.md` 裡 Idle vs Load-H 的 mean |
| 2. 平台段平穩 | 每個 Load 平台段的圖形要平，不能鋸齒狀 | 看 `power_timeline.png`；如果鋸齒明顯，檢查是不是背景在跑系統更新、或散熱降頻 |
| 3. Markers 完整 | 每個 Start_X 都要有對應的 Stop_X | 打開 `markers.csv` 檢查 |
| 4. 取樣頻率正常 | `power_uw.txt` 每筆間隔約 10 秒（`POWER_SAMPLE_PERIOD_SEC` 預設值），不能有長時間斷點 | 看 `power_uw.txt` 的時間戳間隔 |

**數量級對照**（FinalReport 既有結果，僅供參考量級，不要求完全對上）：
- Idle ≈ 5.7W → 100% load ≈ 26.9W
- Burst/TDM proxy：21.78W → 11.25W（約 48% 下降）

只要你這次重現的 Idle/Load 落在同一個數量級（個位數瓦 vs 十幾到二十幾瓦），且 QC 1-4 全過，就符合計畫檔定義的「完成」判準。

---

## 4. 疑難排解（SOP §5 摘錄 + 這次已知的落差）

| 問題 | 可能原因 | 處理方式 |
|---|---|---|
| `power_uw.txt` 整份是空的或都是 0 | 沒套用步驟 1 提到的 metric 名稱修正 | 確認用的是 `步驟2_run_week4_gap_run_fixed.sh` 的版本，不是原始未修正版 |
| preflight 直接報錯連不到 iperf3 server | `TARGET_HOST` 沒設成 `localhost` | 照本指南 Phase B 明確帶 `TARGET_HOST=localhost` |
| `curl localhost:8080/metrics` 沒東西 | Scaphandre container 沒在跑，或沒用 `--privileged` | `docker ps` 確認容器狀態，重開時記得帶 `--privileged` |
| throughput 遠低於 target | 單執行緒 iperf3 CPU 瓶頸 | 目前腳本用 `-P 1`，如果要衝更高流量可改 `-P 4`（要改 `week3_load_sweep.sh`），非必要 |
| 時間戳對不上 | script 跟 python 有一邊沒用 UTC | 目前兩邊都預設 UTC，理論上不會發生；如果發生了回報給我 |

---

## 5. 這一步做完之後

- 對照計畫檔步驟 5：可以考慮用 `Open-Research-Playbook/templates/C-verification-report.md` 的結構（確認理解 → 重現 MRR → 提出後續工作）把這次重現的過程、QC 結果、遇到的落差記下來，非強制但建議。
- 把這次真的產生的 `power_uw.txt` / `markers.csv` / plots 位置回報給我，我可以幫忙看數字是否合理、要不要調整。

---

## 6. 實際執行紀錄與已知問題（2026-08-02 執行，2026-08-03 回報）

> [!NOTE]
> 這節記錄實際在 Ubuntu 執行時遇到的狀況與最終結果，原始逐指令記錄見 Richard 自己保留的 `步驟2/暫存.txt` 與 `picture1.png`/`picture2.png`。這裡整理成可讀版本，供之後寫日誌／填 `C-verification-report.md` 參考。

### 6.1 執行流程摘要

- repo clone 走 §0 建議路徑：`git clone https://github.com/bmw-ntust-internship/internship.git`，HTTPS clone 需要輸入 GitHub 帳密登入，登入後 `git checkout 2026-TEEP-2-JDavid` 成功（`git branch` 確認在正確分支）。
- Scaphandre container 因 Ubuntu 重開機而停止，用 `docker start scaphandre` 重新啟動即可，不需要重建。
- 套用 §1 的 metric 修正（`scaph_domain_power_microwatts` 加總）後開始跑正式量測。

### 6.2 遇到的問題與排除方式

| 問題 | 原因 | 排除方式 |
|---|---|---|
| `run_week4_gap_run.sh` 自動偵測連線速率沒有反應 | `resolve_route_iface` 對 `TARGET_HOST=localhost` 執行 `ip route get localhost` 查不到介面（loopback 沒有一般路由條目），導致 `set_default_targets_from_speed` 拿不到 iface/speed，`TARGET_L/M/H` 全部留空 | 改成明確帶入 `TARGET_L=200M TARGET_M=500M TARGET_H=900M`，繞開自動偵測。之後在這台機器上都建議直接這樣帶，不要依賴自動判斷 |
| 用 `bash -x ... \| head -50` 追蹤時看起來像卡住 | `head` 收滿指定行數就會關閉管線，腳本後續要往 stdout 寫東西時收到 SIGPIPE，在 `set -euo pipefail` 下被中止——不是 Scaphandre 或 iperf3 真的沒回應 | 拿掉 `\| head`，讓腳本自然跑完，確認可以順利完整跑完 3 輪 × 3 個 Load 等級（約 36 分鐘） |
| 誤按 Ctrl+C（原本想按 Ctrl+Shift+C 複製字串）中斷了第一次正式跑（`sweep-01`） | 操作失誤 | 直接開新的 `OUTPUT_DIR=runs/2026-08-03/sweep-02` 重跑一次；`sweep-01` 的殘留資料留著沒清，不影響 `sweep-02` 結果 |

### 6.3 最終結果與數據異常

`sweep-02` 完整跑完，`analyze_week3_data.py` 成功產出 `power_timeline.png`、`power_linearity_boxplot.png`、`stats_summary.md`：

| state | mean (W) | std | cv_pct | count |
|---|---|---|---|---|
| Idle | 0.248 | 0.518 | 208.6% | 36 |
| Load-L | 0.990 | 1.083 | 109.5% | 48 |
| Load-M | 0.729 | 0.080 | 11.0% | 48 |
| Load-H | 1.189 | 1.561 | 131.2% | 47 |

跟 FinalReport 參考數量級（Idle ~5.7W → Load-H ~26.9W）差了一個數量級以上，且各狀態的 CV（變異係數）普遍過高（Load-M 例外，只有 11%）。iperf3 流量端完全正常（900Mbit/s、0% loss 穩定跑滿全程），問題確定集中在功耗量測端。

**診斷**（與 AI 討論後的共同結論，2026-08-03）：
1. 這次讀到的 RAPL domain 只有 `core`/`uncore`，沒有 `dram`，加總出來只是 CPU package power，不是方法論定義的完整「Platform Power」——但這頂多讓數字系統性偏低幾瓦，不足以解釋整個數量級的落差。
2. 真正主因較可能是**取樣時間粒度問題**：`scaph_domain_power_microwatts` 是 Scaphandre 內部算好的瞬時功耗，跟外部每 10 秒一次的 curl 輪詢沒有對齊，加上 RAPL energy counter 偶爾 wraparound，導致同一個 10 秒窗口抓到的可能是極短 Δt 算出來的異常尖峰（例如同一個 Load-H 區段內從 0.09W 跳到 10W），而不是穩定的區間平均功耗。

### 6.4 後續決定（2026-08-03）

- **這個階段不追查/修正這個數據落差。** 對照 `plan_建議.txt`，步驟 2 本身在整體計畫的優先度不算最高，更重要的是銜接步驟 6（Track B，跟上 David 現在實際在做的事）；改善量測精度（例如改讀累積能量計數器 `scaph_socket_rapl_mmio_energy_microjoules`、自行算 Δenergy/Δtime）列為**無時間壓力的 pending 項目**，有餘力可以做（也可能之後拿來跟 David 的方法比較），不做也不影響主線進度。
- **打算主動找 David 討論**：問他當初的 Track A 數據是怎麼避開這種雜訊問題的（例如是否等穩定後才取樣、或用連續累積再取平均），有回覆再補充回這份文件或 `C-verification-report.md`。
- **路徑本身（repo → Scaphandre → iperf3 → sweep script → 分析腳本 → 出圖）已確認可完整重複執行**，可視為步驟 2「最短路徑重現」的目標已達成；數據量級的落差留待未來有時間、或有 David 的方法比較資訊時再處理。
