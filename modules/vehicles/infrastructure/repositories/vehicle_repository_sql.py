from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from sqlalchemy.orm import joinedload
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel
from modules.core.enums import VehicleOptionType
from core.config import settings
from modules.storage.api.upload_routes import get_s3_client
from modules.vehicles.api.schemas import (
    VehicleSearchFilters,
)

from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import selectinload


class VehicleRepositorySQL(VehicleRepository):

    def __init__(self, db):
        self.db = db

    def search(self, filters: VehicleSearchFilters):

        query = (
            self.db.query(VehicleModel)
            .options(
                joinedload(VehicleModel.options)
                .joinedload(VehicleOptionModel.option)
            )
            .distinct()
        )

        # =========================
        # SEARCH GLOBAL
        # =========================
        if filters.search:
            search = f"%{filters.search}%"
            query = query.filter(
                or_(
                    VehicleModel.brand.ilike(search),
                    VehicleModel.model.ilike(search)
                )
            )

        # =========================
        # 🚗 LICENSE PLATE FILTER (NEW)
        # =========================
        if filters.license_plate:
            plate = filters.license_plate.upper().replace(" ", "")

            query = query.filter(
                VehicleModel.license_plate.ilike(f"%{plate}%")
            )

        # =========================
        # FILTERS
        # =========================
        if filters.type:
            query = query.filter(VehicleModel.type == filters.type)

        if filters.brand:
            query = query.filter(VehicleModel.brand == filters.brand)

        if filters.model:
            query = query.filter(VehicleModel.model == filters.model)

        if filters.price_min:
            query = query.filter(VehicleModel.price >= filters.price_min)

        if filters.price_max:
            query = query.filter(VehicleModel.price <= filters.price_max)

        if filters.year_min:
            query = query.filter(VehicleModel.year >= filters.year_min)

        if filters.mileage_max:
            query = query.filter(VehicleModel.mileage <= filters.mileage_max)

        if filters.is_available is not None:
            query = query.filter(VehicleModel.is_available == filters.is_available)

        # =========================
        # SORT
        # =========================
        sort_column = {
            "price": VehicleModel.price,
            "year": VehicleModel.year,
            "mileage": VehicleModel.mileage,
        }[filters.sort_by]

        query = query.order_by(
            asc(sort_column) if filters.order == "asc" else desc(sort_column)
        )

        # =========================
        # TOTAL
        # =========================
        total = query.count()

        # =========================
        # ITEMS
        # =========================
        items = (
            query.offset((filters.page - 1) * filters.size)
            .limit(filters.size)
            .all()
        )

        return items, total



    def save(self, vehicle: Vehicle):

        try:
            model = VehicleModel(
                id=vehicle.id,
                brand=vehicle.brand,
                model=vehicle.model,
                price=vehicle.price,
                type=vehicle.type,
                mileage=vehicle.mileage,
                year=vehicle.year,
                description=vehicle.description,
                engine_type=vehicle.engine_type,
                equipments=vehicle.equipments,
                condition=vehicle.condition,
                is_available=vehicle.is_available,
                images=vehicle.images,
                license_plate=vehicle.license_plate
            )

            self.db.add(model)
            self.db.flush()

            self.db.commit()
            self.db.refresh(model)

            return model

        except Exception:
            self.db.rollback()
            raise


    def get_by_id(self, vehicle_id: str):

        model = (
            self.db.query(VehicleModel)
            .options(
                selectinload(VehicleModel.options)
                .selectinload(VehicleOptionModel.option)
            )
            .filter(VehicleModel.id == vehicle_id)
            .first()
        )

        if not model:
            return None

        return model

    def update(self, vehicle: Vehicle):
        model = self.db.query(VehicleModel).filter_by(id=vehicle.id).first()

        for key, value in vehicle.__dict__.items():
            setattr(model, key, value)

        self.db.commit()


    def get_all(self):
        return self.db.query(VehicleModel).all()

    def delete(self, vehicle_id: str):
        vehicle = self.db.query(VehicleModel).filter_by(id=vehicle_id).first()

        if vehicle:
            self.db.delete(vehicle)
            self.db.commit()

    def delete_image_from_s3(self, key: str):
        s3 = get_s3_client()

        s3.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=key
        )
    
    def get_by_license_plate(self, plate: str):
        return (
            self.db.query(VehicleModel)
            .filter(VehicleModel.license_plate == plate)
            .first()
        )