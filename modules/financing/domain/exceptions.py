from core.exceptions import DomainException

class FinancingDataNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Informations de financement introuvables",
            400
        )



class FinancingContractNotFound(
    DomainException
):

    def __init__(self):

        super().__init__(
            "Contrat de financement introuvable",
            404
        )

class FinancingAmountNegative(DomainException):
    def __init__(self):
        super().__init__(
            message="L'apport et la valeur de reprise dépassent le prix du véhicule.",
            status_code=400
        )

class InstallmentNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "La mensualité de financement est introuvable.",
            404
        )