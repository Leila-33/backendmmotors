from modules.reconditionings.api.schemas import ReconditioningDTO
from modules.core.exceptions import ReconditioningNotFound


class GetReconditioningUseCase:

    def __init__(self, reconditioning_repository):
        self.reconditioning_repository = reconditioning_repository

    def execute(self, vehicle_id: str) -> ReconditioningDTO:

        reconditioning = self.reconditioning_repository.get_by_vehicle_id(vehicle_id)

        if reconditioning is None:
            raise ReconditioningNotFound()

        return self._to_dto(reconditioning)

    def _to_dto(self, r) -> ReconditioningDTO:
        return ReconditioningDTO(
            id=r.id,
            vehicle_id=r.vehicle_id,
            status=r.status,
            cost=r.cost,
            duration_days=r.duration_days,
            tasks=r.tasks or [],
            completed_tasks=r.completed_tasks or [],
            started_at=r.started_at,
            completed_at=r.completed_at,
        )