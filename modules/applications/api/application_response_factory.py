from modules.applications.domain.entities.application import Application
from modules.payments.domain.entities.payment import Payment
from modules.storage.infrastrucure.s3_service import S3Service
from modules.options.api.schemas import OptionResponse
from modules.applications.api.schemas import (
    ApplicationDetailResponse,
    VehicleApplicationResponse,
    FinancingResponse,
    TradeInResponse,
    DocumentResponse,
    EventResponse,
    SelectedDatesResponse,
)
from modules.vehicles.domain.enums import VehicleOptionType
from modules.auth.domain.enums import UserRole
from modules.applications.domain.policies.validate_application_policy import ValidateApplicationPolicy
from modules.applications.domain.policies.reject_application_policy import RejectApplicationPolicy

class ApplicationResponseFactory:

    def __init__(
        self,
        s3_service: S3Service,
    ):
        self.s3_service = s3_service


    def build(
        self,
        application: Application,
        role: UserRole,
        payment_status: str | None = None,
    ) -> ApplicationDetailResponse:


        # =========================
        # VEHICLE OPTIONS
        # =========================

        included_options = []
        optional_options = []

        for vehicle_option in application.vehicle.options:

            option = OptionResponse(
                id=vehicle_option.option.id,
                name=vehicle_option.option.name,
                price=vehicle_option.option.price,
                type=vehicle_option.option.type,
                is_active=vehicle_option.option.is_active,
                billing_type=vehicle_option.option.billing_type

            )

            if vehicle_option.type == VehicleOptionType.INCLUDED:
                included_options.append(option)

            else:
                optional_options.append(option)


        # =========================
        # SELECTED OPTIONS
        # =========================

        options_selected = application.option_ids


        # =========================
        # DOCUMENTS
        # =========================

        documents = []

        for document in application.documents:

            documents.append(
                DocumentResponse(
                    id=document.id,
                    application_id=document.application_id,
                    type=document.type,
                    status=document.status,
                    s3_key=document.s3_key,
                    comment=document.comment,
                    download_url=
                        self.s3_service.generate_download_url(
                            document.s3_key
                        ),
                )
            )


        # =========================
        # EVENTS
        # =========================

        events = [
            EventResponse(
                id=event.id,
                type=event.type,
                message=event.message,
                created_at=event.created_at,
            )
            for event in application.events
        ]

        can_validate = False
        can_reject = False

        if role == UserRole.ADMIN:
            can_validate = ValidateApplicationPolicy.can_validate(application)
            can_reject = RejectApplicationPolicy.can_reject(application)

        # =========================
        # RESPONSE
        # =========================

        return ApplicationDetailResponse(

            id=application.id,

            status=application.status,

            created_at=application.created_at,
            deleted_at=application.deleted_at,

            # USER SNAPSHOT
            first_name=application.first_name,
            last_name=application.last_name,
            email=application.email,
            phone=application.phone,
            address=application.address,
            birth_date=application.birth_date,


            # FINANCIAL INFO
            monthly_income=application.monthly_income,
            monthly_expenses=application.monthly_expenses,
            employment_status=application.employment_status,

            # PRICING
            discount=application.discount,

            # RESERVATION
            selected_dates=(
                SelectedDatesResponse(
                    start=application.reservation.start_date,
                    end=application.reservation.end_date,
                )
                if application.reservation
                else None
            ),


            # VEHICLE
            vehicle=VehicleApplicationResponse(
                id=application.vehicle.id,
                brand=application.vehicle.brand,
                model=application.vehicle.model,
                year=application.vehicle.year,
                price=application.vehicle.price,
                type=application.vehicle.type,
                mileage=application.vehicle.mileage,
                engine_type=application.vehicle.engine_type,

                included_options=included_options,
                optional_options=optional_options,
            ),


            # OPTIONS
            options_selected=options_selected,


            # FINANCING
            financing=(
                FinancingResponse(
                    down_payment=application.financing.down_payment,
                    duration_months=
                        application.financing.duration_months,
                    financed_amount=
                        application.financing.financed_amount,
                    monthly_payment=
                        application.financing.monthly_payment,
                )
                if application.financing
                else None
            ),


            # TRADE IN
            trade_in=(
                TradeInResponse(
                    brand=application.trade_in.brand,
                    model=application.trade_in.model,
                    year=application.trade_in.year,
                    mileage=application.trade_in.mileage,
                    condition=application.trade_in.condition,
                    estimated_value=
                        application.trade_in.estimated_value,
                )
                if application.trade_in
                else None
            ),


            # DOCUMENTS
            documents=documents,


            # EVENTS
            events=events,
            payment_status=(
                payment_status
                if payment_status
                else None
            ),
            # ACTIONS
            can_reject=can_reject,
            can_validate=can_validate

        )