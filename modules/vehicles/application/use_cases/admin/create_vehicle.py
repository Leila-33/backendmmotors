import uuid
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.core.exceptions import (
    VehicleNotFound,
    OptionNotFound,
    VehicleAlreadyExists
)
from modules.vehicles.api.schemas import (
    CreateVehicleRequest,
    VehicleResponse,
    OptionDTO   
)
from modules.core.enums import (
    VehicleOptionType   
)
from core.config import settings
from modules.storage.api.upload_routes import get_s3_client
class CreateVehicle:

    def __init__(self, repo, assign_options_uc):
        self.repo = repo
        self.assign_options_uc = assign_options_uc

    def execute(self, request: CreateVehicleRequest):
        if request.license_plate:
            existing = self.repo.get_by_license_plate(request.license_plate)

        if existing:
            raise VehicleAlreadyExists()

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
            is_available=request.is_available,
            images=request.images, # ✅ direct URLs
            license_plate=request.license_plate
        )

        self.repo.save(vehicle)

        self.assign_options_uc.execute(
            vehicle_id=vehicle.id,
            request=request
        )

        return VehicleMapper.to_response(vehicle)


class VehicleMapper:

    @staticmethod
    def to_response(vehicle):

        s3 = get_s3_client()

        included = []
        optional = []

        for vo in getattr(vehicle, "options", []) or []:

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
        # S3 PRESIGNED URLs
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

        return VehicleResponse(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            price=vehicle.price,
            type=vehicle.type,
            mileage=vehicle.mileage,
            year=vehicle.year,
            description=vehicle.description,
            engine_type=vehicle.engine_type,
            equipments=vehicle.equipments,
            condition=vehicle.condition,
            is_available=vehicle.is_available,
            images=images,
            included_options=included,
            optional_options=optional,
            license_plate=vehicle.license_plate
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