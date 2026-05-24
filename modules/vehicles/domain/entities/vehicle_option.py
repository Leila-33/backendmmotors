from dataclasses import dataclass

from modules.core.enums import VehicleOptionType

@dataclass
class VehicleOption:
    id: str

    vehicle_id: str
    option_id: str

    type: VehicleOptionType