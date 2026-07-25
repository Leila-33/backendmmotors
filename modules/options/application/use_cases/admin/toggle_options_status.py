from modules.options.domain.exceptions import OptionNotFound
from modules.options.api.schemas import UpdateOptionResponse

class ToggleOptionStatusUseCase:


    def __init__(
        self,
        option_repository,
        unit_of_work,
    ):

        self.option_repository = option_repository
        self.unit_of_work = unit_of_work



    def execute(
        self,
        option_id: str,
        request,
    ):


        # =========================
        # GET OPTION
        # =========================

        option = (
            self.option_repository
            .get_by_id(option_id)
        )


        if not option:
            raise OptionNotFound()



        # =========================
        # UPDATE STATUS
        # =========================

        option.is_active = request.is_active



        # =========================
        # SAVE
        # =========================

        self.option_repository.update(
            option
        )


        self.unit_of_work.commit()



        return UpdateOptionResponse(
            id=option.id,
            message=(
                "Option activée"
                if option.is_active
                else "Option désactivée"
            )
        )