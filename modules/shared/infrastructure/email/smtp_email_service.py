import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.shared.infrastructure.email.email_service import EmailService

class SMTPEmailService(EmailService):

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, to: str, subject: str, body: str):

        # =====================
        # CREATE EMAIL MESSAGE
        # =====================
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = to
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        # =====================
        # SMTP CONNECTION
        # =====================
        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()  # sécurité TLS
            server.login(self.username, self.password)
            server.send_message(message)