# 步驟 1：Ubuntu 雙系統建置指南（Track A 環境前置作業）

> 對應計畫：`C:\Users\徐銘亨\.claude\plans\piped-seeking-fog.md` 步驟 1
> 產出日期：2026-07-31

---

## 1. 本機硬體檢查結果（已用 PowerShell 讀取，唯讀操作）

| 項目 | 結果 | 意義 |
|---|---|---|
| CPU | Intel i7-12700H（14 核） | Intel 筆電級 CPU，支援 RAPL（package/core/uncore，通常也有 psys domain），Scaphandre 應可正常讀取 |
| Disk 0 | Micron 2400 512GB，GPT，掛載為 **C:**（72GB 可用 / 484GB） | Windows 系統碟，**空間緊繃，不建議在這顆上動刀** |
| Disk 1 | Crucial CT1000 1TB，GPT，掛載為 **D:**（599GB 可用 / 1TB） | 資料碟，空間充足，且是**獨立實體硬碟**——是安裝 Ubuntu 的最佳位置 |
| 開機模式 | 兩顆都是 GPT + Windows 11 → 幾乎可確定是 UEFI 模式 | Ubuntu 安裝程式需選 UEFI 模式（非 Legacy/CSM） |
| Secure Boot / BitLocker | 權限不足，讀取失敗（需系統管理員權限的 PowerShell 才能查） | 需要你自己確認一次，見下方 §2 |

**關鍵決策：把 Ubuntu 整個裝在 D: 那顆硬碟（Disk 1）的閒置空間，完全不動 C: 系統碟。**
好處：
- 不用碰 Windows 開機磁碟，萬一裝壞了，最壞情況也只是拔掉/停用第二顆硬碟，Windows 完全不受影響。
- 不用擔心 C: 上的 BitLocker/Device Encryption 或系統保留分割區被誤動。
- 599GB 空間绰绰有餘，抓 150–200GB 給 Ubuntu 即可（Track A 的資料量很小，不需要太大）。

---

## 2. 開始前的確認事項（你需要自己做，我這邊權限不夠查）

1. **確認 BitLocker / 裝置加密狀態**：
   - 開「設定 → 隱私權與安全性 → 裝置加密」，看 C: 或 D: 是否顯示「開啟」。
   - 或用系统管理員開 PowerShell 執行：`Get-BitLockerVolume`
   - 如果 D: 有開加密，記得先把 BitLocker 復原金鑰記下來（微軟帳戶或列印），避免縮小分割區時卡住。
2. **備份重要資料**：雖然只動 D: 的閒置空間理論上不影響現有檔案，但分割區操作永遠有小機率意外，建議先把 D: 上重要檔案備份一份（外接硬碟或雲端皆可）。
3. **確認 Secure Boot 狀態**（非必要，但建議）：重開機進 BIOS/UEFI 設定（開機時按 F2/Del/F10，依機型而定）查看 Secure Boot 是否開啟。Ubuntu 22.04+ 預設支援 Secure Boot（有簽名的 shim），**通常不需要關閉**，除非安裝時遇到開機問題再回來調整。

---

## 3. 建置流程

### 3.1 下載 Ubuntu

- 建議版本：**Ubuntu 22.04 LTS** 或更新的 LTS 版本（24.04 LTS 也可以，兩者 RAPL/Scaphandre 支援都沒問題）。
- 下載頁：https://ubuntu.com/download/desktop
- 下載 `.iso` 檔案（約 4-5GB）。

### 3.2 製作開機隨身碟

