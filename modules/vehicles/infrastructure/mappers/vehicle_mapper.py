from modules.warranties.infrastructure.mappers.vehicle_warranty_mapper import VehicleWarrantyMapper
from modules.vehicles.infrastructure.mappers.vehicle_option_mapper import VehicleOptionMapper
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.vehicles.api.schemas import (
    VehicleResponse,
 )
from modules.vehicles.domain.enums import (
    VehicleOptionType,
    
)
from modules.options.api.schemas import OptionResponse
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
