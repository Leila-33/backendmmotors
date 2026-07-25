from core.exceptions import DomainException

class VehicleWarrantyNotAssigned(DomainException):

    def __init__(self):

        super().__init__(
            "Aucune garantie n'est assignée à ce véhicule",
            400
        )

class WarrantyPlanNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Plan de garantie introuvable",
            404
        )

class WarrantyNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Garantie introuvable",
            404
        )

class WarrantyNotAllowedForRental(DomainException):
    def __init__(self):
        super().__init__("Une garantie ne peut pas être ajoutée à un véhicule en location.")

class WarrantyRequiredForSale(DomainException):
    def __init__(self):
        super().__init__("Une garantie est obligatoire pour un véhicule en vente.")

class WarrantyPlanAlreadyExists(DomainException):

    def __init__(self, message="Plan déjà existant"):

        super().__init__(
            message,
            409
        )