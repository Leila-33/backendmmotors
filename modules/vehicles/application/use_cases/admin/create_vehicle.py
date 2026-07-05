import uuid
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.core.exceptions import (
    VehicleNotFound,
    OptionNotFound,
    VehicleAlreadyExists,
    WarrantyRequiredForSale
)

from modules.vehicles.api.schemas import (
    CreateVehicleRequest,
    VehicleResponse,
    OptionDTO,
    VehicleWarrantyResponse,
    WarrantyPlanResponse
)
from modules.core.enums import (
    VehicleOptionType,
    VehicleType,
    VehicleStatus
)

from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from core.config import settings
from modules.storage.api.upload_routes import get_s3_client
class CreateVehicle:

    def __init__(self, repo, assign_options_uc):
        self.repo = repo
        self.assign_options_uc = assign_options_uc

    def execute(self, request: CreateVehicleRequest):

        # =========================
        # CHECK DUPLICATE
        # =========================
        if request.license_plate:
            existing = self.repo.get_by_license_plate(request.license_plate)

            if existing:
                raise VehicleAlreadyExists()

        # =========================
        # BUSINESS RULES
        # =========================

        # SALE → warranty obligatoire
        if request.type == VehicleType.SALE and not request.warranty_plan_id:
            raise WarrantyRequiredForSale()

        # RENT → warranty interdite
        if request.type == VehicleType.RENT:
            request.warranty_plan_id = None

        # =========================
        # DOMAIN VEHICLE
        # =========================
        vehicle = Vehicle(
            id=str(uuid.uuid4()),
            brand=request.brand,
            model=request.model,
            price=request.price,
            type=request.type,
            mileage=request.mileage,
            year=request.year,
            description=request.description,
            engine_type=request.engine_type,
            equipments=request.equipments,
            condition=request.condition,
            is_available=False,
            images=request.images,
            license_plate=request.license_plate,
            status=VehicleStatus.AVAILABLE
        )

        # =========================
        # WARRANTY (OPTIONAL)
        # =========================
        if request.warranty_plan_id:

            vehicle.warranty = VehicleWarranty(
                id=str(uuid.uuid4()),
                vehicle_id=vehicle.id,
                warranty_plan_id=request.warranty_plan_id,
                is_active=False
            )

        # =========================
        # SAVE
        # =========================
        vehicle = self.repo.save(vehicle)

        # =========================
        # OPTIONS
        # =========================
        self.assign_options_uc.execute(
            vehicle_id=vehicle.id,
            request=request
        )

        # =========================
        # RESPONSE
        # =========================
        return VehicleMapper.to_response(vehicle)
    



class VehicleMapper:

    @staticmethod
    def to_response(
        vehicle: VehicleModel
    ) -> VehicleResponse:

        s3 = get_s3_client()

        included = []
        optional = []

        for vo in (vehicle.options or []):

            option_dto = OptionDTO(
                id=vo.option.id,
                name=vo.option.name,
                type=vo.option.type
            )

            if vo.type == VehicleOptionType.INCLUDED:
                included.append(option_dto)

            elif vo.type == VehicleOptionType.OPTIONAL:
                optional.append(option_dto)

        # =========================
        # S3 PRESIGNED URLS
        # =========================
        images = [
            s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.S3_BUCKET,
                    "Key": key
                },
                ExpiresIn=3600
            )
            for key in (vehicle.images or [])
        ]

        warranty = None

        if vehicle.warranty:

            warranty = VehicleWarrantyResponse(
                id=vehicle.warranty.id,
                warranty_plan=(
                    WarrantyPlanResponse(
                        id=vehicle.warranty.warranty_plan.id,
                        name=vehicle.warranty.warranty_plan.name,
                        price=vehicle.warranty.warranty_plan.price,
                        duration_months=(
                            vehicle.warranty
                            .warranty_plan
                            .duration_months
                        )
                    )
                    if vehicle.warranty.warranty_plan
                    else None
                )
            )

        return VehicleResponse(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            price=vehicle.price,
            type=vehicle.type.value,
            mileage=vehicle.mileage,
            year=vehicle.year,

            description=vehicle.description,

            engine_type=(
                vehicle.engine_type.value
                if vehicle.engine_type
                else None
            ),

            equipments=vehicle.equipments or [],

            condition=vehicle.condition.value,
            is_available=vehicle.is_available,

            license_plate=vehicle.license_plate,
            status = vehicle.status,
            published_at = vehicle.published_at,
            final_check_at=vehicle.final_check_at,

            images=images,

            included_options=included,
            optional_options=optional,

            warranty=warranty
        )
    


class AssignOptionsToVehicleUseCase:

    def __init__(self, vehicle_repo, option_repo, vehicle_option_repo):
        self.vehicle_repo = vehicle_repo
        self.option_repo = option_repo
        self.vehicle_option_repo = vehicle_option_repo

    def execute(self, vehicle_id: str, request):

        vehicle = self.vehicle_repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # clean replace
        self.vehicle_option_repo.delete_by_vehicle(vehicle_id)

        # INCLUDED
        for opt_id in request.included_options:

            option = self.option_repo.get_by_id(opt_id)
            if not option:
                raise OptionNotFound()

            self.vehicle_option_repo.create(
                vehicle_id=vehicle_id,
                option_id=opt_id,
                type=VehicleOptionType.INCLUDED
            )

        # OPTIONAL
        for opt_id in request.optional_options:

            option = self.option_repo.get_by_id(opt_id)
            if not option:
                raise OptionNotFound()

            self.vehicle_option_repo.create(
                vehicle_id=vehicle_id,
                option_id=opt_id,
                type=VehicleOptionType.OPTIONAL
            )

        return {"message": "Options assignées au véhicule"}


