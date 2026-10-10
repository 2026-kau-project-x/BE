"""차량 배정·차량 목록·API 키 인증·UTC 시간 응답 테스트."""

from datetime import datetime

import pytest

from app.core.config import settings
from app.main import app
from app.services.ai_client import get_ai_client
from app.services.vehicle_client import Vehicle, nearest_available

BODY = {"origin": {"lat": 37.55, "lng": 126.99}, "destination": {"lat": 37.56, "lng": 127.0}}


class RecordingAi:
    """AI 에 무엇을 넘겼는지 기록하는 가짜 클라이언트."""

    def __init__(self):
        self.vehicle = "not-called"

    def suggest_rendezvous(self, origin, dest, vehicle=None):
        self.vehicle = vehicle
        return dest


def test_nearest_available_skips_busy_vehicles():
    vs = [Vehicle("busy", 37.55, 126.99, False), Vehicle("far", 37.60, 126.99, True), Vehicle("near", 37.56, 126.99, True)]
    assert nearest_available(vs, 37.55, 126.99).id == "near"
    assert nearest_available([vs[0]], 37.55, 126.99) is None


def test_create_trip_assigns_vehicle_and_passes_it_to_ai(client):
    ai = RecordingAi()
    app.dependency_overrides[get_ai_client] = lambda: ai
    data = client.post("/api/v1/trips", json=BODY).json()
    # Dummy 차량 중 운행 중(DUMMY-03)을 제외하고 가장 가까운 DUMMY-01 배정
    assert data["vehicle_id"] == "DUMMY-01"
    assert ai.vehicle is not None and ai.vehicle[0] > BODY["origin"]["lat"]


def test_list_vehicles(client):
    r = client.get("/api/v1/vehicles", params={"lat": 37.55, "lng": 126.99})
    assert r.status_code == 200
    assert {v["id"] for v in r.json()} == {"DUMMY-01", "DUMMY-02", "DUMMY-03"}
    assert client.get("/api/v1/vehicles", params={"lat": 999, "lng": 0}).status_code == 422


def test_timestamps_are_utc_aware(client):
    data = client.post("/api/v1/trips", json=BODY).json()
    # SQLite 에서도 타임존이 붙어 나와야 한다 (UtcDateTime)
    fetched = client.get(f"/api/v1/trips/{data['id']}").json()
    assert datetime.fromisoformat(fetched["created_at"]).utcoffset().total_seconds() == 0


@pytest.fixture()
def api_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "test-key")
    return "test-key"


def test_api_key_required_when_configured(client, api_key):
    assert client.post("/api/v1/trips", json=BODY).status_code == 401
    assert client.post("/api/v1/trips", json=BODY, headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.post("/api/v1/trips", json=BODY, headers={"X-API-Key": api_key}).status_code == 201
    assert client.get("/api/v1/vehicles", params={"lat": 37.5, "lng": 127.0}).status_code == 401
    # 헬스체크는 키 없이 통과 (ALB/ECS)
    assert client.get("/api/v1/health").status_code == 200
