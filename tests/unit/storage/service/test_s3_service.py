from unittest.mock import Mock, patch

import pytest

from modules.storage.infrastrucure.s3_service import S3Service


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def s3_client():
    return Mock()


@pytest.fixture
def s3_service(s3_client):
    return S3Service(
        client=s3_client
    )


# ============================================================
# DELETE FILE
# ============================================================


def test_delete_file_calls_s3_delete_object(
    s3_service,
    s3_client,
):
    s3_service.delete_file(
        key="documents/application-1/file.pdf"
    )

    s3_client.delete_object.assert_called_once()


def test_delete_file_uses_correct_bucket_and_key(
    s3_service,
    s3_client,
):
    key = "documents/application-1/file.pdf"

    s3_service.delete_file(
        key=key
    )

    kwargs = s3_client.delete_object.call_args.kwargs

    assert kwargs["Key"] == key


def test_delete_file_uses_settings_bucket(
    s3_service,
    s3_client,
):
    key = "documents/application-1/file.pdf"

    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_BUCKET = "test-bucket"

        s3_service.delete_file(
            key=key
        )

    s3_client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=key,
    )


def test_delete_file_propagates_client_error(
    s3_service,
    s3_client,
):
    s3_client.delete_object.side_effect = RuntimeError(
        "S3 deletion error"
    )

    with pytest.raises(
        RuntimeError,
        match="S3 deletion error",
    ):
        s3_service.delete_file(
            key="documents/file.pdf"
        )


def test_delete_file_does_not_call_other_s3_methods(
    s3_service,
    s3_client,
):
    s3_service.delete_file(
        key="documents/file.pdf"
    )

    s3_client.generate_presigned_url.assert_not_called()


# ============================================================
# GENERATE UPLOAD URL
# ============================================================


def test_generate_upload_url_returns_upload_url_and_key(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/vehicles/test"
    )

    with patch.object(
        s3_service,
        "_public_url",
        return_value="http://minio:9000/vehicles/test",
    ):
        result = s3_service.generate_upload_url(
            filename="document.pdf",
            content_type="application/pdf",
        )

    assert "upload_url" in result
    assert "key" in result

    assert result["upload_url"] == (
        "http://minio:9000/vehicles/test"
    )

    assert result["key"].endswith(
        "_document.pdf"
    )


def test_generate_upload_url_generates_uuid_key(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/upload"
    )

    fixed_uuid = "12345678-1234-5678-1234-567812345678"

    with patch(
        "modules.storage.infrastrucure.s3_service.uuid.uuid4",
        return_value=fixed_uuid,
    ):
        result = s3_service.generate_upload_url(
            filename="document.pdf",
            content_type="application/pdf",
        )

    assert result["key"] == (
        "12345678-1234-5678-1234-567812345678_document.pdf"
    )


def test_generate_upload_url_calls_presigned_url_with_correct_parameters(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/upload"
    )

    with patch(
        "modules.storage.infrastrucure.s3_service.uuid.uuid4",
        return_value="fixed-uuid",
    ):
        s3_service.generate_upload_url(
            filename="document.pdf",
            content_type="application/pdf",
        )

    s3_client.generate_presigned_url.assert_called_once_with(
        "put_object",
        Params={
            "Bucket": s3_client.generate_presigned_url.call_args.kwargs[
                "Params"
            ]["Bucket"],
            "Key": "fixed-uuid_document.pdf",
            "ContentType": "application/pdf",
        },
        ExpiresIn=3600,
    )


def test_generate_upload_url_uses_settings_bucket(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/upload"
    )

    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_BUCKET = "test-bucket"
        mocked_settings.S3_PUBLIC_ENDPOINT = ""
        mocked_settings.S3_ENDPOINT = "http://minio:9000"

        result = s3_service.generate_upload_url(
            filename="document.pdf",
            content_type="application/pdf",
        )

    assert result["key"].endswith(
        "_document.pdf"
    )

    kwargs = s3_client.generate_presigned_url.call_args.kwargs

    assert kwargs["Params"]["Bucket"] == "test-bucket"


def test_generate_upload_url_calls_public_url_conversion(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/vehicles/upload"
    )

    with patch.object(
        s3_service,
        "_public_url",
        return_value="https://public.example.com/upload",
    ) as public_url:

        result = s3_service.generate_upload_url(
            filename="file.pdf",
            content_type="application/pdf",
        )

    public_url.assert_called_once_with(
        "http://minio:9000/vehicles/upload"
    )

    assert result["upload_url"] == (
        "https://public.example.com/upload"
    )


