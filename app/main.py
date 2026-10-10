from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.db import models  # noqa: F401  (테이블 등록)
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 프로토타입 단계: 마이그레이션 도구(Alembic) 도입 전까지 테이블 자동 생성
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Project X BE", version="0.1.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
