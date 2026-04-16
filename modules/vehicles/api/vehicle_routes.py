from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List

from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from modules.vehicles.application.use_cases.search_vehicles import SearchVehicles
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetail

from modules.vehicles.api.schemas import VehicleSearchResponse, VehicleResponse

router = APIRouter()


def get_repo():
    return VehicleRepositorySQL()


@router.get("/vehicles/search", response_model=List[VehicleSearchResponse])
def search_vehicles(
    type: Optional[str] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    engineType: Optional[str] = None,
    year: Optional[int] = None,
    mileage: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    isAvailable: Optional[bool] = None,
    repo: VehicleRepositorySQL = Depends(get_repo)
):

    filters = {k: v for k, v in locals().items() if v is not None}
    filters.pop("repo")

    use_case = SearchVehicles(repo)
    return use_case.execute(filters)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str, repo: VehicleRepositorySQL = Depends(get_repo)):

    use_case = GetVehicleDetail(repo)
    vehicle = use_case.execute(vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle