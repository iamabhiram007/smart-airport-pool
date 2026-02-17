from sqlalchemy import Column, String, Integer, Float
from app.db.database import Base
import uuid

class RideGroup(Base):
    __tablename__ = "ride_groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    available_seats = Column(Integer, default=4)
    available_luggage = Column(Integer, default=4)

    # NEW: location of first passenger (ride anchor point)
    pickup_lat = Column(Float, nullable=True)
    pickup_lng = Column(Float, nullable=True)
