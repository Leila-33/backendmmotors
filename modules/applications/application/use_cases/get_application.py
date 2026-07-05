# =========================
# IMPORTS
# =========================
from modules.auth.infrastructure.db.user_model import UserModel
from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository
)

from modules.core.exceptions import (
    ApplicationNotFound
)
from modules.payments.domain.repositories.payment_repository import PaymentRepository

from modules.storage.api.upload_routes import get_s3_client
from core.config import settings
from modules.applications.api.schemas import SelectedDatesDTO

class GetApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        payment_repository: PaymentRepository
    ):
        self.application_repository = application_repository
        self.payment_repository = payment_repository

    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        application_id: str,
        current_user: UserModel
    ):

        application = (
            self.application_repository
            .get_full_by_id(application_id)
        )

        # =========================
        # NOT FOUND
        # =========================
        if not application:
            raise ApplicationNotFound()

        # =========================
        # SOFT DELETED
        # =========================
        if application.deleted_at is not None:

            return {
                "deleted": True
            }

        # =========================
        # SECURITY
        # =========================
        if (
            current_user.role != "admin"
            and application.user_id != current_user.id
        ):
            raise ApplicationNotFound()

        # =========================
        # OPTIONS
        # =========================
        included_options = []
        optional_options = []

        for vehicle_option in application.vehicle.options:

            option_data = {
                "id": vehicle_option.option.id,
                "name": vehicle_option.option.name,
                "price": vehicle_option.option.price,
                "type": vehicle_option.type
            }

            if vehicle_option.type == "included":
                included_options.append(option_data)
            else:
                optional_options.append(option_data)

        # =========================
        # SELECTED OPTIONS
        # =========================
        options_selected = [
            item.option_id
            for item in application.options
        ]



       # =========================
        # DOCUMENTS
        # =========================
        documents = []

        s3 = get_s3_client()

        for doc in application.documents:

            download_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.S3_BUCKET,
                    "Key": doc.s3_key
                },
                ExpiresIn=3600
            )

            documents.append({
                "id": doc.id,
                "type": doc.type,
                "status": doc.status,
                "s3_key": doc.s3_key,
                "comment": doc.comment,
                "download_url": download_url
            })
        # =========================
        # EVENTS
        # =========================
        events = []

        for event in application.events:

            events.append({
                "id": event.id,
                "type": event.type,
                "message": event.message,
                "created_at": event.created_at
            })
        latest_payment = self.payment_repository.get_latest_payment(
            application_id=application.id
        )
        # =========================
        # RESPONSE
        # =========================
        return {

            # =========================
            # CORE
            # =========================
            "id": application.id,
            "status": application.status,

            "created_at": application.created_at,

            # =========================
            # USER INFOS
            # =========================
            "first_name": application.first_name,
            "last_name": application.last_name,

            "email": application.email,
            "phone": application.phone,

            "address": application.address,
            "birth_date": application.birth_date,

            # =========================
            # FINANCIAL
            # =========================
            "monthly_income": application.monthly_income,
            "monthly_expenses": application.monthly_expenses,
            "employment_status": application.employment_status,
            
            "selected_dates": (
                SelectedDatesDTO(
                    start=application.reservation.start_date,
                    end=application.reservation.end_date
                )
                if application.reservation
                else None
            ),
            # =========================
            # VEHICLE
            # =========================
            "vehicle": {
                "id": application.vehicle.id,
                "brand": application.vehicle.brand,
                "model": application.vehicle.model,
                "year": application.vehicle.year,
                "price": application.vehicle.price,
                "type": application.vehicle.type,
                "mileage": application.vehicle.mileage,
                "engine_type": application.vehicle.engine_type,

                "included_options": included_options,
                "optional_options": optional_options
            },

            # =========================
            # OPTIONS
            # =========================
            "options_selected": options_selected,

            # =========================
            # FINANCING
            # =========================
            "financing": (
                {
                    "down_payment":
                        application.financing.down_payment,

                    "duration_months":
                        application.financing.duration_months,

                    "financed_amount":
                        application.financing.financed_amount,

                    "monthly_payment":
                        application.financing.monthly_payment
                }
                if application.financing
                else None
            ),

            # =========================
            # TRADE-IN
            # =========================
            "trade_in": (
                {
                    "brand":
                        application.trade_in.brand,

                    "model":
                        application.trade_in.model,

                    "year":
                        application.trade_in.year,

                    "mileage":
                        application.trade_in.mileage,

                    "condition":
                        application.trade_in.condition,

                    "estimated_value":
                        application.trade_in.estimated_value
                }
                if application.trade_in
                else None
            ),

            # =========================
            # DOCUMENTS
            # =========================
            "documents": documents,

            # =========================
            # EVENTS
            # =========================
            "events": events,


            "payment_status" : (
        latest_payment.status
        if latest_payment
        else None
    )
        }