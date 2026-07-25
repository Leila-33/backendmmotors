from dataclasses import dataclass

from modules.vehicles.domain.enums import VehicleOptionType
from modules.options.domain.entities.option import Option


@dataclass
class VehicleOption:

    id: str

    vehicle_id: str

    option_id: str

    type: VehicleOptionType

    option: "Option | None" = None