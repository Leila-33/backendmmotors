from fastapi import Depends
from modules.reconditionings.application.use_cases.admin.start_reconditioning import StartReconditioningUseCase
from modules.dependencies.dependencies import (
    get_reconditioning_repository,
    get_vehicle_repository,
    get_job_queue,
    get_inspection_repository
)
from core.database.dependencies import (
    get_unit_of_work
)


def get_start_reconditioning_uc(
    vehicle_repository=Depends(get_vehicle_repository),
    reconditioning_repository=Depends(get_reconditioning_repository),
    inspection_repository=Depends(get_inspection_repository),
    job_queue=Depends(get_job_queue),
    unit_of_work = Depends(get_unit_of_work)
):
    return StartReconditioningUseCase(
        vehicle_repository=vehicle_repository,
        reconditioning_repository=reconditioning_repository,
        inspection_repository=inspection_repository,
        job_queue=job_queue,
        unit_of_work=unit_of_work
    )