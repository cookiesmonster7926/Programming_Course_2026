# 實作計劃：F1 夢幻車隊經理 (Django Demo Week 7)

**目標：** 用 Django 5 + FastF1 真實資料，展示 MVT 架構、ORM、Admin 後台威力
**架構：** 單一 Django project + `drivers` app，FastF1 抓 2024 賽季真實車手積分
**技術棧：** Django 5, FastF1, SQLite, Bootstrap 5 CDN, uv

---

## Stage 1：專案初始化與環境設定
**狀態：** 未開始

### Task 1.1：建立 uv 環境 + Django 專案骨架
- 建立：`Week7_0410_demo/f1_manager/` (django project)
- 建立：`Week7_0410_demo/requirements.txt`

---

## Stage 2：資料層 (Model + Migration)
**狀態：** 未開始

### Task 2.1：Driver Model
- 建立：`drivers/models.py`
- 欄位：driver_id, name, team, points, image_url, is_signed

---

## Stage 3：Views + URLs
**狀態：** 未開始

### Task 3.1：Dashboard (首頁) + Recruit (FastF1) + Driver Detail
- 建立：`drivers/views.py`
- 建立：`drivers/urls.py`

---

## Stage 4：Templates
**狀態：** 未開始

### Task 4.1：base.html + home.html + driver_detail.html
- 深色 Navbar, Hero Section, Bootstrap Grid 卡片
- Ferrari 紅框條件渲染

---

## Stage 5：Django Admin 客製化
**狀態：** 未開始

### Task 5.1：admin.py
- list_display, search_fields, list_filter
