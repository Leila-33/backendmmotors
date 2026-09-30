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

        customer_name = customer.first_name or "Client"
        vehicle_brand = vehicle.brand or "Véhicule"
        vehicle_model = vehicle.model or ""

        base_price = format_amount(quote.base_price)
        discount = format_optional_amount(quote.discount)
        down_payment = format_optional_amount(quote.down_payment)
        trade_in_value = format_optional_amount(
            quote.trade_in_value
        )
        financed_amount = format_amount(
            quote.financed_amount
        )
        duration = (
            f"{quote.duration_months} mois"
            if quote.duration_months
            else "Non renseignée"
        )
        monthly_payment = format_optional_amount(
            quote.monthly_payment
        )

        # ==========================================================
        # CONTENU
        # ==========================================================

        if is_activation:
            subject = (
                "Activez votre espace client — "
                "Votre offre M-Motors"
            )

            action_text = "Activer mon compte"

            intro_text = (
                f"Votre conseiller a préparé une offre "
                f"commerciale pour vous. "
                f"Pour consulter votre offre, "
                f"activez votre espace client."
            )

        else:
            subject = (
                "Votre nouvelle offre commerciale — "
                "M-Motors"
            )

            action_text = "Consulter mon offre"

            intro_text = (
                "Votre conseiller vous a envoyé "
                "une nouvelle offre commerciale. "
                "Vous pouvez la consulter depuis "
                "votre espace client."
            )

        # ==========================================================
        # VERSION TEXTE
        # ==========================================================

        body = f"""
Bonjour {customer_name},

{intro_text}

VOTRE OFFRE
------------------------------

Véhicule :
{vehicle_brand} {vehicle_model}

Prix du véhicule :
{base_price}

Remise :
{discount}

Apport :
{down_payment}

Reprise :
{trade_in_value}

Montant financé :
{financed_amount}

Durée :
{duration}

Mensualité estimée :
{monthly_payment}/mois

------------------------------

{action_text} :
{action_url}

------------------------------

Cordialement,

L'équipe M-Motors
""".strip()

        # ==========================================================
        # VERSION HTML
        # ==========================================================

        html_body = f"""
<!DOCTYPE html>
<html lang="fr">

<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Votre offre M-Motors</title>
</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f4f6f8;
        font-family: Arial, Helvetica, sans-serif;
        color: #1f2937;
    "
>

    <table
        role="presentation"
        width="100%"
        cellpadding="0"
        cellspacing="0"
        border="0"
        style="background-color: #f4f6f8;"
    >
        <tr>
            <td
                align="center"
                style="padding: 40px 16px;"
            >

                <table
                    role="presentation"
                    width="100%"
                    cellpadding="0"
                    cellspacing="0"
                    border="0"
                    style="
                        max-width: 600px;
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                    "
                >

                    <!-- HEADER -->
                    <tr>
                        <td
                            align="center"
                            style="
                                padding: 32px 24px;
                                background-color: #111827;
                            "
                        >
                            <div
                                style="
                                    font-size: 28px;
                                    font-weight: bold;
                                    color: #ffffff;
                                    letter-spacing: 1px;
                                "
                            >
                                M-Motors
                            </div>
                        </td>
                    </tr>

                    <!-- CONTENT -->
                    <tr>
                        <td
                            style="
                                padding: 40px 40px 32px;
                            "
                        >

                            <h1
                                style="
                                    margin: 0 0 20px;
                                    font-size: 24px;
                                    line-height: 1.3;
                                    color: #111827;
                                "
                            >
                                Votre offre commerciale
                            </h1>

                            <p
                                style="
                                    margin: 0 0 16px;
                                    font-size: 16px;
                                    line-height: 1.6;
                                    color: #4b5563;
                                "
                            >
                                Bonjour
                                <strong>{customer_name}</strong>,
                            </p>

                            <p
                                style="
                                    margin: 0 0 28px;
                                    font-size: 16px;
                                    line-height: 1.6;
                                    color: #4b5563;
                                "
                            >
                                {intro_text}
                            </p>

                            <!-- VEHICLE -->
                            <table
                                role="presentation"
                                width="100%"
                                cellpadding="0"
                                cellspacing="0"
                                border="0"
                                style="
                                    margin-bottom: 24px;
                                    background-color: #f9fafb;
                                    border: 1px solid #e5e7eb;
                                    border-radius: 8px;
                                "
                            >
                                <tr>
                                    <td
                                        style="padding: 24px;"
                                    >

                                        <p
                                            style="
                                                margin: 0 0 8px;
                                                font-size: 12px;
                                                font-weight: bold;
                                                text-transform: uppercase;
                                                letter-spacing: 0.5px;
                                                color: #6b7280;
                                            "
                                        >
                                            Véhicule
                                        </p>

                                        <p
                                            style="
                                                margin: 0;
                                                font-size: 20px;
                                                font-weight: bold;
                                                color: #111827;
                                            "
                                        >
                                            {vehicle_brand}
                                            {vehicle_model}
                                        </p>

                                    </td>
                                </tr>
                            </table>

                            <!-- OFFER -->
                            <table
                                role="presentation"
                                width="100%"
                                cellpadding="0"
                                cellspacing="0"
                                border="0"
                                style="
                                    border-collapse: collapse;
                                    margin-bottom: 28px;
                                "
                            >

                                <tr>
                                    <td
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Prix du véhicule
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #111827;
                                            font-size: 14px;
                                            font-weight: bold;
                                        "
                                    >
                                        {base_price}
                                    </td>
                                </tr>

                                <tr>
                                    <td
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Remise
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #111827;
                                            font-size: 14px;
                                        "
                                    >
                                        {discount}
                                    </td>
                                </tr>

                                <tr>
                                    <td
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Apport
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #111827;
                                            font-size: 14px;
                                        "
                                    >
                                        {down_payment}
                                    </td>
                                </tr>

                                <tr>
                                    <td
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Reprise
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #111827;
                                            font-size: 14px;
                                        "
                                    >
                                        {trade_in_value}
                                    </td>
                                </tr>

                                <tr>
                                    <td
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Montant financé
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #111827;
                                            font-size: 14px;
                                            font-weight: bold;
                                        "
                                    >
                                        {financed_amount}
                                    </td>
                                </tr>

                                <tr>
                                    <td
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Durée
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 12px 0;
                                            border-bottom: 1px solid #e5e7eb;
                                            color: #111827;
                                            font-size: 14px;
                                        "
                                    >
                                        {duration}
                                    </td>
                                </tr>

                                <tr>
                                    <td
                                        style="
                                            padding: 16px 0 0;
                                            color: #6b7280;
                                            font-size: 14px;
                                        "
                                    >
                                        Mensualité estimée
                                    </td>

                                    <td
                                        align="right"
                                        style="
                                            padding: 16px 0 0;
                                            color: #111827;
                                            font-size: 18px;
                                            font-weight: bold;
                                        "
                                    >
                                        {monthly_payment}/mois
                                    </td>
                                </tr>

                            </table>

                            <!-- ACTION BUTTON -->
                            <table
                                role="presentation"
                                cellpadding="0"
                                cellspacing="0"
                                border="0"
                                width="100%"
                            >
                                <tr>
                                    <td align="center">

                                        <a
                                            href="{action_url}"
                                            target="_blank"
                                            style="
                                                display: inline-block;
                                                padding: 14px 28px;
                                                background-color: #111827;
                                                color: #ffffff;
                                                text-decoration: none;
                                                font-size: 16px;
                                                font-weight: bold;
                                                border-radius: 8px;
                                            "
                                        >
                                            {action_text}
                                        </a>

                                    </td>
                                </tr>
                            </table>

                            <!-- FALLBACK LINK -->
                            <p
                                style="
                                    margin: 28px 0 8px;
                                    font-size: 14px;
                                    line-height: 1.5;
                                    color: #6b7280;
                                "
                            >
                                Si le bouton ne fonctionne pas,
                                copiez et collez le lien suivant dans
                                votre navigateur :
                            </p>

                            <p
                                style="
                                    margin: 0;
                                    font-size: 13px;
                                    line-height: 1.5;
                                    word-break: break-all;
                                "
                            >
                                <a
                                    href="{action_url}"
                                    target="_blank"
                                    style="
                                        color: #2563eb;
                                        text-decoration: underline;
                                    "
                                >
                                    {action_url}
                                </a>
                            </p>

                        </td>
                    </tr>

                    <!-- FOOTER -->
                    <tr>
                        <td
                            style="
                                padding: 24px 40px;
                                background-color: #f9fafb;
                                border-top: 1px solid #e5e7eb;
                            "
                        >

                            <p
                                style="
                                    margin: 0;
                                    font-size: 13px;
                                    line-height: 1.5;
                                    text-align: center;
                                    color: #9ca3af;
                                "
                            >
                                © M-Motors — Tous droits réservés.
                            </p>

                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
""".strip()

        return (
            subject,
            body,
            html_body,
        )