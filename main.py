from fastapi import FastAPI
from modules.vehicles.api.vehicle_routes import router
from modules.vehicles.infrastructure.db.models import Base, VehicleModel
from infrastructure.db.session import engine, SessionLocal
app = FastAPI()

app.include_router(router)





def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # vérifier si déjà des données
    if db.query(VehicleModel).first():
        return

    vehicles = [
        VehicleModel(id="1", type="achat", price=20000, brand="BMW", mileage=50000, motorization="diesel", year=2020),
        VehicleModel(id="2", type="location", price=30000, brand="Audi", mileage=30000, motorization="essence", year=2022),
        VehicleModel(id="3", type="achat", price=15000, brand="Peugeot", mileage=80000, motorization="diesel", year=2018),
    ]

    db.add_all(vehicles)
    db.commit()

init_db()