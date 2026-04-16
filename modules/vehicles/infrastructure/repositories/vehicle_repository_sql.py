from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.infrastructure.db.models import VehicleModel
from infrastructure.db.session import SessionLocal


class VehicleRepositorySQL(VehicleRepository):

    def search(self, filters: dict):

        db = SessionLocal()
        try:
            query = db.query(VehicleModel)

            if "type" in filters:
                query = query.filter(VehicleModel.type == filters["type"])

            if "brand" in filters:
                query = query.filter(VehicleModel.brand == filters["brand"])

            if "model" in filters:
                query = query.filter(VehicleModel.model == filters["model"])

            if "engine_type" in filters:
                query = query.filter(VehicleModel.engine_type == filters["engine_type"])

            if "year" in filters:
                query = query.filter(VehicleModel.year >= filters["year"])

            if "mileage" in filters:
                query = query.filter(VehicleModel.mileage <= filters["mileage"])

            if "price_min" in filters:
                query = query.filter(VehicleModel.price >= filters["price_min"])

            if "price_max" in filters:
                query = query.filter(VehicleModel.price <= filters["price_max"])

            if "is_available" in filters:
                query = query.filter(VehicleModel.is_available == filters["is_available"])

            results = query.all()

            return [
                Vehicle(
                    id=v.id,
                    brand=v.brand,
                    model=v.model,
                    price=v.price,
                    type=v.type,
                    mileage=v.mileage,
                    year=v.year,
                    engine_type=v.engine_type,
                    is_available=v.is_available,
                    images=v.images or []
                )
                for v in results
            ]

        finally:
            db.close()


    def get_by_id(self, vehicle_id: str):

        db = SessionLocal()
        try:
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
                engine_type=v.engine_type,
                equipments=v.equipments or [],
                condition=v.condition,
                is_available=v.is_available,
                images=v.images or []
            )   
        finally:
            db.close()