- 需要一支 **8GB 以上**的隨身碟（會被完全清空重寫）。
- 工具：[Rufus](https://rufus.ie/)（Windows 上最常用，免安裝）。
- Rufus 設定重點：
  - Boot selection → 選剛下載的 Ubuntu iso
  - Partition scheme → **GPT**（因為你的系統是 UEFI）
  - Target system → **UEFI (non CSM)**
  - 其餘預設值即可，按 START。

### 3.3 在 D: 上騰出空間（縮小 D: 磁碟區）

1. 開「磁碟管理」（開始鍵 → 輸入 `diskmgmt.msc` → Enter）。
2. 找到 **磁碟 1（D:，1TB 那顆）**，在 D: 磁碟區上按右鍵 → 「壓縮磁碟區」。
3. 輸入要壓縮的空間，建議 **150000–200000 MB（約 150–200GB）**。
4. 壓縮完成後，會看到一塊「未配置」的黑色區塊——**先不要在這裡建立新的磁碟區或格式化**，直接留給 Ubuntu 安裝程式去分割（Ubuntu 安裝程式會自己在這塊未配置空間建立 root / swap / (可選) home 分割區）。

> [!WARNING]
> 只對 **D:（Disk 1）** 做這個操作，不要對 C:（Disk 0，Windows 系統碟）做任何壓縮或分割動作。

### 3.4 從隨身碟開機安装 Ubuntu

1. 把隨身碟插上，重開機，開機時按對應熱鍵（常見 F12/F10/Esc，看機型）進入「一次性開機選單」，選隨身碟（**注意選 UEFI: 隨身碟名稱**，不要選沒有 UEFI 前綴的那個，否則會用 Legacy 模式開機）。
2. 進入 Ubuntu Live 環境後選「Install Ubuntu」。
3. 安裝類型畫面選 **「其他選項」(Something else)**，手動指定分割：
   - 找到剛才從 D: 騰出的「空閒空間」（free space）。
   - 在上面建立：
     - 一個 `/` 分割區（ext4，掛載點 `/`，把大部分空間給它，例如 140GB）
     - 一個 swap 分割區（如果筆電記憶體 ≥16GB，swap 給 4-8GB 即可；若不確定記憶體大小可以先跳過，之後再加 swapfile）
   - **Device for boot loader installation** 這一項選**你這顆實體硬碟本身**（通常會列出兩顆硬碟，選 D: 對應的那顆，而不是 C: 那顆），這樣 GRUB 才會裝在正確的 EFI 系統分割區，並自動接手開機選單同時列出 Windows 和 Ubuntu。
4. 其餘照預設走完安裝（時區、使用者帳號、語言等）。
5. 安裝完成後重開機，應該會看到 GRUB 選單同時列出 **Ubuntu** 和 **Windows Boot Manager**，兩個都能選。

---

## 4. 安裝完成後：驗證 RAPL 可讀性（Track A 的關卡判定）

進 Ubuntu 後開終端機執行：

```bash
ls /sys/class/powercap/
```

- **預期看到**類似 `intel-rapl:0`、`intel-rapl:0:0` 等節點 → 代表 RAPL 可讀，Track A 可以繼續。
- **如果是空的或資料夾不存在**：
  ```bash
  sudo modprobe intel_rapl_common
  ls /sys/class/powercap/
  ```
  再試一次。若還是不行，代表這台筆電的韌體/CPU 對 RAPL 的支援有限制，需要回來跟我討論替代方案（例如改用 `powerstat` 估算，或改讀 battery discharge rate 當 proxy）。

再確認一般使用者能不能讀（Scaphandre 不一定要 root，但要對 `/sys/class/powercap` 有讀取權限）：

```bash
cat /sys/class/powercap/intel-rapl:0/energy_uj
```

能看到一串數字（微焦耳累積值）就代表可以正常讀取。

---

## 5. 安裝 Track A 所需軟體（RAPL 驗證通過後）

```bash
# iperf3
sudo apt update
sudo apt install -y iperf3 python3-pip

# Python 套件
pip3 install pandas matplotlib seaborn

# Scaphandre（用 Docker 跑最簡單，避免自己編譯）
sudo apt install -y docker.io
sudo usermod -aG docker $USER   # 之後要登出重登入才生效
```

Scaphandre 啟動指令（登出重登入、確認 docker 權限生效後再跑）：

```bash
docker run -d --name scaphandre --privileged \
  -v /sys/class/powercap:/sys/class/powercap \
  -p 8080:8080 \
  hubblo/scaphandre prometheus
```

驗證：

```bash
curl localhost:8080/metrics | grep scaph_host_power
```

看到數值輸出（單位通常是微瓦，需除以 1,000,000 轉成瓦特）就代表整條 Track A 量測鏈路（RAPL → Scaphandre → HTTP metrics）打通了，可以進入計畫的步驟 2。

---

## 6. 卡關時怎麼辦

- **開機選單沒看到 GRUB，直接進 Windows**：可能是 UEFI 開機順序沒切過來。重開機進 BIOS，把開機順序第一位改成 "ubuntu" 對應的 EFI 開機項目（通常叫 `ubuntu` 或類似名稱）。
- **開機黑屏卡住 / 進不去 Ubuntu 桌面**：常見是獨顯（NVIDIA/Intel 混合顯示卡）驅動問題，可在 GRUB 選單按 `e` 編輯開機參數，在 `quiet splash` 後面加 `nomodeset` 試試。
- **完全裝壞、GRUB 覆蓋整個開機、Windows 進不去**：因為 Ubuntu 是裝在獨立的 Disk 1，最保險的救援方式是進 BIOS 直接把開機硬碟指定回 Disk 0（Windows 那顆），跳過 GRUB。真的不行再考慮用 Windows 安裝媒體修復開機（`bootrec /fixmbr` 等），但因為 C: 本身完全沒被動過，這種情況機率很低。

遇到任何一步卡住，把錯誤訊息或畫面描述給我，我們一起排除。
