# ── Week8 Mock Server — Docker 隔離部署 ──────────────────────────────────────
# 使用方式：
#   docker build -t week8-mock .
#   docker run -d --name mock_server -p 5050:5050 week8-mock
#   docker logs -f mock_server
#   docker stop mock_server
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# 建立非 root 使用者（安全：即使容器被攻破，也沒有 root 權限）
RUN useradd -m -u 1000 appuser

WORKDIR /app

# 只複製需要的檔案，不暴露整個專案
COPY pyproject.toml .
COPY mock_server.py .
COPY courseid_131113_participants.csv .
COPY templates/ templates/

# 安裝相依套件
RUN pip install --no-cache-dir flask requests

# 切換到非 root
USER appuser

EXPOSE 5050

# 健康檢查：每 30 秒確認 server 還活著
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5050/api/stats')" || exit 1

CMD ["python", "mock_server.py"]
