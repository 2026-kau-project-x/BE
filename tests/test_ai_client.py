"""HttpAiClient 단위 테스트 — 실제 AI 서비스 대신 httpx.MockTransport 로 응답을 흉내낸다."""

import json

import httpx
import pytest

from app.services.ai_client import HttpAiClient, get_ai_client

ORIGIN = (37.55, 126.99)
DEST = (37.56, 127.0)


def _client(handler) -> HttpAiClient:
    return HttpAiClient("http://ai.test", transport=httpx.MockTransport(handler))


def test_sends_optimize_request_and_parses_rendezvous():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"rendezvous": {"lat": 37.558, "lng": 126.998}, "meet_eta_s": 100})

    assert _client(handler).suggest_rendezvous(ORIGIN, DEST) == (37.558, 126.998)
    assert seen["path"] == "/api/v1/optimize"
    # AI 리포 OptimizeRequest 계약: walker / destination
    assert seen["body"] == {
        "walker": {"lat": 37.55, "lng": 126.99},
        "destination": {"lat": 37.56, "lng": 127.0},
    }


@pytest.mark.parametrize(
    "handler",
    [
        lambda req: httpx.Response(500),  # AI 서버 오류
        lambda req: httpx.Response(200, json={"unexpected": True}),  # 계약 위반 응답
        lambda req: httpx.Response(200, content=b"not json"),  # JSON 아님
    ],
    ids=["http-500", "missing-field", "invalid-json"],
)
def test_failures_return_none_instead_of_raising(handler):
    assert _client(handler).suggest_rendezvous(ORIGIN, DEST) is None


def test_network_error_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    assert _client(handler).suggest_rendezvous(ORIGIN, DEST) is None


def test_create_trip_without_rendezvous_when_ai_down(client):
    from app.main import app

    down = _client(lambda req: httpx.Response(503))
    app.dependency_overrides[get_ai_client] = lambda: down
    r = client.post(
        "/api/v1/trips",
        json={"origin": {"lat": 37.55, "lng": 126.99}, "destination": {"lat": 37.56, "lng": 127.0}},
    )
    # AI 장애여도 이동 생성은 성공하고, 랑데부만 비어 있어야 한다
    assert r.status_code == 201
    assert r.json()["rendezvous_lat"] is None
