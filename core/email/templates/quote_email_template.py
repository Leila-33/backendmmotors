class QuoteEmailTemplate:

    @staticmethod
    def render(
        quote,
        customer,
        vehicle,
        action_url,
        is_activation=False,
    ):
        # ==========================================================
        # FORMATAGE DES VALEURS
        # ==========================================================

        def format_amount(value):
            if value is None:
                return "Non renseigné"

            return f"{value:.2f} €"

        def format_optional_amount(value):
            if value is None or value == 0:
                return "Aucune"

            return f"{value:.2f} €"

        # ==========================================================
        # CONTENU DU MESSAGE
        # ==========================================================

        if is_activation:
            subject = (
                "Activez votre espace client "
                "pour consulter votre offre"
            )

            action_text = "Activer mon compte"

            intro = f"""
Bonjour {customer.first_name},

Votre conseiller a préparé une offre commerciale.

Pour accéder à votre offre,
veuillez activer votre espace client.
"""

        else:
            subject = "Votre nouvelle offre commerciale"

            action_text = "Accéder à mon espace client"

            intro = f"""
Bonjour {customer.first_name},

Votre conseiller vous a envoyé
une nouvelle offre commerciale.
"""

        # ==========================================================
        # OFFRE
        # ==========================================================

        body = f"""
{intro}

---------------------------------

VOTRE OFFRE

Véhicule :

{vehicle.brand}
{vehicle.model}


Prix véhicule :

{format_amount(quote.base_price)}


Remise :

{format_optional_amount(quote.discount)}


Apport :

{format_optional_amount(quote.down_payment)}


Reprise :

{format_optional_amount(quote.trade_in_value)}


Montant financé :

{format_amount(quote.financed_amount)}


Durée :

{quote.duration_months or "Non renseignée"} mois


Mensualité estimée :

{format_optional_amount(quote.monthly_payment)}/mois


---------------------------------


{action_text} :

{action_url}


---------------------------------

Cordialement,

L'équipe M-Motors
"""

        return subject, body