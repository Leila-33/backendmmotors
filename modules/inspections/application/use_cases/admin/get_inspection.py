from modules.core.exceptions import InspectionNotFound
from modules.inspections.api.schemas import InspectionDTO


class GetInspectionUseCase:

    def __init__(self, inspection_repository):
        self.inspection_repository = inspection_repository

    def execute(self, vehicle_id: str) -> InspectionDTO:

        inspection = self.inspection_repository.get_by_vehicle_id(vehicle_id)

        if inspection is None:
            raise InspectionNotFound()

        return inspection.to_dto()
    
    def to_dto(self) -> InspectionDTO:
        return InspectionDTO(
            id=self.id,
            vehicle_id=self.vehicle_id,
            status=self.status,
            engine_score=self.engine_score,
            brakes_score=self.brakes_score,
            tires_score=self.tires_score,
            electronics_score=self.electronics_score,
            safety_score=self.safety_score,
            overall_score=self.overall_score,
            failures=self.failures or [],
            recommended_repairs=self.recommended_repairs or [],
            created_at=self.created_at,
            completed_at=self.completed_at,
        )