from enum import Enum


class TripStatus(str, Enum):
    """FE 화면 라벨과 대응: Request / Walking / Waiting / Rendezvous."""

    REQUESTED = "REQUESTED"
    WALKING = "WALKING"
    WAITING = "WAITING"  # 경로 이탈 등으로 대기·재탐색
    RENDEZVOUS = "RENDEZVOUS"  # 이동지원차량과 합류 지점 도착
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


_ALLOWED: dict[TripStatus, set[TripStatus]] = {
    TripStatus.REQUESTED: {TripStatus.WALKING, TripStatus.CANCELLED},
    TripStatus.WALKING: {TripStatus.WAITING, TripStatus.RENDEZVOUS, TripStatus.CANCELLED},
    TripStatus.WAITING: {TripStatus.WALKING, TripStatus.CANCELLED},
    TripStatus.RENDEZVOUS: {TripStatus.COMPLETED, TripStatus.CANCELLED},
    TripStatus.COMPLETED: set(),
    TripStatus.CANCELLED: set(),
}


class InvalidTransition(Exception):
    pass


def transition(current: str, target: TripStatus) -> TripStatus:
    """허용된 전이만 통과시킨다. 아니면 InvalidTransition."""
    cur = TripStatus(current)
    if target not in _ALLOWED[cur]:
        raise InvalidTransition(f"{cur.value} -> {target.value} 는 허용되지 않는 전이입니다")
    return target
