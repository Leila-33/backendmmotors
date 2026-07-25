from typing import List
from sqlalchemy.orm import Session
from modules.vehicles.domain.repositories.vehicle_option_repository import VehicleOptionRepository
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel
from modules.vehicles.domain.entities.vehicle_option import VehicleOption
from modules.vehicles.infrastructure.mappers.vehicle_option_mapper import (
    VehicleOptionMapper
)


class VehicleOptionRepositorySQL(VehicleOptionRepository):

    def __init__(
        self,
        db: Session
    ):
        self.db = db


    # =========================
    # CREATE
    # =========================

    def create(
        self,
        vehicle_option: VehicleOption
    ):

        model = (
            VehicleOptionMapper
            .to_model(vehicle_option)
        )

        self.db.add(model)

        self.db.flush()

        return (
            VehicleOptionMapper
            .to_domain(model)
        )


    # =========================
    # GET BY VEHICLE
    # =========================

    def get_by_vehicle(
        self,
        vehicle_id: str
    ) -> List[VehicleOption]:

        models = (
            self.db
            .query(VehicleOptionModel)
            .filter(
                VehicleOptionModel.vehicle_id == vehicle_id
            )
            .all()
        )


        return [
            VehicleOptionMapper.to_domain(model)
            for model in models
        ]


    # =========================
    # DELETE BY VEHICLE
    # =========================

    def delete_by_vehicle(
        self,
        vehicle_id: str
    ):

        (
            self.db
            .query(VehicleOptionModel)
            .filter(
                VehicleOptionModel.vehicle_id == vehicle_id
            )
            .delete(
                synchronize_session=False
            )
        )


        self.db.flush()