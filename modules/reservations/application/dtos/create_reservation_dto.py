from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreateReservationDTO:

    application_id: str
    start_date: datetime
    end_date: datetime