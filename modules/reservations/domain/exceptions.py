from core.exceptions import DomainException

class ReservationAlreadyCancelled(DomainException):
    def __init__(self):
        super().__init__("La réservation est déjà annulée.")



class ReservationAlreadyStarted(DomainException):
    def __init__(self):
        super().__init__("Impossible d'annuler une réservation déjà commencée.")

class CannotCancelReservation(DomainException):

    def __init__(self):
        super().__init__(
            message="Cette réservation ne peut pas être annulée.",
            status_code=400
        )

class CannotCancelReservation(DomainException):

    def __init__(self):
        super().__init__(
            message="Cette réservation ne peut pas être annulée.",
            status_code=400
        )

class ReservationNotFound(DomainException):

    def __init__(self):
        super().__init__(
            message="Réservation introuvable.",
            status_code=404
        )