from modules.inspections.domain.exceptions import InspectionNotFound
from modules.inspections.infrastructure.mapper.inspection_mapper import InspectionMapper

class GetInspectionUseCase:

    def __init__(
        self,
        inspection_repository
    ):
        self.inspection_repository = inspection_repository


    def execute(
        self,
        vehicle_id: str
    ):

        inspection = (
            self.inspection_repository
            .get_by_vehicle_id(
                vehicle_id
            )
        )


        if not inspection:
            raise InspectionNotFound()


        return InspectionMapper.to_response(
            inspection
        )