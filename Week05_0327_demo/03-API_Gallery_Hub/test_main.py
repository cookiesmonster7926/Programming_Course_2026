# =============================================================================
# test_main.py — API Gallery Hub 後端測試
# 執行：uv run pytest test_main.py -v
# =============================================================================

import json
import os
import pytest
from unittest.mock import patch

# 測試前把 DB 指向暫存檔，避免污染真實資料
TEST_DB = "gallery_test.db"


@pytest.fixture(autouse=True)
def isolate_db(monkeypatch):
    """每個測試使用獨立的暫存資料庫，測試完清除。"""
    import main
    monkeypatch.setattr(main, "DB_FILE", TEST_DB)
    main.init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def client():
    import main
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


# =============================================================================
# Stage 1.1：基本路由測試
# =============================================================================

def test_homepage_returns_200(client):
    """首頁應該正常回應"""
    res = client.get("/")
    assert res.status_code == 200


def test_view_returns_200(client):
    """資料庫顯示頁應該正常回應"""
    res = client.get("/view")
    assert res.status_code == 200


def test_api_data_returns_empty_json(client):
    """/api/data 應回傳空 list（資料庫剛初始化時）"""
    res = client.get("/api/data")
    assert res.status_code == 200
    assert res.content_type == "application/json"
    data = json.loads(res.data)
    assert data == []


def test_view_with_source_filter_returns_200(client):
    """/view?source=PokeAPI 應正常回應"""
    res = client.get("/view?source=PokeAPI")
    assert res.status_code == 200


# =============================================================================
# Stage 1.2：PokeAPI 抓取測試
# =============================================================================

FAKE_POKE = {
    "name": "pikachu",
    "id": 25,
    "types": [{"type": {"name": "electric"}}],
    "height": 4,
    "weight": 60,
}


def test_fetch_poke_redirects(client):
    """/fetch/poke 抓取後應 redirect 回首頁"""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_POKE
        res = client.get("/fetch/poke")
    assert res.status_code == 302


def test_fetch_poke_stores_data(client):
    """/fetch/poke 應將資料存入 DB，source 為 PokeAPI"""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_POKE
        client.get("/fetch/poke")

    res = client.get("/api/data")
    data = json.loads(res.data)
    assert len(data) == 1
    assert data[0]["source"] == "PokeAPI"
    assert "pikachu" in data[0]["title"].lower()


# =============================================================================
# Stage 1.3：GitHub API 抓取測試
# =============================================================================

FAKE_GITHUB = {
    "name": "Linus Torvalds",
    "bio": "Linux kernel creator",
    "public_repos": 7,
    "followers": 200000,
}


def test_fetch_github_redirects(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_GITHUB
        res = client.get("/fetch/github")
    assert res.status_code == 302


def test_fetch_github_stores_data(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_GITHUB
        client.get("/fetch/github")

    data = json.loads(client.get("/api/data").data)
    assert len(data) == 1
    assert data[0]["source"] == "GitHub"
    assert "Linus" in data[0]["title"]


# =============================================================================
# Stage 1.4：天氣 API 抓取測試
# =============================================================================

FAKE_WEATHER = {
    "current": {
        "temperature_2m": 28.5,
        "weathercode": 0,
        "windspeed_10m": 12.3,
    }
}


def test_fetch_weather_redirects(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_WEATHER
        res = client.get("/fetch/weather")
    assert res.status_code == 302


def test_fetch_weather_stores_data(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_WEATHER
        client.get("/fetch/weather")

    data = json.loads(client.get("/api/data").data)
    assert len(data) == 1
    assert data[0]["source"] == "Weather"
    assert "28.5" in data[0]["content"] or "28" in data[0]["content"]


# =============================================================================
# Stage 1.5：RandomUser API 抓取測試
# =============================================================================

FAKE_USER = {
    "results": [{
        "name": {"first": "John", "last": "Doe"},
        "email": "john@example.com",
        "location": {"city": "Taipei", "country": "Taiwan"},
        "picture": {"thumbnail": "https://example.com/pic.jpg"},
    }]
}


def test_fetch_user_redirects(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_USER
        res = client.get("/fetch/user")
    assert res.status_code == 302


def test_fetch_user_stores_data(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_USER
        client.get("/fetch/user")

    data = json.loads(client.get("/api/data").data)
    assert len(data) == 1
    assert data[0]["source"] == "RandomUser"
    assert "John" in data[0]["title"]


# =============================================================================
# Stage 1.6：API 資料格式測試
# =============================================================================

def test_api_data_record_has_required_fields(client):
    """每筆資料都應有 id / source / title / content / fetched_at"""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_POKE
        client.get("/fetch/poke")

    data = json.loads(client.get("/api/data").data)
    record = data[0]
    for field in ("id", "source", "title", "content", "fetched_at"):
        assert field in record, f"缺少欄位：{field}"


def test_multiple_fetches_accumulate(client):
    """多次抓取應累積資料，不會覆蓋"""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = FAKE_POKE
        client.get("/fetch/poke")
        client.get("/fetch/poke")
        client.get("/fetch/poke")

    data = json.loads(client.get("/api/data").data)
    assert len(data) == 3
