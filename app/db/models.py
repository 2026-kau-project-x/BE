from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.types import UtcDateTime


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Trip(Base):
    """이동 1건. 상태머신(app/services/trip_state.py)이 status 를 관리한다."""

    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="REQUESTED", index=True)
    origin_lat: Mapped[float] = mapped_column(Float)
    origin_lng: Mapped[float] = mapped_column(Float)
    dest_lat: Mapped[float] = mapped_column(Float)
    dest_lng: Mapped[float] = mapped_column(Float)
    dest_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # AI가 제안한 랑데부(합류) 지점. 없으면 None
    rendezvous_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    rendezvous_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    # 배정된 이동지원차량 (가용 차량이 없으면 None). 0002 마이그레이션에서 추가
    vehicle_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # UtcDateTime: SQLite 에서도 타임존(UTC)이 유지되도록 (app/db/types.py)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime, default=_now, onupdate=_now)
