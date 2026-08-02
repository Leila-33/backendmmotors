from modules.applications.domain.document_messages import (
    DOCUMENT_LABELS,
    STATUS_MESSAGES,
)


class DocumentMessageBuilder:

    @staticmethod
    def build(
        document_type: str,
        status,
        comment: str | None = None,
    ) -> str:

        config = DOCUMENT_LABELS.get(
            document_type,
            {
                "label": document_type,
                "gender": "m"
            }
        )

        label = config["label"]
        gender = config["gender"]

        message = (
            f"{label} "
            f"{STATUS_MESSAGES[status][gender]}"
        )

        if comment:
            message += f" : {comment}"

        return message