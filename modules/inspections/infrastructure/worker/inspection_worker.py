import infrastructure.db.import_models
from sqlalchemy.orm import configure_mappers

configure_mappers()
from modules.inspections.domain.services.inspection_engine import InspectionEngine
from modules.inspections.infrastructure.repositories.inspection_repository_sql import InspectionRepositorySQL

from infrastructure.db.session import SessionLocal
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from modules.core.exceptions import InspectionNotFound
from datetime import datetime, timezone
from modules.core.enums import InspectionStatus

import json
from datetime import datetime, timezone

from modules.vehicles.infrastructure.queue.redis_connection import redis_conn


def run_inspection(inspection_id: str, admin_id: str):
    session = SessionLocal()

    try:
        inspection_repo = InspectionRepositorySQL(session)
        vehicle_repo = VehicleRepositorySQL(session)


        inspection = inspection_repo.get_by_id(inspection_id)

        if not inspection:
            raise InspectionNotFound()

        vehicle = vehicle_repo.get_by_id(inspection.vehicle_id)

        inspection.status = InspectionStatus.IN_PROGRESS

        inspection.started_at = datetime.now(timezone.utc)

        inspection_repo.update(inspection)
        payload = {
    "event": "inspection_updated",
    "vehicle_id": inspection.vehicle_id,
    "user_id": admin_id,
    "inspection": {
        "status": inspection.status.value
    }
}
        redis_conn.publish(
            "inspection_updates",
            json.dumps(payload)
        )
        engine = InspectionEngine()
        result = engine.run(vehicle)

        inspection.engine_score = result.engine_score
        inspection.brakes_score = result.brakes_score
        inspection.tires_score = result.tires_score
        inspection.electronics_score = result.electronics_score
        inspection.safety_score = result.safety_score

        inspection.failures = result.failures
        inspection.recommended_repairs = result.recommended_repairs

        inspection.overall_score = (
            result.engine_score +
            result.brakes_score +
            result.tires_score +
            result.electronics_score +
            result.safety_score
        ) // 5

        inspection.status = InspectionStatus.COMPLETED
        inspection.completed_at = datetime.now(timezone.utc)

        inspection_repo.update(inspection)

        vehicle.status = "INSPECTED"
        vehicle_repo.update(vehicle)

        session.commit()

        # =========================
        # REDIS PUBSUB
        # =========================

        payload = {
            "event": "inspection_updated",
            "vehicle_id": inspection.vehicle_id,
            "user_id": admin_id,
            "inspection": {
                "status": inspection.status.value,
                "overall_score": inspection.overall_score,
                "engine_score": inspection.engine_score,
                "brakes_score": inspection.brakes_score,
                "tires_score": inspection.tires_score,
                "electronics_score": inspection.electronics_score,
                "safety_score": inspection.safety_score,
                "failures": inspection.failures,
                "recommended_repairs": inspection.recommended_repairs,
            }
        }

        redis_conn.publish(
            "inspection_updates",
            json.dumps(payload)
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()