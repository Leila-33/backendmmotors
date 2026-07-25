from core.exceptions import DomainException

class FavoriteAlreadyExists(DomainException):
    def __init__(self):
        super().__init__("Déjà en favoris", 409)


class FavoriteNotFound(DomainException):
    def __init__(self):
        super().__init__("Favori introuvable", 404)