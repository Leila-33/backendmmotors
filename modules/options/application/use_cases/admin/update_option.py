from modules.options.domain.exceptions import (
    OptionNotFound,
    OptionAlreadyExists,
    SystemOptionCannotBeModified
)
from modules.options.api.schemas import UpdateOptionResponse
from modules.options.domain.enums import OptionType

class UpdateOptionUseCase:

    def __init__(
        self,
        option_repository,
        unit_of_work,
    ):
        self.option_repository = option_repository
        self.unit_of_work = unit_of_work

    def execute(
        self,
        option_id: str,
        request,
    ):

        # =========================
        # GET OPTION
        # =========================

        option = self.option_repository.get_by_id(
            option_id
        )

        if not option:
            raise OptionNotFound()

        # =========================
        # ONLY CUSTOM OPTIONS
        # =========================

        if option.type != OptionType.CUSTOM:
            raise SystemOptionCannotBeModified()

        # =========================
        # NORMALIZE NAME
        # =========================

        name = request.name.strip()

        # =========================
        # DUPLICATE CHECK
        # =========================

        exists = (
            self.option_repository
            .exists_by_name_except_id(
                name,
                option_id
            )
        )

        if exists:
            raise OptionAlreadyExists(name)

        # =========================
        # DOMAIN UPDATE
        # =========================

        option.name = name

        option.type = OptionType.CUSTOM

        option.price = request.price

        option.billing_type = request.billing_type

        # =========================
        # PERSISTENCE
        # =========================

        option = self.option_repository.update(
            option
        )

        self.unit_of_work.commit()

        # =========================
        # RESPONSE
        # =========================

        return UpdateOptionResponse(
            id=option.id,
            message="Option modifiée avec succès"
        )