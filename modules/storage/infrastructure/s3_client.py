import boto3

from core.config.settings import settings


def get_s3_client():
    """
    Crée le client S3 interne utilisé par le backend.

    Le backend communique directement avec MinIO
    via le réseau Docker.
    """

    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


def get_s3_public_client():
    """
    Crée un client S3 configuré avec l'endpoint public.

    Ce client est utilisé uniquement pour générer
    des URLs présignées destinées au navigateur.
    """

    return boto3.client(
        "s3",
        endpoint_url=settings.S3_PUBLIC_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )