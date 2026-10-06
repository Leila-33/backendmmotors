from core.config.settings import settings
import uuid

class S3Service:
    """
    Centralise les opérations de gestion des fichiers sur le stockage S3.

    Le client interne est utilisé pour les opérations serveur.
    Le client public est utilisé pour générer les URLs présignées
    destinées au navigateur.
    """

    def __init__(self, client, public_client):
        self.client = client
        self.public_client = public_client

    # =========================
    # DELETE FILE
    # =========================
    def delete_file(
        self,
        key: str,
    ):
        self.client.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
        )

    # =========================
    # GENERATE UPLOAD URL
    # =========================
    def generate_upload_url(
        self,
        filename: str,
        content_type: str,
    ):
        key = f"{uuid.uuid4()}_{filename}"

        url = self.public_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

        return {
            "upload_url": url,
            "key": key,
        }

    # =========================
    # GENERATE DOWNLOAD URL
    # =========================
    def generate_download_url(
        self,
        key: str,
    ):
        return self.public_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
            },
            ExpiresIn=3600,
        )