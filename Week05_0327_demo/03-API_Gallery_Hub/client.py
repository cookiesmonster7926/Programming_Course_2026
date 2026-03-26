# =============================================================================
# client.py — 模擬鄰座同學抓取火力展示版的 API
#
# 使用方式：
#   1. 確認鄰座的 Flask 伺服器正在執行（uv run python main.py）
#   2. 把下面的 TARGET_IP 換成鄰座的電腦 IP
#   3. 執行：uv run client.py
#   4. 可以加 ?source=PokeAPI 只抓特定來源
# =============================================================================

import requests

TARGET_IP   = "127.0.0.1"  # ← 換成鄰座的 IP
TARGET_PORT = 5002

# 可選：只抓某個來源（PokeAPI / GitHub / Weather / RandomUser）
SOURCE_FILTER = ""   # 空字串 = 抓全部

url = f"http://{TARGET_IP}:{TARGET_PORT}/api/data"
if SOURCE_FILTER:
    url += f"?source={SOURCE_FILTER}"

print("=" * 60)
print(f"  連接目標：{url}")
print("=" * 60)

try:
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        records = response.json()
        print(f"\n  成功！共取得 {len(records)} 筆資料\n")
        print("-" * 60)

        for i, rec in enumerate(records, start=1):
            src   = rec.get("source", "?")
            title = rec.get("title", "?")
            body  = rec.get("content", "?")[:50]
            time  = rec.get("fetched_at", "?")

            print(f"[{i:02d}] [{src}] {title}")
            print(f"       {body}...")
            print(f"       抓取時間：{time}")
            print()

    else:
        print(f"\n  HTTP 錯誤：{response.status_code}")

except requests.exceptions.ConnectionError:
    print(f"\n  無法連線！請確認：")
    print(f"  1. 鄰座的 Flask 是否執行中？")
    print(f"  2. IP 是否正確？（目前設定：{TARGET_IP}）")
    print(f"  3. 是否在同一個 Wi-Fi 下？")

except requests.exceptions.Timeout:
    print("\n  連線逾時，請確認 IP 是否正確。")
