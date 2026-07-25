from datetime import date
from modules.applications.domain.exceptions import CannotRestoreApplication
from modules.applications.domain.enums import ApplicationStatus
from modules.vehicles.domain.enums import VehicleType

class RestoreApplicationPolicy:

    @staticmethod
    def can_restore(
        application,
        reservation_repository
    ) -> bool:

        try:

            RestoreApplicationPolicy.validate(
                application,
                reservation_repository
            )

            return True

        except CannotRestoreApplication:
            return False

    @staticmethod
    def validate(
        application,
        reservation_repository
    ):

        # =========================
        # ONLY CANCELLED
        # =========================
        if (
            application.status
            != ApplicationStatus.CANCELLED
        ):
            raise CannotRestoreApplication(
                "Le dossier n'est pas annulé."
            )

        # =========================
        # PREVIOUS STATUS
        # =========================
        if not application.previous_status:
            raise CannotRestoreApplication(
                "Aucun statut précédent à restaurer."
            )

        # =========================
        # RENTAL-SPECIFIC RULES
        # =========================
        if application.vehicle.type != VehicleType.RENT:
            return

        reservation = application.reservation

        if not reservation:
            raise CannotRestoreApplication(
                "Réservation introuvable."
            )

        today = date.today()

        # -------------------------
        # Rental already started
        # -------------------------
        if today >= reservation.start_date:
            raise CannotRestoreApplication(
                "La période de location a déjà commencé."
            )

        # -------------------------
        # Vehicle availability
        # -------------------------
        overlapping = (
            reservation_repository.exists_overlap(
                vehicle_id=reservation.vehicle_id,
                start_date=reservation.start_date,
                end_date=reservation.end_date,
                exclude_reservation_id=reservation.id
            )
        )

        if overlapping:
            raise CannotRestoreApplication(
                "Le véhicule n'est plus disponible."
            )