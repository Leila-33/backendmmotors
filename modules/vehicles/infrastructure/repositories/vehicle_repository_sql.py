from sqlalchemy import asc, desc, or_, exists
from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload,
)

from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)
from modules.vehicles.domain.exceptions import VehicleNotFound

from modules.vehicles.infrastructure.db.vehicle_model import (
    VehicleModel,
)

from modules.vehicles.infrastructure.db.vehicle_option_model import (
    VehicleOptionModel,
)

from modules.warranties.infrastructure.db.vehicle_warranty_model import (
    VehicleWarrantyModel,
)

from modules.vehicles.infrastructure.mappers.vehicle_mapper import (
    VehicleMapper,
)

from modules.vehicles.application.dtos.vehicle_search_filters_dto import (
    VehicleSearchFiltersDTO,
)

from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.reservations.infrastructure.db.reservation_model import ReservationModel
from modules.test_drives.infrastructure.db.test_drive_model import TestDriveModel
from modules.reconditionings.infrastructure.db.reconditioning_model import ReconditioningModel
from modules.inspections.infrastructure.db.inspection_model import InspectionModel
from modules.leads.infrastructure.db.lead_model import LeadModel
from modules.applications.infrastructure.db.event_model import EventModel
from modules.vehicles.domain.enums import VehicleStatus

class VehicleRepositorySQL(VehicleRepository):

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        filters: VehicleSearchFiltersDTO,
    ):

        query = (
            self.db
            .query(VehicleModel)
            .options(
                joinedload(
                    VehicleModel.options
                ).joinedload(
                    VehicleOptionModel.option
                )
            )
            .filter(
                VehicleModel.status != VehicleStatus.ARCHIVED
            )
            .distinct()
        )

        # =================================================
        # SEARCH
        # =================================================

        if filters.search:

            search = f"%{filters.search}%"

            query = query.filter(
                or_(
                    VehicleModel.brand.ilike(search),
                    VehicleModel.model.ilike(search),
                )
            )

        # =================================================
        # LICENSE PLATE
        # =================================================

        if filters.license_plate:

            plate = (
                filters.license_plate
                .strip()
                .upper()
                .replace(" ", "")
            )

            query = query.filter(
                VehicleModel.license_plate.ilike(
                    f"%{plate}%"
                )
            )

        # =================================================
        # TYPE
        # =================================================

        if filters.type:

            query = query.filter(
                VehicleModel.type == filters.type
            )

        # =================================================
        # BRAND
        # =================================================

        if filters.brand:

            query = query.filter(
                VehicleModel.brand == filters.brand
            )

        # =================================================
        # MODEL
        # =================================================

        if filters.model:

            query = query.filter(
                VehicleModel.model == filters.model
            )

        # =================================================
        # PRICE
        # =================================================

        if filters.price_min is not None:

            query = query.filter(
                VehicleModel.price >= filters.price_min
            )

        if filters.price_max is not None:

            query = query.filter(
                VehicleModel.price <= filters.price_max
            )

        # =================================================
        # YEAR
        # =================================================

        if filters.year_min is not None:

            query = query.filter(
                VehicleModel.year >= filters.year_min
            )

        # =================================================
        # MILEAGE
        # =================================================

        if filters.mileage_max is not None:

            query = query.filter(
                VehicleModel.mileage <= filters.mileage_max
            )

        # =================================================
        # AVAILABILITY
        # =================================================

        if filters.is_available is not None:

            query = query.filter(
                VehicleModel.is_available
                == filters.is_available
            )

        # =================================================
        # SORT
        # =================================================

        sort_column = {
            "price": VehicleModel.price,
            "year": VehicleModel.year,
            "mileage": VehicleModel.mileage,
        }.get(
            filters.sort_by,
            VehicleModel.year,
        )

        if filters.order == "asc":

            query = query.order_by(
                asc(sort_column)
            )

        else:

            query = query.order_by(
                desc(sort_column)
            )

        # =================================================
        # TOTAL
        # =================================================

        total = query.count()

        # =================================================
        # PAGINATION
        # =================================================

        items = (
            query
            .offset(
                (filters.page - 1)
                * filters.size
            )
            .limit(filters.size)
            .all()
        )

        # =================================================
        # DOMAIN
        # =================================================

        vehicles = [
            VehicleMapper.to_domain(model)
            for model in items
        ]

        return vehicles, total

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        vehicle: Vehicle,
    ) -> Vehicle:

        model = VehicleMapper.to_model(
            vehicle
        )

        self.db.add(model)

        self.db.flush()

        return VehicleMapper.to_domain(
            model
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        vehicle_id: str,
    ) -> Vehicle | None:

        model = (
            self.db
            .query(VehicleModel)
            .options(

                selectinload(
                    VehicleModel.options
                ).selectinload(
                    VehicleOptionModel.option
                ),

                selectinload(
                    VehicleModel.warranty
                ).selectinload(
                    VehicleWarrantyModel.warranty_plan
                ),
            )
            .filter(
                VehicleModel.id == vehicle_id
            )
            .first()
        )

        if not model:
            return None

        return VehicleMapper.to_domain(
            model
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        vehicle: Vehicle,
    ) -> Vehicle:

        model = (
            self.db
            .query(VehicleModel)
            .filter(
                VehicleModel.id == vehicle.id
            )
            .first()
        )

        if not model:
            raise VehicleNotFound()

        VehicleMapper.update_model(
            model,
            vehicle,
        )

        self.db.flush()

        return VehicleMapper.to_domain(
            model
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        vehicle_id: str,
    ) -> None:

        model = (
            self.db
            .query(VehicleModel)
            .filter(
                VehicleModel.id == vehicle_id
            )
            .first()
        )

        if model:

            self.db.delete(
                model
            )

            self.db.flush()

    # =====================================================
    # LICENSE PLATE
    # =====================================================

    def get_by_license_plate(
        self,
        plate: str,
    ) -> Vehicle | None:

        model = (
            self.db
            .query(VehicleModel)
            .filter(
                VehicleModel.license_plate
                == plate
            )
            .first()
        )

        if not model:
            return None

        return VehicleMapper.to_domain(
            model
        )
    


    def has_business_history(
        self,
        vehicle_id: str,
    ) -> bool:

        query = (
            self.db.query(VehicleModel.id)
            .filter(
                VehicleModel.id == vehicle_id,
                or_(
                    exists().where(
                        ApplicationModel.vehicle_id
                        == VehicleModel.id
                    ),

                    exists().where(
                        ReservationModel.vehicle_id
                        == VehicleModel.id
                    ),

                    exists().where(
                        TestDriveModel.vehicle_id
                        == VehicleModel.id
                    ),

                    exists().where(
                        ReconditioningModel.vehicle_id
                        == VehicleModel.id
                    ),

                    exists().where(
                        InspectionModel.vehicle_id
                        == VehicleModel.id
                    ),

                    exists().where(
                        LeadModel.vehicle_id
                        == VehicleModel.id
                    ),

                    exists().where(
                        EventModel.vehicle_id
                        == VehicleModel.id
                    ),
                ),
            )
            .first()
        )

        return query is not None