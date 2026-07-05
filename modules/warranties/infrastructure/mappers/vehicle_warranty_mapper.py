from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel

class VehicleWarrantyMapper:

    @staticmethod
    def to_model(domain) -> VehicleWarrantyModel:
        if not domain:
            return None

        return VehicleWarrantyModel(
            id=domain.id,
            vehicle_id=domain.vehicle_id,
            warranty_plan_id=domain.warranty_plan_id,
            start_date=domain.start_date,
            end_date=domain.end_date,
            is_active=domain.is_active,
            current_mileage=domain.current_mileage,
            max_mileage=domain.max_mileage,
        )

    @staticmethod
    def to_domain(model) -> VehicleWarranty:
        if not model:
            return None

        return VehicleWarranty(
            id=model.id,
            vehicle_id=model.vehicle_id,
            warranty_plan_id=model.warranty_plan_id,
            start_date=model.start_date,
            end_date=model.end_date,
            is_active=model.is_active,
            current_mileage=model.current_mileage,
            max_mileage=model.max_mileage,
        )