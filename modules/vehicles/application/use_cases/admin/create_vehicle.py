import uuid
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.api.schemas import (
    CreateVehicleRequest,
)
from modules.vehicles.domain.enums import (
    VehicleOptionType,
    VehicleType,
    VehicleStatus
)
from modules.warranties.domain.exceptions import (
    WarrantyRequiredForSale
)
from modules.vehicles.domain.entities.vehicle_option import VehicleOption
from modules.vehicles.domain.exceptions import VehicleNotFound, VehicleAlreadyExists
from modules.options.domain.exceptions import OptionNotFound
from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.applications.domain.enums import EventType

class CreateVehicle:

    def __init__(
        self,
        repo,
        assign_options_uc,
        event_service,
        unit_of_work
    ):
        self.repo = repo
        self.assign_options_uc = assign_options_uc
        self.event_service = event_service
        self.unit_of_work = unit_of_work


    def execute(
        self,
        request: CreateVehicleRequest,
        current_admin
    ):

        try:

            # =========================
            # CHECK DUPLICATE
            # =========================

            if request.license_plate:

                existing = (
                    self.repo
                    .get_by_license_plate(
                        request.license_plate
                    )
                )

                if existing:
                    raise VehicleAlreadyExists()


            # =========================
            # BUSINESS RULES
            # =========================

            if (
                request.type == VehicleType.SALE
                and not request.warranty_plan_id
            ):
                raise WarrantyRequiredForSale()


            if request.type == VehicleType.RENT:
                request.warranty_plan_id = None


            # =========================
            # CREATE VEHICLE DOMAIN
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
            # WARRANTY
            # =========================

            if request.warranty_plan_id:

                vehicle.warranty = VehicleWarranty(

                    id=str(uuid.uuid4()),

                    vehicle_id=vehicle.id,

                    warranty_plan_id=request.warranty_plan_id,

                    is_active=False
                )


            # =========================
            # SAVE VEHICLE
            # =========================

            vehicle = self.repo.save(vehicle)

            self.event_service.log(
    type=EventType.VEHICLE_CREATED,
    message="Véhicule créé",
    vehicle_id=vehicle.id,
    user_id=current_admin.id,
    event_metadata={
        "brand": vehicle.brand,
        "model": vehicle.model,
    }
)
            # =========================
            # ASSIGN OPTIONS
            # =========================

            self.assign_options_uc.execute(
                vehicle_id=vehicle.id,
                request=request
            )


            # =========================
            # COMMIT GLOBAL
            # =========================

            self.unit_of_work.commit()


            # =========================
            # RESPONSE
            # =========================

            return vehicle


        except Exception:

            self.unit_of_work.rollback()

            raise


class AssignOptionsToVehicleUseCase:

    def __init__(
        self,
        vehicle_repo,
        option_repo,
        vehicle_option_repo
    ):
        self.vehicle_repo = vehicle_repo
        self.option_repo = option_repo
        self.vehicle_option_repo = vehicle_option_repo


    def execute(
        self,
        vehicle_id: str,
        request
    ):

        vehicle = (
            self.vehicle_repo
            .get_by_id(vehicle_id)
        )

        if not vehicle:
            raise VehicleNotFound()


        # =========================
        # REMOVE EXISTING OPTIONS
        # =========================

        self.vehicle_option_repo.delete_by_vehicle(
            vehicle_id
        )


        # =========================
        # ADD INCLUDED
        # =========================

        for opt_id in request.included_options:

            option = (
                self.option_repo
                .get_by_id(opt_id)
            )

            if not option:
                raise OptionNotFound()


            vehicle_option = VehicleOption(
    id=str(uuid.uuid4()),
    vehicle_id=vehicle_id,
    option_id=opt_id,
    type=VehicleOptionType.INCLUDED
)

            self.vehicle_option_repo.create(
                vehicle_option
            )


        # =========================
        # ADD OPTIONAL
        # =========================

        for opt_id in request.optional_options:

            option = (
                self.option_repo
                .get_by_id(opt_id)
            )

            if not option:
                raise OptionNotFound()


            vehicle_option = VehicleOption(
    id=str(uuid.uuid4()),
    vehicle_id=vehicle_id,
    option_id=opt_id,
    type=VehicleOptionType.OPTIONAL
)

            self.vehicle_option_repo.create(
                vehicle_option
            )