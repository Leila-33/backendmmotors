from core.config.settings import settings
import uuid


class S3Service:
    """
    Centralise les opérations de gestion des fichiers sur le stockage S3.

    Le service permet de supprimer des fichiers et de générer
    des URLs temporaires pour leur dépôt ou leur téléchargement.
    """
    def __init__(self, client):

        self.client = client


    # =========================
    # DELETE FILE
    # =========================
    def delete_file(
        self,
        key: str
    ):

        self.client.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=key
        )


    # =========================
    # GENERATE UPLOAD URL
    # =========================
    def generate_upload_url(
        self,
        filename: str,
        content_type: str
    ):

        key = f"{uuid.uuid4()}_{filename}"

        url = self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

        return {
            "upload_url": self._public_url(url),
            "key": key
        }


    # =========================
    # GENERATE DOWNLOAD URL
    # =========================
    def generate_download_url(
        self,
        key: str
    ):

        url = self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
            },
            ExpiresIn=3600,
        )

        return self._public_url(url)


    # =========================
    # MINIO URL -> BROWSER URL
    # =========================
    def _public_url(
        self,
        url: str
    ):

        if settings.S3_PUBLIC_ENDPOINT:
            return url.replace(
                settings.S3_ENDPOINT,
                settings.S3_PUBLIC_ENDPOINT
            )

        return url