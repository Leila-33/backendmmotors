from modules.options.domain.exceptions import OptionNotFound
from modules.options.api.schemas import UpdateOptionResponse
from modules.applications.domain.enums import EventType
import logging
logger = logging.getLogger(__name__)

class ToggleOptionStatusUseCase:


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

        try:
            # =========================
            # GET OPTION
            # =========================

            option = (
                self.option_repository
                .get_by_id(option_id)
            )


            if not option:
                raise OptionNotFound()



            # =========================
            # UPDATE STATUS
            # =========================
            old_status=option.is_active
            
            option.is_active = request.is_active



            # =========================
            # SAVE
            # =========================

            self.option_repository.update(
                option
            )

            self.event_service.log(
        type=(
            EventType.OPTION_ACTIVATED
            if request.is_active
            else EventType.OPTION_DEACTIVATED
        ),
        message=(
            "Option activée"
            if request.is_active
            else "Option désactivée"
        ),
        user_id=current_admin.id,
        event_metadata={
            "option_id": option.id,
            "old_status": old_status,
            "new_status": request.is_active,
        }
    )

            self.unit_of_work.commit()



            return UpdateOptionResponse(
                id=option.id,
                message=(
                    "Option activée"
                    if option.is_active
                    else "Option désactivée"
                )
            )
        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur lors du changement de status de l'option",
                extra={
                    "option_id": option_id
                }
            )

            raise