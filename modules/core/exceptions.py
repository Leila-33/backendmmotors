class DomainException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ApplicationNotFound(DomainException):
    def __init__(self):
        super().__init__("APPLICATION_NOT_FOUND", 404)



class VehicleNotAvailable(DomainException):
    def __init__(self):
        super().__init__("VEHICLE_NOT_AVAILABLE", 400)


class Forbidden(DomainException):
    def __init__(self):
        super().__init__("FORBIDDEN", 403)


class ValidationException(DomainException):
    def __init__(self, message: str):
        super().__init__(message, 400)


class ApplicationNotFound(DomainException):
    def __init__(self):
        super().__init__("APPLICATION_NOT_FOUND", 404)


class ApplicationNotModifiable(DomainException):
    def __init__(self):
        super().__init__("APPLICATION_NOT_MODIFIABLE", 400)


class NoActiveDraft(DomainException):
    def __init__(self):
        super().__init__("NO_ACTIVE_DRAFT", 404)


class ExpenseGreaterThanIncome(DomainException):
    def __init__(self):
        super().__init__("EXPENSES_GREATER_THAN_INCOME", 400)

class NoActiveDraft(DomainException):
    def __init__(self):
        super().__init__("NO_ACTIVE_DRAFT", 404)


class ApplicationNotModifiable(DomainException):
    def __init__(self):
        super().__init__("APPLICATION_NOT_MODIFIABLE", 400)


class OptionNotAllowed(DomainException):
    def __init__(self, option_id: str):
        super().__init__(f"OPTION_NOT_ALLOWED:{option_id}", 400)

class ApplicationNotProcessable(DomainException):
    def __init__(self):
        super().__init__("APPLICATION_NOT_PROCESSABLE", 400)


class InvalidDecision(DomainException):
    def __init__(self):
        super().__init__("INVALID_DECISION", 400)

class InvalidVehicleType(DomainException):
    def __init__(self):
        super().__init__("INVALID_VEHICLE_TYPE", 400)

class OptionNotFound(DomainException):
    def __init__(self):
        super().__init__("OPTION_NOT_FOUND", 404)





class CguNotAccepted(DomainException):
    def __init__(self):
        super().__init__("CGU_NOT_ACCEPTED", 400)



class EmailAlreadyExists(DomainException):
    def __init__(self):
        super().__init__("EMAIL_ALREADY_EXISTS", 409)


class InvalidCredentials(DomainException):
    def __init__(self):
        super().__init__("INVALID_CREDENTIALS", 401)


class AccountDisabled(DomainException):
    def __init__(self):
        super().__init__("ACCOUNT_DISABLED", 403)


class EmailNotVerified(DomainException):
    def __init__(self):
        super().__init__("EMAIL_NOT_VERIFIED", 403)


class TokenInvalid(DomainException):
    def __init__(self):
        super().__init__("TOKEN_INVALID", 401)


class TokenExpired(DomainException):
    def __init__(self):
        super().__init__("TOKEN_EXPIRED", 401)


class TokenRevoked(DomainException):
    def __init__(self):
        super().__init__("TOKEN_REVOKED", 401)


class Forbidden(DomainException):
    def __init__(self, message: str = "Accès interdit"):
        super().__init__(
            message=message,
            status_code=403
        )


class RefreshTokenMissing(DomainException):
    def __init__(self):
        super().__init__("REFRESH_TOKEN_MISSING", 401)


class Unauthorized(DomainException):
    def __init__(self):
        super().__init__("UNAUTHORIZED", 401)

class ReservationNotFound(DomainException):
    def __init__(self):
        super().__init__("RESERVATION_NOT_FOUND", 404)


class UserNotFound(DomainException):
    def __init__(self):
        super().__init__("Utilisateur introuvable", 404)


class VehicleNotAvailable(DomainException):
    def __init__(self):
        super().__init__("VEHICLE_NOT_AVAILABLE", 400)



class InvalidJSON(DomainException):
    def __init__(self):
        super().__init__("INVALID_JSON", 400)


class InvalidListFormat(DomainException):
    def __init__(self):
        super().__init__("INVALID_LIST_FORMAT", 400)


