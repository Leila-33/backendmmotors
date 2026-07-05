import infrastructure.db.import_models
from sqlalchemy.orm import configure_mappers

configure_mappers()
from modules.reconditionings.infrastructure.repositories.reconditioning_repository_sql import (
    ReconditioningRepositorySQL
)
from modules.inspections.infrastructure.repositories.inspection_repository_sql import InspectionRepositorySQL

from modules.reconditionings.application.services.perform_reconditioning_analysis import (
    perform_reconditioning_analysis
)
from modules.notifications.application.services.websocket_manager import manager

from modules.core.enums import ReconditioningStatus
from modules.core.exceptions import ReconditioningNotFound, InspectionNotFound
import json
from datetime import datetime, timezone
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from infrastructure.db.session import SessionLocal

def run_reconditioning(reconditioning_id: str, admin_id: str):
    session = SessionLocal()

    try:
        repo = ReconditioningRepositorySQL(session)
        inspection_repo = InspectionRepositorySQL(session)

        # =========================
        # 1. LOAD RECONDITIONING
        # =========================
        reconditioning = repo.get_by_id(reconditioning_id)

        if reconditioning is None:
            raise ReconditioningNotFound()
        
        inspection = inspection_repo.get_by_vehicle_id(reconditioning.vehicle_id)

        if inspection is None:
            raise InspectionNotFound()
        
        # =========================
        # 2. MARK AS RUNNING
        # =========================
        reconditioning.status = ReconditioningStatus.IN_PROGRESS
        repo.update(reconditioning)
        payload = {
        "event": "reconditioning_updated",
        "vehicle_id": reconditioning.vehicle_id,
        "user_id": admin_id,
        "reconditioning": {
            "status": reconditioning.status.value
        }
    }
        redis_conn.publish(
                "reconditioning_updates",
                json.dumps(payload)
            )
        # =========================
        # 3. ANALYSIS (BUSINESS LOGIC)
        # =========================
        result = perform_reconditioning_analysis(inspection)

        # =========================
        # 4. APPLY RESULTS
        # =========================
        reconditioning.cost = result.cost
        reconditioning.duration_days = result.duration_days

        reconditioning.tasks = result.tasks

        # =========================
        # 5. COMPLETE
        # =========================
        reconditioning.status = ReconditioningStatus.COMPLETED
        reconditioning.completed_at = datetime.now(timezone.utc)
        repo.update(reconditioning)
        payload = {
                "event": "reconditioning_updated",
                "vehicle_id": reconditioning.vehicle_id,
                "user_id": admin_id,
                "reconditioning": {
                    "status": reconditioning.status.value,
                    "cost": reconditioning.cost ,
                    "duration_days": reconditioning.duration_days,
                    "tasks": reconditioning.tasks,
                }
            }

        redis_conn.publish(
                "reconditioning_updates",
                json.dumps(payload)
            )

        return {
            "status": "COMPLETED",
            "reconditioning_id": reconditioning_id
        }
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

