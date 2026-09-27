from datetime import datetime, timedelta, timezone
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
from modules.auth.domain.exceptions import Forbidden
from modules.financing.domain.exceptions import (
    ExpensesGreaterThanIncome,
)
from modules.reservations.domain.enums import ReservationStatus
from modules.vehicles.domain.enums import VehicleType
from modules.vehicles.domain.exceptions import (
    VehicleNotAvailable,
    VehicleNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    vehicle_type=VehicleType.SALE,
    is_available=True,
):
    return SimpleNamespace(
        id=vehicle_id,
        type=vehicle_type,
        is_available=is_available,
    )


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    status=ApplicationStatus.DRAFT,
    discount=0,
    total_price=10000,
):
    return SimpleNamespace(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
        discount=discount,
        base_price=None,
        optional_price=0,
        total_price=total_price,
    )


def make_selected_dates():
    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        start=now + timedelta(days=2),
        end=now + timedelta(days=5),
    )


def make_trade_in(
    *,
    enabled=True,
):
    return SimpleNamespace(
        enabled=enabled,
        brand="Renault",
        model="Clio",
        year=2020,
        mileage=50000,
        condition="GOOD",
    )


def make_financing():
    return SimpleNamespace(
        down_payment=2000,
        duration_months=48,
    )


def make_dto(
    *,
    application_id=None,
    vehicle_id="vehicle-1",
    application_type=ApplicationType.SALE,
    selected_option_ids=None,
    selected_dates=None,
    trade_in=None,
    financing=None,
    documents=None,
    monthly_income=3000,
    monthly_expenses=1000,
):
    return SimpleNamespace(
        id=application_id,
        vehicle_id=vehicle_id,
        application_type=application_type,
        selected_option_ids=selected_option_ids,
        selected_dates=selected_dates,
        trade_in=trade_in,
        financing=financing,
        documents=documents,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="0600000000",
        address="1 rue de Bordeaux",
        birth_date=datetime(1990, 1, 1),
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        employment_status="EMPLOYED",
    )


def make_pricing_result():
    return SimpleNamespace(
        base_price=10000,
        optional_price=1500,
        discount=500,
        total_price=11000,
    )


def make_trade_in_result():
    return SimpleNamespace(
        estimated_value=4000,
    )


def make_financing_result():
    return SimpleNamespace(
        financed_amount=5000,
        monthly_payment=120,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def application_repository():
    repository = Mock()
    repository.create_base.side_effect = lambda application: application
    return repository


@pytest.fixture
def vehicle_repository():
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
def option_repository():
    return Mock()


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def financing_service():
    service = Mock()
    service.calculate.return_value = make_financing_result()
    return service


@pytest.fixture
def trade_in_service():
    service = Mock()
    service.estimate.return_value = make_trade_in_result()
    return service


@pytest.fixture
def document_sync_service():
    return Mock()


@pytest.fixture
def rental_duration_calculator():
    service = Mock()
    service.calculate.return_value = 4
    return service


@pytest.fixture
def pricing_calculator():
    service = Mock()
    service.calculate.return_value = make_pricing_result()
    return service


@pytest.fixture
def use_case(
    application_repository,
    vehicle_repository,
    trade_in_repository,
    financing_repository,
    application_option_repository,
    option_repository,
    reservation_repository,
    financing_service,
    trade_in_service,
    document_sync_service,
    rental_duration_calculator,
    pricing_calculator,
):
    return ApplicationFormService(
        application_repository=application_repository,
        vehicle_repository=vehicle_repository,
        trade_in_repository=trade_in_repository,
        financing_repository=financing_repository,
        application_option_repository=application_option_repository,
        option_repository=option_repository,
        reservation_repository=reservation_repository,
        financing_service=financing_service,
        trade_in_service=trade_in_service,
        document_sync_service=document_sync_service,
        rental_duration_calculator=rental_duration_calculator,
        pricing_calculator=pricing_calculator,
    )


# ============================================================
# FINANCIAL VALIDATION
# ============================================================


def test_financial_information_is_validated(
    use_case,
):
    dto = make_dto(
        monthly_income=3000,
        monthly_expenses=4000,
    )

    with pytest.raises(ExpensesGreaterThanIncome):
        use_case.save(
            dto=dto,
            current_user_id="user-1",
        )


def test_financial_information_is_valid_when_expenses_are_lower(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    pricing_calculator,
):
    application = make_application()

    dto = make_dto()

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_ids.return_value = []

    use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    pricing_calculator.calculate.assert_called_once()


def test_financial_information_is_valid_when_values_are_none(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
):
    application = make_application()

    dto = make_dto(
        monthly_income=None,
        monthly_expenses=None,
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle()
    option_repository.get_by_ids.return_value = []

    result = use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    assert isinstance(result, ApplicationFormResult)


# ============================================================
# EXISTING APPLICATION
# ============================================================


def test_existing_application_is_loaded(
    use_case,
    application_repository,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
    )

    dto = make_dto(
        application_id="application-42",
    )

    application_repository.get_by_id.return_value = application

    result = use_case._get_or_create_application(
        dto=dto,
        current_user_id="user-42",
    )

    application_repository.get_by_id.assert_called_once_with(
        "application-42"
    )

    assert result.application is application
    assert result.is_new is False


def test_existing_application_not_found(
    use_case,
    application_repository,
):
    dto = make_dto(
        application_id="application-42",
    )

    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case._get_or_create_application(
            dto=dto,
            current_user_id="user-42",
        )

    application_repository.get_by_id.assert_called_once_with(
        "application-42"
    )


def test_user_cannot_modify_another_users_application(
    use_case,
    application_repository,
):
    application = make_application(
        application_id="application-42",
        user_id="owner-42",
    )

    dto = make_dto(
        application_id="application-42",
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(Forbidden):
        use_case._get_or_create_application(
            dto=dto,
            current_user_id="another-user",
        )


# ============================================================
# EXISTING DRAFT
# ============================================================


def test_existing_draft_is_reused(
    use_case,
    application_repository,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
        vehicle_id="vehicle-42",
    )

    dto = make_dto(
        application_id=None,
        vehicle_id="vehicle-42",
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    result = use_case._get_or_create_application(
        dto=dto,
        current_user_id="user-42",
    )

    application_repository.find_draft_by_user_and_vehicle.assert_called_once_with(
        user_id="user-42",
        vehicle_id="vehicle-42",
    )

    assert result.application is application
    assert result.is_new is False


# ============================================================
# CREATE APPLICATION
# ============================================================


def test_application_is_created_when_no_draft_exists(
    use_case,
    application_repository,
):
    dto = make_dto(
        application_id=None,
        vehicle_id="vehicle-42",
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = None

    result = use_case._get_or_create_application(
        dto=dto,
        current_user_id="user-42",
    )

    application_repository.create_base.assert_called_once()

    created_application = (
        application_repository.create_base.call_args.args[0]
    )

    assert created_application.user_id == "user-42"
    assert created_application.vehicle_id == "vehicle-42"
    assert created_application.status == ApplicationStatus.DRAFT
    assert created_application.base_price is None
    assert created_application.optional_price == 0
    assert created_application.discount == 0
    assert created_application.total_price is None
    assert created_application.created_at is not None

    assert result.application is created_application
    assert result.is_new is True


# ============================================================
# VEHICLE
# ============================================================


def test_vehicle_not_found(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
):
    application = make_application()

    dto = make_dto()

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.save(
            dto=dto,
            current_user_id="user-1",
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    option_repository.get_by_ids.assert_not_called()


# ============================================================
# OPTIONS
# ============================================================


def test_options_are_loaded(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
):
    application = make_application()

    dto = make_dto(
        selected_option_ids=["option-1", "option-2"],
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_ids.return_value = [
        SimpleNamespace(id="option-1"),
        SimpleNamespace(id="option-2"),
    ]

    use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    option_repository.get_by_ids.assert_called_once_with(
        ["option-1", "option-2"]
    )


# ============================================================
# PRICING
# ============================================================


def test_pricing_is_calculated_for_sale(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    pricing_calculator,
    rental_duration_calculator,
):
    application = make_application()

    dto = make_dto(
        application_type=ApplicationType.SALE,
        selected_option_ids=[],
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle(
        vehicle_type=VehicleType.SALE,
    )

    option_repository.get_by_ids.return_value = []

    use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    pricing_calculator.calculate.assert_called_once_with(
        vehicle=vehicle_repository.get_by_id.return_value,
        options=[],
        discount=0,
        rental_days=1,
    )

    rental_duration_calculator.calculate.assert_not_called()


def test_pricing_is_calculated_for_rent(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    pricing_calculator,
    rental_duration_calculator,
    reservation_repository,
):
    application = make_application()

    dates = make_selected_dates()

    dto = make_dto(
        application_type=ApplicationType.RENT,
        selected_dates=dates,
        selected_option_ids=[],
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle(
        vehicle_id="vehicle-1",
        vehicle_type=VehicleType.RENT,
        is_available=True,
    )
    reservation_repository.exists_overlap.return_value = False
    option_repository.get_by_ids.return_value = []

    rental_duration_calculator.calculate.return_value = 3

    use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    rental_duration_calculator.calculate.assert_called_once_with(
        start_date=dates.start,
        end_date=dates.end,
    )

    pricing_calculator.calculate.assert_called_once_with(
        vehicle=vehicle_repository.get_by_id.return_value,
        options=[],
        discount=0,
        rental_days=3,
    )


def test_pricing_values_are_saved_on_application(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    pricing_calculator,
):
    application = make_application()

    dto = make_dto(
        selected_option_ids=[],
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle()
    option_repository.get_by_ids.return_value = []

    pricing_calculator.calculate.return_value = make_pricing_result()

    use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    assert application.base_price == 10000
    assert application.optional_price == 1500
    assert application.discount == 500
    assert application.total_price == 11000


# ============================================================
# TRADE-IN
# ============================================================


def test_trade_in_is_ignored_when_missing(
    use_case,
    trade_in_service,
    trade_in_repository,
):
    dto = make_dto(
        trade_in=None,
    )

    result = use_case._save_trade_in(
        dto=dto,
        application_id="application-1",
    )

    assert result == 0

    trade_in_service.estimate.assert_not_called()
    trade_in_repository.save.assert_not_called()


def test_trade_in_is_ignored_when_disabled(
    use_case,
    trade_in_service,
    trade_in_repository,
):
    dto = make_dto(
        trade_in=make_trade_in(enabled=False),
    )

    result = use_case._save_trade_in(
        dto=dto,
        application_id="application-1",
    )

    assert result == 0

    trade_in_service.estimate.assert_not_called()
    trade_in_repository.save.assert_not_called()


def test_trade_in_is_estimated_and_saved(
    use_case,
    trade_in_service,
    trade_in_repository,
):
    dto = make_dto(
        trade_in=make_trade_in(enabled=True),
    )

    trade_in_service.estimate.return_value = (
        make_trade_in_result()
    )

    result = use_case._save_trade_in(
        dto=dto,
        application_id="application-42",
    )

    assert result == 4000

    trade_in_service.estimate.assert_called_once()

    trade_in_input = (
        trade_in_service.estimate.call_args.args[0]
    )

    assert trade_in_input.brand == "Renault"
    assert trade_in_input.model == "Clio"
    assert trade_in_input.year == 2020
    assert trade_in_input.mileage == 50000
    assert trade_in_input.condition == "GOOD"

    trade_in_repository.save.assert_called_once()

    saved_trade_in = (
        trade_in_repository.save.call_args.args[0]
    )

    assert saved_trade_in.application_id == "application-42"
    assert saved_trade_in.brand == "Renault"
    assert saved_trade_in.model == "Clio"
    assert saved_trade_in.year == 2020
    assert saved_trade_in.mileage == 50000
    assert saved_trade_in.condition == "GOOD"
    assert saved_trade_in.estimated_value == 4000


def test_trade_in_error_is_propagated(
    use_case,
    trade_in_service,
):
    dto = make_dto(
        trade_in=make_trade_in(),
    )

    trade_in_service.estimate.side_effect = RuntimeError(
        "trade-in error"
    )

    with pytest.raises(
        RuntimeError,
        match="trade-in error",
    ):
        use_case._save_trade_in(
            dto=dto,
            application_id="application-1",
        )


# ============================================================
# FINANCING
# ============================================================


def test_financing_is_ignored_when_missing(
    use_case,
    financing_service,
    financing_repository,
):
    dto = make_dto(
        financing=None,
    )

    application = make_application(
        total_price=10000,
    )

    use_case._save_financing(
        dto=dto,
        application=application,
        trade_in_value=0,
    )

    financing_service.calculate.assert_not_called()
    financing_repository.save.assert_not_called()


def test_financing_is_ignored_when_total_price_is_none(
    use_case,
    financing_service,
    financing_repository,
):
    dto = make_dto(
        financing=make_financing(),
    )

    application = make_application(
        total_price=None,
    )

    use_case._save_financing(
        dto=dto,
        application=application,
        trade_in_value=0,
    )

    financing_service.calculate.assert_not_called()
    financing_repository.save.assert_not_called()


def test_financing_is_calculated_and_saved(
    use_case,
    financing_service,
    financing_repository,
):
    dto = make_dto(
        financing=make_financing(),
    )

    application = make_application(
        application_id="application-42",
        total_price=11000,
    )

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    use_case._save_financing(
        dto=dto,
        application=application,
        trade_in_value=4000,
    )

    financing_service.calculate.assert_called_once()

    financing_input = (
        financing_service.calculate.call_args.args[0]
    )

    assert financing_input.total_price == 11000
    assert financing_input.down_payment == 2000
    assert financing_input.duration_months == 48
    assert financing_input.trade_in_value == 4000

    financing_repository.save.assert_called_once()

    saved_financing = (
        financing_repository.save.call_args.args[0]
    )

    assert saved_financing.application_id == "application-42"
    assert saved_financing.down_payment == 2000
    assert saved_financing.duration_months == 48
    assert saved_financing.financed_amount == 5000
    assert saved_financing.monthly_payment == 120


def test_financing_defaults_down_payment_to_zero(
    use_case,
    financing_service,
    financing_repository,
):
    dto = make_dto(
        financing=SimpleNamespace(
            down_payment=None,
            duration_months=36,
        ),
    )

    application = make_application(
        total_price=9000,
    )

    use_case._save_financing(
        dto=dto,
        application=application,
        trade_in_value=None,
    )

    financing_input = (
        financing_service.calculate.call_args.args[0]
    )

    assert financing_input.down_payment == 0
    assert financing_input.trade_in_value == 0


# ============================================================
# SNAPSHOT
# ============================================================


def test_application_snapshot_is_updated(
    use_case,
):
    dto = make_dto()

    application = make_application()

    use_case._update_snapshot(
        dto=dto,
        application=application,
    )

    assert application.first_name == "John"
    assert application.last_name == "Doe"
    assert application.email == "john@example.com"
    assert application.phone == "0600000000"
    assert application.address == "1 rue de Bordeaux"
    assert application.birth_date == datetime(1990, 1, 1)
    assert application.monthly_income == 3000
    assert application.monthly_expenses == 1000
    assert application.employment_status == "EMPLOYED"


# ============================================================
# OPTIONS SAVE
# ============================================================


def test_options_are_not_saved_when_none(
    use_case,
    application_option_repository,
):
    dto = make_dto(
        selected_option_ids=None,
    )

    use_case._save_options(
        dto=dto,
        application_id="application-1",
    )

    application_option_repository.replace_options.assert_not_called()


def test_options_are_replaced(
    use_case,
    application_option_repository,
):
    dto = make_dto(
        selected_option_ids=["option-1", "option-2"],
    )

    use_case._save_options(
        dto=dto,
        application_id="application-42",
    )

    application_option_repository.replace_options.assert_called_once_with(
        application_id="application-42",
        option_ids=["option-1", "option-2"],
    )


# ============================================================
# DOCUMENTS
# ============================================================


def test_documents_are_not_synced_when_none(
    use_case,
    document_sync_service,
):
    dto = make_dto(
        documents=None,
    )

    use_case._save_documents(
        dto=dto,
        application_id="application-1",
    )

    document_sync_service.sync.assert_not_called()


def test_documents_are_synced(
    use_case,
    document_sync_service,
):
    documents = [
        SimpleNamespace(id="document-1"),
        SimpleNamespace(id="document-2"),
    ]

    dto = make_dto(
        documents=documents,
    )

    use_case._save_documents(
        dto=dto,
        application_id="application-42",
    )

    document_sync_service.sync.assert_called_once_with(
        application_id="application-42",
        documents=documents,
    )


# ============================================================
# RESERVATION
# ============================================================


def test_reservation_is_not_saved_for_sale(
    use_case,
    reservation_repository,
):
    dto = make_dto(
        application_type=ApplicationType.SALE,
        selected_dates=make_selected_dates(),
    )

    application = make_application()

    use_case._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.exists_overlap.assert_not_called()
    reservation_repository.create_or_update.assert_not_called()


def test_reservation_is_not_saved_without_dates(
    use_case,
    reservation_repository,
):
    dto = make_dto(
        application_type=ApplicationType.RENT,
        selected_dates=None,
    )

    application = make_application()

    use_case._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.exists_overlap.assert_not_called()
    reservation_repository.create_or_update.assert_not_called()


def test_overlapping_rental_is_rejected(
    use_case,
    reservation_repository,
):
    dates = make_selected_dates()

    dto = make_dto(
        application_type=ApplicationType.RENT,
        selected_dates=dates,
    )

    application = make_application(
        application_id="application-42",
        vehicle_id="vehicle-42",
    )

    reservation_repository.exists_overlap.return_value = True

    with pytest.raises(VehicleNotAvailable):
        use_case._save_reservation(
            dto=dto,
            application=application,
        )

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-42",
        start_date=dates.start,
        end_date=dates.end,
        exclude_application_id="application-42",
    )

    reservation_repository.create_or_update.assert_not_called()


def test_rental_reservation_is_created(
    use_case,
    reservation_repository,
):
    dates = make_selected_dates()

    dto = make_dto(
        application_type=ApplicationType.RENT,
        selected_dates=dates,
    )

    application = make_application(
        application_id="application-42",
        vehicle_id="vehicle-42",
    )

    reservation_repository.exists_overlap.return_value = False

    use_case._save_reservation(
        dto=dto,
        application=application,
    )

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-42",
        start_date=dates.start,
        end_date=dates.end,
        exclude_application_id="application-42",
    )

    reservation_repository.create_or_update.assert_called_once_with(
        application_id="application-42",
        vehicle_id="vehicle-42",
        start_date=dates.start,
        end_date=dates.end,
        status=ReservationStatus.DRAFT,
    )


# ============================================================
# FULL SAVE — SALE
# ============================================================


def test_save_complete_sale_flow(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    application_option_repository,
    document_sync_service,
    reservation_repository,
    pricing_calculator,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
        vehicle_id="vehicle-42",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-42",
        vehicle_type=VehicleType.SALE,
    )

    dto = make_dto(
        application_id="application-42",
        vehicle_id="vehicle-42",
        application_type=ApplicationType.SALE,
        selected_option_ids=["option-1"],
        documents=["document-1"],
    )

    application_repository.get_by_id.return_value = application

    vehicle_repository.get_by_id.return_value = vehicle
    option_repository.get_by_ids.return_value = [
        SimpleNamespace(id="option-1")
    ]

    pricing_calculator.calculate.return_value = (
        make_pricing_result()
    )

    result = use_case.save(
        dto=dto,
        current_user_id="user-42",
    )

    assert isinstance(result, ApplicationFormResult)
    assert result.application is application
    assert result.is_new is False
    application_repository.get_by_id.assert_called_once_with(
        "application-42"
    )
    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-42"
    )

    option_repository.get_by_ids.assert_called_once_with(
        ["option-1"]
    )

    pricing_calculator.calculate.assert_called_once()

    application_option_repository.replace_options.assert_called_once_with(
        application_id="application-42",
        option_ids=["option-1"],
    )

    document_sync_service.sync.assert_called_once_with(
        application_id="application-42",
        documents=["document-1"],
    )

    reservation_repository.create_or_update.assert_not_called()

    application_repository.update.assert_called_once_with(
        application
    )


# ============================================================
# FULL SAVE — RENT
# ============================================================


def test_save_complete_rent_flow(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    rental_duration_calculator,
    reservation_repository,
    pricing_calculator,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
        vehicle_id="vehicle-42",
    )

    dates = make_selected_dates()

    vehicle = make_vehicle(
        vehicle_id="vehicle-42",
        vehicle_type=VehicleType.RENT,
    )

    dto = make_dto(
        application_id="application-42",
        vehicle_id="vehicle-42",
        application_type=ApplicationType.RENT,
        selected_dates=dates,
        selected_option_ids=[],
    )

    application_repository.get_by_id.return_value = application

    vehicle_repository.get_by_id.return_value = vehicle
    option_repository.get_by_ids.return_value = []

    rental_duration_calculator.calculate.return_value = 3

    reservation_repository.exists_overlap.return_value = False

    pricing_calculator.calculate.return_value = (
        make_pricing_result()
    )

    result = use_case.save(
        dto=dto,
        current_user_id="user-42",
    )

    assert isinstance(result, ApplicationFormResult)
    assert result.application is application

    rental_duration_calculator.calculate.assert_called_once_with(
        start_date=dates.start,
        end_date=dates.end,
    )

    pricing_calculator.calculate.assert_called_once_with(
        vehicle=vehicle,
        options=[],
        discount=0,
        rental_days=3,
    )

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-42",
        start_date=dates.start,
        end_date=dates.end,
        exclude_application_id="application-42",
    )

    reservation_repository.create_or_update.assert_called_once_with(
        application_id="application-42",
        vehicle_id="vehicle-42",
        start_date=dates.start,
        end_date=dates.end,
        status=ReservationStatus.DRAFT,
    )

    application_repository.update.assert_called_once_with(
        application
    )


# ============================================================
# FULL SAVE — TRADE-IN + FINANCING
# ============================================================


def test_save_with_trade_in_and_financing(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    trade_in_service,
    trade_in_repository,
    financing_service,
    financing_repository,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
        vehicle_id="vehicle-42",
    )

    dto = make_dto(
        application_id="application-42",
        vehicle_id="vehicle-42",
        trade_in=make_trade_in(),
        financing=make_financing(),
        selected_option_ids=[],
    )

    application_repository.get_by_id.return_value = application

    vehicle_repository.get_by_id.return_value = make_vehicle()
    option_repository.get_by_ids.return_value = []

    trade_in_service.estimate.return_value = (
        make_trade_in_result()
    )

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    use_case.save(
        dto=dto,
        current_user_id="user-42",
    )

    trade_in_service.estimate.assert_called_once()
    trade_in_repository.save.assert_called_once()

    financing_service.calculate.assert_called_once()
    financing_repository.save.assert_called_once()

    financing_input = (
        financing_service.calculate.call_args.args[0]
    )

    assert financing_input.trade_in_value == 4000


# ============================================================
# PERSISTENCE
# ============================================================


def test_application_is_updated_at_end_of_save(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
):
    application = make_application()

    dto = make_dto(
        selected_option_ids=[],
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle()
    option_repository.get_by_ids.return_value = []

    use_case.save(
        dto=dto,
        current_user_id="user-1",
    )

    application_repository.update.assert_called_once_with(
        application
    )


# ============================================================
# ERRORS
# ============================================================


def test_pricing_error_is_propagated(
    use_case,
    application_repository,
    vehicle_repository,
    option_repository,
    pricing_calculator,
):
    application = make_application()

    dto = make_dto(
        selected_option_ids=[],
    )

    application_repository.find_draft_by_user_and_vehicle.return_value = (
        application
    )

    vehicle_repository.get_by_id.return_value = make_vehicle()
    option_repository.get_by_ids.return_value = []

    pricing_calculator.calculate.side_effect = RuntimeError(
        "pricing error"
    )

    with pytest.raises(
        RuntimeError,
        match="pricing error",
    ):
        use_case.save(
            dto=dto,
            current_user_id="user-1",
        )

    application_repository.update.assert_not_called()


def test_trade_in_error_is_propagated(
    use_case,
    trade_in_service,
):
    dto = make_dto(
        trade_in=make_trade_in(),
    )

    trade_in_service.estimate.side_effect = RuntimeError(
        "trade-in error"
    )

    with pytest.raises(
        RuntimeError,
        match="trade-in error",
    ):
        use_case._save_trade_in(
            dto=dto,
            application_id="application-1",
        )

def test_financing_error_is_propagated(
    use_case,
    financing_service,
):
    dto = make_dto(
        financing=make_financing(),
    )

    application = make_application(
        total_price=10000,
    )

    financing_service.calculate.side_effect = RuntimeError(
        "financing error"
    )

    with pytest.raises(
        RuntimeError,
        match="financing error",
    ):
        use_case._save_financing(
            dto=dto,
            application=application,
            trade_in_value=0,
        )


def test_reservation_error_is_propagated(
    use_case,
    reservation_repository,
):
    dto = make_dto(
        application_type=ApplicationType.RENT,
        selected_dates=make_selected_dates(),
    )

    application = make_application()

    reservation_repository.exists_overlap.side_effect = RuntimeError(
        "reservation error"
    )

    with pytest.raises(
        RuntimeError,
        match="reservation error",
    ):
        use_case._save_reservation(
            dto=dto,
            application=application,
        )