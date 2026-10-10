from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.services.trip_state import TripStatus


class LatLng(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class TripCreate(BaseModel):
    origin: LatLng
    destination: LatLng
    destination_name: str | None = None


class TripStatusUpdate(BaseModel):
    status: TripStatus


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TripStatus
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    dest_name: str | None
    rendezvous_lat: float | None
    rendezvous_lng: float | None
    vehicle_id: str | None
    created_at: datetime
    updated_at: datetime
