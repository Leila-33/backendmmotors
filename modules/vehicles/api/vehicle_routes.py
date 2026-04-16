from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List

from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from modules.vehicles.application.use_cases.search_vehicles import SearchVehicles
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetail

from modules.vehicles.api.schemas import VehicleSearchRequest, VehicleSearchResponse, VehicleResponse

router = APIRouter()


def get_repo():
    return VehicleRepositorySQL()


@router.get("/vehicles/search", response_model=List[VehicleSearchResponse])
def search_vehicles(
    filters: VehicleSearchRequest = Depends(),
    repo: VehicleRepositorySQL = Depends(get_repo)
):

    use_case = SearchVehicles(repo)

    vehicles = use_case.execute(filters.model_dump(exclude_none=True))

    return [
        VehicleSearchResponse.model_validate(v)
        for v in vehicles
    ]


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str,
    repo: VehicleRepositorySQL = Depends(get_repo)
):

    use_case = GetVehicleDetail(repo)

    try:
        vehicle = use_case.execute(vehicle_id)

        return VehicleResponse.model_validate(vehicle)

    except Exception as e:

        if str(e) == "VEHICLE_NOT_FOUND":
            raise HTTPException(404, "Véhicule introuvable")

        raise HTTPException(500, "Erreur serveur")