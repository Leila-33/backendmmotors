from core.exceptions import DomainException
class RefreshTokenMissing(DomainException):
    def __init__(self):
        super().__init__(
            message="Le token de rafraîchissement est manquant",
            status_code=401
        )


class Unauthorized(DomainException):
    def __init__(self):
        super().__init__(
            message="Authentification requise",
            status_code=401
        )


class UserNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Utilisateur introuvable",
            status_code=404
        )


class TokenInvalid(DomainException):
    def __init__(self):
        super().__init__(
            message="Token invalide",
            status_code=401
        )


class TokenExpired(DomainException):
    def __init__(self):
        super().__init__(
            message="Token expiré",
            status_code=401
        )


class TokenRevoked(DomainException):
    def __init__(self):
        super().__init__(
            message="Token révoqué",
            status_code=401
        )


class CguNotAccepted(DomainException):
    def __init__(self):
        super().__init__(
            message="Les conditions générales d'utilisation doivent être acceptées",
            status_code=400
        )


class EmailAlreadyExists(DomainException):
    def __init__(self):
        super().__init__(
            message="Cette adresse e-mail est déjà utilisée",
            status_code=409
        )


class InvalidCredentials(DomainException):
    def __init__(self):
        super().__init__(
            message="Identifiants invalides",
            status_code=401
        )


class AccountDisabled(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce compte est désactivé",
            status_code=403
        )


class EmailNotVerified(DomainException):
    def __init__(self):
        super().__init__(
            message="L'adresse e-mail n'a pas été vérifiée",
            status_code=403
        )

class UserIdRequiredForClient(DomainException):

    def __init__(self):
        super().__init__(
            "user_id requis pour un utilisateur client",
            400
        )

class InvalidUserIds(DomainException):
    def __init__(self, message="Certains utilisateurs sont introuvables"):
        super().__init__(
            message=message,
            status_code=400,
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


class AccountDeleted(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce compte a été supprimé.",
            status_code=403
        )

class InvalidActivationToken(DomainException):

    def __init__(self):
        super().__init__(
            message="Le lien d'activation est invalide.",
            status_code=400,
        )

class ActivationTokenExpired(DomainException):

    def __init__(self):
        super().__init__(
            message="Le lien d'activation a expiré.",
            status_code=410,
        )

class ActivationTokenAlreadyUsed(DomainException):

    def __init__(self):
        super().__init__(
            message="Ce lien d'activation a déjà été utilisé.",
            status_code=409,
        )




class Forbidden(DomainException):
    def __init__(self, message: str = "Accès interdit"):
        super().__init__(message, 403)

class InvalidUserRole(DomainException):

    def __init__(self):
        super().__init__(
            message="Le rôle utilisateur fourni est invalide",
            status_code=400
        )

class InvalidRefreshToken(DomainException):

    def __init__(self):
        super().__init__(
            message="Le refresh token est invalide ou expiré",
            status_code=401
        )