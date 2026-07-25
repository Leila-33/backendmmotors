from modules.reservations.api.dependencies import (
    get_complete_rentals_usecase
)


def run_complete_rentals():

    usecase = (
        get_complete_rentals_usecase()
    )

    usecase.execute()