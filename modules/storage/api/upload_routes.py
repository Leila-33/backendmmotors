from fastapi import APIRouter, Depends
from modules.storage.api.schemas import UploadRequest
from modules.storage.infrastrucure.s3_service import S3Service
from modules.storage.api.dependencies import get_s3_service
router = APIRouter()




@router.post("/upload-url")
def generate_upload_url(
    data: UploadRequest,
    s3_service: S3Service = Depends(get_s3_service)
):

    return s3_service.generate_upload_url(
        filename=data.filename,
        content_type=data.content_type
    )