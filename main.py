from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.ride_group import RideGroup
from app.services.matching import find_matching_ride
from app.services.pricing import calculate_price


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


class RideResponse(BaseModel):
    ride_group_id: str
    remaining_seats: int
    remaining_luggage: int
    price: float


# ---------------------------
# APIs
# ---------------------------

@app.post("/ride/request", response_model=RideResponse)
def create_request(req: RideRequest, db: Session = Depends(get_db)):

    ride_group = find_matching_ride(
        db,
        req.seats,
        req.luggage,
        req.pickup.lat,
        req.pickup.lng,
        req.detour_tolerance_km
    )

    is_new_ride = False

    # ---- CREATE NEW RIDE ----
    if not ride_group:
        is_new_ride = True
        ride_group = RideGroup(
            available_seats=4 - req.seats,
            available_luggage=4 - req.luggage,
            pickup_lat=req.pickup.lat,
            pickup_lng=req.pickup.lng
        )
        db.add(ride_group)
        db.commit()
        db.refresh(ride_group)

    else:
        # ---- ATOMIC BOOKING ----
        try:
            ride_group.available_seats -= req.seats
            ride_group.available_luggage -= req.luggage

            if ride_group.available_seats < 0 or ride_group.available_luggage < 0:
                db.rollback()
                raise HTTPException(status_code=409, detail="Ride just became full, retry")

            db.commit()
            db.refresh(ride_group)

        except Exception:
            db.rollback()
            raise

    # capped demand proxy (cheap & safe)
    active_rides = min(db.query(RideGroup).count(), 20)

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
        "ride_group_id": str(ride_group.id),
        "remaining_seats": ride_group.available_seats,
        "remaining_luggage": ride_group.available_luggage,
        "price": price
    }


@app.get("/ride/groups")
def list_ride_groups(db: Session = Depends(get_db)):
    groups = db.query(RideGroup).all()

    return [
        {
            "id": str(g.id),
            "available_seats": g.available_seats,
            "available_luggage": g.available_luggage,
            "pickup_lat": g.pickup_lat,
            "pickup_lng": g.pickup_lng
        }
        for g in groups
    ]


@app.get("/health")
def health_check():
    return {"status": "ok"}
