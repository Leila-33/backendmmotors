from dataclasses import dataclass


@dataclass
class RemoveFavoriteDTO:
    user_id: str
    vehicle_id: str