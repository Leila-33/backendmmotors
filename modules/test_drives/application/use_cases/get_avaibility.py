from datetime import datetime, timezone
from modules.test_drives.domain.exceptions import InvalidAvailabilityDate

class GetAvailabilityUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, vehicle_id: str, date: str):

        try:

            selected_date = datetime.fromisoformat(date)

        except Exception:
            raise InvalidAvailabilityDate()

        # =========================
        # PAST DATE
        # =========================
        today = datetime.now(timezone.utc).date()

        if selected_date.date() < today:
            raise InvalidAvailabilityDate()

        return self.repository.get_day_availability(
            vehicle_id,
            selected_date
        )