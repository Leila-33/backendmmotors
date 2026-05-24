from core.config import settings
from modules.storage.api.upload_routes import get_s3_client
import boto3


class S3Service:

    def __init__(self):
            self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )


    def delete_file(self, key: str):

        s3 = get_s3_client()

        s3.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=key
        )