from unittest.mock import patch

from core.config.settings import settings
from modules.storage.infrastructure.s3_client import (
    get_s3_client,
    get_s3_public_client,
)


class TestS3Client:
    """Tests de création des clients S3."""

    # =========================
    # INTERNAL CLIENT
    # =========================

    @patch("modules.storage.infrastructure.s3_client.boto3.client")
    def test_get_s3_client(self, mock_boto3_client):
        # Arrange
        mock_client = mock_boto3_client.return_value

        # Act
        result = get_s3_client()

        # Assert
        assert result is mock_client

        mock_boto3_client.assert_called_once_with(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )

    # =========================
    # PUBLIC CLIENT
    # =========================

    @patch("modules.storage.infrastructure.s3_client.boto3.client")
    def test_get_s3_public_client(self, mock_boto3_client):
        # Arrange
        mock_client = mock_boto3_client.return_value

        # Act
        result = get_s3_public_client()

        # Assert
        assert result is mock_client

        mock_boto3_client.assert_called_once_with(
            "s3",
            endpoint_url=settings.S3_PUBLIC_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )