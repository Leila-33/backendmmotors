from modules.reservations.domain.exceptions import InvalidReservationDates

class RentalDurationCalculator:

    def calculate(
        self,
        start_date,
        end_date,
    ) -> int:

        if end_date < start_date:
            raise InvalidReservationDates()

        return (
            end_date - start_date
        ).days + 1