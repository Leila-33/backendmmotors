from dataclasses import dataclass


@dataclass(frozen=True)
class GetVehicleInterestStatusResult:
    already_interested: bool
    quote_id: str | None = None
    quote_status: str | None = None
    application_id: str | None = None