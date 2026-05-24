import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.services.email_service import EmailService
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTPEmailService(EmailService):

    def __init__(self, host, port, username, password, frontend_url):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.frontend_url = frontend_url

    # =====================
    # CORE METHOD
    # =====================
    def send(self, to: str, subject: str, body: str):

        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = to
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(message)

    # =====================
    # BUSINESS METHOD
    # =====================
    def send_verification_email(self, email: str, token: str):

        verification_link = f"{self.frontend_url}/verify-email?token={token}"

        subject = "Vérification de votre compte"

        body = f"""
Bonjour,

Veuillez cliquer sur le lien ci-dessous pour vérifier votre compte :

{verification_link}

Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
"""

        # 🔥 utilise send()
        self.send(
            to=email,
            subject=subject,
            body=body
        )