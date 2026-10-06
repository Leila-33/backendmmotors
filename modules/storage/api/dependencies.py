from modules.storage.infrastructure.s3_service import S3Service
from modules.storage.infrastructure.s3_client import (
    get_s3_client,
    get_s3_public_client,
)


def get_s3_service():
    return S3Service(
        get_s3_client(),
        get_s3_public_client(),
    )