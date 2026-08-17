from datetime import datetime, timedelta
from typing import List

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from modules.applications.domain.entities.event import Event
from modules.applications.domain.enums import EventType
from modules.applications.domain.repositories.event_repository import (
    EventRepository,
)
from modules.applications.infrastructure.db.event_model import EventModel
from modules.applications.infrastructure.mappers.event_mapper import (
    EventMapper,
)


EVENT_CATEGORIES = {

    "application": [
        EventType.APPLICATION_CREATED,
        EventType.APPLICATION_SUBMITTED,
        EventType.APPLICATION_APPROVED,
        EventType.APPLICATION_REJECTED,
        EventType.APPLICATION_ARCHIVED,
        EventType.APPLICATION_CANCELLED,
    ],


    "document": [
        EventType.DOCUMENT_VALIDATED,
        EventType.DOCUMENT_REJECTED,
    ],


    "payment": [
        EventType.PAYMENT_INITIATED,
        EventType.DEPOSIT_PAID,
    ],


    "financing": [
        EventType.FINANCING_CONTRACT_CREATED,
        EventType.FINANCING_COMPLETED,
    ],


    "rental": [
        EventType.RENTAL_PAYMENT_PAID,
        EventType.RENTAL_COMPLETED,
        EventType.RENTAL_CANCELLED,
    ],


    "test_drive": [
        EventType.TEST_DRIVE_CREATED,
        EventType.TEST_DRIVE_CONFIRMED,
        EventType.TEST_DRIVE_REJECTED,
        EventType.TEST_DRIVE_CANCELLED,
        EventType.TEST_DRIVE_COMPLETED,
    ],


    "user": [
        EventType.ADMIN_ACTION,
    ],
}
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


    def find_all(
        self,
        page: int,
        limit: int,
        search: str | None = None,
        event_type: str | None = None,
        date: str | None = None,
    ):


        query = (
            self.session.query(EventModel)
        )


        # =====================
        # SEARCH
        # =====================

        if search:

            search = search.strip()


            query = query.filter(
                or_(
                    EventModel.message.ilike(
                        f"%{search}%"
                    ),

                    EventModel.type.ilike(
                        f"%{search}%"
                    )
                )
            )



        # =====================
        # TYPE
        # =====================

        if event_type and event_type != "all":

            category_events = EVENT_CATEGORIES.get(
                event_type
            )


            if category_events:

                query = query.filter(
                    EventModel.type.in_(
                        category_events
                    )
                )



        # =====================
        # DATE
        # =====================

        if date:

            start = datetime.fromisoformat(date)
            end = start + timedelta(days=1)

            query = query.filter(
                EventModel.created_at >= start,
                EventModel.created_at < end,
            )



        # =====================
        # TOTAL
        # =====================

        total = query.count()



        models = (
            query
            .order_by(
                desc(
                    EventModel.created_at
                )
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
            .all()
        )


        events = [
            EventMapper.to_domain(
                model
            )
            for model in models
        ]


        return events, total