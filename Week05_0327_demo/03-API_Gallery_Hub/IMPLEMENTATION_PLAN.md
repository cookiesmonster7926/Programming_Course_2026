# 實作計劃：API Gallery Hub（Week04 × Week05 火力展示）

**目標：** 把 Week04 的靜態 API 畫廊，升級為 Flask 後端 + SQLite 儲存的即時互動版本。
**架構：** Flask 後端處理抓取邏輯，Jinja2 模板渲染前端，SQLite 持久化資料，JSON API 供同學爬取。
**技術棧：** Python 3.13, Flask, SQLite, requests, pytest

---

## Stage 1：後端核心 + 測試（RED → GREEN）

**目標：** 7 個 Flask 路由 + SQLite `api_gallery` 資料表全部有測試保護
**成功標準：** `uv run pytest test_main.py -v` 全部 PASS
**狀態：** 未開始

### Task 1.1：先寫測試（RED）
**檔案：**
- 建立：`03-API_Gallery_Hub/test_main.py`

測試清單：
- `test_homepage_returns_200`
- `test_view_returns_200`
- `test_api_data_returns_empty_json`
- `test_fetch_poke_redirects`
- `test_fetch_poke_stores_data`
- `test_fetch_github_redirects`
- `test_fetch_github_stores_data`
- `test_fetch_weather_redirects`
- `test_fetch_weather_stores_data`
- `test_fetch_user_redirects`
- `test_fetch_user_stores_data`

### Task 1.2：實作後端（GREEN）
**檔案：**
- 建立：`03-API_Gallery_Hub/main.py`

路由清單：
| Route | 說明 |
|-------|------|
| `GET /` | 渲染 index.html，傳入各 source 的筆數 counts |
| `GET /fetch/poke` | 抓 PokeAPI 隨機寶可夢，存 DB，redirect / |
| `GET /fetch/github` | 抓 GitHub torvalds 資料，存 DB，redirect / |
| `GET /fetch/weather` | 抓 Open-Meteo 台中天氣，存 DB，redirect / |
| `GET /fetch/user` | 抓 RandomUser，存 DB，redirect / |
| `GET /view` | 渲染 view.html，傳入所有資料（可 ?source= 篩選）|
| `GET /api/data` | 回傳所有資料的 JSON |

DB 設計（`api_gallery` 資料表）：
```sql
CREATE TABLE api_gallery (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source     TEXT,   -- PokeAPI / GitHub / Weather / RandomUser
    title      TEXT,
    content    TEXT,
    fetched_at TEXT DEFAULT (datetime('now', 'localtime'))
)
```

---

## Stage 2：前端（HTML + CSS）

**目標：** 首頁 bento-grid + view 卡片頁，視覺風格承接 Week04 暗色主題
**狀態：** 未開始

### Task 2.1：index.html
- 英雄區塊：標題 + 「Week04 ∩ Week05」副標
- 4 張 API 卡片（bento grid）
- 每張：圖示 + API 名稱 + 說明 + 「已抓 N 筆」badge + [抓取] 按鈕
- 底部：[查看資料庫] + [查看 JSON] 按鈕

### Task 2.2：view.html
- 來源 tab 篩選（全部 / PokeAPI / GitHub / Weather / RandomUser）
- 卡片列表，依來源顯示不同邊框顏色
- 顯示 fetched_at 時間

### Task 2.3：style.css
- 暗色主題，延續 Week04 的 #000 背景
- API 色彩識別系統：
  - PokeAPI: #cd2834（寶可夢紅）
  - GitHub: #4caf87（綠）
  - Weather: #0ea5e9（天藍）
  - RandomUser: #a78bfa（紫）

---

## Stage 3：Code Review + Commit

- [ ] 跑 `code-review` skill
- [ ] 跑 `commit-flow` skill

---

完成所有 Stage 後刪除此文件。
