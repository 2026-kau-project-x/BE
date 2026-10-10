from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경변수/.env 에서 읽는 설정. 비밀값은 코드에 두지 않는다."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    database_url: str = "sqlite:///./projectx.db"
    # 비어 있으면 AI 호출 대신 MockAiClient 사용 (Phase 4에서 내부망 주소로 교체)
    ai_service_url: str = ""


settings = Settings()
