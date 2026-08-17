import logging

from modules.options.application.dtos.admin.toggle_option_status_dto import (
    ToggleOptionStatusDTO,
)

from modules.options.application.results.admin.toggle_option_status_result import (
    ToggleOptionStatusResult,
)

from modules.options.domain.exceptions import OptionNotFound

from modules.applications.domain.enums import EventType


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
        dto: ToggleOptionStatusDTO,
    ) -> ToggleOptionStatusResult:

        try:

            # =========================
            # GET OPTION
            # =========================

            option = (
                self.option_repository
                .get_by_id(dto.option_id)
            )

            if not option:
                raise OptionNotFound()

            # =========================
            # OLD STATUS
            # =========================

            old_status = option.is_active

            # =========================
            # DOMAIN UPDATE
            # =========================

            option.is_active = dto.is_active

            # =========================
            # PERSISTENCE
            # =========================

            self.option_repository.update(
                option
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=(
                    EventType.OPTION_ACTIVATED
                    if dto.is_active
                    else EventType.OPTION_DEACTIVATED
                ),
                message=(
                    "Option activée"
                    if dto.is_active
                    else "Option désactivée"
                ),
                user_id=dto.admin_id,
                event_metadata={
                    "option_id": option.id,
                    "old_status": old_status,
                    "new_status": dto.is_active,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Statut de l'option modifié avec succès",
                extra={
                    "option_id": option.id,
                    "admin_id": dto.admin_id,
                    "old_status": old_status,
                    "new_status": option.is_active,
                },
            )
            # =========================
            # RESULT
            # =========================

            return ToggleOptionStatusResult(
                id=option.id,
                is_active=option.is_active,
                message=(
                    "Option activée"
                    if option.is_active
                    else "Option désactivée"
                ),
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors du changement de statut de l'option",
                extra={
                    "option_id": dto.option_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise