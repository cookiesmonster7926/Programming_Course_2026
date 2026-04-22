"""
app.py — 學生端 Web App（Port 5001）
  GET /dashboard   → 渲染 HTML shell
  GET /api/feed    → 向 mock_server 取資料 → 五步 RE 清洗 → 回傳 JSON
"""
import re
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

MOCK_API = "http://127.0.0.1:5050/api/live_chat?source=internal_forum"

# ── PII 偵測 patterns ────────────────────────────────────────────────────────
_PII_PATTERNS = {
    "PHONE": re.compile(r'09\d{2}-\d{3}-\d{3}'),
    "EMAIL": re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'),
    "LINE":  re.compile(r'(?<![a-zA-Z0-9._%+\-])@[a-zA-Z][a-zA-Z0-9_]{5,}'),
    "HTML":  re.compile(r'<[^>]+>'),
    "FLAG":  re.compile(r'SYSTEM_FLAG_\{[A-Z0-9!@#]+\}'),
}


def detect_pii(text: str) -> list[str]:
    return [label for label, pat in _PII_PATTERNS.items() if pat.search(text)]


# ── 清洗函式 ─────────────────────────────────────────────────────────────────

def _mask_email(m: re.Match) -> str:
    local, domain = m.group(1), m.group(2)
    if len(local) <= 3:
        return local[0] + "***" + domain
    return local[:3] + "***" + local[-3:] + domain


def _mask_line_id(m: re.Match) -> str:
    name = m.group(0)[1:]
    if len(name) <= 4:
        return "@" + name[0] + "***"
    return "@" + name[:3] + "***" + name[-4:]


def clean_text(raw: str) -> str:
    """
    五步清洗：
      Step 1 — 去除頭尾連續特殊符號
      Step 2 — 手機號碼中段打碼：09XX-XXX-XXX → 09XX-***-XXX
      Step 3 — Email 打碼：hacker_99@gmail.com → hac***_99@gmail.com
      Step 4 — LINE ID 打碼：@happy_student99 → @hap***nt99
      Step 5 — 移除 HTML 標籤（Level 2 注入內容）
    """
    # Step 1
    text = re.sub(r'^[^\w\u4e00-\u9fff，。？！、…]+', '', raw)
    text = re.sub(r'[^\w\u4e00-\u9fff，。？！、…]+$', '', text)

    # Step 2
    text = re.sub(r'(09\d{2}-)(\d{3})(-\d{3})', r'\1***\3', text)

    # Step 3
    text = re.sub(
        r'([a-zA-Z0-9._%+\-]+)(@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        _mask_email, text
    )

    # Step 4
    text = re.sub(r'(?<![a-zA-Z0-9._%+\-])@[a-zA-Z][a-zA-Z0-9_]{5,}', _mask_line_id, text)

    # Step 5（Level 2：移除 HTML 標籤，並收合多餘空白）
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r' {2,}', ' ', text).strip()

    return text


# ── 路由 ────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    from flask import redirect, url_for
    return redirect(url_for("dashboard"))

@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.get("/api/feed")
def api_feed():
    try:
        resp = requests.get(MOCK_API, timeout=5)
        resp.raise_for_status()
        raw_messages = resp.json().get("messages", [])
        server_level = resp.json().get("level", 1)
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "無法連線到 Mock Server（port 5050）"}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    results = []
    for msg in raw_messages:
        raw     = msg["raw_text"]
        cleaned = clean_text(raw)
        results.append({
            "id":           msg["id"],          # UUID，供前端 Dedup 使用
            "raw_text":     raw,
            "cleaned_text": cleaned,
            "pii_labels":   detect_pii(raw),
            "level":        msg.get("level", 1),
        })

    return jsonify({
        "status":   "success",
        "level":    server_level,
        "messages": results,
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)
