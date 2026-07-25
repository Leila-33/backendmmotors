from fastapi import APIRouter, Depends, Query

from modules.leads.api.schemas import (
    CreateLeadRequest, 
    CreateLeadResponse
)
from modules.leads.api.dependencies import (
    get_create_lead_use_case
)
from core.security.dependencies import get_optional_current_user
from modules.leads.application.use_cases.create_lead import CreateLeadUseCase

router = APIRouter(tags=["Leads"])

@router.post(
    "",
    response_model=CreateLeadResponse
)
def create_lead(

    request: CreateLeadRequest,

    use_case: CreateLeadUseCase = Depends(
        get_create_lead_use_case
    ),

    current_user = Depends(
        get_optional_current_user
    )

):

    user_id = None


    if current_user:
        user_id = current_user.id



    return use_case.execute(
        request,
        user_id=user_id
    )
