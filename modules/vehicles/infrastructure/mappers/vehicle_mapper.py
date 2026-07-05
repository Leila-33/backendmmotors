from modules.warranties.infrastructure.mappers.vehicle_warranty_mapper import VehicleWarrantyMapper
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel

class VehicleMapper:

    @staticmethod
    def to_model(domain, model=None):

        model = model or VehicleModel()

        model.id = domain.id
        model.brand = domain.brand
        model.model = domain.model
        model.price = domain.price
        model.type = domain.type
        model.mileage = domain.mileage
        model.year = domain.year
        model.description = domain.description
        model.engine_type = domain.engine_type
        model.equipments = domain.equipments
        model.condition = domain.condition
        model.is_available = domain.is_available
        model.images = domain.images
        model.license_plate = domain.license_plate
        model.status = domain.status
        model.published_at = domain.published_at,
        model.final_check_at=domain.final_check_at,


        # WARRANTY
        model.warranty = VehicleWarrantyMapper.to_model(domain.warranty)

        return model

    @staticmethod
    def to_domain(model):

        return Vehicle(
            id=model.id,
            brand=model.brand,
            model=model.model,
            price=model.price,
            type=model.type,
            mileage=model.mileage,
            year=model.year,
            description=model.description,
            engine_type=model.engine_type,
            equipments=model.equipments,
            condition=model.condition,
            is_available=model.is_available,
            images=model.images,
            license_plate=model.license_plate,
            status=model.status,
            published_at=model.published_at,
            final_check_at=model.final_check_at,
            warranty=VehicleWarrantyMapper.to_domain(model.warranty)
        )