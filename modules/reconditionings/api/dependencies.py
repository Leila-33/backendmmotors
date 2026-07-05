from fastapi import Depends

from modules.reconditionings.application.use_cases.admin.get_reconditioning import (
    GetReconditioningUseCase
)
from modules.reconditionings.application.use_cases.admin.start_reconditioning import StartReconditioningUseCase

from modules.core.infrastructure.dependencies import get_reconditioning_repository
from modules.core.infrastructure.dependencies import (
    get_reconditioning_repository,
    get_vehicle_repository,
    get_job_queue,
    get_inspection_repository
)

def get_reconditioning_uc(repo=Depends(get_reconditioning_repository)):
    return GetReconditioningUseCase(repo)


def get_start_reconditioning_uc(
    vehicle_repository=Depends(get_vehicle_repository),
    reconditioning_repository=Depends(get_reconditioning_repository),
    inspection_repository=Depends(get_inspection_repository),
    job_queue=Depends(get_job_queue),
):
    return StartReconditioningUseCase(
        vehicle_repository=vehicle_repository,
        reconditioning_repository=reconditioning_repository,
        inspection_repository=inspection_repository,
        job_queue=job_queue
    )