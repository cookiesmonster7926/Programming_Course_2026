"""
mock_server.py — 教師端 CTF 競賽 API 伺服器（Port 5050）

路由總覽：
  GET /                              → Admin 監控主控台
  GET /forum                         → 學生論壇頁
  GET /api/live_chat                 → 取得含雜訊留言（支援 ?student_id=）
  GET /api/claim_flag                → 兌換 Flag（?student_id=&flag=）
  GET /api/set_level                 → 切換難度（?level=1 或 2）
  GET /api/stats                     → 即時統計 JSON
"""
import random
import string
import threading
import time
from collections import deque
from datetime import datetime
from uuid import uuid4
import csv
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

# ── 權限控制 (保護助教端 Console) ──────────────────────────────────────────────
@app.before_request
def require_admin():
    sensitive_routes = ["/", "/api/set_level", "/api/stats"]
    if request.path in sensitive_routes:
        auth = request.authorization
        if not auth or auth.username != "admin" or auth.password != "131113":
            return Response(
                "需要管理員權限", 401,
                {"WWW-Authenticate": 'Basic realm="Teacher Admin Console"'}
            )


# ── 載入有效學號名單 (CSV) ──────────────────────────────────────────────────
VALID_STUDENT_IDS = set()
try:
    with open("courseid_131113_participants.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("學號"):
                VALID_STUDENT_IDS.add(row["學號"].strip())
    print(f"✅ 成功載入 {len(VALID_STUDENT_IDS)} 位有效學號")
except Exception as e:
    print(f"⚠️ 無法載入有效學號名單: {e}")


# ── 全域執行緒鎖 ──────────────────────────────────────────────────────────────
_lock = threading.Lock()

# ── 系統狀態 ─────────────────────────────────────────────────────────────────
_state: dict = {
    "current_level": 1,
    "start_ts": time.monotonic(),
    "total_requests": 0,
    "total_messages": 0,
}

# ── 學生追蹤 ─────────────────────────────────────────────────────────────────
# {student_id: {"count": int, "last_seen": float, "rate_q": deque}}
_students: dict[str, dict] = {}
_request_log: deque = deque(maxlen=30)

# ── IP 層全域速率限制（防止未帶 student_id 的暴力請求）────────────────────────
# {ip: deque of timestamps}，每 IP 每秒最多 IP_RATE_LIMIT 次
IP_RATE_LIMIT = 5   # 次/秒
_ip_rate: dict[str, deque] = {}

# ── 允許不帶 student_id 的內部來源白名單 ─────────────────────────────────────
# 只有 ?source=internal_forum 等老師內部頁面可繞過學號要求
ALLOWED_SOURCES: set[str] = {"internal_forum"}

# ── CTF Flag 系統 ─────────────────────────────────────────────────────────────
_generated_flags: set[str] = set()
_claimed_flags:   set[str] = set()
# {student_id: {"score": int, "flags": int}}
_scoreboard: dict[str, dict] = {}

FLAG_CHARS    = string.ascii_uppercase + string.digits
FLAG_COOLDOWN = 60.0   # 1 分鐘冷卻（秒） - 固定產出不因被擊殺而重置
_last_flag_ts: float = 0.0   # 上一次生成彩蛋的時間戳
_active_flags: list[str] = []  # 多隻 Boss 共存：累積存活、等待被搶的首殺彩蛋清單

# ── 語料庫 ───────────────────────────────────────────────────────────────────
SENTENCES = [
    # ── 課業 ──
    "有沒有人要一起修 Python？",
    "今天作業好難，有人會嗎？",
    "期中考快到了好緊張，誰要一起讀書",
    "這題我不會，有人可以教我嗎",
    "教授說期末要交專案，還沒開始做",
    "明天有沒有人要去圖書館讀書",
    "物理實驗報告還沒寫，快瘋了",
    "微積分明天考試，有人要組讀書會嗎",
    "期末 project 一個人做好累，有人要組隊嗎",
    "選課系統又當機了，搶不到課",
    "今天實驗課的程式跑不起來，有人遇到一樣的問題嗎",
    "線性代數期中考剩三天，有沒有神人可以救我",
    "上課睡著被教授叫起來點名，整個班都在看我",
    "報告要求 APA 格式，有人知道怎麼引用 ChatGPT 嗎",
    "期末考排到最後一天，整個讀書計畫全毀了",
    "教授說這次作業不能用 AI，請問 2024 年了還有這種事",
    "有沒有人有上學期的考古題？跪求",
    # ── 食物 / 生活 ──
    "學餐的雞排漲價了，有夠貴",
    "下課要去哪裡吃飯？",
    "宿舍網路又斷了，誰有行動熱點",
    "有人知道哪裡可以借自行車嗎？",
    "便利商店 711 新出的飯糰好吃嗎？有人吃過嗎",
    "今天學餐只剩滷肉飯，我已經連吃五天了",
    "圖書館附近那間咖啡廳一杯要一百五，窮學生傷不起",
    "宿舍熱水器又壞了，洗冷水澡是什麼體驗",
    "有人要一起叫 UberEats 嗎？可以免運",
    "宿舍禁止煮東西但我剛剛用電鍋煮了泡麵，求平安",
    # ── 娛樂 / 抱怨 ──
    "有人去看了演唱會嗎？超羨慕",
    "剛剛打 LOL 被隊友噴了一個小時，心情很差",
    "Netflix 又漲價了，有沒有人要一起共帳",
    "今天早八遲到被記缺席，鬧鐘明明有設",
    "有人在玩原神嗎？我的樹脂快滿了",
    "昨晚追劇追到凌晨三點，今天九點有課，人間地獄",
    "下週有假日但作業一堆，假日等於沒放",
    "宿舍室友每天打遊戲到半夜，我是來念書的還是來陪玩的",
    # ── 程式 / 技術 ──
    "有人知道 for 迴圈跑到一半 break 和 continue 差在哪嗎",
    "我的 Python 一直出現 IndentationError，已經死亡",
    "昨天 debug 了三小時，問題是少打一個冒號，我要退學",
    "有人知道怎麼用 requests 抓 API 嗎？老師說這週要用到",
    "f-string 跟 format 哪個比較好？教授說都可以但我選擇困難",
    "git push 被拒絕了，有沒有人知道為什麼",
    "我的 virtual env 裝了三個，不知道哪個是對的",
    "有人會用 regex 嗎？看了一小時還是不懂 .* 和 .+ 的差別",
    "程式跑出 KeyError 但我確定那個 key 存在，我已經瘋了",
]

PHONES = [
    "0912-345-678", "0987-654-321", "0933-111-222",
    "0966-777-888", "0911-222-333", "0955-000-111",
    "0922-888-777", "0978-123-456", "0931-456-789",
    "0963-222-111", "0916-888-000", "0975-321-654",
]

EMAILS_VALID = [
    "hacker_99@gmail.com", "student_jack@ntust.edu.tw",
    "mary.wang@yahoo.com.tw", "test_user123@hotmail.com",
    "python_fan@example.com", "alice_chen@school.edu.tw",
    "bob_lin_2025@proton.me", "coding_nerd@outlook.com",
    "night_owl_2026@gmail.com", "campus_foodie@yahoo.com.tw",
    "regex_master@ntut.edu.tw", "lazy_coder_tw@gmail.com",
]

EMAILS_MALFORMED = [        # Level 2 專用
    "user@@gmail.com",
    "@school.edu.tw",
    "user@",
    "test..user@gmail",
    "noatdomain.com",
    "ab@c",
    "double@@at@gmail.com",
    "spaces in@email.com",
]

LINE_IDS = [
    "@happy_student99", "@python_beginner", "@night_owl_coder",
    "@milk_tea_lover", "@campus_cat_fan", "@debug_master_tw",
    "@weekend_hacker", "@regex_warrior", "@flask_newbie",
    "@exam_survivor", "@instant_noodle_life", "@git_push_force",
]

NOISE_TOKENS = [
    "###@@", "!!!%%%", "$$$>>>", "***!!!",
    "^^^---", "~~~###", ">>???<<", "##!!##",
    "@@$$%%", "%%^^&&", "!!>>##", "$$!!@@",
    "???###", "<<<%%%", "&&***%%",
]

# ── 秘寶提示語模板（hint text 本體，不含 dirty_flag）────────────────────────
FLAG_HINTS = [
    (
        "【系統提示】🏆 恭喜！你發現了本課隱藏秘寶。"
        "這是一組加密序號，請先將序號中的雜訊字元濾除，"
        "再帶入課堂神秘函式即可召喚分數："
    ),
    (
        "【系統廣播】🎯 限時任務觸發！偵測到加密彩蛋。"
        "序號已被污染，需先執行清洗程序，"
        "清洗完畢後帶入神秘函式提交："
    ),
    (
        "【緊急通知】🔐 隱藏關卡已解鎖！"
        "找到下方加密序號並還原其真實內容，"
        "呼叫神秘函式搶得首殺積分："
    ),
    (
        "【系統警告】⚡ 異常資料流中偵測到彩蛋訊號！"
        "請將序號中的干擾字元移除後，"
        "使用神秘函式完成兌換："
    ),
    (
        "【隱藏訊息】🏅 你的資料清洗技術觸發了彩蛋！"
        "序號已加入雜訊保護，先清洗再提交，"
        "快把它帶入神秘函式："
    ),
]

HTML_TAGS_L2 = [                # Level 2 注入
    "<script>alert('xss')</script>",
    "<h1>緊急公告</h1>",
    "<b>重要通知</b>",
    "<img src=x onerror='alert(1)'>",
    "<a href='javascript:void(0)'>點我獲獎</a>",
    "<!-- hidden: debug_mode=true -->",
    "<style>body{background:red}</style>",
    "<marquee>系統洗版中...</marquee>",
]

LEVEL_DESC = {
    1: "頭尾雜訊 + 手機 / Email / LINE 個資",
    2: "Level 1 + HTML 標籤注入 + 格式錯誤 Email",
}


# ── 資料生成 helpers ──────────────────────────────────────────────────────────

def _noise() -> str:
    token = random.choice(NOISE_TOKENS)
    if random.random() < 0.30:
        token += random.choice(NOISE_TOKENS)
    return token


def _pii_fragment(level: int) -> str:
    pool = EMAILS_VALID if (level == 1 or random.random() < 0.5) else EMAILS_MALFORMED
    p, e, l = random.choice(PHONES), random.choice(pool), random.choice(LINE_IDS)
    roll = random.random()
    if roll < 0.20:   return f"  電話：{p}"
    elif roll < 0.38: return f"  聯絡我：{e}"
    elif roll < 0.52: return f"  Line：{l}"
    elif roll < 0.68: return f"  電話 {p}，email {e}"
    elif roll < 0.82: return f"  email {e}，Line {l}"
    elif roll < 0.93: return f"  電話 {p}，Line {l}"
    else:             return f"  電話 {p}，email {e}，Line {l}"


def _build_raw_text(level: int) -> str:
    parts: list[str] = []
    if random.random() < 0.60:
        parts.append(_noise() + " ")
    parts.append(random.choice(SENTENCES))
    parts.append(_pii_fragment(level))
    if random.random() < 0.60:
        parts.append(" " + _noise())
    raw = "".join(parts)

    if level == 2 and random.random() < 0.75:
        tag = random.choice(HTML_TAGS_L2)
        pos = random.randint(0, len(raw))
        raw = raw[:pos] + tag + raw[pos:]

    return raw


def _make_dirty_flag(clean_flag: str) -> str:
    """
    SYSTEM_FLAG_A1B2C3D4 → SYSTEM_FLAG_{A1!B2@C3#D4}
    在後綴第 2、4、6 位後分別插入 !、@、#，並用 {} 包裹。
    學生需用 re.sub(r'[!@#{}]', '', code) 還原乾淨序號。
    """
    prefix = "SYSTEM_FLAG_"
    suffix = list(clean_flag[len(prefix):])   # 8 chars
    for pos, noise in zip([6, 4, 2], ['#', '@', '!']):
        suffix.insert(pos, noise)
    return prefix + "{" + "".join(suffix) + "}"


def _try_generate_flag() -> tuple[str, str] | None:
    """
    全域 Boss 機制：每 1 分鐘生成一顆「共用彩蛋」，並且只要沒被打掉就會累積。
    只要有彩蛋還活著，所有學生的 API 都有 50% 機率會隨機看到其中一顆！
    """
    global _last_flag_ts, _active_flags
    
    with _lock:
        now_ts = time.monotonic()
        
        # 1. 檢查是否經過 60 秒，若經過即新增一顆彩蛋至累積池中
        if now_ts - _last_flag_ts >= FLAG_COOLDOWN:
            clean = "SYSTEM_FLAG_" + "".join(random.choices(FLAG_CHARS, k=8))
            _active_flags.append(clean)
            _generated_flags.add(clean)
            _last_flag_ts = now_ts
            print(f"🌟 [New Boss Spawn] 全域累積彩蛋新增: {clean} (目前活著的彩蛋數: {len(_active_flags)})")
                
        # 2. 如果目前有活著的彩蛋，給予 50% 機率讓學生在拉取訊息時看到其中一顆
        if _active_flags and random.random() < 0.5:
            chosen = random.choice(_active_flags)
            return chosen, _make_dirty_flag(chosen)
            
    return None


def _inject_noise_into_text(text: str) -> str:
    """在字串中隨機位置插入 1–2 個雜訊 token，製造 hint 本體的污染感。"""
    words = text.split("，")          # 以逗號為切分點，保留語意邊界
    if len(words) < 2:
        return text
    # 隨機選 1–2 個插入位置（不插在句首）
    n_inserts = random.randint(1, 2)
    positions = random.sample(range(1, len(words)), min(n_inserts, len(words) - 1))
    for pos in sorted(positions, reverse=True):
        words.insert(pos, _noise())
    return "，".join(words)


def _build_flag_message(dirty_flag: str, level: int) -> dict:
    """
    生成一條獨立的秘寶訊息（不混入正常留言）。
    - 從多個提示語模板中隨機挑一個
    - hint 本體內隨機插入雜訊 token（清洗時外層雜訊被 Step 1 去掉，內層仍殘留）
    - dirty_flag 的 {!@#} 噪音需學生額外寫 regex 清除
    """
    hint   = _inject_noise_into_text(random.choice(FLAG_HINTS))
    prefix = _noise()
    suffix = _noise()
    raw    = f"{prefix} {hint}{dirty_flag} {suffix}"
    return {"id": str(uuid4()), "raw_text": raw, "level": level, "is_flag": True}


def _generate_message(level: int) -> dict:
    raw = _build_raw_text(level)
    return {"id": str(uuid4()), "raw_text": raw, "level": level}


# ── 速率限制（在 _lock 內呼叫）────────────────────────────────────────────────

def _update_student_and_check_rate(student_id: str) -> bool:
    """
    更新學生的連線資料並回傳是否應被速率限制（True = 限制）。
    必須在持有 _lock 時呼叫。
    """
    now_ts = time.monotonic()
    if student_id not in _students:
        _students[student_id] = {
            "count": 0,
            "last_seen": now_ts,
            "rate_q": deque(),
        }
    s = _students[student_id]
    s["count"] += 1
    s["last_seen"] = now_ts

    q = s["rate_q"]
    while q and now_ts - q[0] > 1.0:   # 清除 1 秒外的時間戳
        q.popleft()
    if len(q) >= 2:
        return True     # 超速
    q.append(now_ts)
    return False


# ── Flask 路由 ────────────────────────────────────────────────────────────────

@app.get("/")
def admin_console():
    return render_template("admin.html")


@app.get("/forum")
def forum():
    return render_template("forum.html")


def _track_source(source_id: str) -> None:
    """
    追蹤非學生來源（source=internal_forum 等），不套速率限制。
    必須在持有 _lock 時呼叫。
    """
    now_ts = time.monotonic()
    if source_id not in _students:
        _students[source_id] = {"count": 0, "last_seen": now_ts, "rate_q": deque()}
    s = _students[source_id]
    s["count"]    += 1
    s["last_seen"] = now_ts


@app.get("/api/live_chat")
def live_chat():
    student_id = request.args.get("student_id", "").strip()
    source     = request.args.get("source",     "").strip()

    # ── IP 層全域速率保護（所有請求都過）────────────────────────────────────
    client_ip = request.remote_addr or "unknown"
    now_ts = time.monotonic()
    with _lock:
        if client_ip not in _ip_rate:
            _ip_rate[client_ip] = deque()
        q_ip = _ip_rate[client_ip]
        while q_ip and now_ts - q_ip[0] > 1.0:
            q_ip.popleft()
        if len(q_ip) >= IP_RATE_LIMIT:
            return jsonify({
                "status":      "error",
                "message":     "請求過於頻繁，請稍後再試（IP 限制：5 次/秒）",
                "retry_after": 1,
            }), 429
        q_ip.append(now_ts)

    if student_id:
        # 有學號 → 追蹤 + 學生層速率限制（2 次/秒）
        with _lock:
            limited = _update_student_and_check_rate(student_id)
        if limited:
            return jsonify({
                "status":      "error",
                "message":     f"[{student_id}] 請求過於頻繁，請降低速率（上限 2 次/秒）",
                "retry_after": 1,
            }), 429
    elif source in ALLOWED_SOURCES:
        # 白名單 source（如 internal_forum，老師的論壇頁）→ 追蹤但不限速
        with _lock:
            _track_source(f"[{source}]")
    else:
        # 沒有學號、也不在白名單 → 拒絕
        return jsonify({
            "status":  "error",
            "message": "請提供 student_id 參數（例：?student_id=B10901001）",
        }), 403

    if student_id and student_id not in VALID_STUDENT_IDS:
        return jsonify({
            "status":  "error",
            "message": f"學號 {student_id} 不在修課名單中，請確認！",
        }), 403



    with _lock:
        level = _state["current_level"]
        _state["total_requests"] += 1
        seq = _state["total_requests"]

    count    = random.randint(3, 5)
    messages = [_generate_message(level) for _ in range(count)]

    # Flag 彩蛋：獨立生成，隨機插入訊息串中
    flag_result = _try_generate_flag()
    if flag_result:
        clean_flag, dirty_flag = flag_result
        flag_msg = _build_flag_message(dirty_flag, level)
        messages.insert(random.randint(0, len(messages)), flag_msg)

    display_id = student_id or (f"[{source}]" if source else "—")
    with _lock:
        _state["total_messages"] += count
        _request_log.appendleft({
            "seq":        seq,
            "ts":         datetime.now().strftime("%H:%M:%S"),
            "student_id": display_id,
            "level":      level,
            "msg_count":  count,
            "messages":   [m["raw_text"] for m in messages],
        })

    return jsonify({"status": "success", "level": level, "messages": messages})


@app.get("/api/claim_flag")
def claim_flag():
    global _last_flag_ts, _active_flag
    
    student_id = request.args.get("student_id", "").strip()
    flag       = request.args.get("flag", "").strip()

    if not student_id or not flag:
        return jsonify({"status": "error", "message": "缺少 student_id 或 flag 參數"}), 400

    if student_id not in VALID_STUDENT_IDS:
        return jsonify({"status": "error", "message": f"學號 {student_id} 不在修課名單中"}), 403


    with _lock:
        if flag not in _generated_flags:
            return jsonify({"status": "failed", "message": "無效的 Flag，請確認字串是否正確"})

        if flag in _claimed_flags:
            return jsonify({"status": "failed", "message": "太慢了，已被搶先！"})

        # ── 首殺成功 ──
        _claimed_flags.add(flag)
        
        # 如果搶下的是存活的 active flag 之一，消滅它！
        if flag in _active_flags:
            _active_flags.remove(flag)
            print(f"💥 [Boss Defeated] 學生 {student_id} 首殺了彩蛋 {flag}！ (剩餘彩蛋數: {len(_active_flags)})")
            
        if student_id not in _scoreboard:
            _scoreboard[student_id] = {"score": 0, "flags": 0}
        _scoreboard[student_id]["score"] += 10
        _scoreboard[student_id]["flags"] += 1

    return jsonify({
        "status":      "success",
        "message":     "🎉 恭喜首殺！",
        "student_id":  student_id,
        "flag":        flag,
        "score_gained": 10,
    })


@app.get("/api/set_level")
def set_level():
    try:
        level = int(request.args.get("level", 0))
        if level not in (1, 2):
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "level 必須為 1 或 2"}), 400

    with _lock:
        _state["current_level"] = level

    return jsonify({"status": "success", "current_level": level, "desc": LEVEL_DESC[level]})


