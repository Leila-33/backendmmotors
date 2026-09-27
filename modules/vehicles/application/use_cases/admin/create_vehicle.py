import uuid
import logging
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.enums import VehicleType, VehicleStatus
from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty

from modules.vehicles.domain.exceptions import VehicleAlreadyExists
from modules.warranties.domain.exceptions import WarrantyRequiredForSale

from modules.applications.domain.enums import EventType

from modules.vehicles.application.dtos.admin.create_vehicle_dto import (
    CreateVehicleDTO,
)

from modules.vehicles.domain.entities.vehicle_option import (
    VehicleOption,
)
from modules.vehicles.domain.enums import VehicleOptionType

from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
)

from modules.options.domain.exceptions import (
    OptionNotFound,
)
from modules.vehicles.domain.utils.license_plate import (
    normalize_license_plate,
)
logger = logging.getLogger(__name__)


class CreateVehicleUseCase:
    """
    Crée un véhicule après vérification de l'unicité de sa plaque
    et des règles métier liées à son type et à sa garantie.

    Le véhicule est associé à ses options et, si nécessaire, à une garantie,
    puis sa création est enregistrée dans l'historique des événements.
    """
    def __init__(
        self,
        vehicle_repository,
        warranty_repository,
        assign_options_usecase,
        event_service,
        unit_of_work,
    ):
        self.vehicle_repository = vehicle_repository
        self.warranty_repository = warranty_repository
        self.assign_options_usecase = assign_options_usecase
        self.event_service = event_service
        self.uow = unit_of_work

    def execute(
        self,
        dto: CreateVehicleDTO,
        admin_id: str,
    ):

        try:

            # =========================
            # DUPLICATE
            # =========================
            license_plate = normalize_license_plate(
                dto.license_plate
            )

            if license_plate:

                existing = (
                    self.vehicle_repository
                    .get_by_license_plate(
                        license_plate
                    )
                )

                if existing:
                    raise VehicleAlreadyExists()

            # =========================
            # BUSINESS RULES
            # =========================

            if (
                dto.type == VehicleType.SALE
                and not dto.warranty_plan_id
            ):
                raise WarrantyRequiredForSale()

            warranty_plan_id = (
                dto.warranty_plan_id
                if dto.type == VehicleType.SALE
                else None
            )

            # =========================
            # VEHICLE
            # =========================
    # Un véhicule à vendre doit être marqué
    # comme indisponible (is_available=False) jusqu'à sa validation.
    # Un véhicule de location est disponible par défaut.
            vehicle = Vehicle(
                id=str(uuid.uuid4()),
                brand=dto.brand,
                model=dto.model,
                price=dto.price,
                type=dto.type,
                mileage=dto.mileage,
                year=dto.year,
                description=dto.description,
                engine_type=dto.engine_type,
                equipments=dto.equipments,
                condition=dto.condition,
                is_available=dto.type != VehicleType.SALE,
                images=dto.images,
                license_plate=license_plate,

                # =========================
                # STATUT INITIAL
                # =========================
                #
                # Location :
                #   → publié immédiatement
                #
                # Vente :
                #   → en attente de validation finale
                #
                status=(
                    VehicleStatus.PUBLISHED
                    if dto.type == VehicleType.RENT
                    else VehicleStatus.AVAILABLE
                ),
            )

            # =========================
            # WARRANTY
            # =========================

            if warranty_plan_id:

                vehicle.warranty = VehicleWarranty(
                    id=str(uuid.uuid4()),
                    vehicle_id=vehicle.id,
                    warranty_plan_id=warranty_plan_id,
                    is_active=False,
                )
                self.warranty_repository.save(vehicle.warranty)

            # =========================
            # SAVE
            # =========================

            vehicle = (
                self.vehicle_repository
                .save(vehicle)
            )

            # =========================
            # OPTIONS
            # =========================

            self.assign_options_usecase.execute(
                vehicle_id=vehicle.id,
                included_option_ids=dto.included_options,
                optional_option_ids=dto.optional_options,
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.VEHICLE_CREATED,
                message="Véhicule créé",
                vehicle_id=vehicle.id,
                user_id=admin_id,
                event_metadata={
                    "brand": vehicle.brand,
                    "model": vehicle.model,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            logger.info(
                "Véhicule créé",
                extra={
                    "vehicle_id": vehicle.id,
                    "admin_id": admin_id,
                },
            )

            return vehicle

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur création véhicule",
                extra={
                    "admin_id": admin_id,
                },
            )

            raise





class AssignOptionsToVehicleUseCase:
    """
    Associe les options incluses et optionnelles à un véhicule
    après vérification de leur existence.

    Les associations existantes sont remplacées afin de synchroniser
    les options du véhicule avec celles fournies.
    """
    def __init__(
        self,
        vehicle_repository,
        option_repository,
        vehicle_option_repository,
    ):
        self.vehicle_repository = vehicle_repository
        self.option_repository = option_repository
        self.vehicle_option_repository = (
            vehicle_option_repository
        )

    def execute(
        self,
        vehicle_id: str,
        included_option_ids: list[str],
        optional_option_ids: list[str],
    ):

        # =========================
        # VEHICLE
        # =========================

        vehicle = (
            self.vehicle_repository
            .get_by_id(vehicle_id)
        )

        if vehicle is None:
            raise VehicleNotFound()

        included_option_ids = (
            included_option_ids or []
        )

        optional_option_ids = (
            optional_option_ids or []
        )

        # =========================
        # VALIDATE OPTIONS
        # =========================

        included_options = []

        for option_id in included_option_ids:

            option = (
                self.option_repository
                .get_by_id(option_id)
            )

            if option is None:
                raise OptionNotFound()

            included_options.append(option)

        optional_options = []

        for option_id in optional_option_ids:

            option = (
                self.option_repository
                .get_by_id(option_id)
            )

            if option is None:
                raise OptionNotFound()

            optional_options.append(option)

        # =========================
        # REMOVE EXISTING
        # =========================

        self.vehicle_option_repository.delete_by_vehicle(
            vehicle_id
        )

        # =========================
        # INCLUDED
        # =========================

        for option in included_options:

            vehicle_option = VehicleOption(
                id=str(uuid.uuid4()),
                vehicle_id=vehicle_id,
                option_id=option.id,
                type=VehicleOptionType.INCLUDED,
            )

            self.vehicle_option_repository.create(
                vehicle_option
            )

        # =========================
        # OPTIONAL
        # =========================

        for option in optional_options:

            vehicle_option = VehicleOption(
                id=str(uuid.uuid4()),
                vehicle_id=vehicle_id,
                option_id=option.id,
                type=VehicleOptionType.OPTIONAL,
            )

            self.vehicle_option_repository.create(
                vehicle_option
            )