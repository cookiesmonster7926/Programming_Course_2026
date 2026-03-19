# 🎓 2026 程式設計課程 - 助教範例

[English](README.md) | **繁體中文**

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Managed with uv](https://img.shields.io/badge/managed%20with-uv-purple)

歡迎來到本學期的程式設計課程專案！這裡是你的**課程學習導航首頁**。

本專案存放了助教每週上課使用的範例程式碼、課堂練習以及相關的補充文件。為了讓大家在不同作業系統上都能有最順暢的開發體驗，本專案全面採用 [uv](https://astral.sh/uv) 進行 Python 環境與套件的統一管理。

> [!IMPORTANT]
> **上傳公告：**
> 每週的範例程式碼與教學文件，將會固定於 **當週的星期天** 統一推送到此 GitHub 專案。請同學記得定時回來執行 `git pull` 更新最新進度！

---

## 🗺️ 課程目錄與進度導航

請點擊下方表格中的「資料夾連結」，即可進入該週的詳細說明與程式碼頁面：

| 週次 | 目錄與連結 | 主題內容與學習重點 |
| --- | --- | --- |
| **Week 02** | [📂 Week02_0306_demo](./Week02_0306_demo/) | 開發環境建置、uv 基本操作、打字挑戰遊戲實作 |
| **Week 03** | [📂 Week03_0313_demo](./Week03_0313_demo/) | - |
| **Week 04** | 🚧 *稍後更新* | - |

*(助教每週會持續更新此表格...)*

---

## 🚀 學生專用：如何下載並執行助教的程式碼？

只要跟著以下三個簡單的步驟，就能把助教寫好的範例原封不動地在你的電腦上跑起來：

### Step 1. 安裝 uv 環境管理工具

如果你還沒安裝 `uv`，請打開終端機（Terminal）或 PowerShell 並輸入對應指令：

* **macOS / Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

* **Windows**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2. Clone 專案並同步環境

將本倉庫 Clone 到你的電腦上，接著進入資料夾並讓 `uv` 自動幫你準備好所有的 Python 版本與套件：

```bash
# 下載專案
git clone https://github.com/cookiesmonster7926/Programming_Course_2026.git

# 進入資料夾
cd Programming_Course_2026

# 一鍵同步助教的環境
uv sync
```

> 💡 **提示**：執行 `uv sync` 後，`uv` 會根據 `uv.lock` 檔自動幫你建置最純淨的虛擬環境，你完全不需要手動執行 `pip install`！

### Step 3. 執行當週範例

要執行特定週次的程式，請確認你人在 `Programming_Course_2026` 主目錄下，然後使用 `uv run` 指令加上檔案路徑即可。例如：

```bash
uv run Week02_0306_demo/main.py
```
