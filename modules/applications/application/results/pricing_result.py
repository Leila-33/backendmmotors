from dataclasses import dataclass


@dataclass(frozen=True)
class PricingResult:
    """
    Résultat du calcul du prix d'une application.
    """

    base_price: float
    optional_price: float
    discount: float
    total_price: float