from fastapi import Depends
from modules.options.application.use_cases.admin.create_option import CreateOptionUseCase
from modules.options.application.use_cases.admin.get_options import GetOptionsUseCase
from modules.options.application.use_cases.admin.update_option import UpdateOptionUseCase
from modules.options.application.use_cases.admin.toggle_options_status import ToggleOptionStatusUseCase
from modules.dependencies.dependencies import (
    get_option_repository,
    get_event_service
)
from core.database.dependencies import (
    get_unit_of_work
)

def get_create_option_usecase(

    option_repository=Depends(
        get_option_repository
    ),
    event_service=Depends(get_event_service),

    unit_of_work=Depends(
        get_unit_of_work
    ),
    

):

    return CreateOptionUseCase(

        option_repository=option_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,

    )

def get_get_options_uc(repo=Depends(get_option_repository)):
    return GetOptionsUseCase(repo)

def get_update_option_uc(

    option_repository=Depends(
        get_option_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work=Depends(
        get_unit_of_work
    ),

):

    return UpdateOptionUseCase(

        option_repository=option_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,

    )


def get_toggle_option_status_usecase(

    option_repository=Depends(
        get_option_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work=Depends(
        get_unit_of_work
    ),

):

    return ToggleOptionStatusUseCase(

        option_repository=option_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,

    )



