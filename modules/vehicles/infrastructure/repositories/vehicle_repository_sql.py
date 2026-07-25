from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel
from sqlalchemy.orm import joinedload
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel
from modules.vehicles.api.schemas import (
    VehicleSearchFilters,
)
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import selectinload


class VehicleRepositorySQL(VehicleRepository):

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    # =========================
    # SEARCH
    # =========================

    def search(
        self,
        filters: VehicleSearchFilters
    ):

        query = (
            self.db.query(VehicleModel)
            .options(
                joinedload(
                    VehicleModel.options
                )
                .joinedload(
                    VehicleOptionModel.option
                )
            )
            .distinct()
        )


        if filters.search:

            search = f"%{filters.search}%"

            query = query.filter(
                or_(
                    VehicleModel.brand.ilike(search),
                    VehicleModel.model.ilike(search)
                )
            )


        if filters.license_plate:

            plate = (
                filters.license_plate
                .upper()
                .replace(" ", "")
            )

            query = query.filter(
                VehicleModel.license_plate.ilike(
                    f"%{plate}%"
                )
            )


        if filters.type:
            query = query.filter(
                VehicleModel.type == filters.type
            )


        if filters.brand:
            query = query.filter(
                VehicleModel.brand == filters.brand
            )


        if filters.model:
            query = query.filter(
                VehicleModel.model == filters.model
            )


        if filters.price_min is not None:
            query = query.filter(
                VehicleModel.price >= filters.price_min
            )


        if filters.price_max is not None:
            query = query.filter(
                VehicleModel.price <= filters.price_max
            )


        if filters.year_min is not None:
            query = query.filter(
                VehicleModel.year >= filters.year_min
            )


        if filters.mileage_max is not None:
            query = query.filter(
                VehicleModel.mileage <= filters.mileage_max
            )


        if filters.is_available is not None:
            query = query.filter(
                VehicleModel.is_available ==
                filters.is_available
            )


        sort_column = {
            "price": VehicleModel.price,
            "year": VehicleModel.year,
            "mileage": VehicleModel.mileage,
        }.get(
            filters.sort_by
        )


        query = query.order_by(
            asc(sort_column)
            if filters.order == "asc"
            else desc(sort_column)
        )


        total = query.count()


        items = (
            query
            .offset(
                (filters.page - 1)
                * filters.size
            )
            .limit(filters.size)
            .all()
        )


        return (
    [
        VehicleMapper.to_domain(model)
        for model in items
    ],
    total
)


    # =========================
    # SAVE
    # =========================

    def save(
        self,
        vehicle: Vehicle
    ):

        model = VehicleMapper.to_model(vehicle)

        self.db.add(model)

        self.db.flush()

        return VehicleMapper.to_domain(model)

    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        vehicle_id: str
    ) -> Vehicle | None:


        model = (
            self.db.query(VehicleModel)

            .options(

                selectinload(
                    VehicleModel.options
                )
                .selectinload(
                    VehicleOptionModel.option
                ),


                selectinload(
                    VehicleModel.warranty
                )
                .selectinload(
                    VehicleWarrantyModel.warranty_plan
                )

            )

            .filter(
                VehicleModel.id == vehicle_id
            )

            .first()
        )


        if not model:
            return None


        return VehicleMapper.to_domain(model)




    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        vehicle: Vehicle
    ) -> Vehicle:


        model = (
            self.db.query(
                VehicleModel
            )
            .filter(
                VehicleModel.id == vehicle.id
            )
            .first()
        )


        if not model:
            raise VehicleNotFound()


        VehicleMapper.update_model(
            model,
            vehicle
        )


        self.db.flush()


        return VehicleMapper.to_domain(model)




    # =========================
    # DELETE
    # =========================

    def delete(
        self,
        vehicle_id: str
    ):

        model = (
            self.db.query(
                VehicleModel
            )
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



    # =========================
    # ALL
    # =========================

    def get_all(
        self
    ) -> list[Vehicle]:


        models = (
            self.db
            .query(VehicleModel)
            .all()
        )


        return [
           VehicleMapper.to_domain(
                model
            )
            for model in models
        ]



    # =========================
    # LICENSE PLATE
    # =========================

    def get_by_license_plate(
        self,
        plate: str,
    ):

        normalized_plate = (
            plate
            .strip()
            .upper()
        )


        model = (
            self.db
            .query(
                VehicleModel
            )
            .filter(
                VehicleModel.license_plate == normalized_plate
            )
            .first()
        )


        if not model:
            return None


        return VehicleMapper.to_domain(model)