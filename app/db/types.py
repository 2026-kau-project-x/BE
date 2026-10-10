"""DB 공용 컬럼 타입."""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


class UtcDateTime(TypeDecorator):
    """항상 UTC(타임존 포함) datetime 으로 저장·조회되는 컬럼.

    SQLite 는 타임존을 저장하지 못해서, 읽어오면 타임존 없는(naive) datetime 이 된다 →
    API 응답에서 "Z"(UTC 표시)가 빠져 FE 가 현지 시각으로 오해할 수 있다.
    읽을 때 UTC 를 다시 붙이고, 쓸 때는 UTC 로 변환해 DB 종류와 무관하게 같은 값을 돌려준다.
    Postgres(timestamptz)는 원래 타임존을 보존하므로 이 처리가 사실상 무해하다.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("UtcDateTime 에는 타임존이 있는 datetime 만 저장할 수 있습니다")
        return value.astimezone(timezone.utc)

    def process_result_value(self, value: datetime | None, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
