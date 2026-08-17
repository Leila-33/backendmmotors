from dataclasses import dataclass
from modules.applications.domain.document_messages import (
    DOCUMENT_LABELS,
)


@dataclass(frozen=True)
class NotificationContent:
    title: str
    message: str


class DocumentNotificationBuilder:

    @staticmethod
    def build_rejected(
        document_type: str,
        comment: str | None = None,
    ) -> NotificationContent:

        document_config = DOCUMENT_LABELS.get(
            document_type,
            {
                "label": document_type,
                "gender": "m",
            }
        )

        label = document_config["label"]

        message = (
            f"Bonjour,\n\n"
            f"Votre document « {label} » a été refusé."
        )

        if comment:
            message += (
                f"\n\nMotif : {comment}"
            )

        message += (
            "\n\nMerci de le corriger et de le renvoyer "
            "depuis votre espace client.\n\n"
            "Cordialement,\n"
            "L'équipe M-Motors"
        )

        return NotificationContent(
            title=f"{label} refusé",
            message=message,
        )