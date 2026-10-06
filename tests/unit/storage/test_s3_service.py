from unittest.mock import MagicMock, patch

from core.config.settings import settings
from modules.storage.infrastructure.s3_service import S3Service


class TestS3Service:
    """Tests du service de gestion des fichiers S3."""

    def setup_method(self):
        self.client = MagicMock()
        self.public_client = MagicMock()

        self.service = S3Service(
            client=self.client,
            public_client=self.public_client,
        )

    # =========================
    # DELETE FILE
    # =========================

    def test_delete_file_calls_delete_object(self):
        # Arrange
        key = "vehicles/test-image.jpg"

        # Act
        self.service.delete_file(key)

        # Assert
        self.client.delete_object.assert_called_once_with(
            Bucket=settings.S3_BUCKET,
            Key=key,
        )

    # =========================
    # GENERATE UPLOAD URL
    # =========================

    @patch(
        "modules.storage.infrastructure.s3_service.uuid.uuid4"
    )
    def test_generate_upload_url(self, mock_uuid4):
        # Arrange
        mock_uuid4.return_value = "test-uuid"

        self.public_client.generate_presigned_url.return_value = (
            "https://s3.example.com/upload-url"
        )

        # Act
        result = self.service.generate_upload_url(
            filename="vehicle.jpg",
            content_type="image/jpeg",
        )

        # Assert
        assert result == {
            "upload_url": "https://s3.example.com/upload-url",
            "key": "test-uuid_vehicle.jpg",
        }

        self.public_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": "test-uuid_vehicle.jpg",
                "ContentType": "image/jpeg",
            },
            ExpiresIn=3600,
        )

    # =========================
    # GENERATE DOWNLOAD URL
    # =========================

    def test_generate_download_url(self):
        # Arrange
        key = "vehicles/test-image.jpg"

        self.public_client.generate_presigned_url.return_value = (
            "https://s3.example.com/download-url"
        )

        # Act
        result = self.service.generate_download_url(key)

        # Assert
        assert result == "https://s3.example.com/download-url"

        self.public_client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
            },
            ExpiresIn=3600,
        )