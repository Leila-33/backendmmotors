from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.core.exceptions import VehicleNotFound

class DeleteVehicle:

    def __init__(self, repo: VehicleRepository):
        self.repo = repo

    def execute(self, vehicle_id: str):

        vehicle = self.repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # DELETE IMAGES S3
        # =========================
        for key in (vehicle.images or []):
            self.repo.delete_image_from_s3(key)

        # =========================
        # DELETE VEHICLE
        # =========================
        self.repo.delete(vehicle_id)

        return {"message": "Véhicule supprimé"}