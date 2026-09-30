import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.email.services.email_service import EmailService
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.email.templates.verification_email_template import (
    VerificationEmailTemplate
)
from core.email.templates.quote_email_template import QuoteEmailTemplate


class SMTPEmailService(EmailService):

    def __init__(
        self,
        host,
        port,
        username,
        password,
        frontend_url,
        from_email,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.frontend_url = frontend_url
        self.from_email = from_email

    # =====================
    # CORE METHOD
    # =====================
    def send(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ):
        message = MIMEMultipart("alternative")

        message["From"] = self.from_email
        message["To"] = to
        message["Subject"] = subject

        # =====================
        # PLAIN TEXT VERSION
        # =====================
        message.attach(
            MIMEText(
                body,
                "plain",
                "utf-8",
            )
        )

        # =====================
        # HTML VERSION
        # =====================
        if html_body:
            message.attach(
                MIMEText(
                    html_body,
                    "html",
                    "utf-8",
                )
            )

        # =====================
        # SMTP
        # =====================
        with smtplib.SMTP(
            self.host,
            self.port,
        ) as server:

            server.starttls()

            server.login(
                self.username,
                self.password,
            )

            server.send_message(message)

    # =====================
    # VERIFICATION EMAIL
    # =====================
    def send_verification_email(
        self,
        email: str,
        token: str,
    ):
        verification_link = (
            f"{self.frontend_url}"
            f"/verify-email"
            f"?token={token}"
        )

        subject, body, html_body = (
            VerificationEmailTemplate.render(
                verification_link
            )
        )

        self.send(
            to=email,
            subject=subject,
            body=body,
            html_body=html_body,
        )

    # =====================
    # QUOTE EMAIL
    # =====================
    def send_quote_email(
        self,
        quote,
        customer,
        vehicle,
        activation_token=None,
    ):
        # =========================
        # ACTION URL
        # =========================
        if activation_token:

            action_url = (
                f"{self.frontend_url}"
                f"/activate-account"
                f"?token={activation_token}"
            )

            is_activation = True

        else:

            action_url = (
                f"{self.frontend_url}"
                f"/sales/quotes/{quote.id}"
            )

            is_activation = False

        # =========================
        # TEMPLATE
        # =========================
        subject, body, html_body = (
            QuoteEmailTemplate.render(
                quote=quote,
                customer=customer,
                vehicle=vehicle,
                action_url=action_url,
                is_activation=is_activation,
            )
        )

        # =========================
        # SEND
        # =========================
        self.send(
            to=customer.email,
            subject=subject,
            body=body,
            html_body=html_body,
        )