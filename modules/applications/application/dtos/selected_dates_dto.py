from dataclasses import dataclass
from datetime import date

@dataclass
class SelectedDatesDTO:
    start: date
    end: date