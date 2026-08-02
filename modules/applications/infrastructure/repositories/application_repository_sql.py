from datetime import datetime, timezone
import logging
logger = logging.getLogger(__name__)
from sqlalchemy.orm import selectinload, Session 
from modules.applications.domain.enums import ApplicationStatus, ViewMode
from modules.reservations.domain.enums import ReservationStatus
from modules.auth.domain.exceptions import UserIdRequiredForClient
from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.applications.domain.entities.application import Application
from modules.vehicles.infrastructure.db.vehicle_model import (
    VehicleModel
)
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.infrastructure.mappers.application_mapper import ApplicationMapper
from modules.auth.domain.enums import UserRole
from sqlalchemy import and_, or_
from modules.vehicles.domain.enums import VehicleType

class ApplicationRepositorySQL(ApplicationRepository):

    def __init__(self, session: Session):
        self.session = session


    # =========================
    # CREATE
    # =========================
    def create_base(
        self,
        application: Application
    ) -> Application:

        model = ApplicationMapper.to_model(application)

        self.session.add(model)
        self.session.flush()

        return ApplicationMapper.to_domain(model)


    # =========================
    # GET BY ID
    # =========================
    def get_by_id(
        self,
        application_id: str
    ) -> Application | None:

        model = (
            self.session.query(ApplicationModel)
            .filter_by(id=application_id)
            .first()
        )

        if not model:
            return None

        return ApplicationMapper.to_domain(model)



    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        application: Application
    ) -> Application:

        model = (
            self.session.query(ApplicationModel)
            .filter_by(id=application.id)
            .first()
        )

        if not model:
            return None


        ApplicationMapper.update_model(
            model,
            application
        )

        self.session.flush()

        return ApplicationMapper.to_domain(model)



    # =========================
    # GET FULL
    # =========================
    def get_full_by_id(
        self,
        application_id: str
    ) -> Application | None:

        model = (
            self.session.query(ApplicationModel)
            .options(
                selectinload(ApplicationModel.vehicle),
                selectinload(ApplicationModel.documents),
                selectinload(ApplicationModel.financing),
                selectinload(ApplicationModel.trade_in),
                selectinload(ApplicationModel.options),
            )
            .filter(
                ApplicationModel.id == application_id
            )
            .first()
        )

        if not model:
            return None

        return ApplicationMapper.to_domain(model)







    # =========================
    # FIND ALL
    # =========================
    def find_all(
        self,
        page,
        limit,
        search,
        search_field,
        status,
        application_type,
        sort,
        view_mode,
        user_id=None,
        role=UserRole.CLIENT
    ):

        query = (
            self.session.query(ApplicationModel)
            .join(
                VehicleModel
            )
            .options(
                selectinload(ApplicationModel.vehicle)
            )
        )


        # SOFT DELETE

        query = query.filter(
            ApplicationModel.deleted_at.is_(None)
        )


        # ROLE

        if role != "admin":

            if not user_id:
                raise UserIdRequiredForClient()

            query = query.filter(
                ApplicationModel.user_id == user_id
            )



        # VIEW MODE

        if view_mode == ViewMode.ACTIVE:

            query = query.filter(
                ApplicationModel.is_archived.is_(False),
                ApplicationModel.status != ApplicationStatus.CANCELLED
            )


        elif view_mode == ViewMode.CANCELLED:

            query = query.filter(
                ApplicationModel.status == ApplicationStatus.CANCELLED
            )


        elif view_mode == ViewMode.ARCHIVED:

            query = query.filter(
                ApplicationModel.is_archived.is_(True)
            )



        # SEARCH

        if search:

            search = search.strip()


            if search_field == "vehicle":

                query = query.filter(
                    or_(
                        VehicleModel.brand.ilike(
                            f"%{search}%"
                        ),
                        VehicleModel.model.ilike(
                            f"%{search}%"
                        )
                    )
                )


            else:

                query = query.filter(
                    or_(
                        ApplicationModel.first_name.ilike(
                            f"%{search}%"
                        ),
                        ApplicationModel.last_name.ilike(
                            f"%{search}%"
                        )
                    )
                )



        # STATUS

        if status and status != "all":

            query = query.filter(
                ApplicationModel.status == status
            )



        # TYPE VEHICULE

        if application_type and application_type != "all":

            query = query.filter(
                VehicleModel.type == application_type
            )



        # SORT

        if sort == "created_at_asc":

            query = query.order_by(
                ApplicationModel.created_at.asc()
            )

        else:

            query = query.order_by(
                ApplicationModel.created_at.desc()
            )



        # =========================
        # TOTAL
        # =========================
        total = query.count()


        # =========================
        # PAGINATION
        # =========================
        models = (
            query
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
            .all()
        )


        # =========================
        # ORM -> DOMAIN
        # =========================
        items = [
            ApplicationMapper.to_domain(app)
            for app in models
        ]


        return items, total




    # =========================
    # UPDATE STATUS
    # =========================
    def update_status(
        self,
        application_id,
        status,
        reason=None
    ):

        application = self.get_by_id(
            application_id
        )


        if not application:
            return None


        application.status = status

        self.session.flush()


        return ApplicationMapper.to_domain(application)


    # =========================
    # ACTIVE APPLICATION
    # =========================
    def find_active_by_user_and_vehicle(
        self,
        user_id: str,
        vehicle_id: str,
    ) -> Application | None:

        model = (
            self.session.query(ApplicationModel)
            .join(ApplicationModel.vehicle)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.vehicle_id == vehicle_id,
                ApplicationModel.deleted_at.is_(None),
                or_(
                    # =========================
                    # LOCATION
                    # =========================
                    and_(
                        VehicleModel.type == VehicleType.RENT,
                        ApplicationModel.status.in_([
                            ApplicationStatus.DRAFT,
                            ApplicationStatus.PROCESSING,
                            ApplicationStatus.SUBMITTED,
                        ]),
                    ),

                    # =========================
                    # VENTE
                    # =========================
                    and_(
                        VehicleModel.type == VehicleType.SALE,
                        ApplicationModel.status.in_([
                            ApplicationStatus.DRAFT,
                            ApplicationStatus.PROCESSING,
                            ApplicationStatus.SUBMITTED,
                            ApplicationStatus.APPROVED,
                            ApplicationStatus.PAID,
                            ApplicationStatus.COMPLETED,
                        ]),
                    ),
                ),
            )
            .first()
        )

        if not model:
            return None

        return ApplicationMapper.to_domain(model)


    def find_draft_by_user_and_vehicle(
        self,
        user_id: str,
        vehicle_id: str,
    ) -> Application | None:

        model = (
            self.session.query(ApplicationModel)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.vehicle_id == vehicle_id,
                ApplicationModel.status == ApplicationStatus.DRAFT,
                ApplicationModel.deleted_at.is_(None),
            )
            .first()
        )

        if model is None:
            return None

        return ApplicationMapper.to_domain(model)
    
    # =========================
    # QUOTE
    # =========================
    def find_by_quote_id(
        self,
        quote_id: str
    ) -> Application | None:

        model = (
            self.session.query(ApplicationModel)
            .filter(
                ApplicationModel.quote_id == quote_id
            )
            .first()
        )

        if not model:
            return None

        return ApplicationMapper.to_domain(model)

    def delete(self, application_id: str):
	    self.session.query(ApplicationModel)\
	            .filter(ApplicationModel.id == application_id)\
	            .delete()