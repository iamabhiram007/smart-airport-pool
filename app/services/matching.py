from sqlalchemy.orm import Session
from app.models.ride_group import RideGroup
import math

MAX_SEATS = 4
MAX_LUGGAGE = 4


# Haversine distance (km)
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def find_matching_ride(db: Session, seats: int, luggage: int,
                       pickup_lat: float, pickup_lng: float,
                       tolerance_km: float):

    groups = db.query(RideGroup).with_for_update().all()

    best_group = None
    best_remaining = 999

    for g in groups:

        # capacity check
        remaining_seats = g.available_seats - seats
        remaining_luggage = g.available_luggage - luggage

        if remaining_seats < 0 or remaining_luggage < 0:
            continue

        # distance check
        dist = distance_km(g.pickup_lat, g.pickup_lng, pickup_lat, pickup_lng)
        if dist > tolerance_km:
            continue

        # choose fullest ride (bin packing)
        if remaining_seats < best_remaining:
            best_remaining = remaining_seats
            best_group = g

    return best_group
