from datetime import datetime, timezone
from uuid import uuid4
import logging

from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveSlotUnavailable,
    TestDrivePastDate,
    TestDriveAlreadyExists
)

from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotAvailableForTestDrive,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType
)
from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole



logger = logging.getLogger(__name__)


class CreateTestDriveUseCase:
    """
    Crée une demande d'essai routier après vérification de l'existence
    et de la disponibilité du véhicule, de l'absence d'une demande
    bloquante et de la disponibilité du créneau choisi.

    La création est enregistrée dans l'historique des événements.
    Après validation de la transaction, les administrateurs sont
    notifiés et le nombre d'essais en attente est diffusé en temps réel.
    """

    def __init__(
        self,
        user_repository,
        test_drive_repository,
        vehicle_repository,
        event_service,
        notification_service,
        unit_of_work,
    ):
        self.user_repository = user_repository
        self.test_drive_repository = test_drive_repository
        self.vehicle_repository = vehicle_repository
        self.event_service = event_service
        self.notification_service = notification_service
        self.unit_of_work = unit_of_work

    async def execute(
        self,
        dto,
        user_id: str,
    ) -> TestDrive:

        try:
            # =========================
            # VEHICLE
            # =========================

            vehicle = self.vehicle_repository.get_by_id(
                dto.vehicle_id
            )

            if vehicle is None:
                raise VehicleNotFound()

            if vehicle.status != VehicleStatus.PUBLISHED:
                raise VehicleNotAvailableForTestDrive()

            # =========================
            # EXISTING REQUEST
            # =========================

            if self.test_drive_repository.has_existing_blocking_test_drive(
                user_id=user_id,
                vehicle_id=dto.vehicle_id,
            ):
                raise TestDriveAlreadyExists()

            # =========================
            # APPOINTMENT DATE
            # =========================

            now = datetime.now(timezone.utc)
            appointment_date = dto.appointment_date

            if appointment_date.tzinfo is None:
                raise ValueError(
                    "La date du rendez-vous doit inclure un fuseau horaire."
                )

            if appointment_date <= now:
                raise TestDrivePastDate()

            # =========================
            # SLOT AVAILABILITY
            # =========================

            existing = self.test_drive_repository.find_conflicting_slot(
                vehicle_id=dto.vehicle_id,
                appointment_date=appointment_date,
            )

            if existing:
                raise TestDriveSlotUnavailable()

            # =========================
            # CREATE TEST DRIVE
            # =========================

            test_drive = TestDrive(
                id=str(uuid4()),
                user_id=user_id,
                vehicle_id=dto.vehicle_id,
                appointment_date=appointment_date,
                status=TestDriveStatus.PENDING,
                comment=dto.comment,
                created_at=now,
            )

            self.test_drive_repository.create(test_drive)

            # =========================
            # DOMAIN EVENT / HISTORY
            # =========================

            self.event_service.log(
                type=EventType.TEST_DRIVE_CREATED,
                message="Demande d'essai véhicule créée",
                user_id=user_id,
                vehicle_id=vehicle.id,
                test_drive_id=test_drive.id,
                event_metadata={
                    "appointment_date": (
                        test_drive.appointment_date.isoformat()
                    ),
                    "status": test_drive.status.value,
                },
            )

            # =========================
            # LOAD ADMINS
            # =========================

            admins = self.user_repository.get_by_role(
                UserRole.ADMIN
            )
            for admin in admins:
                try:
                    await self.notification_service.send(
                        user_id=str(admin.id),
                        title="Nouvel essai routier",
                        message="Un client a demandé un essai routier.",
                        notif_type=NotificationType.TEST_DRIVE_CREATED,
                        entity_type=NotificationEntityType.TEST_DRIVE,
                        entity_id=test_drive.id,
                    )
                except Exception:
                    logger.exception(
                        "Échec de notification de l'administrateur : "
                        "admin_id=%s, test_drive_id=%s",
                        admin.id,
                        test_drive.id,
                    )
            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

        except Exception:
            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création essai routier",
                extra={
                    "user_id": user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )
            raise

        # =====================================================
        # POST-COMMIT: PENDING COUNT UPDATE
        # =====================================================

        try:
            pending_count = (
                self.test_drive_repository.count_pending()
            )

            for admin in admins:
                await self.notification_service.send_update(
                    user_id=str(admin.id),
                    payload={
                        "type": "TEST_DRIVE_PENDING_UPDATED",
                        "count": pending_count,
                    },
                )

        except Exception:
            logger.exception(
                "Échec de diffusion du compteur des essais en attente : "
                "test_drive_id=%s",
                test_drive.id,
            )

        logger.info(
            "Demande d'essai routier créée",
            extra={
                "test_drive_id": test_drive.id,
                "user_id": user_id,
                "vehicle_id": test_drive.vehicle_id,
            },
        )

        return test_drive