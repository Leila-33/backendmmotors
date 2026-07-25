class VerificationEmailTemplate:


    @staticmethod
    def render(
        verification_link: str,
    ):

        subject = (
            "Vérification de votre compte"
        )


        body = f"""
Bonjour,


Bienvenue sur notre plateforme.


Veuillez cliquer sur le lien ci-dessous
pour vérifier votre adresse email :


{verification_link}


Si vous n'êtes pas à l'origine de cette demande,
ignorez simplement cet email.


Cordialement.
"""


        return (
            subject,
            body,
        )