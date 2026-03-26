# =============================================================================
# API Gallery Hub — Week04 × Week05 火力展示版
#
# 把 Week04 的靜態 API 畫廊，升級為 Flask 後端 + SQLite 即時儲存版本。
#
# 對比學習重點：
#   Week04：Python script 抓資料 → 生成靜態 .html 檔案 → GitHub Pages
#   Week05：按按鈕 → Flask route 即時抓 → 存進 SQLite → 同學用 IP 連進來
# =============================================================================

import random
import sqlite3

import requests
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

DB_FILE = "gallery.db"

# 天氣代碼對應中文說明（Open-Meteo WMO code）
WEATHER_CODES = {
    0: "晴天", 1: "大致晴朗", 2: "局部多雲", 3: "陰天",
    45: "有霧", 48: "結冰霧",
    51: "毛毛雨（輕）", 53: "毛毛雨（中）", 55: "毛毛雨（重）",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "陣雨（輕）", 81: "陣雨（中）", 82: "陣雨（重）",
    95: "雷陣雨",
}


# =============================================================================
# 資料庫初始化
# =============================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_gallery (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source     TEXT,
            title      TEXT,
            content    TEXT,
            fetched_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()


def insert_record(source, title, content):
    """共用的資料庫新增函式"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO api_gallery (source, title, content) VALUES (?, ?, ?)",
        (source, title, content)
    )
    conn.commit()
    conn.close()


def get_counts():
    """回傳各來源的資料筆數 dict，供首頁顯示「已抓 N 筆」"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM api_gallery GROUP BY source"
    ).fetchall()
    conn.close()
    return {row["source"]: row["cnt"] for row in rows}


# =============================================================================
# 路由
# =============================================================================

@app.route("/")
def index():
    """首頁：API 畫廊 bento grid，顯示各來源已抓筆數"""
    counts = get_counts()
    return render_template("index.html", counts=counts)


@app.route("/fetch/poke")
def fetch_poke():
    """
    抓取 PokeAPI 隨機寶可夢資料
    每次抓不同的寶可夢（1 ~ 151 第一世代），讓資料更有趣
    """
    try:
        poke_id = random.randint(1, 151)
        url = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
        data = requests.get(url, timeout=5).json()

        name    = data.get("name", "unknown").capitalize()
        poke_id = data.get("id", poke_id)
        types   = " / ".join(t["type"]["name"] for t in data.get("types", []))
        height  = data.get("height", 0)
        weight  = data.get("weight", 0)

        title   = f"#{poke_id:03d} {name}"
        content = f"類型：{types}　身高：{height * 0.1:.1f}m　體重：{weight * 0.1:.1f}kg"
        insert_record("PokeAPI", title, content)
    except Exception as e:
        print(f"[PokeAPI 錯誤] {e}")

    return redirect(url_for("index"))


@app.route("/fetch/github")
def fetch_github():
    """
    抓取 GitHub 知名用戶資料（torvalds = Linux 之父）
    展示 GitHub API 的公開資訊可以怎麼使用
    """
    try:
        url = "https://api.github.com/users/torvalds"
        data = requests.get(url, headers={"Accept": "application/vnd.github+json"}, timeout=5).json()

        name      = data.get("name", "Unknown")
        bio       = data.get("bio") or "（無簡介）"
        repos     = data.get("public_repos", 0)
        followers = data.get("followers", 0)

        title   = name
        content = f"{bio}　公開 repo：{repos} 個　追蹤者：{followers:,} 人"
        insert_record("GitHub", title, content)
    except Exception as e:
        print(f"[GitHub 錯誤] {e}")

    return redirect(url_for("index"))


@app.route("/fetch/weather")
def fetch_weather():
    """
    抓取 Open-Meteo 台中即時天氣（不需要 API Key！）
    latitude/longitude 是台中市中心的座標
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=24.1477&longitude=120.6736"
            "&current=temperature_2m,weathercode,windspeed_10m"
        )
        data    = requests.get(url, timeout=5).json()
        current = data.get("current", {})

        temp      = current.get("temperature_2m", "?")
        code      = current.get("weathercode", 0)
        windspeed = current.get("windspeed_10m", "?")
        weather   = WEATHER_CODES.get(code, f"代碼 {code}")

        title   = f"台中市 · {weather}"
        content = f"氣溫：{temp}°C　風速：{windspeed} km/h"
        insert_record("Weather", title, content)
    except Exception as e:
        print(f"[Weather 錯誤] {e}")

    return redirect(url_for("index"))


@app.route("/fetch/user")
def fetch_user():
    """
    抓取 RandomUser.me 隨機假用戶
    展示「結構化資料」：每個 user 都有固定的欄位格式
    """
    try:
        url  = "https://randomuser.me/api/"
        data = requests.get(url, timeout=5).json()
        user = data["results"][0]

        first   = user["name"]["first"]
        last    = user["name"]["last"]
        email   = user["email"]
        city    = user["location"]["city"]
        country = user["location"]["country"]

        title   = f"{first} {last}"
        content = f"Email：{email}　地點：{city}, {country}"
        insert_record("RandomUser", title, content)
    except Exception as e:
        print(f"[RandomUser 錯誤] {e}")

    return redirect(url_for("index"))


@app.route("/view")
def view():
    """
    顯示資料庫所有資料，支援 ?source= 篩選
    例如：/view?source=PokeAPI
    """
    source_filter = request.args.get("source", "")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    if source_filter:
        rows = conn.execute(
            "SELECT * FROM api_gallery WHERE source = ? ORDER BY id DESC",
            (source_filter,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM api_gallery ORDER BY id DESC"
        ).fetchall()
    conn.close()

    posts = [dict(row) for row in rows]
    sources = ["PokeAPI", "GitHub", "Weather", "RandomUser"]
    return render_template("view.html", posts=posts, active_source=source_filter, sources=sources)


@app.route("/api/data")
def api_data():
    """
    JSON API 端點 — 讓鄰座同學的 client.py 來抓
    也可以用來學習「API 是什麼」：這就是一個最簡單的 REST API
    """
    source_filter = request.args.get("source", "")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    if source_filter:
        rows = conn.execute(
            "SELECT * FROM api_gallery WHERE source = ? ORDER BY id DESC",
            (source_filter,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM api_gallery ORDER BY id DESC"
        ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


# =============================================================================
# 啟動入口
# =============================================================================
if __name__ == "__main__":
    init_db()

    print("=" * 55)
    print("  API Gallery Hub 啟動中...")
    print("  首頁：      http://127.0.0.1:5002")
    print("  資料庫：    http://127.0.0.1:5002/view")
    print("  JSON API：  http://127.0.0.1:5002/api/data")
    print("=" * 55)

    # 用 5002，避開 macOS AirPlay (5000) 和 02-Data-Hub (5001)
    app.run(debug=True, port=5002)
