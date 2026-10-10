import logging
from functools import lru_cache
from typing import Protocol

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

LatLngTuple = tuple[float, float]


class AiClient(Protocol):
    def suggest_rendezvous(self, origin: LatLngTuple, dest: LatLngTuple) -> LatLngTuple | None:
        """랑데부(합류) 지점 (lat, lng). AI 를 쓸 수 없으면 None — 이동 생성 자체는 막지 않는다."""
        ...


class MockAiClient:
    """AI 서비스 없이 개발할 때: 목적지 근처 고정 오프셋을 랑데부 지점으로 반환."""

    def suggest_rendezvous(self, origin: LatLngTuple, dest: LatLngTuple) -> LatLngTuple | None:
        return dest[0] + 0.0003, dest[1] + 0.0003


class HttpAiClient:
    """내부망 AI 서비스(AI 리포, :8001)의 POST /api/v1/optimize 를 호출한다.

    AI 장애가 사용자 이동을 막으면 안 되므로(안전 우선) 네트워크 오류·타임아웃·잘못된 응답은
    예외를 던지지 않고 경고 로그 후 None 을 돌려준다. 차량 위치(vehicle)는 Dummy Vehicle API
    연동 전이라 아직 보내지 않는다 → AI 는 목적지 자체를 랑데부 지점으로 돌려준다.
    """

    def __init__(self, base_url: str, timeout_s: float = 3.0, transport: httpx.BaseTransport | None = None) -> None:
        # transport 는 테스트에서 httpx.MockTransport 를 주입하기 위한 구멍
        self._client = httpx.Client(base_url=base_url, timeout=timeout_s, transport=transport)

    def suggest_rendezvous(self, origin: LatLngTuple, dest: LatLngTuple) -> LatLngTuple | None:
        body = {
            "walker": {"lat": origin[0], "lng": origin[1]},
            "destination": {"lat": dest[0], "lng": dest[1]},
        }
        try:
            r = self._client.post("/api/v1/optimize", json=body)
            r.raise_for_status()
            point = r.json()["rendezvous"]
            return float(point["lat"]), float(point["lng"])
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as e:
            logger.warning("AI /optimize 호출 실패 — 랑데부 없이 진행: %s", e)
            return None


@lru_cache
def get_ai_client() -> AiClient:
    # lru_cache: 요청마다 httpx 커넥션 풀을 새로 만들지 않도록 프로세스당 하나만 생성
    if settings.ai_service_url:
        return HttpAiClient(settings.ai_service_url, timeout_s=settings.ai_timeout_s)
    return MockAiClient()
