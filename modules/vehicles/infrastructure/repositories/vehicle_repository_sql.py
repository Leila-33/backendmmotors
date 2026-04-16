from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.infrastructure.db.models import VehicleModel
from infrastructure.db.session import SessionLocal


class VehicleRepositorySQL(VehicleRepository):

    def search(self, filters: dict):

        db = SessionLocal()
        query = db.query(VehicleModel)

        if "type" in filters:
            query = query.filter(VehicleModel.type == filters["type"])

        if "brand" in filters:
            query = query.filter(VehicleModel.brand == filters["brand"])

        if "engineType" in filters:
            query = query.filter(VehicleModel.engineType == filters["engineType"])

        if "year" in filters:
            query = query.filter(VehicleModel.year >= filters["year"])

        if "mileage" in filters:
            query = query.filter(VehicleModel.mileage <= filters["mileage"])

        if "price_max" in filters:
            query = query.filter(VehicleModel.price <= filters["price_max"])

        results = query.all()

        # 🔥 mapping ORM → DOMAIN (important)
        return [
            Vehicle(
                id=v.id,
                brand=v.brand,
                model=v.model,
                price=v.price,
                type=v.type,
                mileage=v.mileage,
                year=v.year,
                engineType=v.engineType,
                isAvailable=v.isAvailable,
                images=v.images or []
            )
            for v in results
        ]
    


    def get_by_id(self, vehicle_id: str):

        db = SessionLocal()

        v = db.query(VehicleModel).filter(VehicleModel.id == vehicle_id).first()

        if not v:
            return None

        return Vehicle(
            id=v.id,
            brand=v.brand,
            model=v.model,
            price=v.price,
            type=v.type,
            mileage=v.mileage,
            year=v.year,
            description=v.description,
            engineType=v.engineType,
            equipments=v.equipments or [],
            condition=v.condition,
            isAvailable=v.isAvailable,
            images=v.images or []
        )