from dataclasses import dataclass


@dataclass(frozen=True)
class GetFavoritesDTO:
    user_id: str