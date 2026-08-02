from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn
)

from modules.applications.infrastructure.db.application_trade_in_model import (
    ApplicationTradeInModel
)


class ApplicationTradeInMapper:


    @staticmethod
    def to_domain(
        model: ApplicationTradeInModel
    ) -> ApplicationTradeIn:

        return ApplicationTradeIn(
            application_id=model.application_id,
            brand=model.brand,
            model=model.model,
            year=model.year,
            mileage=model.mileage,
            condition=model.condition,
            estimated_value=model.estimated_value,
        )


    @staticmethod
    def to_model(
        entity: ApplicationTradeIn
    ) -> ApplicationTradeInModel:

        return ApplicationTradeInModel(
            application_id=entity.application_id,
            brand=entity.brand,
            model=entity.model,
            year=entity.year,
            mileage=entity.mileage,
            condition=entity.condition,
            estimated_value=entity.estimated_value,
        )


    @staticmethod
    def update_model(
        model: ApplicationTradeInModel,
        entity: ApplicationTradeIn
    ) -> ApplicationTradeInModel:

        model.brand = entity.brand
        model.model = entity.model
        model.year = entity.year
        model.mileage = entity.mileage
        model.condition = entity.condition
        model.estimated_value = entity.estimated_value

        return model