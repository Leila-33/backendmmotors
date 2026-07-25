from modules.vehicles.api.schemas import (
    VehicleLifecycleDTO
)
from modules.inspections.infrastructure.mapper.inspection_mapper import InspectionMapper
from modules.reconditionings.infrastructure.mapper.reconditioning_mapper import ReconditioningMapper
class GetVehicleLifecycleUseCase:

    def __init__(
        self,
        inspection_repository,
        reconditioning_repository,
    ):
        self.inspection_repository = inspection_repository
        self.reconditioning_repository = reconditioning_repository



    def execute(
        self,
        vehicle_id: str
    ) -> VehicleLifecycleDTO:


        inspection = (
            self.inspection_repository
            .get_by_vehicle_id(vehicle_id)
        )


        reconditioning = (
            self.reconditioning_repository
            .get_by_vehicle_id(vehicle_id)
        )



        return VehicleLifecycleDTO(

            inspection=(
                InspectionMapper.to_response(inspection)

                if inspection

                else None
            ),


            reconditioning=(

                ReconditioningMapper.to_response(reconditioning)

                if reconditioning

                else None
            )
        )