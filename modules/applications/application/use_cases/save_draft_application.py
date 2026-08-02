from datetime import datetime, timezone
from uuid import uuid4

from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.api.schemas import SaveDraftApplicationDTO
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.repositories.event_repository import EventRepository

from modules.applications.domain.entities.event import Event
from modules.auth.domain.entities.user import User
from core.database.unit_of_work import UnitOfWork


from datetime import datetime, timezone
from uuid import uuid4


class SaveDraftApplicationUseCase:

    def __init__(
        self,
        application_form_service,
        event_repository: EventRepository,
        uow: UnitOfWork,
    ):
        self.application_form_service = application_form_service
        self.event_repository = event_repository
        self.uow = uow


    def execute(
        self,
        dto,
        current_user: User
    ):

        try:

            result = self.application_form_service.save(
                dto=dto,
                current_user=current_user,
            )


            if result.is_new:

                self.event_repository.save(
                    Event(
                        id=str(uuid4()),
                        application_id=result.application.id,
                        user_id=current_user.id,
                        type=EventType.APPLICATION_CREATED,
                        message="Dossier créé.",
                        created_at=datetime.now(timezone.utc),
                    )
                )


            self.uow.commit()


            return result.application

        except Exception:
            self.uow.rollback()
            raise