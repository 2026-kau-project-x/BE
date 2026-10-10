from typing import Protocol

from app.core.config import settings


class AiClient(Protocol):
    def suggest_rendezvous(self, dest_lat: float, dest_lng: float) -> tuple[float, float]: ...


class MockAiClient:
    """AI 서비스 준비 전 임시 구현: 목적지 근처 고정 오프셋을 랑데부 지점으로 반환."""

    def suggest_rendezvous(self, dest_lat: float, dest_lng: float) -> tuple[float, float]:
        return dest_lat + 0.0003, dest_lng + 0.0003


class HttpAiClient:
    """Phase 4: 내부망 AI 서비스(/optimize) 호출. 아직 미구현 — 인터페이스만 고정."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def suggest_rendezvous(self, dest_lat: float, dest_lng: float) -> tuple[float, float]:
        raise NotImplementedError("AI 서비스 /optimize 연동은 Phase 4")


def get_ai_client() -> AiClient:
    return HttpAiClient(settings.ai_service_url) if settings.ai_service_url else MockAiClient()
