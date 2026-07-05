from fastapi import Depends
from modules.core.infrastructure.dependencies import (
    get_inspection_repository,
    get_vehicle_repository,
    get_job_queue,
)

from modules.inspections.application.use_cases.admin.get_inspection import GetInspectionUseCase
from modules.inspections.application.use_cases.admin.start_inspection import StartInspectionUseCase


def get_inspection_uc(repo=Depends(get_inspection_repository)):
    return GetInspectionUseCase(repo)


def get_start_inspection_uc(
    vehicle_repository=Depends(get_vehicle_repository),
    inspection_repository=Depends(get_inspection_repository),
    job_queue=Depends(get_job_queue),
):
    return StartInspectionUseCase(
        vehicle_repository=vehicle_repository,
        inspection_repository=inspection_repository,
        job_queue=job_queue
    )