"""Alembic 실행 환경. `alembic upgrade head` / `alembic revision --autogenerate -m "..."` 가 이 파일을 거친다.

- alembic.ini 는 ASCII 만 쓴다 (Windows 는 .ini 를 cp949 로 읽어 한글 주석이 있으면 깨짐).
- DB 주소: 테스트 등에서 config 에 sqlalchemy.url 을 넣으면 그것을, 아니면 앱 설정(DATABASE_URL)을 쓴다.
- autogenerate 비교 대상: app/db/models.py 의 모델들 (Base.metadata)
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.db import models  # noqa: F401  (모델을 import 해야 Base.metadata 에 테이블이 등록된다)
from app.db.session import Base

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
url = config.get_main_option("sqlalchemy.url") or settings.database_url
# SQLite 는 ALTER TABLE 지원이 빈약해서 "테이블 복사 후 교체" 방식(batch)으로 변경해야 한다
render_as_batch = url.startswith("sqlite")


def run_migrations_offline() -> None:
    """DB 연결 없이 SQL 문만 출력 (`alembic upgrade head --sql`)."""
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, render_as_batch=render_as_batch)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=render_as_batch)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
