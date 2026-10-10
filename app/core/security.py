"""API 키 인증 (프로토타입용 최소 보호).

설정(API_KEY)이 비어 있으면 인증을 끈다 → 로컬 개발·테스트는 그대로 동작.
값이 있으면 모든 /trips·/vehicles 요청에 `X-API-Key` 헤더가 같아야 한다 (health 는 제외 — ALB/ECS 헬스체크용).

[한계] 앱에 넣은 키는 앱을 뜯어보면 꺼낼 수 있다. "아무나 서버를 두드리는 것"을 막는 수준이며,
사용자·보호자·운전자 구분이 필요한 Phase 4 에서는 계정 기반 인증(JWT 등)으로 교체해야 한다.
"""

import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = settings.api_key
    if not expected:
        return
    # compare_digest: 문자열 비교 시간이 일치 길이에 따라 달라지지 않게 해 키 추측(타이밍 공격)을 막는다
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or missing API key")
