from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.applications.application.results.application_form_result import (
    ApplicationFormResult,
)
from modules.applications.application.services.application_form_service import (
    ApplicationFormService,
)
from modules.applications.domain.enums import (
    ApplicationStatus,
    ApplicationType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.financing.domain.exceptions import (
    ExpensesGreaterThanIncome,
)
from modules.reservations.domain.enums import (
    ReservationStatus,
)
from modules.vehicles.domain.exceptions import (
    VehicleNotAvailable,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def trade_in_repository():
    return Mock()


@pytest.fixture
def financing_repository():
    return Mock()


@pytest.fixture
def application_option_repository():
    return Mock()


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def financing_service():
    return Mock()


@pytest.fixture
def trade_in_service():
    return Mock()


@pytest.fixture
def document_sync_service():
    return Mock()


@pytest.fixture
def service(
    application_repository,
    trade_in_repository,
    financing_repository,
    application_option_repository,
    reservation_repository,
    financing_service,
    trade_in_service,
    document_sync_service,
):
    return ApplicationFormService(
        application_repository=application_repository,
        trade_in_repository=trade_in_repository,
        financing_repository=financing_repository,
        application_option_repository=application_option_repository,
        reservation_repository=reservation_repository,
        financing_service=financing_service,
        trade_in_service=trade_in_service,
        document_sync_service=document_sync_service,
    )


@pytest.fixture
def application():
    return SimpleNamespace(
        id="app-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        status=ApplicationStatus.DRAFT,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        address=None,
        birth_date=None,
        monthly_income=None,
        monthly_expenses=None,
        employment_status=None,
    )


@pytest.fixture
def dto():
    return SimpleNamespace(
        id=None,
        vehicle_id="vehicle-123",
        first_name="Leila",
        last_name="El",
        email="leila@example.com",
        phone="0600000000",
        address="Bordeaux",
        birth_date=date(1990, 1, 1),
        monthly_income=2500,
        monthly_expenses=1000,
        employment_status="CDI",
        trade_in=None,
        financing=None,
        total_price=None,
        selected_option_ids=None,
        documents=None,
        application_type=ApplicationType.SALE,
        selected_dates=None,
    )


# ============================================================
# SAVE
# ============================================================


def test_save_returns_application_form_result(
    service,
    dto,
    application,
    application_repository,
):
    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    result = service.save(
        dto=dto,
        current_user_id="user-123",
    )

    assert isinstance(result, ApplicationFormResult)
    assert result.application is application
    assert result.is_new is False


def test_save_updates_application(
    service,
    dto,
    application,
    application_repository,
):
    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    service.save(
        dto=dto,
        current_user_id="user-123",
    )

    application_repository.update.assert_called_once_with(
        application
    )


def test_save_stops_when_financial_information_is_invalid(
    service,
    dto,
    application_repository,
):
    dto.monthly_income = 1000
    dto.monthly_expenses = 1500

    with pytest.raises(ExpensesGreaterThanIncome):
        service.save(
            dto=dto,
            current_user_id="user-123",
        )

    application_repository.update.assert_not_called()


# ============================================================
# _get_or_create_application
# ============================================================


def test_get_existing_application_by_id(
    service,
    dto,
    application,
    application_repository,
):
    dto.id = "app-123"

    application_repository.get_by_id.return_value = application

    result = service._get_or_create_application(
        dto=dto,
        current_user_id="user-123",
    )

    assert result.application is application
    assert result.is_new is False

    application_repository.get_by_id.assert_called_once_with(
        "app-123"
    )

    application_repository.find_draft_by_user_and_vehicle.assert_not_called()
    application_repository.create_base.assert_not_called()


def test_existing_application_by_id_raises_when_not_found(
    service,
    dto,
    application_repository,
):
    dto.id = "app-123"

    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        service._get_or_create_application(
            dto=dto,
            current_user_id="user-123",
        )

    application_repository.find_draft_by_user_and_vehicle.assert_not_called()
    application_repository.create_base.assert_not_called()


def test_get_existing_draft(
    service,
    dto,
    application,
    application_repository,
):
    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    result = service._get_or_create_application(
        dto=dto,
        current_user_id="user-123",
    )

    assert result.application is application
    assert result.is_new is False

    application_repository.find_draft_by_user_and_vehicle.assert_called_once_with(
        user_id="user-123",
        vehicle_id="vehicle-123",
    )

    application_repository.create_base.assert_not_called()


def test_creates_new_application_when_no_draft_exists(
    service,
    dto,
    application_repository,
):
    application_repository.find_draft_by_user_and_vehicle.return_value = None

    created_application = SimpleNamespace(
        id="app-new",
        user_id="user-123",
        vehicle_id="vehicle-123",
        status=ApplicationStatus.DRAFT,
    )

    application_repository.create_base.return_value = (
        created_application
    )

    result = service._get_or_create_application(
        dto=dto,
        current_user_id="user-123",
    )

    assert result.application is created_application
    assert result.is_new is True

    application_repository.create_base.assert_called_once()

    created = application_repository.create_base.call_args.args[0]

    assert created.user_id == "user-123"
    assert created.vehicle_id == "vehicle-123"
    assert created.status == ApplicationStatus.DRAFT
    assert created.created_at is not None


# ============================================================
# _save_trade_in
# ============================================================


def test_trade_in_returns_zero_when_not_provided(
    service,
    dto,
    trade_in_service,
    trade_in_repository,
):
    dto.trade_in = None

    result = service._save_trade_in(
        dto=dto,
        application_id="app-123",
    )

    assert result == 0
    trade_in_service.estimate.assert_not_called()
    trade_in_repository.save.assert_not_called()


def test_trade_in_returns_zero_when_disabled(
    service,
    dto,
    trade_in_service,
    trade_in_repository,
):
    dto.trade_in = SimpleNamespace(
        enabled=False,
        brand="BMW",
        model="X1",
        year=2020,
        mileage=50000,
        condition="GOOD",
    )

    result = service._save_trade_in(
        dto=dto,
        application_id="app-123",
    )

    assert result == 0
    trade_in_service.estimate.assert_not_called()
    trade_in_repository.save.assert_not_called()


def test_trade_in_is_estimated_and_saved(
    service,
    dto,
    trade_in_service,
    trade_in_repository,
):
    dto.trade_in = SimpleNamespace(
        enabled=True,
        brand="BMW",
        model="X1",
        year=2020,
        mileage=50000,
        condition="GOOD",
    )

    trade_in_service.estimate.return_value = SimpleNamespace(
        estimated_value=12000
    )

    result = service._save_trade_in(
        dto=dto,
        application_id="app-123",
    )

    assert result == 12000

    trade_in_service.estimate.assert_called_once()

    trade_in_repository.save.assert_called_once()

    saved_trade_in = trade_in_repository.save.call_args.args[0]

    assert saved_trade_in.application_id == "app-123"
    assert saved_trade_in.brand == "BMW"
    assert saved_trade_in.model == "X1"
    assert saved_trade_in.year == 2020
    assert saved_trade_in.mileage == 50000
    assert saved_trade_in.condition == "GOOD"
    assert saved_trade_in.estimated_value == 12000


# ============================================================
# _save_financing
# ============================================================


def test_financing_does_nothing_when_not_provided(
    service,
    dto,
    financing_service,
    financing_repository,
):
    dto.financing = None

    service._save_financing(
        dto=dto,
        application_id="app-123",
        trade_in_value=0,
    )

    financing_service.calculate.assert_not_called()
    financing_repository.save.assert_not_called()


def test_financing_does_nothing_when_total_price_is_none(
    service,
    dto,
    financing_service,
    financing_repository,
):
    dto.financing = SimpleNamespace(
        down_payment=5000,
        duration_months=48,
    )
    dto.total_price = None

    service._save_financing(
        dto=dto,
        application_id="app-123",
        trade_in_value=10000,
    )

    financing_service.calculate.assert_not_called()
    financing_repository.save.assert_not_called()


def test_financing_is_calculated_and_saved(
    service,
    dto,
    financing_service,
    financing_repository,
):
    dto.total_price = 30000
    dto.financing = SimpleNamespace(
        down_payment=5000,
        duration_months=48,
    )

    financing_service.calculate.return_value = SimpleNamespace(
        financed_amount=13000,
        monthly_payment=270.83,
    )

    service._save_financing(
        dto=dto,
        application_id="app-123",
        trade_in_value=12000,
    )

    financing_service.calculate.assert_called_once()

    financing_input = financing_service.calculate.call_args.args[0]

    assert financing_input.total_price == 30000
    assert financing_input.down_payment == 5000
    assert financing_input.duration_months == 48
    assert financing_input.trade_in_value == 12000

    financing_repository.save.assert_called_once()

    saved_financing = financing_repository.save.call_args.args[0]

    assert saved_financing.application_id == "app-123"
    assert saved_financing.down_payment == 5000
    assert saved_financing.duration_months == 48
    assert saved_financing.financed_amount == 13000
    assert saved_financing.monthly_payment == 270.83


# ============================================================
# _update_snapshot
# ============================================================


def test_update_snapshot_copies_user_information(
    service,
    dto,
    application,
):
    service._update_snapshot(
        dto=dto,
        application=application,
    )

    assert application.first_name == "Leila"
    assert application.last_name == "El"
    assert application.email == "leila@example.com"
    assert application.phone == "0600000000"
    assert application.address == "Bordeaux"
    assert application.birth_date == date(1990, 1, 1)
    assert application.monthly_income == 2500
    assert application.monthly_expenses == 1000
    assert application.employment_status == "CDI"


# ============================================================
# _save_options
# ============================================================


def test_options_are_not_saved_when_none(
    service,
    dto,
    application_option_repository,
):
    dto.selected_option_ids = None

    service._save_options(
        dto=dto,
        application_id="app-123",
    )

    application_option_repository.replace_options.assert_not_called()


def test_options_are_replaced_when_provided(
    service,
    dto,
    application_option_repository,
):
    dto.selected_option_ids = [
        "option-1",
        "option-2",
    ]

    service._save_options(
        dto=dto,
        application_id="app-123",
    )

    application_option_repository.replace_options.assert_called_once_with(
        application_id="app-123",
        option_ids=[
            "option-1",
            "option-2",
        ],
    )


# ============================================================
# _save_documents
# ============================================================


def test_documents_are_not_synced_when_none(
    service,
    dto,
    document_sync_service,
):
    dto.documents = None

    service._save_documents(
        dto=dto,
        application_id="app-123",
    )

    document_sync_service.sync.assert_not_called()


def test_documents_are_synced_when_provided(
    service,
    dto,
    document_sync_service,
):
    documents = [
        SimpleNamespace(id="doc-1"),
        SimpleNamespace(id="doc-2"),
    ]

    dto.documents = documents

    service._save_documents(
        dto=dto,
        application_id="app-123",
    )

    document_sync_service.sync.assert_called_once_with(
        application_id="app-123",
        documents=documents,
    )


# ============================================================
# _save_reservation
# ============================================================


def test_reservation_is_not_saved_for_non_rental_application(
    service,
    dto,
    application,
    reservation_repository,
):
    dto.application_type = ApplicationType.SALE
    dto.selected_dates = SimpleNamespace(
        start=date(2026, 9, 10),
        end=date(2026, 9, 15),
    )

    service._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.exists_overlap.assert_not_called()
    reservation_repository.create_or_update.assert_not_called()


def test_reservation_is_not_saved_without_selected_dates(
    service,
    dto,
    application,
    reservation_repository,
):
    dto.application_type = ApplicationType.RENT
    dto.selected_dates = None

    service._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.exists_overlap.assert_not_called()
    reservation_repository.create_or_update.assert_not_called()


def test_rental_reservation_checks_overlap(
    service,
    dto,
    application,
    reservation_repository,
):
    dto.application_type = ApplicationType.RENT
    dto.selected_dates = SimpleNamespace(
        start=date(2026, 9, 10),
        end=date(2026, 9, 15),
    )

    reservation_repository.exists_overlap.return_value = False

    service._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
        exclude_application_id="app-123",
    )


def test_rental_reservation_raises_when_overlap_exists(
    service,
    dto,
    application,
    reservation_repository,
):
    dto.application_type = ApplicationType.RENT
    dto.selected_dates = SimpleNamespace(
        start=date(2026, 9, 10),
        end=date(2026, 9, 15),
    )

    reservation_repository.exists_overlap.return_value = True

    with pytest.raises(VehicleNotAvailable):
        service._save_reservation(
            dto=dto,
            application=application,
        )

    reservation_repository.create_or_update.assert_not_called()


def test_rental_reservation_is_created_when_no_overlap(
    service,
    dto,
    application,
    reservation_repository,
):
    dto.application_type = ApplicationType.RENT
    dto.selected_dates = SimpleNamespace(
        start=date(2026, 9, 10),
        end=date(2026, 9, 15),
    )

    reservation_repository.exists_overlap.return_value = False

    service._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.create_or_update.assert_called_once_with(
        application_id="app-123",
        vehicle_id="vehicle-123",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
        status=ReservationStatus.DRAFT,
    )


# ============================================================
# _validate_financial_information
# ============================================================


def test_financial_information_is_valid_when_expenses_are_lower_than_income(
    service,
    dto,
):
    dto.monthly_income = 2500
    dto.monthly_expenses = 1500

    service._validate_financial_information(dto)


def test_financial_information_is_valid_when_expenses_equal_income(
    service,
    dto,
):
    dto.monthly_income = 2000
    dto.monthly_expenses = 2000

    service._validate_financial_information(dto)


def test_financial_information_is_valid_when_income_is_none(
    service,
    dto,
):
    dto.monthly_income = None
    dto.monthly_expenses = 1000

    service._validate_financial_information(dto)


def test_financial_information_is_valid_when_expenses_are_none(
    service,
    dto,
):
    dto.monthly_income = 2500
    dto.monthly_expenses = None

    service._validate_financial_information(dto)


def test_financial_information_raises_when_expenses_exceed_income(
    service,
    dto,
):
    dto.monthly_income = 2000
    dto.monthly_expenses = 2500

    with pytest.raises(ExpensesGreaterThanIncome):
        service._validate_financial_information(dto)


# ============================================================
# COMPLETE SAVE FLOW
# ============================================================


def test_save_complete_flow_for_new_application(
    service,
    dto,
    application,
    application_repository,
    trade_in_service,
    trade_in_repository,
    financing_service,
    financing_repository,
    application_option_repository,
    document_sync_service,
    reservation_repository,
):
    dto.trade_in = SimpleNamespace(
        enabled=True,
        brand="BMW",
        model="X1",
        year=2020,
        mileage=50000,
        condition="GOOD",
    )

    trade_in_service.estimate.return_value = SimpleNamespace(
        estimated_value=10000
    )

    dto.total_price = 30000
    dto.financing = SimpleNamespace(
        down_payment=5000,
        duration_months=48,
    )

    financing_service.calculate.return_value = SimpleNamespace(
        financed_amount=15000,
        monthly_payment=300,
    )

    dto.selected_option_ids = [
        "option-1",
        "option-2",
    ]

    dto.documents = [
        SimpleNamespace(id="doc-1"),
    ]

    dto.application_type = ApplicationType.SALE

    application_repository.find_draft_by_user_and_vehicle.return_value = None

    # La fixture application est déjà ton application créée
    created_application = application

    application_repository.create_base.return_value = created_application

    result = service.save(
        dto=dto,
        current_user_id="user-123",
    )

    assert result.application is created_application
    assert result.is_new is True

    trade_in_service.estimate.assert_called_once()
    trade_in_repository.save.assert_called_once()

    financing_service.calculate.assert_called_once()
    financing_repository.save.assert_called_once()

    application_option_repository.replace_options.assert_called_once_with(
        application_id="app-123",
        option_ids=[
            "option-1",
            "option-2",
        ],
    )

    document_sync_service.sync.assert_called_once_with(
        application_id="app-123",
        documents=dto.documents,
    )

    reservation_repository.create_or_update.assert_not_called()

    application_repository.update.assert_called_once_with(
        created_application
    )