from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.warranties.domain.repositories.vehicle_warranty_respository import (
    VehicleWarrantyRepository
)
from modules.warranties.infrastructure.mappers.vehicle_warranty_mapper import VehicleWarrantyMapper
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel
from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.warranties.domain.repositories.vehicle_warranty_respository import (
    VehicleWarrantyRepository,
)

class VehicleWarrantyRepositorySQL(VehicleWarrantyRepository):

    def __init__(
        self,
        db,
    ):
        self.db = db

    # =========================
    # SAVE
    # =========================
    def save(
        self,
        warranty: VehicleWarranty,
    ) -> VehicleWarranty:

        model = VehicleWarrantyMapper.to_model(
            warranty
        )

        self.db.add(model)

        return VehicleWarrantyMapper.to_domain(model)

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(
        self,
        warranty_id: str,
    ) -> VehicleWarranty | None:

        model = (
            self.db.query(VehicleWarrantyModel)
            .filter(
                VehicleWarrantyModel.id == warranty_id
            )
            .first()
        )

        if not model:
            return None

        return VehicleWarrantyMapper.to_domain(model)

    # =========================
    # GET BY VEHICLE
    # =========================
    def get_by_vehicle_id(
        self,
        vehicle_id: str,
    ) -> VehicleWarranty | None:

        model = (
            self.db.query(VehicleWarrantyModel)
            .filter(
                VehicleWarrantyModel.vehicle_id == vehicle_id
            )
            .first()
        )

        if not model:
            return None

        return VehicleWarrantyMapper.to_domain(model)

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        warranty: VehicleWarranty,
    ) -> VehicleWarranty:

        model = (
            self.db.query(VehicleWarrantyModel)
            .filter(
                VehicleWarrantyModel.id == warranty.id
            )
            .first()
        )

        if not model:
            return None

        VehicleWarrantyMapper.update_model(
            model,
            warranty,
        )

        return VehicleWarrantyMapper.to_domain(model)

    # =========================
    # DELETE
    # =========================
    def delete(
        self,
        warranty_id: str,
    ) -> None:

        model = (
            self.db.query(VehicleWarrantyModel)
            .filter(
                VehicleWarrantyModel.id == warranty_id
            )
            .first()
        )

        if model:
            self.db.delete(model)