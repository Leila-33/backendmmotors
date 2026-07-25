class QuoteEmailTemplate:

    @staticmethod
    def render(
        quote,
        customer,
        vehicle,
        action_url,
        is_activation=False,
    ):


        if is_activation:

            subject = (
                "Activez votre espace client "
                "pour consulter votre offre"
            )

            action_text = (
                "Activer mon compte"
            )

            intro = f"""
Bonjour {customer.first_name},

Votre conseiller a préparé une offre commerciale.

Pour accéder à votre offre,
veuillez activer votre espace client.
"""

        else:

            subject = (
                "Votre nouvelle offre commerciale"
            )

            action_text = (
                "Accéder à mon espace client"
            )

            intro = f"""
Bonjour {customer.first_name},

Votre conseiller vous a envoyé
une nouvelle offre commerciale.
"""



        body = f"""

{intro}


---------------------------------

VOTRE OFFRE

Véhicule :

{vehicle.brand}
{vehicle.model}


Prix véhicule :

{quote.base_price:.2f} €


Remise :

{quote.discount:.2f} €


Apport :

{quote.down_payment:.2f} €


Reprise :

{quote.trade_in_value:.2f} €


Montant financé :

{quote.financed_amount:.2f} €


Durée :

{quote.duration_months} mois


Mensualité estimée :

{quote.monthly_payment:.2f} €/mois


---------------------------------


{action_text} :

{action_url}


---------------------------------


Cordialement,

Votre conseiller commercial

"""


        return (
            subject,
            body
        )