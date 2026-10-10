from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

# 테이블 생성은 Alembic 마이그레이션이 담당한다 (`alembic upgrade head`, migrations/ 참고)
app = FastAPI(title="Project X BE", version="0.1.0")

# Flutter 웹(Chrome)은 다른 포트에서 뜨므로 브라우저 CORS 허용이 필요하다. 모바일 앱은 CORS 와 무관
if settings.cors_origin_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=settings.cors_origin_regex,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")
