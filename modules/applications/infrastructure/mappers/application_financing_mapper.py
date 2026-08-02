from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing
)
from modules.applications.infrastructure.db.application_financing_model import (
    ApplicationFinancingModel
)


class ApplicationFinancingMapper:


    @staticmethod
    def to_domain(
        model: ApplicationFinancingModel
    ) -> ApplicationFinancing:

        return ApplicationFinancing(
            application_id=model.application_id,
            down_payment=model.down_payment,
            duration_months=model.duration_months,
            financed_amount=model.financed_amount,
            monthly_payment=model.monthly_payment,
        )


    @staticmethod
    def to_model(
        entity: ApplicationFinancing
    ) -> ApplicationFinancingModel:

        return ApplicationFinancingModel(
            application_id=entity.application_id,
            down_payment=entity.down_payment,
            duration_months=entity.duration_months,
            financed_amount=entity.financed_amount,
            monthly_payment=entity.monthly_payment,
        )


    @staticmethod
    def update_model(
        model: ApplicationFinancingModel,
        entity: ApplicationFinancing
    ) -> ApplicationFinancingModel:

        model.down_payment = entity.down_payment
        model.duration_months = entity.duration_months
        model.financed_amount = entity.financed_amount
        model.monthly_payment = entity.monthly_payment

        return model