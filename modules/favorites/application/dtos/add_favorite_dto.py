from dataclasses import dataclass


@dataclass
class AddFavoriteDTO:
    user_id: str
    vehicle_id: str