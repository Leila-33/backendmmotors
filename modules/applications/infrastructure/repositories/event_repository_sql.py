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
from modules.applications.domain.enums import (
    EventCategory,
)
from modules.applications.domain.event_category import EVENT_CATEGORIES

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
        event_category: EventCategory | None = None,
        date: str | None = None,
    ):
        """
        Récupère les événements avec :
        - recherche textuelle ;
        - filtre par catégorie ;
        - filtre par date ;
        - pagination.
        """

        # =====================================================
        # QUERY DE BASE
        # =====================================================

        query = self.session.query(EventModel)

        # =====================================================
        # RECHERCHE
        # =====================================================

        if search:

            search = search.strip()

            if search:

                search_pattern = f"%{search}%"

                query = query.filter(
                    or_(
                        EventModel.message.ilike(
                            search_pattern
                        ),
                        EventModel.type.ilike(
                            search_pattern
                        ),
                    )
                )

        # =====================================================
        # FILTRE PAR CATÉGORIE
        # =====================================================

        if event_category:

            category_events = EVENT_CATEGORIES.get(
                event_category
            )
            # Catégorie inconnue :
            # aucune correspondance possible.
            if category_events is None:
                return [], 0

            query = query.filter(
                EventModel.type.in_(
                    event_type.value
                    for event_type in category_events
                )
            )

        # =====================================================
        # FILTRE PAR DATE
        # =====================================================

        if date:

            start = datetime.fromisoformat(date)

            end = start + timedelta(days=1)

            query = query.filter(
                EventModel.created_at >= start,
                EventModel.created_at < end,
            )

        # =====================================================
        # TOTAL
        # =====================================================

        total = query.count()

        # =====================================================
        # PAGINATION
        # =====================================================

        models = (
            query
            .order_by(
                desc(EventModel.created_at)
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
            .all()
        )

        # =====================================================
        # MAPPING
        # =====================================================

        events = [
            EventMapper.to_domain(model)
            for model in models
        ]

        return events, total