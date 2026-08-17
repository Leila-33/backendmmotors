import logging
from uuid import uuid4

from modules.options.domain.entities.option import Option
from modules.options.domain.enums import OptionType
from modules.options.domain.exceptions import OptionAlreadyExists
from modules.applications.domain.enums import EventType

from modules.options.application.dtos.admin.create_option_dto import (
    CreateOptionDTO,
)
from modules.options.application.results.admin.create_option_result import (
    CreateOptionResult,
)

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
        dto: CreateOptionDTO,
    ):

        try:

            # =========================
            # NORMALIZE
            # =========================

            name = dto.name.strip()

            # =========================
            # BUSINESS RULE
            # =========================

            exists = (
                self.option_repository
                .exists_by_name(name)
            )

            if exists:
                raise OptionAlreadyExists(name)

            # =========================
            # CREATE DOMAIN ENTITY
            # =========================

            option = Option(
                id=str(uuid4()),
                name=name,
                type=OptionType.CUSTOM,
                price=dto.price,
                billing_type=dto.billing_type,
                is_active=True,
            )

            # =========================
            # PERSIST
            # =========================

            option = (
                self.option_repository
                .save(option)
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.OPTION_CREATED,
                message="Option créée",
                user_id=dto.admin_id,
                event_metadata={
                    "option_id": option.id,
                    "name": option.name,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Option créée avec succès",
                extra={
                    "option_id": option.id,
                    "admin_id": dto.admin_id,
                    "option_name": option.name,
                },
            )

            # =========================
            # RESULT
            # =========================

            return CreateOptionResult(
                option_id=option.id,
                message="Option créée avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de la création d'une option",
                extra={
                    "option_name": (
                        dto.name
                        if dto
                        else None
                    ),
                    "admin_id": (
                        dto.admin_id
                        if dto
                        else None
                    ),
                },
            )

            raise