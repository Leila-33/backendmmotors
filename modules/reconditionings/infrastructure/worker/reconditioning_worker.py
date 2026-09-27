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
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.inspections.domain.exceptions import InspectionNotFound
from modules.reconditionings.domain.exceptions import ReconditioningNotFound
import json
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from core.database.session import SessionLocal
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType
from modules.applications.infrastructure.repositories.event_repository_sql import EventRepositorySQL
from modules.applications.application.services.event_service import EventService
import logging


logger = logging.getLogger(__name__)


def run_reconditioning(
    reconditioning_id: str,
    admin_id: str,
):
    """
    Exécute le traitement d'un reconditionnement depuis la file d'attente.

    Le traitement démarre le reconditionnement, analyse les réparations
    issues de l'inspection, applique le coût, la durée et les tâches,
    puis termine le reconditionnement et met à jour l'état du véhicule.

    Les changements sont enregistrés dans l'historique des événements
    et publiés en temps réel après chaque étape importante.
    """
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

        event_repository = EventRepositorySQL(db)
        event_service = EventService(event_repository)
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
        vehicle = (
    vehicle_repository
    .get_by_id(
        reconditioning.vehicle_id
    )
)

        if not vehicle:
            raise VehicleNotFound()
        
        event_service.log(
    type=EventType.RECONDITIONING_STARTED,
    message="Reconditioning démarré",
    vehicle_id=vehicle.id,
    user_id=admin_id,
    event_metadata={
        "reconditioning_id": reconditioning.id
    }
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


        logger.info(
    "Reconditionnement démarré",
    extra={
        "reconditioning_id": reconditioning.id,
        "vehicle_id": vehicle.id,
        "admin_id": admin_id,
    }
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


        event_service.log(
            type=EventType.RECONDITIONING_COMPLETED,
            message="Reconditioning terminé",
            vehicle_id=vehicle.id,
            user_id=admin_id,
            event_metadata={
                "reconditioning_id": reconditioning.id
            }
        )


        if vehicle:

            vehicle.mark_as_reconditioned()

            vehicle_repository.update(
                vehicle
            )



        unit_of_work.commit()

        logger.info(
            "Reconditionnement terminé",
            extra={
                "reconditioning_id": reconditioning.id,
                "vehicle_id": vehicle.id,
                "cost": reconditioning.cost,
                "duration_days": reconditioning.duration_days,
                "tasks_count": len(reconditioning.tasks),
            }
        )

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

        logger.exception(
            "Erreur pendant le reconditionnement véhicule",
            extra={
                "reconditioning_id": reconditioning_id,
                "admin_id": admin_id,
            }
        )

        raise



    finally:

        db.close()