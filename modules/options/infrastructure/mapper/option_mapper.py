from modules.options.domain.entities.option import (
    Option,
)
from modules.options.infrastructure.db.option_model import OptionModel

class OptionMapper:


    @staticmethod
    def to_domain(
        model
    ) -> Option:


        return Option(

            id=model.id,

            name=model.name,

            type=model.type,

            price=model.price,

            billing_type=model.billing_type,

            is_active=model.is_active,

        )



    @staticmethod
    def to_model(
        option: Option
    ):

        return OptionModel(

            id=option.id,

            name=option.name,

            type=option.type,

            price=option.price,

            billing_type=option.billing_type,

            is_active=option.is_active,

        )



    @staticmethod
    def update_model(
        model,
        option: Option
    ):


        model.name = (
            option.name
        )

        model.type = (
            option.type
        )

        model.price = (
            option.price
        )

        model.billing_type = (
            option.billing_type
        )

        model.is_active = (
            option.is_active
        )


        return model