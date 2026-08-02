from dataclasses import dataclass

from modules.notifications.domain.enums import NotificationType
from modules.applications.domain.enums import ApplicationStatus


@dataclass(frozen=True)
class NotificationContent:
    title: str
    message: str
    type: NotificationType


class ApplicationNotificationBuilder:

    @staticmethod
    def build(
        application,
        status: ApplicationStatus,
        reason: str | None = None,
        user_first_name: str = "cher client",
    ) -> NotificationContent:

        application_number = (
            application.id[:8].upper()
        )

        base_intro = (
            f"Bonjour {user_first_name},\n\n"
            f"Votre dossier n°{application_number} "
        )


        # =========================
        # APPROVED
        # =========================

        if status == ApplicationStatus.APPROVED:

            return NotificationContent(
                title="Dossier validé",

                message=(
                    base_intro +
                    "a été validé avec succès.\n\n"

                    "Vous pouvez désormais suivre "
                    "les prochaines étapes depuis "
                    "votre espace client.\n\n"

                    "Nous vous remercions "
                    "pour votre confiance.\n\n"

                    "Cordialement,\n"
                    "L'équipe M-Motors"
                ),

                type=NotificationType.APPLICATION_APPROVED,
            )


        # =========================
        # REJECTED
        # =========================

        if status == ApplicationStatus.REJECTED:

            message = (
                base_intro +
                "a été refusé.\n\n"
            )

            if reason:

                message += (
                    f"Motif : {reason}\n\n"
                )


            message += (
                "Vous pouvez modifier votre dossier "
                "et le soumettre à nouveau.\n\n"

                "Cordialement,\n"
                "L'équipe M-Motors"
            )


            return NotificationContent(

                title="Dossier refusé",

                message=message,

                type=NotificationType.APPLICATION_REJECTED,
            )


        # =========================
        # SUBMITTED
        # =========================

        if status == ApplicationStatus.SUBMITTED:

            return NotificationContent(

                title="Dossier soumis",

                message=(
                    base_intro +
                    "a bien été transmis "
                    "à notre équipe.\n\n"

                    "Nous allons procéder "
                    "à son analyse.\n\n"

                    "Cordialement,\n"
                    "L'équipe M-Motors"
                ),

                type=NotificationType.APPLICATION_SUBMITTED,
            )


        # =========================
        # DEFAULT
        # =========================

        return NotificationContent(

            title="Dossier mis à jour",

            message=(
                base_intro +
                "a été mis à jour.\n\n"

                "Cordialement,\n"
                "L'équipe M-Motors"
            ),

            type=NotificationType.APPLICATION_UPDATED,
        )