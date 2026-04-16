from fastapi import APIRouter, HTTPException, Depends

from modules.applications.infrastructure.repositories.application_repository_sql import ApplicationRepositorySQL
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from modules.auth.dependencies import get_current_user
from modules.applications.application.use_cases.create_application import CreateApplication
from modules.applications.application.use_cases.update_application import UpdateApplication
from modules.applications.application.use_cases.upload_document import UploadDocument
from modules.applications.application.use_cases.submit_application import SubmitApplication
from modules.applications.application.use_cases.submit_new_application import SubmitNewApplication

from modules.applications.api.schemas import (
  CreateApplicationRequest,
    UpdateApplicationRequest,   
    UploadDocumentRequest,
    UploadDocumentWithDraftRequest,
    ApplicationResponse,
    DocumentResponse,
    SubmitApplicationRequest,
    SubmitNewApplicationRequest

)
router = APIRouter()


# 🔹 Dependency
def get_repository():
    return ApplicationRepositorySQL()

def get_vehicle_repository():
    return VehicleRepositorySQL()

# =========================
# 🟢 CREATE APPLICATION (DRAFT)
# =========================
@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    data: CreateApplicationRequest,
    repo=Depends(get_repository),
    vehicle_repo=Depends(get_vehicle_repository),
    current_user=Depends(get_current_user)
):

    use_case = CreateApplication(repo, vehicle_repo)

    try:
        result = use_case.execute(data, current_user.id)

        return ApplicationResponse(**result)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création du dossier"
        )


# =========================
# 🟡 UPLOAD DOCUMENT
# =========================
@router.post(
    "/applications/{application_id}/documents",
    response_model=DocumentResponse
)
def upload_document(
    application_id: str,
    data: UploadDocumentRequest,
    repo=Depends(get_repository),
    current_user=Depends(get_current_user)
):

    use_case = UploadDocument(repo)

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

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'ajout du document"
        )
    
@router.post(
    "/documents/with-draft",
    response_model=DocumentResponse
)
def upload_document_with_draft(
    data: UploadDocumentWithDraftRequest,
    repo=Depends(get_repository),
    current_user=Depends(get_current_user)
):

    use_case = UploadDocument(repo)

    try:
        return use_case.execute_with_draft(
            user_id=current_user.id,
            data=data
        )

    except Exception as e:

        if str(e) == "VEHICLE_NOT_FOUND":
            raise HTTPException(404, "Véhicule introuvable")

        if str(e) == "VEHICLE_NOT_AVAILABLE":
            raise HTTPException(400, "Véhicule indisponible")

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création du dossier et ajout du document"
        )
# =========================
# 🔵 SUBMIT APPLICATION
# =========================
@router.post("/applications/{application_id}/submit")
def submit_application(
    application_id: str,
    data: SubmitApplicationRequest,  # ✅ AJOUT
    repo=Depends(get_repository)
):

    use_case = SubmitApplication(repo)

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
    repo=Depends(get_repository)
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
    repo=Depends(get_repository),
    current_user=Depends(get_current_user)
):

    use_case = SubmitNewApplication(repo)

    try:
        result = use_case.execute(data, current_user.id)
        return ApplicationResponse(**result)

    except Exception as e:

        if str(e) == "VEHICLE_NOT_FOUND":
            raise HTTPException(404, "Véhicule introuvable")

        if str(e) == "VEHICLE_NOT_AVAILABLE":
            raise HTTPException(400, "Véhicule indisponible")

        raise HTTPException(500, "Erreur lors de la soumission du dossier")


