from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경변수/.env 에서 읽는 설정. 비밀값은 코드에 두지 않는다."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    database_url: str = "sqlite:///./projectx.db"
    # 비어 있으면 AI 호출 대신 MockAiClient 사용. 로컬은 http://localhost:8001, Phase 4는 내부망 주소
    ai_service_url: str = ""
    # AI 응답 대기 한도(초). 넘으면 랑데부 없이 이동을 생성한다
    ai_timeout_s: float = 3.0
    # 비어 있으면 인증 끔. 값이 있으면 /trips·/vehicles 에 X-API-Key 헤더 필요 (app/core/security.py)
    api_key: str = ""
    # 브라우저(Flutter 웹) 호출 허용 Origin 정규식. 기본값은 로컬 개발 서버(포트 무관)만 허용
    cors_origin_regex: str = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"


settings = Settings()
