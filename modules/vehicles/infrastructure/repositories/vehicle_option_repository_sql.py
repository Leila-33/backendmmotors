import uuid
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel


class VehicleOptionRepositorySQL:

    def __init__(self, db):
        self.db = db

    # =========================
    # CREATE LINK
    # =========================
    def create(self, vehicle_id: str, option_id: str, type: str):

        model = VehicleOptionModel(
            id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            option_id=option_id,
            type=type
        )

        self.db.add(model)
        self.db.commit()
        return model

    # =========================
    # GET BY VEHICLE
    # =========================
    def get_by_vehicle(self, vehicle_id: str):
        return (
            self.db.query(VehicleOptionModel)
            .filter_by(vehicle_id=vehicle_id)
            .all()
        )

    # =========================
    # DELETE BY VEHICLE
    # =========================
    def delete_by_vehicle(self, vehicle_id: str):
        self.db.query(VehicleOptionModel)\
            .filter_by(vehicle_id=vehicle_id)\
            .delete()
        self.db.commit()