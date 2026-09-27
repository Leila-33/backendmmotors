from modules.reservations.domain.exceptions import InvalidReservationDates

class RentalDurationCalculator:
    """
    Calcule la durée d'une location à partir des dates
    de début et de fin, en comptant les deux jours.
    """

    def calculate(
        self,
        start_date,
        end_date,
    ) -> int:
        """
        Retourne le nombre de jours de location.

        Les dates de début et de fin sont incluses dans le calcul.
        Une exception est levée si la date de fin est antérieure
        à la date de début.
        """
        if end_date < start_date:
            raise InvalidReservationDates()

        return (
            end_date - start_date
        ).days + 1