class GetWarrantyPlansUseCase:
    """
    Récupère l'ensemble des plans de garantie disponibles.
    """
    def __init__(
        self,
        repository,
    ):
        self.repository = repository

    def execute(self):

        return self.repository.find_all()