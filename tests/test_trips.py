BODY = {
    "origin": {"lat": 37.55, "lng": 126.99},
    "destination": {"lat": 37.56, "lng": 127.0},
    "destination_name": "테스트 목적지",
}


def test_health(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_create_trip_gets_mock_rendezvous(client):
    r = client.post("/api/v1/trips", json=BODY)
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "REQUESTED"
    assert data["rendezvous_lat"] is not None


def test_valid_transition_chain(client):
    tid = client.post("/api/v1/trips", json=BODY).json()["id"]
    for s in ("WALKING", "WAITING", "WALKING", "RENDEZVOUS", "COMPLETED"):
        r = client.patch(f"/api/v1/trips/{tid}/status", json={"status": s})
        assert r.status_code == 200, s
        assert r.json()["status"] == s


def test_invalid_transition_returns_409(client):
    tid = client.post("/api/v1/trips", json=BODY).json()["id"]
    r = client.patch(f"/api/v1/trips/{tid}/status", json={"status": "COMPLETED"})
    assert r.status_code == 409


def test_trip_not_found(client):
    assert client.get("/api/v1/trips/999").status_code == 404


def test_cors_allows_local_flutter_web_only(client):
    # Flutter 웹 개발 서버는 임의 포트(localhost:xxxxx)에서 뜬다
    preflight = {"Access-Control-Request-Method": "POST"}
    ok = client.options("/api/v1/trips", headers={"Origin": "http://localhost:53211", **preflight})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:53211"
    other = client.options("/api/v1/trips", headers={"Origin": "https://example.com", **preflight})
    assert "access-control-allow-origin" not in other.headers
