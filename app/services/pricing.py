import math

BASE_RATE_PER_KM = 12      # ₹ per km
SURGE_THRESHOLD = 5        # rides considered busy


def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )

    return 2 * R * math.asin(math.sqrt(a))


def calculate_price(pickup_lat, pickup_lng, drop_lat, drop_lng,
                    seats_remaining, is_new_ride, active_requests):

    MAX_SEATS = 4

    # base fare
    dist = distance_km(pickup_lat, pickup_lng, drop_lat, drop_lng)
    base_price = dist * BASE_RATE_PER_KM

    # occupancy safe calculation
    occupancy = MAX_SEATS - seats_remaining
    occupancy = max(1, occupancy)

    shared_price = base_price / occupancy

    # surge ONLY when new ride created
    if is_new_ride:
        surge_multiplier = 1 + (active_requests / SURGE_THRESHOLD) * 0.3
    else:
        surge_multiplier = 1.0

    final_price = shared_price * surge_multiplier

    return round(final_price, 2)