def test_generate_upload_url_propagates_client_error(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.side_effect = RuntimeError(
        "presigned URL error"
    )

    with pytest.raises(
        RuntimeError,
        match="presigned URL error",
    ):
        s3_service.generate_upload_url(
            filename="file.pdf",
            content_type="application/pdf",
        )


# ============================================================
# GENERATE DOWNLOAD URL
# ============================================================


def test_generate_download_url_returns_public_url(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/vehicles/file.pdf"
    )

    with patch.object(
        s3_service,
        "_public_url",
        return_value="https://public.example.com/file.pdf",
    ):

        result = s3_service.generate_download_url(
            key="file.pdf"
        )

    assert result == (
        "https://public.example.com/file.pdf"
    )


def test_generate_download_url_calls_get_object(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/vehicles/file.pdf"
    )

    s3_service.generate_download_url(
        key="documents/file.pdf"
    )

    s3_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={
            "Bucket": s3_client.generate_presigned_url.call_args.kwargs[
                "Params"
            ]["Bucket"],
            "Key": "documents/file.pdf",
        },
        ExpiresIn=3600,
    )


def test_generate_download_url_uses_correct_key(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/vehicles/file.pdf"
    )

    s3_service.generate_download_url(
        key="documents/application-1/file.pdf"
    )

    kwargs = s3_client.generate_presigned_url.call_args.kwargs

    assert kwargs["Params"]["Key"] == (
        "documents/application-1/file.pdf"
    )


def test_generate_download_url_uses_settings_bucket(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/file.pdf"
    )

    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_BUCKET = "test-bucket"
        mocked_settings.S3_PUBLIC_ENDPOINT = ""
        mocked_settings.S3_ENDPOINT = "http://minio:9000"

        s3_service.generate_download_url(
            key="file.pdf"
        )

    kwargs = s3_client.generate_presigned_url.call_args.kwargs

    assert kwargs["Params"]["Bucket"] == "test-bucket"


def test_generate_download_url_propagates_client_error(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.side_effect = RuntimeError(
        "download URL error"
    )

    with pytest.raises(
        RuntimeError,
        match="download URL error",
    ):
        s3_service.generate_download_url(
            key="file.pdf"
        )


# ============================================================
# _PUBLIC_URL
# ============================================================


def test_public_url_replaces_internal_endpoint(
    s3_service,
):
    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_PUBLIC_ENDPOINT = (
            "https://files.example.com"
        )
        mocked_settings.S3_ENDPOINT = (
            "http://minio:9000"
        )

        result = s3_service._public_url(
            "http://minio:9000/vehicles/file.pdf"
        )

    assert result == (
        "https://files.example.com/vehicles/file.pdf"
    )


def test_public_url_returns_original_url_when_public_endpoint_is_not_configured(
    s3_service,
):
    url = "http://minio:9000/vehicles/file.pdf"

    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_PUBLIC_ENDPOINT = (
            ""
        )
        mocked_settings.S3_ENDPOINT = (
            "http://minio:9000"
        )

        result = s3_service._public_url(
            url
        )

    assert result == url


def test_public_url_returns_original_url_when_public_endpoint_is_none(
    s3_service,
):
    url = "http://minio:9000/vehicles/file.pdf"

    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_PUBLIC_ENDPOINT = None
        mocked_settings.S3_ENDPOINT = (
            "http://minio:9000"
        )

        result = s3_service._public_url(
            url
        )

    assert result == url


def test_public_url_replaces_only_endpoint(
    s3_service,
):
    with patch(
        "modules.storage.infrastrucure.s3_service.settings"
    ) as mocked_settings:

        mocked_settings.S3_PUBLIC_ENDPOINT = (
            "https://cdn.example.com"
        )
        mocked_settings.S3_ENDPOINT = (
            "http://minio:9000"
        )

        result = s3_service._public_url(
            "http://minio:9000/vehicles/file.pdf?token=123"
        )

    assert result == (
        "https://cdn.example.com/vehicles/file.pdf?token=123"
    )


# ============================================================
# INTEGRATION BETWEEN METHODS
# ============================================================


def test_generate_upload_url_returns_generated_key(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/upload"
    )

    with patch(
        "modules.storage.infrastrucure.s3_service.uuid.uuid4",
        return_value="my-uuid",
    ):
        result = s3_service.generate_upload_url(
            filename="photo.jpg",
            content_type="image/jpeg",
        )

    assert result["key"] == "my-uuid_photo.jpg"


def test_generate_download_url_returns_string(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/download"
    )

    result = s3_service.generate_download_url(
        key="photo.jpg"
    )

    assert isinstance(
        result,
        str,
    )


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_generate_upload_url_does_not_delete_file(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/upload"
    )

    s3_service.generate_upload_url(
        filename="file.pdf",
        content_type="application/pdf",
    )

    s3_client.delete_object.assert_not_called()


def test_generate_download_url_does_not_delete_file(
    s3_service,
    s3_client,
):
    s3_client.generate_presigned_url.return_value = (
        "http://minio:9000/download"
    )

    s3_service.generate_download_url(
        key="file.pdf"
    )

    s3_client.delete_object.assert_not_called()


def test_delete_file_does_not_generate_url(
    s3_service,
    s3_client,
):
    s3_service.delete_file(
        key="file.pdf"
    )

    s3_client.generate_presigned_url.assert_not_called()