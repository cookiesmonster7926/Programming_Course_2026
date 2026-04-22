
---

# 🏎️ 專案需求文件：F1 夢幻車隊經理 (Django 實習 Demo)

## 一、 專案概述
本專案為大一基礎程式設計實習課的示範系統。系統將透過串接外部公開 API（如 Ergast F1 API 或自建 Mock API），實作一個動態的車手招募與管理平台。重點展示 Django MVT 架構的高效開發能力，特別是 ORM 的資料操作與內建 Admin 後台的威力。

## 二、 核心技術棧
* **後端框架：** Django 5.x
* **資料庫：** SQLite (搭配 Django ORM)
* **前端渲染：** Django Templates + Bootstrap 5
* **第三方套件：** `requests` (用於 API 呼叫), `pillow` (用於圖片處理，若有上傳需求)

## 三、 功能需求與實作規格

### 1. 資料庫模型設計 (Models)
完全捨棄 `CREATE TABLE`，使用 Django ORM 建立清晰的資料結構。

* **Model Name:** `Driver`
* **欄位設計：**
    * `driver_id` (CharField, unique=True)：車手 API 原始 ID。
    * `name` (CharField)：車手姓名。
    * `team` (CharField)：所屬車隊。
    * `points` (IntegerField)：目前積分。
    * `image_url` (URLField)：車手照片網址。
    * `is_signed` (BooleanField, default=True)：是否已簽約。

### 2. 核心功能視圖 (Views & URLs)

* **功能 A：車隊總覽展示牆 (Dashboard)**
    * **路由：** `/` (首頁)
    * **邏輯：** 使用 `Driver.objects.all().order_by('-points')` 撈出所有已簽約車手，並依照積分高低排序（展示 ORM 排序的極致簡潔）。
    * **畫面：** 傳遞 `drivers` 變數至前端，渲染成 Bootstrap Grid 排版的精美角色卡片。
* **功能 B：一鍵盲抽招募 (API Fetch & Create)**
    * **路由：** `/recruit/`
    * **邏輯：**
        1. 觸發 `requests.get()` 呼叫 F1 API 取回隨機或最新車手 JSON 資料。
        2. 解析 JSON。
        3. 透過 `Driver.objects.update_or_create(...)` 寫入資料庫（展示 ORM 如何優雅處理重複資料，避免 `INSERT` 遇到 Primary Key 衝突的麻煩）。
        4. `return redirect('home')` 回首頁。
* **功能 C：車手獨立資訊頁 (動態路由 - 進階展示)**
    * **路由：** `/driver/<int:id>/`
    * **邏輯：** 使用 `Driver.objects.get(id=id)` 撈取單一車手詳細資訊（展示動態 URL 參數的捕捉與查詢）。
    * **畫面：** 顯示該車手更詳盡的數據或圖表。

### 3. 前端介面設計 (Templates)
* **`base.html` (母版)：** 包含全站共用的深色系 Navbar（帶有「車隊經理系統」Logo），以及全站共用的 Bootstrap 5 CDN。
* **`home.html`：**
    * 頂部設計一個醒目的 Hero Section，包含一個大按鈕：「🏎️ 砸錢盲抽新車手！」。
    * 下方使用 `{% for driver in drivers %}` 迴圈渲染卡片。
    * **空資料狀態：** 若資料庫無資料，使用 `{% empty %}` 顯示「目前車庫空空如也，請先去招募車手！」。
    * **條件渲染：** 若車隊是 "Ferrari"，卡片邊框自動變紅色（展示 Template 內的 `{% if %}` 條件判斷）。

### 4. 內建後台極致客製化 (Django Admin)
這是火力展示的重頭戲，讓學生看到不用寫半行前端，就能擁有強大管理系統。
* 在 `admin.py` 中使用 `@admin.register(Driver)`。
* 開啟 `list_display = ('name', 'team', 'points')`：在列表頁直接顯示多個欄位。
* 開啟 `search_fields = ('name', 'team')`：自動生成搜尋列。
* 開啟 `list_filter = ('team',)`：側邊欄自動生成依據「車隊」過濾的篩選器。

---

## 四、 🌟 為什麼這個 Demo 稱得上「火力展示」？

在上課進行 Demo 時，你可以引導學生注意以下幾個「痛點解決」的瞬間：

1.  **「還在手刻 SQL 字串拼接？」**
    展示 `Driver.objects.create(name=data['name'], ...)`，對比上週用 Flask 寫 `execute("INSERT INTO table (name) VALUES (?)", (data['name'],))`，說明 ORM 如何避免 SQL Injection 並提升可讀性。
2.  **「上週的重複資料報錯怎麼辦？」**
    展示 `get_or_create` 或 `update_or_create`，告訴他們：只要一行 code，Django 就會自己幫你判斷資料庫裡有沒有這個人，有的話更新，沒有的話新增。
3.  **「免費送你一個史詩級後台」**
    這點最震撼。當你打開 `/admin`，示範你只加了三行程式碼，就擁有了一個可以搜尋、過濾、分頁、甚至整批刪除資料的管理介面時，大一學生絕對會眼睛一亮。
4.  **「排序只需一個單字」**
    在 View 裡面加上 `.order_by('-points')`，前端的車手卡片就瞬間從積分高排到低，不需要寫複雜的 `ORDER BY DESC`。
