from modules.warranties.infrastructure.mappers.vehicle_warranty_mapper import VehicleWarrantyMapper
from modules.vehicles.infrastructure.mappers.vehicle_option_mapper import VehicleOptionMapper
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.vehicles.api.schemas import (
    VehicleResponse,
    OptionDTO,
 )
from modules.vehicles.domain.enums import (
    VehicleOptionType,
    
)
from modules.warranties.infrastructure.mappers.warranty_plan_mapper import WarrantyPlanMapper


class VehicleMapper:

    def __init__(self, s3_service):
        self.s3_service = s3_service

    @staticmethod
    def to_domain(
        model
    ) -> Vehicle:


        return Vehicle(

            id=model.id,


            # =========================
            # BASIC INFO
            # =========================

            brand=model.brand,

            model=model.model,

            price=model.price,

            type=model.type,

            mileage=model.mileage,

            year=model.year,


            # =========================
            # DETAILS
            # =========================

            description=model.description,

            engine_type=model.engine_type,

            equipments=(
                model.equipments
                or []
            ),

            condition=model.condition,


            # =========================
            # LICENSE
            # =========================

            license_plate=(
                model.license_plate
            ),


            # =========================
            # STATUS
            # =========================

            is_available=(
                model.is_available
            ),

            status=model.status,


            published_at=(
                model.published_at
            ),

            final_check_at=(
                model.final_check_at
            ),


            # =========================
            # MEDIA
            # =========================

            images=(
                model.images
                or []
            ),



            # =========================
            # RELATIONS DOMAIN
            # =========================

            options=[

                VehicleOptionMapper.to_domain(
                    option
                )

                for option in (
                    model.options or []
                )

            ],


            warranty=(

                VehicleWarrantyMapper.to_domain(
                    model.warranty
                )

                if model.warranty

                else None

            )

        )



    @staticmethod
    def to_model(
        vehicle: Vehicle
    ):

        return VehicleModel(

            id=vehicle.id,

            brand=vehicle.brand,

            model=vehicle.model,

            price=vehicle.price,

            type=vehicle.type,

            mileage=vehicle.mileage,

            year=vehicle.year,


            description=vehicle.description,


            engine_type=(
                vehicle.engine_type
            ),


            equipments=(
                vehicle.equipments
            ),


            condition=(
                vehicle.condition
            ),


            license_plate=(
                vehicle.license_plate
            ),


            is_available=(
                vehicle.is_available
            ),


            published_at=(
                vehicle.published_at
            ),


            final_check_at=(
                vehicle.final_check_at
            ),


            images=(
                vehicle.images
            ),


            status=(
                vehicle.status
            )

        )



    @staticmethod
    def update_model(
        model,
        vehicle: Vehicle
    ):


        model.brand = vehicle.brand

        model.model = vehicle.model

        model.price = vehicle.price

        model.type = vehicle.type

        model.mileage = vehicle.mileage

        model.year = vehicle.year


        model.description = (
            vehicle.description
        )


        model.engine_type = (
            vehicle.engine_type
        )


        model.equipments = (
            vehicle.equipments
        )


        model.condition = (
            vehicle.condition
        )


        model.license_plate = (
            vehicle.license_plate
        )


        model.is_available = (
            vehicle.is_available
        )


        model.status = (
            vehicle.status
        )


        model.published_at = (
            vehicle.published_at
        )


        model.final_check_at = (
            vehicle.final_check_at
        )


        model.images = (
            vehicle.images
        )


        return model

class VehicleResponseMapper:

    def __init__(self, s3_service):
        self.s3_service = s3_service

    def to_response(self,
        vehicle: Vehicle
    ) -> VehicleResponse:

        included = []

        optional = []



        # =========================
        # OPTIONS
        # =========================

        for vo in (
            vehicle.options or []
        ):


            if not vo.option:
                continue


            option_dto = OptionDTO(

                id=vo.option.id,

                name=vo.option.name,

                type=(
                    vo.option.type.value
                    if hasattr(
                        vo.option.type,
                        "value"
                    )
                    else vo.option.type
                )

            )


            if (
                vo.type ==
                VehicleOptionType.INCLUDED
            ):

                included.append(
                    option_dto
                )


            elif (
                vo.type ==
                VehicleOptionType.OPTIONAL
            ):

                optional.append(
                    option_dto
                )



        # =========================
        # IMAGES S3
        # =========================

        images = [
            self.s3_service.generate_download_url(key)
            for key in vehicle.images or []
        ]



        # =========================
        # WARRANTY
        # =========================

        warranty_plan = None

        if (
            vehicle.warranty
            and vehicle.warranty.warranty_plan
        ):
            warranty_plan = WarrantyPlanMapper.to_response(
                vehicle.warranty.warranty_plan
            )



        # =========================
        # RESPONSE
        # =========================

        return VehicleResponse(

            id=vehicle.id,


            brand=vehicle.brand,

            model=vehicle.model,


            price=vehicle.price,


            type=(

                vehicle.type.value

                if hasattr(
                    vehicle.type,
                    "value"
                )

                else vehicle.type

            ),



            mileage=vehicle.mileage,

            year=vehicle.year,


            description=vehicle.description,



            engine_type=(

                vehicle.engine_type.value

                if vehicle.engine_type

                else None

            ),



            equipments=(
                vehicle.equipments or []
            ),



            condition=(

                vehicle.condition.value

                if hasattr(
                    vehicle.condition,
                    "value"
                )

                else vehicle.condition

            ),



            is_available=(
                vehicle.is_available
            ),



            license_plate=(
                vehicle.license_plate
            ),



            status=(

                vehicle.status.value

                if hasattr(
                    vehicle.status,
                    "value"
                )

                else vehicle.status

            ),



            published_at=(
                vehicle.published_at
            ),


            final_check_at=(
                vehicle.final_check_at
            ),



            images=images,


            included_options=included,


            optional_options=optional,


            warranty_plan=warranty_plan

        )