from uuid import uuid4
from modules.options.domain.entities.option import Option
from modules.options.api.schemas import CreateOptionResponse
from modules.options.domain.exceptions import OptionAlreadyExists
from modules.options.domain.enums import OptionType

class CreateOptionUseCase:


    def __init__(
        self,
        option_repository,
        unit_of_work,
    ):
        self.option_repository = option_repository
        self.unit_of_work = unit_of_work



    def execute(
        self,
        request,
    ):


        # =========================
        # NORMALIZE NAME
        # =========================

        name = (
            request.name
            .strip()
        )


        # =========================
        # BUSINESS RULE
        # =========================

        exists = (
            self.option_repository
            .exists_by_name(
                name
            )
        )


        if exists:
            raise OptionAlreadyExists(
                name
            )


        # =========================
        # CREATE DOMAIN
        # =========================

        option = Option(

            id=str(uuid4()),

            name=name,

            type=OptionType.CUSTOM,

            price=request.price,

            billing_type=request.billing_type,

            is_active=True,

        )


        # =========================
        # SAVE
        # =========================

        option = (
            self.option_repository
            .save(option)
        )


        self.unit_of_work.commit()



        return CreateOptionResponse(

            id=option.id,

            message="Option créée avec succès"

        )