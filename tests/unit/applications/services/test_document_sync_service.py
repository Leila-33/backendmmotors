from unittest.mock import Mock

import pytest

from modules.applications.application.services.document_sync_service import (
    DocumentSyncService,
)
from modules.applications.domain.enums import DocumentStatus


@pytest.fixture
def document_repository():
    return Mock()


@pytest.fixture
def s3_service():
    return Mock()


@pytest.fixture
def service(
    document_repository,
    s3_service,
):
    return DocumentSyncService(
        document_repository=document_repository,
        s3_service=s3_service,
    )


def make_document(
    document_id="doc-1",
    document_type="IDENTITY",
    s3_key="documents/old.pdf",
    status=DocumentStatus.REJECTED,
    comment="Document invalide",
):
    document = Mock()

    document.id = document_id
    document.type = document_type
    document.s3_key = s3_key
    document.status = status
    document.comment = comment

    return document


def make_dto(
    document_type="IDENTITY",
    s3_key="documents/new.pdf",
):
    document = Mock()

    document.type = document_type
    document.s3_key = s3_key

    return document


# ============================================================
# DOCUMENT EXISTANT — MÊME FICHIER
# ============================================================


def test_does_nothing_when_existing_document_has_same_s3_key(
    service,
    document_repository,
    s3_service,
):
    existing = make_document(
        document_type="IDENTITY",
        s3_key="documents/identity.pdf",
    )

    incoming = make_dto(
        document_type="IDENTITY",
        s3_key="documents/identity.pdf",
    )

    document_repository.get_by_application.return_value = [
        existing
    ]

    service.sync(
        application_id="app-123",
        documents=[incoming],
    )

    s3_service.delete_file.assert_not_called()
    document_repository.save.assert_not_called()
    document_repository.create.assert_not_called()
    document_repository.delete.assert_not_called()


# ============================================================
# DOCUMENT EXISTANT — FICHIER MODIFIÉ
# ============================================================


def test_replaces_existing_document_when_s3_key_changes(
    service,
    document_repository,
    s3_service,
):
    existing = make_document(
        document_type="IDENTITY",
        s3_key="documents/old.pdf",
    )

    incoming = make_dto(
        document_type="IDENTITY",
        s3_key="documents/new.pdf",
    )

    document_repository.get_by_application.return_value = [
        existing
    ]

    service.sync(
        application_id="app-123",
        documents=[incoming],
    )

    s3_service.delete_file.assert_called_once_with(
        "documents/old.pdf"
    )

    document_repository.save.assert_called_once_with(
        existing
    )

    assert existing.s3_key == "documents/new.pdf"
    assert existing.status == DocumentStatus.PENDING
    assert existing.comment is None

    document_repository.create.assert_not_called()
    document_repository.delete.assert_not_called()


def test_resets_status_to_pending_when_existing_document_changes(
    service,
    document_repository,
    s3_service,
):
    existing = make_document(
        document_type="IDENTITY",
        s3_key="documents/old.pdf",
        status=DocumentStatus.REJECTED,
        comment="Mauvais document",
    )

    incoming = make_dto(
        document_type="IDENTITY",
        s3_key="documents/new.pdf",
    )

    document_repository.get_by_application.return_value = [
        existing
    ]

    service.sync(
        application_id="app-123",
        documents=[incoming],
    )

    assert existing.status == DocumentStatus.PENDING
    assert existing.comment is None


# ============================================================
# NOUVEAU DOCUMENT
# ============================================================


def test_creates_new_document_when_type_does_not_exist(
    service,
    document_repository,
):
    incoming = make_dto(
        document_type="PAYSLIP",
        s3_key="documents/payslip.pdf",
    )

    document_repository.get_by_application.return_value = []

    service.sync(
        application_id="app-123",
        documents=[incoming],
    )

    document_repository.create.assert_called_once()

    created = document_repository.create.call_args.args[0]

    assert created.application_id == "app-123"
    assert created.type == "PAYSLIP"
    assert created.s3_key == "documents/payslip.pdf"
    assert created.status == DocumentStatus.PENDING
    assert created.id is not None

    document_repository.save.assert_not_called()


def test_creates_multiple_new_documents(
    service,
    document_repository,
):
    documents = [
        make_dto(
            document_type="IDENTITY",
            s3_key="documents/identity.pdf",
        ),
        make_dto(
            document_type="PAYSLIP",
            s3_key="documents/payslip.pdf",
        ),
    ]

    document_repository.get_by_application.return_value = []

    service.sync(
        application_id="app-123",
        documents=documents,
    )

    assert document_repository.create.call_count == 2

    created_documents = [
        call.args[0]
        for call in document_repository.create.call_args_list
    ]

    assert created_documents[0].type == "IDENTITY"
    assert created_documents[0].s3_key == "documents/identity.pdf"

    assert created_documents[1].type == "PAYSLIP"
    assert created_documents[1].s3_key == "documents/payslip.pdf"


