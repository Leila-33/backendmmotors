from typing import List, Optional

from sqlalchemy.orm import Session

from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.warranties.domain.repositories.vehicle_warranty_respository import (
    VehicleWarrantyRepository
)

from modules.warranties.infrastructure.mappers.warranty_mapper import (
    to_domain,
    to_model
)

from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel
from modules.core.exceptions import WarrantyNotFound
from modules.warranties.infrastructure.mappers.vehicle_warranty_mapper import VehicleWarrantyMapper
class VehicleWarrantyRepositorySQL(VehicleWarrantyRepository):

    def __init__(self, session: Session):

        self.session = session

    # =========================
    # CREATE
    # =========================
    def create(self, warranty: VehicleWarranty) -> VehicleWarranty:

        model = to_model(warranty)

        self.session.add(model)

        self.session.flush()

        return to_domain(model)

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, warranty_id: str) -> Optional[VehicleWarranty]:

        model = (
            self.session.query(VehicleWarrantyModel)
            .filter(VehicleWarrantyModel.id == warranty_id)
            .first()
        )

        if not model:
            return None

        return to_domain(model)

    # =========================
    # GET BY VEHICLE ID
    # =========================
    def get_by_vehicle_id(self, vehicle_id: str) -> Optional[VehicleWarranty]:

        model = (
            self.session.query(VehicleWarrantyModel)
            .filter(
                VehicleWarrantyModel.vehicle_id == vehicle_id,
                VehicleWarrantyModel.is_active == True
            )
            .first()
        )

        if not model:
            return None

        return to_domain(model)

    # =========================
    # LIST ALL
    # =========================
    def list_all(self) -> List[VehicleWarranty]:

        models = (
            self.session.query(VehicleWarrantyModel)
            .order_by(VehicleWarrantyModel.start_date.desc())
            .all()
        )

        return [to_domain(m) for m in models]

    # =========================
    # UPDATE
    # =========================
    def update(self, warranty: VehicleWarranty) -> VehicleWarranty:

        model = (
            self.session.query(VehicleWarrantyModel)
            .filter(VehicleWarrantyModel.id == warranty.id)
            .first()
        )

        if not model:
            raise WarrantyNotFound

        model.vehicle_id = warranty.vehicle_id
        model.warranty_plan_id = warranty.warranty_plan_id
        model.start_date = warranty.start_date
        model.end_date = warranty.end_date
        model.is_active = warranty.is_active
        model.current_mileage = warranty.current_mileage

        self.session.flush()

        return to_domain(model)

    # =========================
    # COMMIT
    # =========================
    def commit(self):

        self.session.commit()


    def save(self, warranty):

        try:
            model = VehicleWarrantyModel(
                id=warranty.id,
                vehicle_id=warranty.vehicle_id,
                warranty_plan_id=warranty.warranty_plan_id,
                start_date=warranty.start_date,
                end_date=warranty.end_date,
                is_active=warranty.is_active,
                current_mileage=warranty.current_mileage,
                max_mileage=warranty.max_mileage
            )

            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)

            return to_domain(model)

        except Exception:
            self.session.rollback()
            raise

    def update(self, warranty):

        model = (
            self.session.query(VehicleWarrantyModel)
            .filter_by(id=warranty.id)
            .first()
        )

        if not model:
            return None

        model.is_active = warranty.is_active
        model.start_date = warranty.start_date
        model.end_date = warranty.end_date
        model.current_mileage = warranty.current_mileage
        model.max_mileage = warranty.max_mileage

        self.session.commit()
        self.session.refresh(model)

        return VehicleWarrantyMapper.to_domain(model)