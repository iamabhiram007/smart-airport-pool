from app.db.database import engine, Base
from app.models.ride_group import RideGroup

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