@app.get("/api/stats")
def api_stats():
    with _lock:
        elapsed = time.monotonic() - _state["start_ts"]
        h, rem  = divmod(int(elapsed), 3600)
        m, s    = divmod(rem, 60)
        now_ts  = time.monotonic()

        active = sorted(
            [
                {
                    "student_id":    sid,
                    "count":         info["count"],
                    "last_seen_ago": int(now_ts - info["last_seen"]),
                }
                for sid, info in _students.items()
                if now_ts - info["last_seen"] < 300   # 5 分鐘內算活躍
            ],
            key=lambda x: x["count"], reverse=True,
        )

        board = sorted(
            [
                {"student_id": sid, "score": d["score"], "flags": d["flags"]}
                for sid, d in _scoreboard.items()
            ],
            key=lambda x: x["score"], reverse=True,
        )

        return jsonify({
            "total_requests":   _state["total_requests"],
            "total_messages":   _state["total_messages"],
            "uptime":           f"{h:02d}:{m:02d}:{s:02d}",
            "avg_per_req":      round(_state["total_messages"] / max(_state["total_requests"], 1), 1),
            "current_level":    _state["current_level"],
            "level_desc":       LEVEL_DESC[_state["current_level"]],
            "active_students":  active,
            "scoreboard":       board,
            "generated_flags":         len(_generated_flags),
            "claimed_flags":           len(_claimed_flags),
            "flag_cooldown_remaining": max(0, int(FLAG_COOLDOWN - (now_ts - _last_flag_ts))),
            "log":                     list(_request_log)[:20],
        })


if __name__ == "__main__":
    # host='0.0.0.0' 讓同網段的學生筆電也能連進來
    # threaded=True  讓 Flask 同時處理多條請求，60 人並發不會卡 queue
    # 教室環境：學生用 http://<老師IP>:5050/api/live_chat?student_id=學號 呼叫
    print("\n" + "="*55)
    print("  📡  Mock Server 已啟動")
    print("  學生 API：http://10.22.180.180:5050/api/live_chat")
    print("  Admin  ：http://127.0.0.1:5050/")
    print("  Forum  ：http://10.22.180.180:5050/forum")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True, use_reloader=False)

