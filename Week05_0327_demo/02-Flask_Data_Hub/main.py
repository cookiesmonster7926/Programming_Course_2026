# =============================================================================
# Flask Data Collector Hub - 跨平台資料蒐集器
# Week 05 範例：使用 Flask + SQLite + requests 蒐集外部 API 資料
# =============================================================================

import sqlite3       # Python 內建資料庫模組，不需要安裝
import requests      # 用來發送 HTTP 請求（需安裝：uv pip install requests）
from flask import Flask, render_template, redirect, url_for, jsonify

# 建立 Flask 應用程式實例
app = Flask(__name__)

# 資料庫檔案名稱（會自動在同一個資料夾建立）
DB_FILE = "test.db"


# =============================================================================
# 資料庫初始化：建立資料表（如果還不存在）
# =============================================================================
def init_db():
    """
    每次啟動時執行，確保資料表存在。
    IF NOT EXISTS 讓我們可以安全地重複執行這段程式碼。
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_posts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            source  TEXT,    -- 資料來源，例如 "JSONPlaceholder" 或 "GitHub"
            title   TEXT,    -- 標題
            content TEXT     -- 內文
        )
    """)

    conn.commit()   # 將變更寫入磁碟
    conn.close()    # 關閉連線，釋放資源


# =============================================================================
# 路由 1：首頁 /
# 渲染首頁，上面有三顆功能按鈕
# =============================================================================
@app.route("/")
def index():
    return render_template("index.html")


# =============================================================================
# 路由 2：抓取 JSONPlaceholder 文章 /fetch_web
# 模擬「從一般網路 API 抓資料」的場景
# =============================================================================
@app.route("/fetch_web")
def fetch_web():
    # 發送 GET 請求到外部 API
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = requests.get(url, timeout=5)
    data = response.json()   # 把回應的 JSON 文字轉成 Python dict

    # 從回應資料取出我們需要的欄位
    title   = data.get("title", "（無標題）")
    content = data.get("body",  "（無內容）")

    # 存入資料庫
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO external_posts (source, title, content) VALUES (?, ?, ?)",
        ("JSONPlaceholder", title, content)
    )
    conn.commit()
    conn.close()

    # 完成後導回首頁
    return redirect(url_for("index"))


# =============================================================================
# 路由 3：抓取 GitHub 使用者資料 /fetch_github
# 模擬「從 GitHub API 抓公開資訊」的場景
# =============================================================================
@app.route("/fetch_github")
def fetch_github():
    url = "https://api.github.com/users/google"
    # GitHub API 建議在 Header 加入 Accept，讓回應格式更穩定
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()

    title   = data.get("name", "（無名稱）")
    content = data.get("bio",  "（無簡介）")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO external_posts (source, title, content) VALUES (?, ?, ?)",
        ("GitHub", title, content)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# =============================================================================
# 路由 4：顯示資料庫內容 /view
# 從資料庫讀所有紀錄，渲染成卡片頁面
# =============================================================================
@app.route("/view")
def view():
    conn = sqlite3.connect(DB_FILE)
    # row_factory 讓每一筆資料可以用「欄位名稱」來存取，例如 row["title"]
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM external_posts ORDER BY id DESC")
    posts = cursor.fetchall()   # 取出所有資料列
    conn.close()

    return render_template("view.html", posts=posts)


# =============================================================================
# 路由 5：JSON API /api/posts
# 把資料庫內容包成 JSON 回傳，讓鄰座同學可以用 requests 來抓
# =============================================================================
@app.route("/api/posts")
def api_posts():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM external_posts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # 把 sqlite3.Row 物件轉成一般的 dict，才能被 jsonify 序列化
    posts = [dict(row) for row in rows]
    return jsonify(posts)


# =============================================================================
# 啟動入口
# =============================================================================
if __name__ == "__main__":
    init_db()   # 先確保資料庫和資料表都已建立

    print("=" * 50)
    print("  Flask Data Hub 啟動中...")
    print("  開啟瀏覽器前往：http://127.0.0.1:5000")
    print("  你的 API 端點：http://127.0.0.1:5000/api/posts")
    print("=" * 50)

    app.run(debug=True)
