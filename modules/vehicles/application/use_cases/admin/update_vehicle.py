from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.api.schemas import UpdateVehicleRequest
from modules.vehicles.application.use_cases.admin.create_vehicle import AssignOptionsToVehicleUseCase, VehicleMapper
from modules.core.exceptions import (
    VehicleNotFound,
    VehicleAlreadyExists,
    WarrantyNotAllowedForRental,
    WarrantyRequiredForSale
)
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel
from modules.core.enums import VehicleType
import uuid

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

        # =========================
        # 2. CHECK LICENSE PLATE
        # =========================
        if data.license_plate:

            existing = self.repo.get_by_license_plate(
                data.license_plate
            )

            if existing and existing.id != vehicle.id:
                raise VehicleAlreadyExists()

        # =========================
        # 3. WARRANTY RULES (IMPORTANT)
        # =========================
        payload = data.model_dump(exclude_unset=True)

        if "warranty_plan_id" in payload:

            new_warranty = data.warranty_plan_id

            # =========================
            # BUSINESS RULES (FINAL STATE)
            # =========================
            if data.type == VehicleType.SALE and new_warranty is None:
                raise WarrantyRequiredForSale()

            if data.type == VehicleType.RENT and new_warranty is not None:
                raise WarrantyNotAllowedForRental()

            # =========================
            # APPLY CHANGE
            # =========================
            if new_warranty is None:
                vehicle.warranty = None
            else:
                if vehicle.warranty:
                    vehicle.warranty.warranty_plan_id = new_warranty
                else:
                    vehicle.warranty = VehicleWarrantyModel(
                        id=str(uuid.uuid4()),
                        vehicle_id=vehicle.id,
                        warranty_plan_id=new_warranty,
                        is_active=False
                    )
        # =========================
        # 4. IMAGES (KEEP ORDER)
        # =========================
        if data.images is not None:

            old_images = vehicle.images or []
            new_images = data.images or []

            images_to_delete = set(old_images) - set(new_images)

            for key in images_to_delete:
                self.repo.delete_image_from_s3(key)

            vehicle.images = new_images

        # =========================
        # 5. UPDATE FIELDS
        # =========================
        update_data = data.model_dump(exclude_unset=True)

        allowed_fields = {
            "brand", "model", "price", "type",
            "mileage", "year", "description",
            "engine_type", "equipments",
            "condition", "is_available", "license_plate"
        }

        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(vehicle, key, value)

        # =========================
        # 6. SAVE
        # =========================
        self.repo.update(vehicle)

        # =========================
        # 7. OPTIONS
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
        # 8. RESPONSE
        # =========================
        return VehicleMapper.to_response(vehicle)