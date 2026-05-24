class DomainException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ApplicationNotFound(DomainException):
    def __init__(self):
        super().__init__("APPLICATION_NOT_FOUND", 404)


class VehicleNotFound(DomainException):
    def __init__(self):
        super().__init__("VEHICLE_NOT_FOUND", 404)


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


class EmailAlreadyExists(DomainException):
    def __init__(self):
        super().__init__("EMAIL_ALREADY_EXISTS", 409)


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
    def __init__(self):
        super().__init__("FORBIDDEN", 403)


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
        super().__init__("USER_NOT_FOUND", 404)


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