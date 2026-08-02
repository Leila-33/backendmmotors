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


class ReservationNotFound(DomainException):

    def __init__(self):
        super().__init__(
            message="Réservation introuvable.",
            status_code=404
        )


class ReservationStartDateInPast(DomainException):

    def __init__(self):
        super().__init__(
            message="La date de début de réservation ne peut pas être dans le passé.",
            status_code=400
        )


class ReservationEndDateInPast(DomainException):

    def __init__(self):
        super().__init__(
            message="La date de fin de réservation ne peut pas être dans le passé.",
            status_code=400
        )


class InvalidReservationDates(DomainException):

    def __init__(self):
        super().__init__(
            message="La date de fin doit être postérieure ou égale à la date de début.",
            status_code=400
        )
