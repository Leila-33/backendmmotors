from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.infrastructure.db.warranty_plan_model import WarrantyPlanModel


def to_domain(model: WarrantyPlanModel) -> WarrantyPlan:
    return WarrantyPlan(
        id=model.id,
        name=model.name,
        description=model.description,
        plan_type=model.plan_type,
        duration_months=model.duration_months,
        mileage_limit=model.mileage_limit,
        covers_engine=model.covers_engine,
        covers_transmission=model.covers_transmission,
        covers_electronics=model.covers_electronics,
        covers_assistance=model.covers_assistance,
        covers_wear_parts=model.covers_wear_parts,
        deductible=model.deductible,
        price=model.price,
        active=model.active,
    )


def to_model(domain: WarrantyPlan) -> WarrantyPlanModel:
    return WarrantyPlanModel(
        id=domain.id,
        name=domain.name,
        description=domain.description,
        plan_type=domain.plan_type,
        duration_months=domain.duration_months,
        mileage_limit=domain.mileage_limit,
        covers_engine=domain.covers_engine,
        covers_transmission=domain.covers_transmission,
        covers_electronics=domain.covers_electronics,
        covers_assistance=domain.covers_assistance,
        covers_wear_parts=domain.covers_wear_parts,
        deductible=domain.deductible,
        price=domain.price,
        active=domain.active,
    )