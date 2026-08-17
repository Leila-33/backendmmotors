import logging

from modules.options.domain.exceptions import (
    OptionNotFound,
    OptionAlreadyExists,
    SystemOptionCannotBeModified,
)
from modules.options.domain.enums import OptionType
from modules.applications.domain.enums import EventType

from modules.options.application.dtos.admin.update_option_dto import (
    UpdateOptionDTO,
)
from modules.options.application.results.admin.update_option_result import (
    UpdateOptionResult,
)

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
        dto: UpdateOptionDTO,
    ) -> UpdateOptionResult:

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
            # ONLY CUSTOM OPTIONS
            # =========================

            if option.type != OptionType.CUSTOM:
                raise SystemOptionCannotBeModified()

            # =========================
            # NORMALIZE NAME
            # =========================

            name = dto.name.strip()

            # =========================
            # DUPLICATE CHECK
            # =========================

            exists = (
                self.option_repository
                .exists_by_name_except_id(
                    name,
                    dto.option_id,
                )
            )

            if exists:
                raise OptionAlreadyExists(name)

            # =========================
            # KEEP OLD VALUES
            # =========================

            old_name = option.name
            old_price = option.price
            old_billing_type = option.billing_type

            # =========================
            # UPDATE DOMAIN ENTITY
            # =========================

            option.name = name
            option.price = dto.price
            option.billing_type = dto.billing_type

            # =========================
            # PERSISTENCE
            # =========================

            self.option_repository.update(option)

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.OPTION_UPDATED,
                message="Option modifiée",
                user_id=dto.admin_id,
                event_metadata={
                    "option_id": option.id,
                    "old_name": old_name,
                    "new_name": option.name,
                    "old_price": old_price,
                    "new_price": option.price,
                    "old_billing_type": (
                        old_billing_type.value
                        if old_billing_type
                        else None
                    ),
                    "new_billing_type": (
                        option.billing_type.value
                        if option.billing_type
                        else None
                    ),
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
                "Option modifiée avec succès",
                extra={
                    "option_id": option.id,
                    "admin_id": dto.admin_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return UpdateOptionResult(
                id=option.id,
                message="Option modifiée avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de la modification de l'option",
                extra={
                    "option_id": dto.option_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise