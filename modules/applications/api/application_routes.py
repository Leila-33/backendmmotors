from fastapi import APIRouter, HTTPException, Depends

from modules.auth.dependencies import get_current_user
from modules.applications.application.use_cases.create_application import CreateApplication
from modules.applications.application.use_cases.update_application import UpdateApplication
from modules.applications.application.use_cases.upload_document import UploadDocument
from modules.applications.application.use_cases.submit_application import SubmitApplication
from modules.applications.application.use_cases.submit_new_application import SubmitNewApplication
from modules.applications.application.use_cases.create_application_with_document import SubmitNewApplication
from modules.applications.application.use_cases.get_applications_status import GetApplicationStatus
from modules.applications.application.use_cases.create_application_with_document import CreateApplicationWithDocument
from modules.applications.api.schemas import (
  CreateApplicationRequest,
    UpdateApplicationRequest,   
    UploadDocumentRequest,
    UploadDocumentWithDraftRequest,
    ApplicationResponse,
    DocumentResponse,
    SubmitApplicationRequest,
    SubmitNewApplicationRequest,
    ApplicationStatusResponse

)
router = APIRouter()




from modules.applications.api.dependencies import (
    get_application_repository,
    get_document_repository,
    get_event_repository,
)

from modules.vehicles.api.dependencies import get_vehicle_repository

# =========================
# 🟢 CREATE APPLICATION (DRAFT)
# =========================
@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    data: CreateApplicationRequest,
    repo=Depends(get_application_repository),
    vehicle_repo=Depends(get_vehicle_repository),
    event_repo=Depends(get_event_repository),  # 🔥 AJOUT ICI
    current_user=Depends(get_current_user)
):

    use_case = CreateApplication(repo, vehicle_repo, event_repo)

    try:
        result = use_case.execute(data, current_user.id)

        return ApplicationResponse.model_validate(result)

    except Exception as e:

        if str(e) == "VEHICLE_NOT_FOUND":
            raise HTTPException(404, "Véhicule introuvable")

        if str(e) == "VEHICLE_NOT_AVAILABLE":
            raise HTTPException(400, "Véhicule indisponible")

        raise HTTPException(500, "Erreur serveur")


# =========================
# 🟡 UPLOAD DOCUMENT
# =========================
@router.post("/applications/{application_id}/documents", response_model=DocumentResponse)
def upload_document(
    application_id: str,
    data: UploadDocumentRequest,
    application_repo=Depends(get_application_repository),
    document_repo=Depends(get_document_repository),
    event_repo=Depends(get_event_repository),  # 🔥 AJOUT ICI
    current_user=Depends(get_current_user)
):

    use_case = UploadDocument(application_repo, document_repo, event_repo)

    try:
        return use_case.execute(
            user_id=current_user.id,
            application_id=application_id,
            data=data
        )

    except Exception as e:

        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(404, "Dossier introuvable")

        if str(e) == "APPLICATION_NOT_EDITABLE":
            raise HTTPException(400, "Le dossier ne peut plus être modifié")

        if str(e) == "FORBIDDEN":
            raise HTTPException(403, "Accès interdit")

        raise HTTPException(500, "Erreur lors de l'ajout du document")
    
    
@router.post("/documents/with-draft", response_model=DocumentResponse)
def upload_document_with_draft(
    data: UploadDocumentWithDraftRequest,
    application_repo=Depends(get_application_repository),
    document_repo=Depends(get_document_repository),
    event_repo=Depends(get_event_repository),
    current_user=Depends(get_current_user)
):

    use_case = CreateApplicationWithDocument(application_repo, document_repo, event_repo)

    try:
        return use_case.execute(
            user_id=current_user.id,
            data=data
        )

    except Exception as e:

        if str(e) == "VEHICLE_NOT_FOUND":
            raise HTTPException(404, "Véhicule introuvable")

        if str(e) == "VEHICLE_NOT_AVAILABLE":
            raise HTTPException(400, "Véhicule indisponible")

        raise HTTPException(500, "Erreur serveur")
# =========================
# 🔵 SUBMIT APPLICATION
# =========================
@router.post("/applications/{application_id}/submit")
def submit_application(
    application_id: str,
    data: SubmitApplicationRequest,
    repo=Depends(get_application_repository),
    event_repo=Depends(get_event_repository)
):

    use_case = SubmitApplication(repo, event_repo)

    try:
        result = use_case.execute(
            application_id,
            data
        )

        return result

    except Exception as e:

        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(404, "Dossier introuvable")

        if str(e) == "APPLICATION_NOT_MODIFIABLE":
            raise HTTPException(
                400,
                "Le dossier ne peut plus être modifié"
            )

        if str(e) == "DOCUMENTS_REQUIRED":
            raise HTTPException(
                400,
                "Veuillez ajouter au moins un document"
            )
        if "MISSING_DOCUMENTS" in str(e):
            missing = str(e).split(":")[1]
            raise HTTPException(
                400,
                f"Documents manquants : {missing}"
            )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la soumission du dossier"
        )
    
# Update application

@router.put("/applications/{application_id}")
def update_application(
    application_id: str,
    data: UpdateApplicationRequest,
    repo=Depends(get_application_repository)
):

    use_case = UpdateApplication(repo)

    try:
        result = use_case.execute(application_id, data) 
        return result

    except Exception as e:

        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(404, "Dossier introuvable")

        if str(e) == "APPLICATION_NOT_EDITABLE":
            raise HTTPException(
                400,
                "Le dossier ne peut plus être modifié"
            )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la mise à jour du dossier"
        )
    

# Submit new application

@router.post("/applications", response_model=ApplicationResponse)
def submit_new_application(
    data: SubmitNewApplicationRequest,
    repo=Depends(get_application_repository),
    event_repo=Depends(get_event_repository),
    current_user=Depends(get_current_user)
):

    use_case = SubmitNewApplication(repo, event_repo)

    try:
        result = use_case.execute(data, current_user.id)
        return ApplicationResponse(**result)

    except Exception as e:

        if str(e) == "VEHICLE_NOT_FOUND":
            raise HTTPException(404, "Véhicule introuvable")

        if str(e) == "VEHICLE_NOT_AVAILABLE":
            raise HTTPException(400, "Véhicule indisponible")

        raise HTTPException(500, "Erreur lors de la soumission du dossier")


# Get application status

@router.get(
    "/applications/{application_id}/status",
    response_model=ApplicationStatusResponse
)
def get_application_status(
    application_id: str,
    application_repo=Depends(get_application_repository),
    vehicle_repo=Depends(get_vehicle_repository),
    current_user=Depends(get_current_user)
):

    use_case = GetApplicationStatus(application_repo, vehicle_repo)

    try:
        result = use_case.execute(application_id, current_user.id)
        return result

    except Exception as e:

        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(404, "Dossier introuvable")

        if str(e) == "FORBIDDEN":
            raise HTTPException(403, "Accès interdit")

        raise HTTPException(500, "Erreur serveur")
    

@router.get("/applications/{application_id}")
def get_application_detail_client(
    application_id: str,
    repo=Depends(get_application_repository),
    current_user=Depends(get_current_user)
):

    result = repo.get_detail_application(
        application_id,
        user_id=current_user.id,
        is_admin=False
    )

    if not result:
        raise HTTPException(status_code=404, detail="Dossier introuvable")

    return result