class MissingField(DomainException):
    def __init__(self, field: str):
        super().__init__(f"MISSING_FIELD_{field.upper()}", 400)


class VehicleAlreadyExists(DomainException):
    def __init__(self):
        super().__init__("Un véhicule avec cette immatriculation existe déjà")

class DocumentNotFound(DomainException):

    def __init__(self):
        super().__init__(
            "DOCUMENT_NOT_FOUND",
            404
        )

class ApplicationCannotBeDeleted(DomainException):

    def __init__(self):
        super().__init__(
            "APPLICATION_CANNOT_BE_DELETED",
            400
        )

class TestDriveSlotUnavailable(DomainException):

    def __init__(self):
        super().__init__(
            "TEST_DRIVE_SLOT_UNAVAILABLE",
            409
        )

class TestDrivePastDate(DomainException):

    def __init__(self):

        super().__init__(
            "La date ne peut pas être dans le passé",
            400
        )

class InvalidAvailabilityDate(DomainException):

    def __init__(self):

        super().__init__(
            "Date de disponibilité invalide",
            400
        )




class TestDriveNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Essai routier introuvable",
            404
        )


class NotificationNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Notification introuvable",
            404
        )



class UserIdRequiredForClient(DomainException):

    def __init__(self):
        super().__init__(
            "user_id requis pour un utilisateur client",
            400
        )

class FavoriteAlreadyExists(DomainException):
    def __init__(self):
        super().__init__("Déjà en favoris", 409)


class FavoriteNotFound(DomainException):
    def __init__(self):
        super().__init__("Favori introuvable", 404)

class TestDriveStatusForbidden(DomainException):

    def __init__(self):

        super().__init__(
            "Les clients ne peuvent que annuler un essai routier",
            403
        )



class WarrantyPlanAlreadyExists(DomainException):

    def __init__(self, message="Plan déjà existant"):

        super().__init__(
            message,
            409
        )

class WarrantyPlanNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Plan de garantie introuvable",
            404
        )

class VehicleWarrantyNotAssigned(DomainException):

    def __init__(self):

        super().__init__(
            "Aucune garantie n'est assignée à ce véhicule",
            400
        )
        
class PaymentNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Paiement introuvable",
            404
        )

class WarrantyNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Garantie introuvable",
            404
        )

class InvalidNotificationType(DomainException):

    def __init__(self, notif_type: str):

        super().__init__(
            f"Type de notification invalide : {notif_type}",
            400
        )

class PaymentNotAllowed(DomainException):

    def __init__(self):

        super().__init__(
            "Le dossier doit être approuvé avant paiement",
            400
        )



class ApplicationNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Dossier introuvable",
            404
        )


class FinancingDataNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Informations de financement introuvables",
            400
        )



class FinancingContractNotFound(
    DomainException
):

    def __init__(self):

        super().__init__(
            "Contrat de financement introuvable",
            404
        )

class WarrantyNotAllowedForRental(DomainException):
    def __init__(self):
        super().__init__("Une garantie ne peut pas être ajoutée à un véhicule en location.")

class WarrantyRequiredForSale(DomainException):
    def __init__(self):
        super().__init__("Une garantie est obligatoire pour un véhicule en vente.")

class ApplicationAlreadyExists(DomainException):
    def __init__(self):
        super().__init__(
            "Une demande de dossier existe déjà pour ce véhicule."
        )


class ReservationAlreadyCancelled(DomainException):
    def __init__(self):
        super().__init__("La réservation est déjà annulée.")

class ApplicationAlreadyCancelled(DomainException):
    def __init__(self):
        super().__init__("Le dossier est déjà annulé.")

class ReservationAlreadyStarted(DomainException):
    def __init__(self):
        super().__init__("Impossible d'annuler une réservation déjà commencée.")


class CannotCancelApplication(DomainException):

    def __init__(self):
        super().__init__(
            message="Cette application ne peut pas être annulée.",
            status_code=400
        )

