from modules.applications.domain.entities.application import Application
from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.applications.infrastructure.mappers.document_mapper import DocumentMapper
from modules.applications.infrastructure.mappers.application_financing_mapper import ApplicationFinancingMapper
from modules.applications.infrastructure.mappers.application_trade_in_mapper import ApplicationTradeInMapper
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from modules.reservations.infrastructure.mapper.reservation_mapper import ReservationMapper
from modules.applications.infrastructure.mappers.event_mapper import EventMapper
from modules.auth.infrastructure.mappers.user_mapper import UserMapper

class ApplicationMapper:


    # =====================================================
    # MODEL -> DOMAIN
    # =====================================================

    @staticmethod
    def to_domain(
        model: ApplicationModel
    ) -> Application:

        return Application(

            # =====================
            # IDENTIFIERS
            # =====================
            id=model.id,

            user_id=model.user_id,

            vehicle_id=model.vehicle_id,

            quote_id=model.quote_id,


            # =====================
            # SNAPSHOT USER
            # =====================
            first_name=model.first_name,

            last_name=model.last_name,

            email=model.email,

            phone=model.phone,

            address=model.address,

            birth_date=model.birth_date,


            # =====================
            # FINANCIAL INFO
            # =====================
            monthly_income=model.monthly_income,

            monthly_expenses=model.monthly_expenses,

            employment_status=model.employment_status,


            # =====================
            # STATUS
            # =====================
            status=model.status,

            previous_status=model.previous_status,


            created_at=model.created_at,

            submitted_at=model.submitted_at,

            # =====================
            # PRICING
            # =====================
            base_price=model.base_price,

            optional_price=model.optional_price,

            total_price=model.total_price,

            discount=model.discount,

            # =====================
            # ARCHIVE
            # =====================
            is_archived=model.is_archived,

            deleted_at=model.deleted_at,

            user= UserMapper.to_domain(
                                model.user
                            ),
            # =====================
            # VEHICLE
            # =====================
            vehicle=(
                VehicleMapper.to_domain(
                    model.vehicle
                )
                if model.vehicle
                else None
            ),


            # =====================
            # DOCUMENTS
            # =====================
            documents=[
                DocumentMapper.to_domain(doc)
                for doc in model.documents
            ]
            if model.documents
            else [],


            # =====================
            # FINANCING
            # =====================
            financing=(
                ApplicationFinancingMapper.to_domain(
                    model.financing
                )
                if model.financing
                else None
            ),


            # =====================
            # TRADE IN
            # =====================
            trade_in=(
                ApplicationTradeInMapper.to_domain(
                    model.trade_in
                )
                if model.trade_in
                else None
            ),


            # =====================
            # OPTIONS SELECTED
            # =====================
            option_ids=[
                option.option_id
                for option in model.options
            ]
            if model.options
            else [],


            # =====================
            # EVENTS
            # =====================
            events=[
                EventMapper.to_domain(event)
                for event in model.events
            ]
            if model.events
            else [],


            # =====================
            # RESERVATION
            # =====================
            reservation=(
                ReservationMapper.to_domain(
                    model.reservation
                )
                if model.reservation
                else None
            ),
        )


    # =====================================================
    # DOMAIN -> MODEL
    # =====================================================
    @staticmethod
    def to_model(
        entity: Application
    ) -> ApplicationModel:


        return ApplicationModel(

            id=entity.id,

            user_id=entity.user_id,

            vehicle_id=entity.vehicle_id,

            quote_id=entity.quote_id,


            # SNAPSHOT
            first_name=entity.first_name,

            last_name=entity.last_name,

            email=entity.email,

            phone=entity.phone,

            address=entity.address,

            birth_date=entity.birth_date,


            # FINANCIAL
            monthly_income=entity.monthly_income,

            monthly_expenses=entity.monthly_expenses,

            employment_status=entity.employment_status,


            # STATUS
            status=entity.status,

            previous_status=entity.previous_status,


            submitted_at=entity.submitted_at,


            # PRICING
            base_price=entity.base_price,

            optional_price=entity.optional_price,

            total_price=entity.total_price,

            discount=entity.discount,


            is_archived=entity.is_archived,

            deleted_at=entity.deleted_at,
        )



    # =====================================================
    # UPDATE EXISTING MODEL
    # =====================================================
    @staticmethod
    def update_model(
        model: ApplicationModel,
        entity: Application
    ):


        model.quote_id = entity.quote_id


        # SNAPSHOT
        model.first_name = entity.first_name

        model.last_name = entity.last_name

        model.email = entity.email

        model.phone = entity.phone

        model.address = entity.address

        model.birth_date = entity.birth_date


        # FINANCIAL
        model.monthly_income = entity.monthly_income

        model.monthly_expenses = entity.monthly_expenses

        model.employment_status = entity.employment_status


        # STATUS
        model.status = entity.status

        model.previous_status = entity.previous_status


        model.submitted_at = entity.submitted_at

        # PRICING
        model.base_price=entity.base_price

        model.optional_price=entity.optional_price

        model.total_price=entity.total_price

        model.discount=entity.discount,



        model.is_archived = entity.is_archived

        model.deleted_at = entity.deleted_at


        return model