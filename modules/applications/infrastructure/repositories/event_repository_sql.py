from sqlalchemy.orm import Session

from modules.applications.infrastructure.db.event_model import EventModel
from modules.applications.domain.entities.event import Event


class EventRepositorySQL:

    def __init__(self, session: Session):

        self.session = session

    # =========================
    # SAVE EVENT
    # =========================
    def save(self, event: Event):

        self.session.add(
            EventModel(
                id=event.id,
                application_id=event.application_id,
                test_drive_id=event.test_drive_id,
                type=event.type,
                message=event.message,
                user_id=event.user_id,
                metadata=event.event_metadata,
                created_at=event.created_at
            )
        )

        self.session.flush()

    # =========================
    # COMMIT
    # =========================
    def commit(self):

        self.session.commit()

    # =========================
    # GET BY APPLICATION
    # =========================
    def get_by_application_id(self, application_id: str):

        results = (
            self.session.query(EventModel)
            .filter(EventModel.application_id == application_id)
            .order_by(EventModel.created_at.asc())
            .all()
        )

        return [
            Event(
                id=e.id,
                application_id=e.application_id,
                type=e.type,
                message=e.message,
                user_id=e.user_id,
                event_metadata=e.metadata,
                created_at=e.created_at
            )
            for e in results
        ]

    # =========================
    # DELETE BY APPLICATION
    # =========================
    def delete_by_application(self, application_id: str):

        self.session.query(EventModel)\
            .filter(EventModel.application_id == application_id)\
            .delete()

        self.session.flush()


    def get_by_test_drive_id(self, test_drive_id: str):

        return (
            self.session.query(EventModel)
            .filter(EventModel.test_drive_id == test_drive_id)
            .order_by(EventModel.created_at.asc())
            .all()
        )