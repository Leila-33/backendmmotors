from modules.vehicles.domain.entities.vehicle_option import (
    VehicleOption,
)
from modules.vehicles.infrastructure.db.vehicle_option_model import (
    VehicleOptionModel,
)
from modules.options.infrastructure.mapper.option_mapper import OptionMapper


class VehicleOptionMapper:


    @staticmethod
    def to_domain(
        model
    ) -> VehicleOption:


        return VehicleOption(

            id=model.id,

            vehicle_id=model.vehicle_id,

            option_id=model.option_id,

            type=model.type,

            option=(

                OptionMapper.to_domain(
                    model.option
                )

                if model.option

                else None

            )

        )



    @staticmethod
    def to_model(
        option: VehicleOption
    ):

        return VehicleOptionModel(

            id=option.id,

            vehicle_id=option.vehicle_id,

            option_id=option.option_id,

            type=option.type,

        )



    @staticmethod
    def update_model(
        model,
        option: VehicleOption
    ):

        model.type = option.type

        model.option_id = option.option_id

        return model