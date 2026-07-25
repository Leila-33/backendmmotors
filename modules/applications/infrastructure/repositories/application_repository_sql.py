from uuid import uuid4
from datetime import datetime, timezone

import logging

from core.config.settings import settings
from modules.storage.infrastrucure.s3_client import get_s3_client

logger = logging.getLogger(__name__)

from sqlalchemy import or_

from sqlalchemy.orm import selectinload, Session 
from modules.applications.domain.enums import ApplicationStatus, ViewMode
from modules.reservations.domain.enums import ReservationStatus

from modules.auth.domain.exceptions import UserIdRequiredForClient


from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.applications.infrastructure.db.application_option_model import ApplicationOptionModel
from modules.applications.infrastructure.db.document_model import DocumentModel
from modules.applications.infrastructure.db.application_financing_model import ApplicationFinancingModel
from modules.applications.infrastructure.db.application_trade_in_model import ApplicationTradeInModel
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel





class ApplicationRepositorySQL:

    def __init__(self, session: Session):
        self.session = session

    # =========================
    # BASE
    # =========================
    def create_base(self, **kwargs) -> ApplicationModel:
        app = ApplicationModel(**kwargs)
        self.session.add(app)
        return app

    def get_by_id(self, application_id: str):
        return (
            self.session.query(ApplicationModel)
            .filter_by(id=application_id)
            .first()
        )

    def update(self, application: ApplicationModel):
        self.session.add(application)
        return application

    # =========================
    # OPTIONS
    # =========================


    def replace_options(
        self,
        application_id: str,
        option_ids: list[str]
    ):

        self.session.query(ApplicationOptionModel)\
            .filter_by(application_id=application_id)\
            .delete()

        for option_id in option_ids:

            self.session.add(
                ApplicationOptionModel(
                    id=str(uuid4()),
                    application_id=application_id,
                    option_id=option_id
                )
            )

        self.session.flush()

    # =========================
    # FINANCING
    # =========================
    def save_financing(self, application_id: str, data):

        existing = (
            self.session.query(ApplicationFinancingModel)
            .filter_by(application_id=application_id)
            .first()
        )

        if existing:
            existing.down_payment = data.down_payment
            existing.duration_months = data.duration_months
            existing.financed_amount = data.financed_amount
            existing.monthly_payment = data.monthly_payment

        else:
            self.session.add(
                ApplicationFinancingModel(
                    application_id=application_id,
                    down_payment=data.down_payment,
                    duration_months=data.duration_months,
                    financed_amount=data.financed_amount,
                    monthly_payment=data.monthly_payment
                )
            )

    # =========================
    # TRADE-IN
    # =========================
    def save_trade_in(self, application_id: str, trade_in_value: float, data):

        existing = (
            self.session.query(ApplicationTradeInModel)
            .filter_by(application_id=application_id)
            .first()
        )

        if existing:
            existing.brand = data.brand
            existing.model = data.model
            existing.year = data.year
            existing.mileage = data.mileage
            existing.condition = data.condition
            existing.estimated_value = trade_in_value

        else:
            self.session.add(
                ApplicationTradeInModel(
                    application_id=application_id,
                    brand=data.brand,
                    model=data.model,
                    year=data.year,
                    mileage=data.mileage,
                    condition=data.condition,
                    estimated_value=trade_in_value
                )
            )
    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


    def get_full_by_id(
    self,
    application_id: str
):

        return (
            self.session.query(ApplicationModel)
            .filter_by(id=application_id)
            .first()
        )
    




    def sync_documents(
        self,
        application_id: str,
        documents: list
    ):

        s3 = get_s3_client()

        # =========================
        # EXISTING DOCS
        # =========================
        existing_docs = (
            self.session.query(DocumentModel)
            .filter_by(application_id=application_id)
            .all()
        )

        # =========================
        # MAPS
        # =========================
        existing_by_type = {
            doc.type: doc
            for doc in existing_docs
        }

        incoming_types = {
            doc.type
            for doc in documents
        }

        # =========================
        # UPSERT
        # =========================
        for incoming in documents:

            existing = existing_by_type.get(
                incoming.type
            )

            # =========================
            # UPDATE EXISTING
            # =========================
            if existing:

                # fichier changé
                if existing.s3_key != incoming.s3_key:

                    # delete old S3 file
                    try:

                        s3.delete_object(
                            Bucket=settings.S3_BUCKET,
                            Key=existing.s3_key
                        )

                    except Exception:
                        logger.exception(
                            f"Failed deleting S3 file: {existing.s3_key}"
                        )

                    existing.s3_key = incoming.s3_key

                    # reset validation
                    existing.status = "pending"
                    existing.comment = None

            # =========================
            # INSERT NEW
            # =========================
            else:

                self.session.add(
                    DocumentModel(
                        id=str(uuid4()),
                        application_id=application_id,
                        type=incoming.type,
                        s3_key=incoming.s3_key,
                        status="pending"
                    )
                )

        # =========================
        # DELETE REMOVED DOCS
        # =========================
        for existing in existing_docs:

            if existing.type in incoming_types:
                continue

            # delete S3
            try:

                s3.delete_object(
                    Bucket=settings.S3_BUCKET,
                    Key=existing.s3_key
                )

            except Exception:
                logger.exception(
                    f"Failed deleting removed S3 file: {existing.s3_key}"
                )

            # delete DB
            self.session.delete(existing)

        self.session.flush()





 


    def find_all(
        self,
        page,
        limit,
        search,
        search_field,
        status,
        application_type,
        sort,
        view_mode="active",
        user_id=None,
        role="client"
    ):

        query = (
            self.session.query(ApplicationModel)
            .options(selectinload(ApplicationModel.vehicle))
        )

        # =========================
        # SOFT DELETE
        # =========================
        query = query.filter(
            ApplicationModel.deleted_at.is_(None)
        )

        # =========================
        # ROLE FILTER
        # =========================
        if role != "admin":

            if not user_id:
                raise UserIdRequiredForClient()

            query = query.filter(
                ApplicationModel.user_id == user_id
            )

        # =========================
        # ARCHIVE
        # =========================
        # =========================
        # VIEW MODE FILTER
        # =========================
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
        # =========================
        # SEARCH
        # =========================
        if search:

            search = search.strip()

            if search_field == "vehicle":
                query = query.filter(
                    or_(
                        VehicleModel.brand.ilike(f"%{search}%"),
                        VehicleModel.model.ilike(f"%{search}%")
                    )
                )
            else:
                query = query.filter(
                    or_(
                        ApplicationModel.first_name.ilike(f"%{search}%"),
                        ApplicationModel.last_name.ilike(f"%{search}%")
                    )
                )

        # =========================
        # STATUS
        # =========================
        if status and status != "all":
            query = query.filter(ApplicationModel.status == status)

        # =========================
        # TYPE
        # =========================
        if application_type and application_type != "all":
            query = query.filter(VehicleModel.type == application_type)

        # =========================
        # SORT
        # =========================
        query = query.order_by(
            ApplicationModel.created_at.asc()
            if sort == "created_at_asc"
            else ApplicationModel.created_at.desc()
        )

        # =========================
        # TOTAL
        # =========================
        total = query.order_by(None).count()

        # =========================
        # PAGINATION
        # =========================
        items = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return items, total

    def update_status(self, application_id: str, status: str, reason: str = None):

        application = self.session.query(ApplicationModel).filter_by(
            id=application_id
        ).first()

        application.status = status
        application.rejection_reason = reason

        self.session.flush()

        return application
    
    def delete(self, application_id: str):

        self.session.query(ApplicationModel)\
            .filter(ApplicationModel.id == application_id)\
            .delete()

        self.session.commit()

    def archive(self, application_id: str):

            self.session.query(ApplicationModel).filter(
                ApplicationModel.id == application_id
            ).update({
                ApplicationModel.is_archived: True
            })

            self.session.commit()

    # =========================
    # UNARCHIVE
    # =========================
    def unarchive(self, application_id: str):

        self.session.query(ApplicationModel).filter(
            ApplicationModel.id == application_id
        ).update({
            ApplicationModel.is_archived: False
        })

        self.session.commit()

    # =========================
    # SOFT DELETE
    # =========================
    def soft_delete(self, application_id: str):

        application = (
            self.session.query(ApplicationModel)
            .filter(ApplicationModel.id == application_id)
            .first()
        )

        if not application:
            return None

        # Soft delete du dossier
        application.deleted_at = datetime.now(timezone.utc)

        # Libération de la réservation
        if application.reservation:
            application.reservation.status = ReservationStatus.CANCELLED

        self.session.commit()

        return application

    def find_active_by_user_and_vehicle(
    self,
    user_id: str,
    vehicle_id: str
):
        return (
            self.session.query(ApplicationModel)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.vehicle_id == vehicle_id,
                ApplicationModel.status.in_([
                    ApplicationStatus.DRAFT,
                    ApplicationStatus.PROCESSING,
                    ApplicationStatus.SUBMITTED,
                ]),
                ApplicationModel.deleted_at.is_(None)
            )
            .first()
        )
    
    def find_by_quote_id(
    self,
    quote_id: str
) -> ApplicationModel | None:

        model = (
            self.session
            .query(ApplicationModel)
            .filter(
                ApplicationModel.quote_id == quote_id
            )
            .first()
        )


        if not model:
            return None
        
        return model