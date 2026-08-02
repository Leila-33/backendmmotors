from core.exceptions import DomainException

class ApplicationNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Dossier introuvable.",
            404
        )


class ApplicationNotModifiable(DomainException):

    def __init__(self):

        super().__init__(
            "Ce dossier ne peut plus être modifié.",
            400
        )

class ApplicationAlreadyExists(DomainException):
    def __init__(self):
        super().__init__(
            "Une demande de dossier existe déjà pour ce véhicule."
        )

class ApplicationAlreadyCancelled(DomainException):
    def __init__(self):
        super().__init__("Le dossier est déjà annulé.")

class CannotCancelApplication(DomainException):

    def __init__(self):
        super().__init__(
            message="Cette application ne peut pas être annulée.",
            status_code=400
        )

class CannotRestoreApplication(
    DomainException
):

    def __init__(
        self,
        reason: str = None
    ):
        message = (
            "Cette application ne peut pas être restaurée."
        )

        if reason:
            message = f"{message} {reason}"

        super().__init__(
            message=message,
            status_code=400
        )


class DocumentNotFound(DomainException):

    def __init__(self):
        super().__init__(
            "Document introuvable",
            404
        )

class NoActiveDraft(DomainException):
    def __init__(self):
        super().__init__(
            message="Aucun brouillon actif disponible",
            status_code=404
        )

class ApplicationAlreadyArchived(DomainException):

    def __init__(self):

        super().__init__(
            "Le dossier est déjà archivé.",
            409
        )

class CannotArchiveApplication(DomainException):

    def __init__(
        self,
        message: str = "Le dossier ne peut pas être archivé."
    ):

        super().__init__(
            message,
            409
        )  

class ApplicationNotArchived(DomainException):

    def __init__(self):

        super().__init__(
            "Le dossier n'est pas archivé.",
            409
        )   

class CannotDeleteApplication(DomainException):

    def __init__(
        self,
        message: str = (
            "Le dossier ne peut pas être supprimé."
        ),
    ):

        super().__init__(
            message,
            409,
        )

class ApplicationAlreadyDeleted(DomainException):

    def __init__(self):

        super().__init__(
            "Le dossier est déjà supprimé.",
            409
        )

class CannotSubmitApplication(DomainException):

    def __init__(
        self,
        message: str = "Le dossier ne peut pas être soumis."
    ):

        super().__init__(
            message,
            400
        )

class ApplicationCannotBeDeleted(DomainException):

    def __init__(self):

        super().__init__(
            "Seuls les dossiers à l'état brouillon peuvent être supprimés.",
            409
        )

