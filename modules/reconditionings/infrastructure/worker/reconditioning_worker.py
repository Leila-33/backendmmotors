import core.database.import_models
from sqlalchemy.orm import configure_mappers

configure_mappers()
from modules.reconditionings.infrastructure.repositories.reconditioning_repository_sql import (
    ReconditioningRepositorySQL
)
from modules.inspections.infrastructure.repositories.inspection_repository_sql import InspectionRepositorySQL
from modules.reconditionings.application.services.perform_reconditioning_analysis import (
    perform_reconditioning_analysis
)
from modules.inspections.domain.exceptions import InspectionNotFound
from modules.reconditionings.domain.exceptions import ReconditioningNotFound
import json
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from core.database.session import SessionLocal
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from core.database.unit_of_work import UnitOfWork



def run_reconditioning(
    reconditioning_id: str,
    admin_id: str,
):

    db = SessionLocal()

    unit_of_work = UnitOfWork(db)

    try:

        reconditioning_repository = (
            ReconditioningRepositorySQL(db)
        )

        inspection_repository = (
            InspectionRepositorySQL(db)
        )

        vehicle_repository = (
            VehicleRepositorySQL(db)
        )


        # =========================
        # 1. GET RECONDITIONING
        # =========================

        reconditioning = (
            reconditioning_repository
            .get_by_id(reconditioning_id)
        )


        if reconditioning is None:
            raise ReconditioningNotFound()



        # =========================
        # 2. GET INSPECTION
        # =========================

        inspection = (
            inspection_repository
            .get_by_vehicle_id(
                reconditioning.vehicle_id
            )
        )


        if inspection is None:
            raise InspectionNotFound()



        # =========================
        # 3. START
        # =========================

        reconditioning.start()


        reconditioning_repository.update(
            reconditioning
        )


        unit_of_work.commit()



        redis_conn.publish(
            "reconditioning_updates",
            json.dumps({

                "event": "reconditioning_updated",

                "vehicle_id": reconditioning.vehicle_id,

                "user_id": admin_id,

                "reconditioning": {
                    "status": reconditioning.status.value
                }

            })
        )



        # =========================
        # 4. ANALYSIS
        # =========================

        result = (
            perform_reconditioning_analysis(
                inspection
            )
        )



        # =========================
        # 5. APPLY RESULT
        # =========================

        reconditioning.apply_result(
            cost=result.cost,
            duration_days=result.duration_days,
            tasks=result.tasks,
        )



        # =========================
        # 6. COMPLETE
        # =========================

        reconditioning.complete()


        reconditioning_repository.update(
            reconditioning
        )


        vehicle = (
            vehicle_repository
            .get_by_id(
                reconditioning.vehicle_id
            )
        )


        if vehicle:

            vehicle.mark_as_reconditioned()

            vehicle_repository.update(
                vehicle
            )



        unit_of_work.commit()



        # =========================
        # 7. REALTIME UPDATE
        # =========================

        redis_conn.publish(
            "reconditioning_updates",
            json.dumps({

                "event": "reconditioning_updated",

                "vehicle_id": reconditioning.vehicle_id,

                "user_id": admin_id,

                "reconditioning": {

                    "status": (
                        reconditioning.status.value
                    ),

                    "cost": (
                        reconditioning.cost
                    ),

                    "duration_days": (
                        reconditioning.duration_days
                    ),

                    "tasks": (
                        reconditioning.tasks
                    )

                }

            })
        )



        return {
            "status": "COMPLETED",
            "reconditioning_id": reconditioning.id
        }



    except Exception:

        unit_of_work.rollback()

        raise



    finally:

        db.close()