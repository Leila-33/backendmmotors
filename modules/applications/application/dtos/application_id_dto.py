from dataclasses import dataclass

@dataclass(frozen=True)
class ApplicationIdDTO:
    application_id: str