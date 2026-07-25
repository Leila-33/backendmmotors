import core.database.import_models
from sqlalchemy.orm import configure_mappers
configure_mappers()
from modules.inspections.domain.services.inspection_engine import InspectionEngine
from modules.inspections.infrastructure.repositories.inspection_repository_sql import InspectionRepositorySQL
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from core.database.session import SessionLocal
from modules.inspections.domain.exceptions import InspectionNotFound
from modules.vehicles.domain.exceptions import VehicleNotFound
import json
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from core.database.unit_of_work import UnitOfWork



def run_inspection(
    vehicle_id: str,
    admin_id: str,
):

    db = SessionLocal()

    unit_of_work = UnitOfWork(db)

    try:

        inspection_repository = (
            InspectionRepositorySQL(db)
        )

        vehicle_repository = (
            VehicleRepositorySQL(db)
        )

        # =====================================
        # LOAD VEHICLE
        # =====================================

        vehicle = (
            vehicle_repository.get_by_id(
                vehicle_id
            )
        )

        if not vehicle:
            raise VehicleNotFound()

        # =====================================
        # LOAD INSPECTION
        # =====================================

        inspection = (
            inspection_repository.get_by_vehicle_id(
                vehicle_id
            )
        )

        if not inspection:
            raise InspectionNotFound()

        # =====================================
        # START INSPECTION
        # =====================================

        inspection.start()

        inspection_repository.update(
            inspection
        )

        unit_of_work.commit()

        # =====================================
        # REDIS UPDATE
        # =====================================

        redis_conn.publish(
            "inspection_updates",
            json.dumps(
                {
                    "event": "inspection_updated",
                    "vehicle_id": vehicle.id,
                    "user_id": admin_id,
                    "inspection": {
                        "status": inspection.status.value,
                    },
                }
            ),
        )

        # =====================================
        # RUN ENGINE
        # =====================================

        engine = InspectionEngine()

        result = engine.run(
            vehicle
        )

        # =====================================
        # COMPLETE INSPECTION
        # =====================================

        inspection.complete(
            result
        )

        inspection_repository.update(
            inspection
        )

        # =====================================
        # UPDATE VEHICLE
        # =====================================

        vehicle.mark_as_inspected()

        vehicle_repository.update(
            vehicle
        )

        unit_of_work.commit()

        # =====================================
        # FINAL REDIS UPDATE
        # =====================================

        redis_conn.publish(
            "inspection_updates",
            json.dumps(
                {
                    "event": "inspection_updated",
                    "vehicle_id": vehicle.id,
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
                    },
                }
            ),
        )

    except Exception:

        unit_of_work.rollback()

        redis_conn.publish(
            "inspection_updates",
            json.dumps(
                {
                    "event": "inspection_failed",
                    "vehicle_id": vehicle_id,
                    "user_id": admin_id,
                }
            ),
        )

        raise

    finally:

        db.close()