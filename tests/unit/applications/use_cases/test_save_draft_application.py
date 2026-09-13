from unittest.mock import Mock, patch

import pytest

from modules.applications.application.dtos.save_draft_application_dto import (
    SaveDraftApplicationDTO,
)
from modules.applications.application.use_cases.save_draft_application import (
    SaveDraftApplicationUseCase,
)
from modules.applications.domain.enums import EventType


@pytest.fixture
def application_form_service():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    application_form_service,
    event_service,
    uow,
):
    return SaveDraftApplicationUseCase(
        application_form_service=application_form_service,
        event_service=event_service,
        uow=uow,
    )


@pytest.fixture
def dto():
    return Mock(spec=SaveDraftApplicationDTO)


@pytest.fixture
def application():
    application = Mock()

    application.id = "application-1"
    application.vehicle_id = "vehicle-1"

    status = Mock()
    status.value = "DRAFT"
    application.status = status

    return application


@pytest.fixture
def new_result(application):
    result = Mock()
    result.is_new = True
    result.application = application
    return result


@pytest.fixture
def existing_result(application):
    result = Mock()
    result.is_new = False
    result.application = application
    return result


def test_creates_event_when_application_is_new(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    new_result,
):
    application_form_service.save.return_value = new_result

    result = use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    assert result is new_result.application

    application_form_service.save.assert_called_once_with(
        dto=dto,
        current_user_id="user-1",
    )

    event_service.log.assert_called_once_with(
        application_id="application-1",
        user_id="user-1",
        vehicle_id="vehicle-1",
        type=EventType.APPLICATION_CREATED,
        message="Dossier créé.",
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_does_not_create_event_when_application_already_exists(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    existing_result,
):
    application_form_service.save.return_value = existing_result

    result = use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    assert result is existing_result.application

    application_form_service.save.assert_called_once_with(
        dto=dto,
        current_user_id="user-1",
    )

    event_service.log.assert_not_called()

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_returns_saved_application(
    use_case,
    application_form_service,
    dto,
    new_result,
):
    application_form_service.save.return_value = new_result

    result = use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    assert result is new_result.application


def test_commits_after_successful_save(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    new_result,
):
    application_form_service.save.return_value = new_result

    use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    uow.commit.assert_called_once()


def test_rolls_back_when_save_fails(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
):
    error = RuntimeError("Erreur lors de la sauvegarde")

    application_form_service.save.side_effect = error

    with pytest.raises(RuntimeError, match="Erreur lors de la sauvegarde"):
        use_case.execute(
            dto=dto,
            current_user_id="user-1",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()
    event_service.log.assert_not_called()


def test_rolls_back_when_event_logging_fails(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    new_result,
):
    application_form_service.save.return_value = new_result

    error = RuntimeError("Erreur événement")
    event_service.log.side_effect = error

    with pytest.raises(RuntimeError, match="Erreur événement"):
        use_case.execute(
            dto=dto,
            current_user_id="user-1",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_rolls_back_when_commit_fails(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    new_result,
):
    application_form_service.save.return_value = new_result

    error = RuntimeError("Erreur commit")
    uow.commit.side_effect = error

    with pytest.raises(RuntimeError, match="Erreur commit"):
        use_case.execute(
            dto=dto,
            current_user_id="user-1",
        )

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()


def test_passes_current_user_id_to_save_service(
    use_case,
    application_form_service,
    dto,
    existing_result,
):
    application_form_service.save.return_value = existing_result

    use_case.execute(
        dto=dto,
        current_user_id="user-42",
    )

    application_form_service.save.assert_called_once_with(
        dto=dto,
        current_user_id="user-42",
    )


def test_event_contains_correct_application_and_user_data(
    use_case,
    application_form_service,
    event_service,
    dto,
    new_result,
):
    application_form_service.save.return_value = new_result

    use_case.execute(
        dto=dto,
        current_user_id="user-99",
    )

    event_service.log.assert_called_once_with(
        application_id="application-1",
        user_id="user-99",
        vehicle_id="vehicle-1",
        type=EventType.APPLICATION_CREATED,
        message="Dossier créé.",
    )