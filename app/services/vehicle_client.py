"""이동지원차량 위치·상태 조회.

실제 차량 관제 API 가 생기기 전까지는 DummyVehicleClient 가 "요청 위치 주변에 차량 몇 대가 있다"고
가정한 가짜 데이터를 만든다. 위치가 요청 지점 기준 고정 오프셋이라 어느 지역에서 테스트해도
비슷한 거리에 차량이 있고, 매번 같은 결과가 나와 테스트가 안정적이다.
실제 API 로 교체할 때는 VehicleClient 프로토콜만 지키는 HttpVehicleClient 를 추가하면 된다.
"""

from dataclasses import dataclass
from typing import Protocol

from app.services.geo import haversine_m


@dataclass(frozen=True)
class Vehicle:
    id: str
    lat: float
    lng: float
    available: bool  # False = 다른 승객 운행 중


class VehicleClient(Protocol):
    def list_vehicles(self, near_lat: float, near_lng: float) -> list[Vehicle]: ...


# (id, 위도 오프셋, 경도 오프셋, 가용 여부). 위도 0.01° ≈ 1.1 km, 경도 0.01° ≈ 0.9 km(서울)
_DUMMY_FLEET = [
    ("DUMMY-01", +0.012, +0.004, True),  # 북쪽 약 1.4 km
    ("DUMMY-02", -0.006, +0.018, True),  # 남동쪽 약 1.7 km
    ("DUMMY-03", +0.002, -0.003, False),  # 바로 근처지만 운행 중 → 배정 대상 아님
]


class DummyVehicleClient:
    def list_vehicles(self, near_lat: float, near_lng: float) -> list[Vehicle]:
        return [Vehicle(vid, near_lat + dlat, near_lng + dlng, ok) for vid, dlat, dlng, ok in _DUMMY_FLEET]


def nearest_available(vehicles: list[Vehicle], lat: float, lng: float) -> Vehicle | None:
    """가용 차량 중 직선거리가 가장 가까운 차량. 없으면 None."""
    candidates = [v for v in vehicles if v.available]
    if not candidates:
        return None
    return min(candidates, key=lambda v: haversine_m(lat, lng, v.lat, v.lng))


def get_vehicle_client() -> VehicleClient:
    return DummyVehicleClient()
