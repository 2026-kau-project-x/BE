from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Trip
from app.db.session import get_db
from app.schemas.trip import TripCreate, TripOut, TripStatusUpdate
from app.services.ai_client import AiClient, get_ai_client
from app.services.trip_state import InvalidTransition, transition
from app.services.vehicle_client import VehicleClient, get_vehicle_client, nearest_available

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripOut, status_code=201)
def create_trip(
    body: TripCreate,
    db: Session = Depends(get_db),
    ai: AiClient = Depends(get_ai_client),
    vehicles: VehicleClient = Depends(get_vehicle_client),
):
    # 출발지에서 가장 가까운 가용 차량을 배정하고, 그 차량 위치로 AI 에 합류 지점을 묻는다
    vehicle = nearest_available(vehicles.list_vehicles(body.origin.lat, body.origin.lng), body.origin.lat, body.origin.lng)
    rendezvous = ai.suggest_rendezvous(
        (body.origin.lat, body.origin.lng),
        (body.destination.lat, body.destination.lng),
        (vehicle.lat, vehicle.lng) if vehicle else None,
    )
    r_lat, r_lng = rendezvous if rendezvous else (None, None)
    trip = Trip(
        origin_lat=body.origin.lat,
        origin_lng=body.origin.lng,
        dest_lat=body.destination.lat,
        dest_lng=body.destination.lng,
        dest_name=body.destination_name,
        rendezvous_lat=r_lat,
        rendezvous_lng=r_lng,
        vehicle_id=vehicle.id if vehicle else None,
    )
    db.add(trip)
    db.commit()
    return trip


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(404, "trip not found")
    return trip


@router.patch("/{trip_id}/status", response_model=TripOut)
def update_status(trip_id: int, body: TripStatusUpdate, db: Session = Depends(get_db)):
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(404, "trip not found")
    try:
        trip.status = transition(trip.status, body.status).value
    except InvalidTransition as e:
        raise HTTPException(409, str(e)) from e
    db.commit()
    return trip