class CannotCancelReservation(DomainException):

    def __init__(self):
        super().__init__(
            message="Cette réservation ne peut pas être annulée.",
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

class InspectionAlreadyRunning(DomainException):
    def __init__(self):
        super().__init__(
            message="Une inspection est déjà en cours pour ce véhicule.",
            status_code=409
        )


class ReconditioningAlreadyRunning(DomainException):
    def __init__(self):
        super().__init__(
            message="Un reconditionnement est déjà en cours pour ce véhicule.",
            status_code=409
        )

class InspectionAlreadyCompleted(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce véhicule a déjà été inspecté.",
            status_code=409
        )


class VehicleNotEligibleForInspection(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce véhicule n'est pas éligible à une inspection.",
            status_code=400
        )


class VehicleNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Véhicule introuvable.",
            status_code=404
        )

class InspectionNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Inspection introuvable.",
            status_code=404
        )

class ReconditioningNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Reconditionnement introuvable pour ce véhicule",
            status_code=404
        )

class InspectionNotCompleted(DomainException):
    def __init__(self):
        super().__init__(
            message="L'inspection doit être terminée avant de lancer le reconditionnement.",
            status_code=400
        )

class InvalidRepairConfiguration(DomainException):
    def __init__(self, code: str):
        super().__init__(
            message=f"Le code de réparation '{code}' n'est pas configuré.",
            status_code=500
        )
        
class ReconditioningNotCompleted(DomainException):
    def __init__(self):
        super().__init__(
            message="Le reconditionnement n'est pas terminé",
            status_code=400
        )

class VehicleNotReadyForPublication(DomainException):
    def __init__(self):
        super().__init__(
            message="Le véhicule n'est pas prêt à être publié",
            status_code=400
        )
class VehicleAlreadyPublished(DomainException):
    def __init__(self):
        super().__init__(
            message="Le véhicule est déjà publié",
            status_code=400
        )
        
class VehicleNotPublished(DomainException):
    def __init__(self):
        super().__init__(
            message="Le véhicule doit être publié avant modification de disponibilité",
            status_code=400
        )
class VehicleAvailabilityAlreadySet(DomainException):
    def __init__(self):
        super().__init__(
            message="La disponibilité est déjà dans cet état",
            status_code=400
        )

class FinancingAmountNegative(DomainException):
    def __init__(self):
        super().__init__(
            message="L'apport et la valeur de reprise dépassent le prix du véhicule.",
            status_code=400
        )

class SupportTicketNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Ticket introuvable.",
            status_code=404
        )

class TicketAccessDenied(DomainException):
    def __init__(self):
        super().__init__(
            message="Accès refusé à ce ticket.",
            status_code=403
        )

class InvalidTicketStatus(DomainException):
    def __init__(self):
        super().__init__(
            message="Statut de ticket invalide.",
            status_code=400
        )

class NoAvailableAgent(DomainException):
    def __init__(self):
        super().__init__(
            message="Aucun agent SAV disponible.",
            status_code=503
        )
        


class TicketClosedException(DomainException):
    def __init__(self):
        super().__init__(
            message="Impossible d'envoyer un message sur un ticket fermé.",
            status_code=400
        )

class EmptyMessageException(DomainException):
    def __init__(self):
        super().__init__(
            message="Le message ne peut pas être vide.",
            status_code=400
        )

class MessageTooLongException(DomainException):
    def __init__(self, max_length: int = 2000):
        super().__init__(
            message=f"Le message dépasse la limite autorisée ({max_length} caractères).",
            status_code=400
        )

class InvalidRole(DomainException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Rôle invalide : {role}",
            status_code=400
        )

class AccountDeleted(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce compte a été supprimé.",
            status_code=403
        )

class InvalidUserIds(DomainException):
    def __init__(self):
        super().__init__(
            message="Aucun utilisateur sélectionné ou identifiants invalides.",
            status_code=400
        )

class UserAlreadyArchived(DomainException):
    def __init__(self, user_id: str):
        super().__init__(
            message=f"Utilisateur {user_id} déjà archivé.",
            status_code=409
        )

class CannotArchiveAdmin(DomainException):
    def __init__(self, user_id: str):
        super().__init__(
            message=f"Impossible d'archiver l'administrateur {user_id}.",
            status_code=403
        )

class InvalidTicketState(DomainException):
    def __init__(self):
        super().__init__(
            message="Seuls les tickets résolus ou fermés peuvent être archivés.",
            status_code=400,
        )