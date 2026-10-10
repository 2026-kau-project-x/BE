from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.services.vehicle_client import VehicleClient, get_vehicle_client

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


class VehicleOut(BaseModel):
    id: str
    lat: float
    lng: float
    available: bool


@router.get("", response_model=list[VehicleOut])
def list_vehicles(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    vehicles: VehicleClient = Depends(get_vehicle_client),
):
    """주어진 위치 주변의 이동지원차량 목록 (현재는 Dummy). 운전자 앱·지도 표시용."""
    return [VehicleOut(**v.__dict__) for v in vehicles.list_vehicles(lat, lng)]
