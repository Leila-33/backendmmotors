from fastapi import APIRouter
from pydantic import BaseModel, Field
import boto3
import uuid

from core.config import settings

router = APIRouter()


# =========================
# REQUEST MODEL
# =========================
class UploadRequest(BaseModel):
    filename: str = Field(..., description="Nom du fichier")
    content_type: str = Field(..., description="MIME type du fichier (ex: image/png)")

# =========================
# S3 CLIENT
# =========================
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


# =========================
# GENERATE UPLOAD URL
# =========================
@router.post("/upload-url")
def generate_upload_url(data: UploadRequest):

    s3 = get_s3_client()

    unique_name = f"{uuid.uuid4()}_{data.filename}"

    # =========================
    # UPLOAD PRESIGNED URL (PUT)
    # =========================
    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.S3_BUCKET,
            "Key": unique_name,
            "ContentType": data.content_type,
        },
        ExpiresIn=60,
    )

    # =========================
    # RETURN CLEAN RESPONSE
    # =========================
    return {
        "upload_url": upload_url,
        "key": unique_name   # ✅ IMPORTANT
    }