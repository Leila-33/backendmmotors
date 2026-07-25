from modules.options.api.schemas import OptionResponse


class GetOptionsUseCase:

    def __init__(
        self,
        option_repository,
    ):
        self.option_repository = option_repository


    def execute(self):

        options = (
            self.option_repository
            .get_all()
        )


        return [
            OptionResponse(
                id=option.id,
                name=option.name,
                type=option.type.value,
                price=option.price,
                billing_type=(
                    option.billing_type.value
                ),
                is_active=option.is_active,
            )
            for option in options
        ]