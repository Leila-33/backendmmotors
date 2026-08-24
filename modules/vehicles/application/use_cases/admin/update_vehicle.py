from uuid import uuid4
import logging

from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)
from modules.vehicles.domain.exceptions import (
    VehicleAlreadyExists,
    VehicleNotFound,
)
from modules.vehicles.domain.enums import VehicleType

from modules.vehicles.application.use_cases.admin.create_vehicle import (
    AssignOptionsToVehicleUseCase,
)

from modules.vehicles.application.dtos.admin.update_vehicle_dto import (
    UpdateVehicleDTO,
)

from modules.warranties.domain.exceptions import (
    WarrantyNotAllowedForRental,
    WarrantyRequiredForSale,
)
from modules.warranties.domain.repositories.vehicle_warranty_respository import (
    VehicleWarrantyRepository,
)
from modules.warranties.domain.entities.vehicle_warranty import (
    VehicleWarranty,
)

from modules.storage.infrastrucure.s3_service import S3Service
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType

from modules.vehicles.domain.utils.license_plate import (
    normalize_license_plate,
)

logger = logging.getLogger(__name__)


class UpdateVehicleUseCase:

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
        self.vehicle_warranty_repository = (
            vehicle_warranty_repository
        )
        self.assign_options_uc = assign_options_uc
        self.unit_of_work = unit_of_work
        self.event_service = event_service
        self.s3_service = s3_service

    def execute(
        self,
        dto: UpdateVehicleDTO,
    ):

        try:

            # =====================================================
            # GET VEHICLE
            # =====================================================

            vehicle = self.repo.get_by_id(
                dto.vehicle_id
            )

            if vehicle is None:
                raise VehicleNotFound()

            # =====================================================
            # LICENSE PLATE
            # =====================================================
            license_plate = normalize_license_plate(
                dto.license_plate
            )
            if license_plate:

                existing = (
                    self.repo.get_by_license_plate(
                        license_plate
                    )
                )

                if (
                    existing
                    and existing.id != vehicle.id
                ):
                    raise VehicleAlreadyExists()

            # =====================================================
            # PAYLOAD
            # =====================================================

            update_data = dto.model_dump(
                exclude_unset=True
            )

            # =====================================================
            # WARRANTY
            # =====================================================

            if "warranty_plan_id" in update_data:

                warranty_plan_id = (
                    update_data["warranty_plan_id"]
                )

                vehicle_type = update_data.get(
                    "type",
                    vehicle.type,
                )

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
                # DELETE
                # =========================

                if warranty_plan_id is None:

                    if warranty:
                        self.vehicle_warranty_repository.delete(
                            warranty.id
                        )

                # =========================
                # CREATE
                # =========================

                elif warranty is None:

                    warranty = VehicleWarranty(
                        id=str(uuid4()),
                        vehicle_id=vehicle.id,
                        warranty_plan_id=warranty_plan_id,
                        is_active=False,
                    )

                    self.vehicle_warranty_repository.save(
                        warranty
                    )

                # =========================
                # UPDATE
                # =========================

                else:

                    warranty.warranty_plan_id = (
                        warranty_plan_id
                    )

                    self.vehicle_warranty_repository.update(
                        warranty
                    )

            # =====================================================
            # IMAGES
            # =====================================================

            images_to_delete = []

            if dto.images is not None:

                old_images = vehicle.images or []
                new_images = dto.images

                images_to_delete = list(
                    set(old_images) - set(new_images)
                )

                vehicle.images = new_images

            # =====================================================
            # VEHICLE FIELDS
            # =====================================================
            if "license_plate" in update_data:
                update_data["license_plate"] = normalize_license_plate(
                    update_data["license_plate"]
                )
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
                "license_plate",
            }

            updated_fields = []

            for key, value in update_data.items():

                if key in allowed_fields:

                    setattr(
                        vehicle,
                        key,
                        value,
                    )

                    updated_fields.append(key)

            # =====================================================
            # SAVE VEHICLE
            # =====================================================

            self.repo.update(vehicle)

            # =====================================================
            # OPTIONS
            # =====================================================

            if (
                dto.included_options is not None
                or dto.optional_options is not None
            ):

                self.assign_options_uc.execute(
                    vehicle_id=vehicle.id,
                    request=dto,
                )

            # =====================================================
            # EVENT
            # =====================================================

            self.event_service.log(
                type=EventType.VEHICLE_UPDATED,
                message="Informations véhicule mises à jour",
                vehicle_id=vehicle.id,
                user_id=dto.admin_id,
                event_metadata={
                    "updated_fields": updated_fields,
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.unit_of_work.commit()

            # =====================================================
            # DELETE OLD S3 IMAGES
            # =====================================================

            for key in images_to_delete:
                self.s3_service.delete_file(key)

            logger.info(
                "Véhicule mis à jour",
                extra={
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                    "updated_fields": updated_fields,
                },
            )

            # =====================================================
            # RESULT
            # =====================================================

            return vehicle

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur mise à jour véhicule",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise