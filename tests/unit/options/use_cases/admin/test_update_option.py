from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.options.domain.enums import OptionType
from modules.options.domain.exceptions import (
    OptionAlreadyExists,
    OptionNotFound,
    SystemOptionCannotBeModified,
)

from modules.options.application.dtos.admin.update_option_dto import (
    UpdateOptionDTO,
)
from modules.options.application.results.admin.update_option_result import (
    UpdateOptionResult,
)
from modules.options.application.use_cases.admin.update_option import (
    UpdateOptionUseCase,
)
from modules.options.domain.enums import BillingType

@pytest.fixture
def option_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    option_repository,
    event_service,
    unit_of_work,
):
    return UpdateOptionUseCase(
        option_repository=option_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


def make_dto(
    option_id="option-123",
    admin_id="admin-123",
    name="  GPS Premium  ",
    price=350.00,
    billing_type=BillingType.FIXED,
):
    return UpdateOptionDTO(
        option_id=option_id,
        admin_id=admin_id,
        name=name,
        price=price,
        billing_type=billing_type,
    )


def make_option(
    option_id="option-123",
    name="GPS",
    price=250.00,
    billing_type=None,
    option_type=OptionType.CUSTOM,
):
    option = Mock()
    option.id = option_id
    option.name = name
    option.price = price
    option.billing_type = billing_type
    option.type = option_type
    return option


def test_update_option_success(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(
        name="GPS",
        price=250.00,
        billing_type=BillingType.FIXED,
    )

    dto = make_dto(
        name="  GPS Premium  ",
        price=350.00,
        billing_type=BillingType.FIXED,
    )

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = False

    result = use_case.execute(dto)

    assert option.name == "GPS Premium"
    assert option.price == 350.00
    assert option.billing_type == BillingType.FIXED

    option_repository.get_by_id.assert_called_once_with(
        "option-123"
    )

    option_repository.exists_by_name_except_id.assert_called_once_with(
        "GPS Premium",
        "option-123",
    )

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once_with(
        type=EventType.OPTION_UPDATED,
        message="Option modifiée",
        user_id="admin-123",
        event_metadata={
            "option_id": "option-123",
            "old_name": "GPS",
            "new_name": "GPS Premium",
            "old_price": 250.00,
            "new_price": 350.00,
            "old_billing_type": BillingType.FIXED.value,
            "new_billing_type": BillingType.FIXED.value,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(result, UpdateOptionResult)
    assert result.id == "option-123"
    assert result.message == "Option modifiée avec succès"



def test_update_option_normalizes_name(
    use_case,
    option_repository,
):
    option = make_option()
    dto = make_dto(name="  Climatisation  ")

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = False

    use_case.execute(dto)

    assert option.name == "Climatisation"

    option_repository.exists_by_name_except_id.assert_called_once_with(
        "Climatisation",
        "option-123",
    )


def test_update_option_raises_when_option_not_found(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    dto = make_dto()

    option_repository.get_by_id.return_value = None

    with pytest.raises(OptionNotFound):
        use_case.execute(dto)

    option_repository.get_by_id.assert_called_once_with(
        "option-123"
    )

    option_repository.exists_by_name_except_id.assert_not_called()
    option_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_update_option_rejects_system_option(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(
        option_type=OptionType.INCLUDED
    )

    dto = make_dto()

    option_repository.get_by_id.return_value = option

    with pytest.raises(SystemOptionCannotBeModified):
        use_case.execute(dto)

    option_repository.exists_by_name_except_id.assert_not_called()
    option_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_update_option_rejects_duplicate_name(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option()

    dto = make_dto(
        name="  Climatisation  "
    )

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = True

    with pytest.raises(OptionAlreadyExists):
        use_case.execute(dto)

    option_repository.exists_by_name_except_id.assert_called_once_with(
        "Climatisation",
        "option-123",
    )

    option_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()

    # Les anciennes valeurs doivent rester inchangées.
    assert option.name == "GPS"
    assert option.price == 250.00


def test_update_option_rolls_back_when_update_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option()

    dto = make_dto()

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = False

    option_repository.update.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_update_option_rolls_back_when_event_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option()

    dto = make_dto()

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = False

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_update_option_rolls_back_when_commit_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option()

    dto = make_dto()

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = False

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


def test_update_option_records_billing_type_values_in_event(
    use_case,
    option_repository,
    event_service,
):
    old_billing_type = BillingType.FIXED
    new_billing_type = BillingType.DAILY

    option = make_option(
        billing_type=old_billing_type
    )

    dto = make_dto(
        billing_type=new_billing_type
    )

    option_repository.get_by_id.return_value = option
    option_repository.exists_by_name_except_id.return_value = False

    use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.OPTION_UPDATED,
        message="Option modifiée",
        user_id="admin-123",
        event_metadata={
            "option_id": "option-123",
            "old_name": "GPS",
            "new_name": "GPS Premium",
            "old_price": 250.00,
            "new_price": 350.00,
            "old_billing_type": old_billing_type.value,
            "new_billing_type": new_billing_type.value,
        },
    )