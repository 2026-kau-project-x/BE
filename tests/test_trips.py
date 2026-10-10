import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


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
