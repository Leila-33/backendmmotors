import json
from modules.inspections.domain.entities.inspection import Inspection
from modules.inspections.infrastructure.db.inspection_model import InspectionModel


class InspectionMapper:

    @staticmethod
    def to_domain(model: InspectionModel) -> Inspection:
        return Inspection(
            id=model.id,
            vehicle_id=model.vehicle_id,
            status=model.status,
            engine_score=model.engine_score,
            brakes_score=model.brakes_score,
            tires_score=model.tires_score,
            electronics_score=model.electronics_score,
            safety_score=model.safety_score,
            failures=json.loads(model.failures) if model.failures else [],
            recommended_repairs=json.loads(model.recommended_repairs) if model.recommended_repairs else [],
            started_at=model.started_at,
            completed_at=model.completed_at,
        )

    @staticmethod
    def to_model(entity: Inspection) -> InspectionModel:
        return InspectionModel(
            id=entity.id,
            vehicle_id=entity.vehicle_id,
            status=entity.status,
            engine_score=entity.engine_score,
            brakes_score=entity.brakes_score,
            tires_score=entity.tires_score,
            electronics_score=entity.electronics_score,
            safety_score=entity.safety_score,
            failures=json.dumps(entity.failures or []),
            recommended_repairs=json.dumps(entity.recommended_repairs or []),
            started_at=entity.started_at,
            completed_at=entity.completed_at,
        )