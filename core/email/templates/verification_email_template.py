class VerificationEmailTemplate:

    @staticmethod
    def render(
        verification_link: str,
    ):
        subject = "Vérifiez votre adresse e-mail — M-Motors"

        # =========================
        # PLAIN TEXT VERSION
        # =========================
        body = f"""
Bonjour,

Bienvenue chez M-Motors !

Pour finaliser la création de votre compte, veuillez vérifier votre adresse e-mail en cliquant sur le lien suivant :

{verification_link}

Ce lien vous permet de confirmer votre adresse e-mail et d'activer votre compte.

Si vous n'êtes pas à l'origine de cette inscription, vous pouvez simplement ignorer cet e-mail.

À bientôt,
L'équipe M-Motors
""".strip()

        # =========================
        # HTML VERSION
        # =========================
        html_body = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Vérification de votre compte</title>
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
                                Vérifiez votre adresse e-mail
                            </h1>

                            <p
                                style="
                                    margin: 0 0 16px;
                                    font-size: 16px;
                                    line-height: 1.6;
                                    color: #4b5563;
                                "
                            >
                                Bonjour,
                            </p>

                            <p
                                style="
                                    margin: 0 0 24px;
                                    font-size: 16px;
                                    line-height: 1.6;
                                    color: #4b5563;
                                "
                            >
                                Bienvenue chez <strong>M-Motors</strong> !
                                Pour finaliser la création de votre compte,
                                veuillez confirmer votre adresse e-mail.
                            </p>

                            <!-- BUTTON -->
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
                                            href="{verification_link}"
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
                                            Vérifier mon adresse e-mail
                                        </a>

                                    </td>
                                </tr>
                            </table>

                            <p
                                style="
                                    margin: 28px 0 8px;
                                    font-size: 14px;
                                    line-height: 1.5;
                                    color: #6b7280;
                                "
                            >
                                Si le bouton ne fonctionne pas, copiez et
                                collez le lien suivant dans votre navigateur :
                            </p>

                            <p
                                style="
                                    margin: 0 0 24px;
                                    font-size: 13px;
                                    line-height: 1.5;
                                    word-break: break-all;
                                "
                            >
                                <a
                                    href="{verification_link}"
                                    target="_blank"
                                    style="
                                        color: #2563eb;
                                        text-decoration: underline;
                                    "
                                >
                                    {verification_link}
                                </a>
                            </p>

                            <p
                                style="
                                    margin: 0;
                                    font-size: 14px;
                                    line-height: 1.6;
                                    color: #6b7280;
                                "
                            >
                                Si vous n'êtes pas à l'origine de cette
                                inscription, vous pouvez simplement ignorer
                                cet e-mail.
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

### Ce que tu obtiens
