from app.db.database import engine, Base
from app.models import ride_group  # ensure model imported

print("Dropping old tables...")
Base.metadata.drop_all(bind=engine)

print("Creating database tables...")
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