# ============================================================
# DOCUMENT RETIRÉ DE LA LISTE
# ============================================================


def test_deletes_existing_document_when_type_is_removed(
    service,
    document_repository,
    s3_service,
):
    existing = make_document(
        document_id="doc-123",
        document_type="IDENTITY",
        s3_key="documents/identity.pdf",
    )

    incoming = make_dto(
        document_type="PAYSLIP",
        s3_key="documents/payslip.pdf",
    )

    document_repository.get_by_application.return_value = [
        existing
    ]

    service.sync(
        application_id="app-123",
        documents=[incoming],
    )

    s3_service.delete_file.assert_called_once_with(
        "documents/identity.pdf"
    )

    document_repository.delete.assert_called_once_with(
        "doc-123"
    )

    document_repository.create.assert_called_once()

    created = document_repository.create.call_args.args[0]

    assert created.type == "PAYSLIP"


def test_deletes_all_existing_documents_when_incoming_list_is_empty(
    service,
    document_repository,
    s3_service,
):
    existing_identity = make_document(
        document_id="doc-1",
        document_type="IDENTITY",
        s3_key="documents/identity.pdf",
    )

    existing_payslip = make_document(
        document_id="doc-2",
        document_type="PAYSLIP",
        s3_key="documents/payslip.pdf",
    )

    document_repository.get_by_application.return_value = [
        existing_identity,
        existing_payslip,
    ]

    service.sync(
        application_id="app-123",
        documents=[],
    )

    assert s3_service.delete_file.call_count == 2

    s3_service.delete_file.assert_any_call(
        "documents/identity.pdf"
    )

    s3_service.delete_file.assert_any_call(
        "documents/payslip.pdf"
    )

    assert document_repository.delete.call_count == 2

    document_repository.delete.assert_any_call("doc-1")
    document_repository.delete.assert_any_call("doc-2")

    document_repository.create.assert_not_called()
    document_repository.save.assert_not_called()


# ============================================================
# SYNCHRONISATION MIXTE
# ============================================================


def test_sync_handles_new_updated_unchanged_and_removed_documents(
    service,
    document_repository,
    s3_service,
):
    unchanged = make_document(
        document_id="doc-1",
        document_type="IDENTITY",
        s3_key="documents/identity.pdf",
    )

    updated = make_document(
        document_id="doc-2",
        document_type="PAYSLIP",
        s3_key="documents/old-payslip.pdf",
        status=DocumentStatus.REJECTED,
        comment="À corriger",
    )

    removed = make_document(
        document_id="doc-3",
        document_type="ADDRESS",
        s3_key="documents/address.pdf",
    )

    incoming_unchanged = make_dto(
        document_type="IDENTITY",
        s3_key="documents/identity.pdf",
    )

    incoming_updated = make_dto(
        document_type="PAYSLIP",
        s3_key="documents/new-payslip.pdf",
    )

    incoming_new = make_dto(
        document_type="RIB",
        s3_key="documents/rib.pdf",
    )

    document_repository.get_by_application.return_value = [
        unchanged,
        updated,
        removed,
    ]

    service.sync(
        application_id="app-123",
        documents=[
            incoming_unchanged,
            incoming_updated,
            incoming_new,
        ],
    )

    # Document inchangé
    assert unchanged.s3_key == "documents/identity.pdf"

    # Document remplacé
    assert updated.s3_key == "documents/new-payslip.pdf"
    assert updated.status == DocumentStatus.PENDING
    assert updated.comment is None

    s3_service.delete_file.assert_any_call(
        "documents/old-payslip.pdf"
    )

    document_repository.save.assert_called_once_with(
        updated
    )

    # Nouveau document
    document_repository.create.assert_called_once()

    created = document_repository.create.call_args.args[0]

    assert created.type == "RIB"
    assert created.s3_key == "documents/rib.pdf"
    assert created.application_id == "app-123"
    assert created.status == DocumentStatus.PENDING

    # Document supprimé
    s3_service.delete_file.assert_any_call(
        "documents/address.pdf"
    )

    document_repository.delete.assert_called_once_with(
        "doc-3"
    )


# ============================================================
# APPLICATION ID
# ============================================================


def test_uses_application_id_to_load_existing_documents(
    service,
    document_repository,
):
    document_repository.get_by_application.return_value = []

    service.sync(
        application_id="application-456",
        documents=[],
    )

    document_repository.get_by_application.assert_called_once_with(
        "application-456"
    )