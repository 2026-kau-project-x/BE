"""Alembic 마이그레이션 검증: 빈 DB 에 upgrade head 한 결과가 모델(app/db/models.py)과 일치하는지.

모델을 바꾸고 마이그레이션 생성(`alembic revision --autogenerate`)을 잊으면 이 테스트가 실패한다.
"""

from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

from app.db.session import Base

BE_ROOT = Path(__file__).resolve().parents[1]


def _config(url: str) -> Config:
    cfg = Config(str(BE_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BE_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    cfg.attributes["configure_logger"] = False  # pytest 로그 설정을 덮어쓰지 않게
    return cfg


def test_upgrade_matches_models_and_downgrade_works(tmp_path):
    url = f"sqlite:///{(tmp_path / 'migrate.db').as_posix()}"
    cfg = _config(url)

    command.upgrade(cfg, "head")
    engine = create_engine(url)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == [], f"모델과 마이그레이션이 다릅니다. autogenerate 필요: {diff}"

    command.downgrade(cfg, "base")
    with engine.connect() as conn:
        assert compare_metadata(MigrationContext.configure(conn), Base.metadata) != []
    engine.dispose()
