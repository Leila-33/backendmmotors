from modules.vehicles.api.schemas import (
    VehicleResponse,
    PaginatedVehicleResponse,
    VehicleInterestStatusResponse,
    VehicleLifecycleResponse,
    OptionResponse,
)

from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.enums import VehicleOptionType

from core.pagination.paginated_result import PaginatedResult

from modules.inspections.infrastructure.mapper.inspection_mapper import (
    InspectionMapper,
)
from modules.reconditionings.infrastructure.mapper.reconditioning_mapper import (
    ReconditioningMapper,
)
from modules.warranties.infrastructure.mappers.warranty_plan_mapper import (
    WarrantyPlanMapper,
)


class VehicleResponseMapper:

    def __init__(self, s3_service):
        self.s3_service = s3_service

    # =====================================================
    # VEHICLE DETAIL
    # =====================================================

    def to_response(
        self,
        vehicle: Vehicle,
    ) -> VehicleResponse:

        included = []
        optional = []

        # =================================================
        # OPTIONS
        # =================================================

        for vehicle_option in vehicle.options or []:

            if not vehicle_option.option:
                continue

            option = vehicle_option.option

            option_response = OptionResponse(
                id=option.id,
                name=option.name,
                type=(
                    option.type.value
                    if hasattr(option.type, "value")
                    else option.type
                ),
                price=option.price,
                is_active=option.is_active,
                billing_type=option.billing_type,
            )

            if (
                vehicle_option.type
                == VehicleOptionType.INCLUDED
            ):
                included.append(
                    option_response
                )

            elif (
                vehicle_option.type
                == VehicleOptionType.OPTIONAL
            ):
                optional.append(
                    option_response
                )

        # =================================================
        # IMAGES
        # =================================================

        images = [
            self.s3_service.generate_download_url(key)
            for key in vehicle.images or []
        ]

        # =================================================
        # WARRANTY
        # =================================================

        warranty_plan = None

        if (
            vehicle.warranty
            and vehicle.warranty.warranty_plan
        ):
            warranty_plan = (
                WarrantyPlanMapper.to_response(
                    vehicle.warranty.warranty_plan
                )
            )

        # =================================================
        # RESPONSE
        # =================================================

        return VehicleResponse(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            price=vehicle.price,

            type=(
                vehicle.type.value
                if hasattr(vehicle.type, "value")
                else vehicle.type
            ),

            mileage=vehicle.mileage,
            year=vehicle.year,
            description=vehicle.description,

            engine_type=(
                vehicle.engine_type.value
                if hasattr(
                    vehicle.engine_type,
                    "value",
                )
                else vehicle.engine_type
            ),

            equipments=vehicle.equipments or [],

            condition=(
                vehicle.condition.value
                if hasattr(
                    vehicle.condition,
                    "value",
                )
                else vehicle.condition
            ),

            is_available=vehicle.is_available,

            license_plate=vehicle.license_plate,

            status=(
                vehicle.status.value
                if hasattr(
                    vehicle.status,
                    "value",
                )
                else vehicle.status
            ),

            published_at=vehicle.published_at,
            final_check_at=vehicle.final_check_at,

            images=images,

            included_options=included,
            optional_options=optional,

            warranty_plan=warranty_plan,
        )

    # =====================================================
    # INTEREST STATUS
    # =====================================================

    @staticmethod
    def to_interest_status_response(
        result,
    ) -> VehicleInterestStatusResponse:

        return VehicleInterestStatusResponse(
            already_interested=result.already_interested,
            quote_id=result.quote_id,
            quote_status=result.quote_status,
            application_id=result.application_id,
        )

    # =====================================================
    # VEHICLE LIFECYCLE
    # =====================================================

    @staticmethod
    def to_lifecycle_response(
        result,
    ) -> VehicleLifecycleResponse:

        return VehicleLifecycleResponse(
            inspection=(
                InspectionMapper.to_response(
                    result.inspection
                )
                if result.inspection
                else None
            ),

            reconditioning=(
                ReconditioningMapper.to_response(
                    result.reconditioning
                )
                if result.reconditioning
                else None
            ),
        )

    # =====================================================
    # PAGINATED VEHICLES
    # =====================================================

    def to_paginated_response(
        self,
        result: PaginatedResult,
    ) -> PaginatedVehicleResponse:

        return PaginatedVehicleResponse(
            items=[
                self.to_response(vehicle)
                for vehicle in result.items
            ],
            total=result.total,
            page=result.page,
            size=result.limit,
        )

