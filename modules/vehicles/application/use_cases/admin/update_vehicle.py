import uuid
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.api.schemas import UpdateVehicleRequest
from modules.vehicles.domain.exceptions import VehicleAlreadyExists, VehicleNotFound
from modules.vehicles.domain.enums import VehicleType
from modules.vehicles.application.use_cases.admin.create_vehicle import AssignOptionsToVehicleUseCase
from modules.warranties.domain.exceptions import (
    WarrantyNotAllowedForRental,
    WarrantyRequiredForSale
)
from core.database.unit_of_work import UnitOfWork
from modules.storage.infrastrucure.s3_service import S3Service
from modules.warranties.domain.repositories.vehicle_warranty_respository import VehicleWarrantyRepository
from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from uuid import uuid4
from modules.applications.domain.enums import EventType

class UpdateVehicle:

    def __init__(
        self,
        repo: VehicleRepository,
        vehicle_warranty_repository: VehicleWarrantyRepository,
        assign_options_uc: AssignOptionsToVehicleUseCase,
        event_service,
        unit_of_work: UnitOfWork,
        s3_service: S3Service,
    ):
        self.repo = repo
        self.vehicle_warranty_repository = vehicle_warranty_repository
        self.assign_options_uc = assign_options_uc
        self.unit_of_work = unit_of_work
        self.event_service = event_service
        self.s3_service = s3_service

    def execute(
        self,
        vehicle_id: str,
        data: UpdateVehicleRequest,
        current_admin
    ):

        # =========================
        # 1. GET VEHICLE
        # =========================
        vehicle = self.repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # 2. LICENSE PLATE
        # =========================
        if data.license_plate:

            existing = self.repo.get_by_license_plate(
                data.license_plate
            )

            if existing and existing.id != vehicle.id:
                raise VehicleAlreadyExists()

        # =========================
        # 3. WARRANTY
        # =========================
        payload = data.model_dump(exclude_unset=True)

        if "warranty_plan_id" in payload:

                warranty_plan_id = payload["warranty_plan_id"]
                vehicle_type = payload.get("type", vehicle.type)

                if (
                    vehicle_type == VehicleType.SALE
                    and warranty_plan_id is None
                ):
                    raise WarrantyRequiredForSale()

                if (
                    vehicle_type == VehicleType.RENT
                    and warranty_plan_id is not None
                ):
                    raise WarrantyNotAllowedForRental()

                warranty = (
                    self.vehicle_warranty_repository
                    .get_by_vehicle_id(vehicle.id)
                )


                # =========================
                # DELETE WARRANTY
                # =========================
                if warranty_plan_id is None:

                    if warranty:
                        self.vehicle_warranty_repository.delete(
                            warranty.id
                        )


                # =========================
                # CREATE WARRANTY
                # =========================
                elif warranty is None:

                    warranty = VehicleWarranty(
                        id=str(uuid4()),
                        vehicle_id=vehicle.id,
                        warranty_plan_id=warranty_plan_id,
                        is_active=False
                    )

                    self.vehicle_warranty_repository.save(
                        warranty
                    )


                # =========================
                # UPDATE WARRANTY
                # =========================
                else:

                    warranty.warranty_plan_id = warranty_plan_id

                    self.vehicle_warranty_repository.update(
                        warranty
                    )
        # =========================
        # 4. IMAGES
        # =========================
        if data.images is not None:

            old_images = vehicle.images or []
            new_images = data.images

            images_to_delete = list(
                set(old_images) - set(new_images)
            )

            vehicle.images = new_images

        else:
            images_to_delete = []

        # =========================
        # 5. UPDATE FIELDS
        # =========================
        update_data = data.model_dump(exclude_unset=True)

        allowed_fields = {
            "brand",
            "model",
            "price",
            "type",
            "mileage",
            "year",
            "description",
            "engine_type",
            "equipments",
            "condition",
            "is_available",
            "license_plate",
        }

        updated_fields = []

        for key, value in update_data.items():

            if key in allowed_fields:

                setattr(vehicle, key, value)

                updated_fields.append(key)

        # =========================
        # 6. SAVE VEHICLE
        # =========================
        self.repo.update(vehicle)
        
        self.event_service.log(
            type=EventType.VEHICLE_UPDATED,
            message="Informations véhicule mises à jour",
            vehicle_id=vehicle.id,
            user_id=current_admin.id,
            event_metadata={
                "updated_fields": updated_fields,
            }
        )
        # =========================
        # 7. UPDATE OPTIONS
        # =========================
        if (
            data.included_options is not None
            or data.optional_options is not None
        ):
            self.assign_options_uc.execute(
                vehicle_id=vehicle.id,
                request=data,
            )

        # =========================
        # 8. COMMIT
        # =========================
        self.unit_of_work.commit()

        # =========================
        # 9. DELETE REMOVED IMAGES
        # =========================
        # Après le commit uniquement
        for key in images_to_delete:
            self.s3_service.delete_file(key)

        # =========================
        # 10. RESPONSE
        # =========================
        return vehicle