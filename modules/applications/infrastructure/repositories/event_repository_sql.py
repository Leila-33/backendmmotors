from modules.applications.infrastructure.db.event_model import EventModel
from modules.applications.domain.entities.event import Event
from typing import List

from modules.applications.domain.repositories.event_repository import (
    EventRepository
)

from sqlalchemy.orm import Session
from modules.applications.infrastructure.mappers.event_mapper import (
    EventMapper
)


class EventRepositorySQL(EventRepository):

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    # =========================
    # SAVE
    # =========================

    def save(
        self,
        event: Event
    ) -> Event:

        model = EventMapper.to_model(
            event
        )

        self.session.add(model)

        return event



    # =========================
    # APPLICATION EVENTS
    # =========================

    def get_by_application_id(
        self,
        application_id: str
    ) -> List[Event]:

        models = (
            self.session.query(EventModel)
            .filter(
                EventModel.application_id == application_id
            )
            .order_by(
                EventModel.created_at.desc()
            )
            .all()
        )

        return [
            EventMapper.to_domain(model)
            for model in models
        ]



    # =========================
    # TEST DRIVE EVENTS
    # =========================

    def get_by_test_drive_id(
        self,
        test_drive_id: str
    ) -> List[Event]:

        models = (
            self.session.query(EventModel)
            .filter(
                EventModel.test_drive_id == test_drive_id
            )
            .order_by(
                EventModel.created_at.desc()
            )
            .all()
        )

        return [
            EventMapper.to_domain(model)
            for model in models
        ]



    # =========================
    # DELETE APPLICATION EVENTS
    # =========================

    def delete_by_application(
        self,
        application_id: str
    ):

        (
            self.session.query(EventModel)
            .filter(
                EventModel.application_id == application_id
            )
            .delete(
                synchronize_session=False
            )
        )