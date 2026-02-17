from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import engine, Base, get_db
from app.models.ride_group import RideGroup
from app.services.matching import find_matching_ride
from app.services.pricing import calculate_price


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Ride Pooling System")


# ---------------------------
# Schemas
# ---------------------------

class Location(BaseModel):
    lat: float
    lng: float


class RideRequest(BaseModel):
    passenger_id: str
    pickup: Location
    drop: Location
    seats: int = 1
    luggage: int = 1
    detour_tolerance_km: float = 3


# ---------------------------
# APIs
# ---------------------------

@app.post("/ride/request")
def create_request(req: RideRequest, db: Session = Depends(get_db)):

    # try to find pooling match
    ride_group = find_matching_ride(
        db,
        req.seats,
        req.luggage,
        req.pickup.lat,
        req.pickup.lng,
        req.detour_tolerance_km
    )

    # determine if new ride is created
    is_new_ride = False

    if not ride_group:
        is_new_ride = True
        ride_group = RideGroup(
            available_seats=4,
            available_luggage=4,
            pickup_lat=req.pickup.lat,
            pickup_lng=req.pickup.lng
        )
        db.add(ride_group)
        db.commit()
        db.refresh(ride_group)

    # ---- ATOMIC BOOKING ----
    try:
        ride_group.available_seats -= req.seats
        ride_group.available_luggage -= req.luggage

        # if someone else already took last seat
        if ride_group.available_seats < 0 or ride_group.available_luggage < 0:
            db.rollback()
            return {"error": "Ride just became full, please retry"}

        db.commit()
        db.refresh(ride_group)

    except Exception:
        db.rollback()
        raise

    # demand proxy
    active_rides = db.query(RideGroup).count()

    # pricing
    price = calculate_price(
        req.pickup.lat,
        req.pickup.lng,
        req.drop.lat,
        req.drop.lng,
        ride_group.available_seats,
        is_new_ride,
        active_rides
    )

    return {
        "ride_group_id": ride_group.id,
        "remaining_seats": ride_group.available_seats,
        "remaining_luggage": ride_group.available_luggage,
        "price": price
    }


@app.get("/ride/groups")
def list_ride_groups(db: Session = Depends(get_db)):

    groups = db.query(RideGroup).all()

    return [
        {
            "id": g.id,
            "available_seats": g.available_seats,
            "available_luggage": g.available_luggage,
            "pickup_lat": g.pickup_lat,
            "pickup_lng": g.pickup_lng
        }
        for g in groups
    ]
