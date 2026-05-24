from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.api.schemas import UpdateVehicleRequest
from modules.vehicles.application.use_cases.admin.create_vehicle import AssignOptionsToVehicleUseCase, VehicleMapper
from modules.core.exceptions import (
    VehicleNotFound,
    VehicleAlreadyExists
)
class UpdateVehicle:

    def __init__(
        self,
        repo: VehicleRepository,
        assign_options_uc: AssignOptionsToVehicleUseCase
    ):
        self.repo = repo
        self.assign_options_uc = assign_options_uc

    def execute(self, vehicle_id: str, data: UpdateVehicleRequest):

        # =========================
        # 1. GET VEHICLE
        # =========================
        vehicle = self.repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()
        
        if data.license_plate:

            existing = self.repo.get_by_license_plate(
                data.license_plate
            )

        if existing and existing.id != vehicle.id:
            raise VehicleAlreadyExists()

        # =========================
        # 2. HANDLE IMAGES (IMPORTANT)
        # =========================
        if data.images is not None:
            old_images = set(vehicle.images or [])
            new_images = set(data.images or [])

            # 🔥 images supprimées par l'utilisateur
            images_to_delete = old_images - new_images

            for key in images_to_delete:
                self.repo.delete_image_from_s3(key)

            # 👉 update images
            vehicle.images = list(new_images)

        # =========================
        # 3. UPDATE FIELDS (SAFE)
        # =========================
        update_data = data.model_dump(exclude_unset=True)

        allowed_fields = {
            "brand", "model", "price", "type",
            "mileage", "year", "description",
            "engine_type", "equipments",
            "condition", "is_available", "license_plate"
            # ⚠️ images retiré d’ici (déjà géré)
        }

        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(vehicle, key, value)

        # =========================
        # 4. SAVE VEHICLE
        # =========================
        self.repo.update(vehicle)

        # =========================
        # 5. UPDATE OPTIONS
        # =========================
        if (
            data.included_options is not None or
            data.optional_options is not None
        ):
            self.assign_options_uc.execute(
                vehicle_id=vehicle.id,
                request=data
            )

        # =========================
        # 6. RESPONSE
        # =========================
        return VehicleMapper.to_response(vehicle)