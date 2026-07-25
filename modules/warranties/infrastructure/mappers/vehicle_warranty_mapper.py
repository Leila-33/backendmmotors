from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel

from modules.warranties.infrastructure.mappers.warranty_plan_mapper import (
    WarrantyPlanMapper,
)



class VehicleWarrantyMapper:


    # =========================
    # MODEL -> DOMAIN
    # =========================

    @staticmethod
    def to_domain(
        model: VehicleWarrantyModel
    ):

        return VehicleWarranty(

            id=model.id,

            vehicle_id=model.vehicle_id,

            warranty_plan_id=model.warranty_plan_id,

            is_active=model.is_active,

            start_date=model.start_date,

            end_date=model.end_date,

            current_mileage=model.current_mileage,

            max_mileage=model.max_mileage,

            warranty_plan=(

                WarrantyPlanMapper.to_domain(
                    model.warranty_plan
                )

                if model.warranty_plan

                else None
            )

        )



    # =========================
    # DOMAIN -> MODEL
    # =========================

    @staticmethod
    def to_model(
        warranty: VehicleWarranty
    ):

        return VehicleWarrantyModel(

            id=warranty.id,

            vehicle_id=warranty.vehicle_id,

            warranty_plan_id=warranty.warranty_plan_id,

            is_active=warranty.is_active,

            start_date=warranty.start_date,

            end_date=warranty.end_date,

            current_mileage=warranty.current_mileage,

            max_mileage=warranty.max_mileage,

        )



    # =========================
    # UPDATE MODEL
    # =========================

    @staticmethod
    def update_model(
        model: VehicleWarrantyModel,
        warranty: VehicleWarranty
    ):


        model.is_active = (
            warranty.is_active
        )


        model.start_date = (
            warranty.start_date
        )


        model.end_date = (
            warranty.end_date
        )


        model.current_mileage = (
            warranty.current_mileage
        )


        model.max_mileage = (
            warranty.max_mileage
        )


        model.warranty_plan_id = (
            warranty.warranty_plan_id
        )


        return model



    # =========================
    # DOMAIN -> RESPONSE
    # =========================

    @staticmethod
    def to_response(
        warranty: VehicleWarranty
    ):


        return {

            "id": warranty.id,

            "vehicle_id": warranty.vehicle_id,

            "warranty_plan_id": warranty.warranty_plan_id,

            "is_active": warranty.is_active,

            "start_date": warranty.start_date,

            "end_date": warranty.end_date,

            "current_mileage": warranty.current_mileage,

            "max_mileage": warranty.max_mileage,


            "warranty_plan": (

                WarrantyPlanMapper.to_response(
                    warranty.warranty_plan
                )

                if warranty.warranty_plan

                else None

            )

        }