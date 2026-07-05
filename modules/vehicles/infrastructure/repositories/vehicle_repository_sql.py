from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel
from sqlalchemy.orm import joinedload
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel
from modules.core.enums import VehicleOptionType
from core.config import settings
from modules.storage.api.upload_routes import get_s3_client
from modules.vehicles.api.schemas import (
    VehicleSearchFilters,
)
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper

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
            model = VehicleMapper.to_model(vehicle)

            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)

            return model

        except Exception:
            self.db.rollback()
            raise


    def get_by_id(self, vehicle_id: str):
        return (
            self.db.query(VehicleModel)
            .options(
                selectinload(VehicleModel.options)
                .selectinload(VehicleOptionModel.option),

                selectinload(VehicleModel.warranty)
                .selectinload(VehicleWarrantyModel.warranty_plan)
            )
            .filter(VehicleModel.id == vehicle_id)
            .first()
        )



    def update(self, vehicle: VehicleModel):

        model = (
            self.db.query(VehicleModel)
            .filter_by(id=vehicle.id)
            .first()
        )

        if not model:
            return None

        # =========================
        # 1. SIMPLE FIELDS
        # =========================
        model.brand = vehicle.brand
        model.model = vehicle.model
        model.price = vehicle.price
        model.type = vehicle.type
        model.mileage = vehicle.mileage
        model.year = vehicle.year
        model.description = vehicle.description
        model.engine_type = vehicle.engine_type
        model.equipments = vehicle.equipments
        model.condition = vehicle.condition
        model.is_available = vehicle.is_available
        model.license_plate = vehicle.license_plate
        model.images = vehicle.images
        model.status = vehicle.status
        model.published_at = vehicle.published_at,
        model.final_check_at=vehicle.final_check_at,

        # =========================
        # 2. WARRANTY (SAFE UPDATE)
        # =========================
        if vehicle.warranty:

            if model.warranty:
                model.warranty.warranty_plan_id = vehicle.warranty.warranty_plan_id
                model.warranty.is_active = vehicle.warranty.is_active
                model.warranty.start_date = vehicle.warranty.start_date
                model.warranty.end_date = vehicle.warranty.end_date
                model.warranty.current_mileage = vehicle.warranty.current_mileage
                model.warranty.max_mileage = vehicle.warranty.max_mileage

            else:
                model.warranty = VehicleWarrantyModel(
                    id=vehicle.warranty.id,
                    vehicle_id=vehicle.id,
                    warranty_plan_id=vehicle.warranty.warranty_plan_id,
                    is_active=vehicle.warranty.is_active,
                    start_date=vehicle.warranty.start_date,
                    end_date=vehicle.warranty.end_date,
                    current_mileage=vehicle.warranty.current_mileage,
                    max_mileage=vehicle.warranty.max_mileage,
                )

        # =========================
        # 3. COMMIT
        # =========================
        self.db.commit()
        self.db.refresh(model)

        return model


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

    