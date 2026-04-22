# =============================================================================
# client.py — 模擬鄰座同學抓取你的 API
#
# 使用方式：
#   1. 確認鄰座的 Flask 伺服器正在運行
#   2. 把下面的 TARGET_IP 換成鄰座的電腦 IP
#   3. 執行：uv run client.py
# =============================================================================

import requests

# ↓ 把這個 IP 換成鄰座同學的電腦 IP（在同一個 Wi-Fi 下）
# 如果要測試自己的：保持 127.0.0.1 即可
TARGET_IP   = "192.168.0.250"
TARGET_PORT = 5002

url = f"http://{TARGET_IP}:{TARGET_PORT}/api/data"

print("=" * 55)
print(f"  正在連接：{url}")
print("=" * 55)

try:
    response = requests.get(url, timeout=5)

    # 檢查 HTTP 狀態碼
    if response.status_code == 200:
        posts = response.json()   # 把 JSON 字串轉成 Python list

        print(f"\n  成功！共取得 {len(posts)} 筆資料\n")
        print("-" * 55)

        for i, post in enumerate(posts, start=1):
            print(f"[{i}] 來源：{post.get('source', '未知')}")
            print(f"    標題：{post.get('title', '（無）')}")
            print(f"    內容：{post.get('content', '（無）')[:60]}...")
            print()

    else:
        print(f"\n  伺服器回應錯誤：HTTP {response.status_code}")

except requests.exceptions.ConnectionError:
    print(f"\n  無法連線到 {url}")
    print("  請確認：")
    print("  1. 鄰座的 Flask 是否正在執行？")
    print("  2. IP 地址是否正確？")
    print("  3. 是否在同一個 Wi-Fi 下？")

except requests.exceptions.Timeout:
    print(f"\n  連線逾時！請確認 IP 是否正確。")
