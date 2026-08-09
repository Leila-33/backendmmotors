from modules.options.domain.exceptions import (
    OptionNotFound,
    OptionAlreadyExists,
    SystemOptionCannotBeModified
)
from modules.options.api.schemas import UpdateOptionResponse
from modules.options.domain.enums import OptionType
from modules.applications.domain.enums import EventType
import logging
logger = logging.getLogger(__name__)

class UpdateOptionUseCase:

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
        option_id: str,
        request,
        current_admin
    ):

        # =========================
        # GET OPTION
        # =========================
        try:
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
            self.event_service.log(
            type=EventType.OPTION_UPDATED,
            message="Option modifiée",
            user_id=current_admin.id,
            event_metadata={
                "option_id": option.id,
                "name": option.name,
            }
        )
          
            self.unit_of_work.commit()

            # =========================
            # RESPONSE
            # =========================

            return UpdateOptionResponse(
                id=option.id,
                message="Option modifiée avec succès"
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur lors de la modification de l'option",
                extra={
                    "option_id": option_id
                }
            )

            raise