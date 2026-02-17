from sqlalchemy import Column, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import uuid


class RideGroup(Base):
    __tablename__ = "ride_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    available_seats = Column(Integer, nullable=False)
    available_luggage = Column(Integer, nullable=False)

    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
