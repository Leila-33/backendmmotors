from uuid import uuid4

from sqlalchemy.orm import Session

from modules.applications.domain.repositories.application_option_repository import (
    ApplicationOptionRepository
)

from modules.applications.infrastructure.db.application_option_model import (
    ApplicationOptionModel
)


class ApplicationOptionRepositorySQL(
    ApplicationOptionRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db


    # =========================
    # REPLACE OPTIONS
    # =========================
    def replace_options(
        self,
        application_id: str,
        option_ids: list[str]
    ):

        (
            self.db.query(
                ApplicationOptionModel
            )
            .filter_by(
                application_id=application_id
            )
            .delete(
                synchronize_session=False
            )
        )


        for option_id in option_ids:

            self.db.add(
                ApplicationOptionModel(
                    id=str(uuid4()),
                    application_id=application_id,
                    option_id=option_id,
                )
            )


        self.db.flush()



    # =========================
    # DELETE BY APPLICATION
    # =========================
    def delete_by_application(
        self,
        application_id: str
    ) -> None:

        (
            self.db.query(
                ApplicationOptionModel
            )
            .filter(
                ApplicationOptionModel.application_id == application_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.flush()