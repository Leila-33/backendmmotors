from modules.options.domain.entities.option import (
    Option,
)

from modules.options.infrastructure.db.option_model import (
    OptionModel,
)

from modules.options.application.results.admin.create_option_result import (
    CreateOptionResult,
)

from modules.options.application.results.admin.update_option_result import (
    UpdateOptionResult,
)

from modules.options.application.results.admin.toggle_option_status_result import (
    ToggleOptionStatusResult,
)

from modules.options.api.schemas import (
    CreateOptionResponse,
    UpdateOptionResponse,
    ToggleOptionStatusResponse,
    OptionResponse,
    GetOptionsResponse,
)


class OptionMapper:

    # =====================================================
    # MODEL → DOMAIN
    # =====================================================

    @staticmethod
    def to_domain(
        model: OptionModel,
    ) -> Option:

        return Option(
            id=model.id,
            name=model.name,
            type=model.type,
            price=model.price,
            billing_type=model.billing_type,
            is_active=model.is_active,
        )

    # =====================================================
    # DOMAIN → MODEL
    # =====================================================

    @staticmethod
    def to_model(
        option: Option,
    ) -> OptionModel:

        return OptionModel(
            id=option.id,
            name=option.name,
            type=option.type,
            price=option.price,
            billing_type=option.billing_type,
            is_active=option.is_active,
        )

    # =====================================================
    # DOMAIN → EXISTING MODEL
    # =====================================================

    @staticmethod
    def update_model(
        model: OptionModel,
        option: Option,
    ) -> OptionModel:

        model.name = option.name
        model.type = option.type
        model.price = option.price
        model.billing_type = option.billing_type
        model.is_active = option.is_active

        return model

    # =====================================================
    # CREATE RESULT → RESPONSE
    # =====================================================

    @staticmethod
    def to_create_response(
        result: CreateOptionResult,
    ) -> CreateOptionResponse:

        return CreateOptionResponse(
            id=result.option_id,
            message=result.message,
        )

    # =====================================================
    # DOMAIN → RESPONSE
    # =====================================================

    @staticmethod
    def to_response(
        option: Option,
    ) -> OptionResponse:

        return OptionResponse(
            id=option.id,
            name=option.name,
            type=option.type.value,
            price=option.price,
            billing_type=option.billing_type.value,
            is_active=option.is_active,
        )

    # =====================================================
    # LIST RESULT → RESPONSE
    # =====================================================

    @staticmethod
    def to_list_response(
        result,
    ) -> GetOptionsResponse:

        return GetOptionsResponse(
            options=[
                OptionMapper.to_response(
                    option
                )
                for option in result.options
            ]
        )

    # =====================================================
    # TOGGLE RESULT → RESPONSE
    # =====================================================

    @staticmethod
    def to_toggle_status_response(
        result: ToggleOptionStatusResult,
    ) -> ToggleOptionStatusResponse:

        return ToggleOptionStatusResponse(
            id=result.id,
            is_active=result.is_active,
            message=result.message,
        )

    # =====================================================
    # UPDATE RESULT → RESPONSE
    # =====================================================

    @staticmethod
    def to_update_response(
        result: UpdateOptionResult,
    ) -> UpdateOptionResponse:

        return UpdateOptionResponse(
            id=result.id,
            message=result.message,
        )