from uuid import uuid4
from modules.options.domain.entities.option import Option
from modules.options.api.schemas import CreateOptionResponse
from modules.options.domain.exceptions import OptionAlreadyExists
from modules.options.domain.enums import OptionType
from modules.applications.domain.enums import EventType
import logging
logger = logging.getLogger(__name__)

class CreateOptionUseCase:


    def __init__(
        self,
        option_repository,
        event_service,
        unit_of_work,
    ):
        self.option_repository = option_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work



    def execute(
        self,
        request,
        current_admin
    ):

        try:
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

            self.event_service.log(
            type=EventType.OPTION_CREATED,
            message="Option créée",
            user_id=current_admin.id,
            event_metadata={
                "option_id": option.id,
                "name": option.name,
            }
        )
            self.unit_of_work.commit()



            return CreateOptionResponse(

                id=option.id,

                message="Option créée avec succès"

            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur lors de la création d'une option",
                extra={
                    "option_name": option.name,
                }
            )

            raise