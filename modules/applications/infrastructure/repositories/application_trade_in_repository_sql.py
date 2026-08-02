from sqlalchemy.orm import Session

from modules.applications.domain.repositories.application_trade_in_repository import (
    ApplicationTradeInRepository
)
from modules.applications.domain.entities.application_trade_in import ApplicationTradeIn

from modules.applications.infrastructure.db.application_trade_in_model import (
    ApplicationTradeInModel
)

from modules.applications.infrastructure.mappers.application_trade_in_mapper import (
    ApplicationTradeInMapper
)


class ApplicationTradeInRepositorySQL(
    ApplicationTradeInRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db


    # =========================
    # SAVE / UPDATE TRADE IN
    # =========================
    def save(
        self,
        trade_in: ApplicationTradeIn
    ):

        existing = (
            self.db.query(
                ApplicationTradeInModel
            )
            .filter_by(
                application_id=trade_in.application_id
            )
            .first()
        )


        if existing:

            ApplicationTradeInMapper.update_model(
                existing,
                trade_in
            )


        else:

            existing = ApplicationTradeInMapper.to_model(
                trade_in
            )

            self.db.add(existing)


        self.db.flush()


        return ApplicationTradeInMapper.to_domain(
            existing
        )



    # =========================
    # GET BY APPLICATION
    # =========================
    def get_by_application(
        self,
        application_id: str
    ):

        model = (
            self.db.query(
                ApplicationTradeInModel
            )
            .filter_by(
                application_id=application_id
            )
            .first()
        )


        if not model:
            return None


        return ApplicationTradeInMapper.to_domain(
            model
        )



    # =========================
    # DELETE BY APPLICATION
    # =========================
    def delete_by_application(
        self,
        application_id: str
    ) -> None:

        (
            self.db.query(
                ApplicationTradeInModel
            )
            .filter(
                ApplicationTradeInModel.application_id == application_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.flush()