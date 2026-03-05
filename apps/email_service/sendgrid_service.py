import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _redact_email(email: str) -> str:
    """Redact email for safe logging."""
    local, _, domain = email.partition("@")
    return f"{local[:2]}***@{domain}" if local else email


class SendGridEmailService:
    """
    SendGrid email service for sending template-based emails.
    Equivalent to Rails SendgridEmailService.
    """

    MAX_BATCH_SIZE = 1000

    @staticmethod
    def enabled():
        return bool(getattr(settings, "SENDGRID_API_KEY", None)) and bool(
            getattr(settings, "SENDGRID_FROM_EMAIL", None)
        )

    @classmethod
    def send_template_email(
        cls,
        to: str,
        subject: str,
        template_id: str,
        dynamic_data: dict | None = None,
    ) -> dict:
        if not cls.enabled():
            logger.warning("SendGrid is not configured. Skipping email send.")
            return {"success": False, "status_code": 0}

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, To

            message = Mail(
                from_email=(
                    getattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com"),
                    getattr(settings, "SENDGRID_FROM_NAME", "Template"),
                ),
                to_emails=To(to),
                subject=subject,
            )
            message.template_id = template_id
            if dynamic_data:
                message.dynamic_template_data = dynamic_data

            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info("Email sent to %s, status: %s", _redact_email(to), response.status_code)
            return {"success": response.status_code in (200, 201, 202), "status_code": response.status_code}

        except Exception as e:
            logger.error("Failed to send email to %s: %s", _redact_email(to), e)
            return {"success": False, "status_code": 0}

    @classmethod
    def send_batch_template_emails(
        cls,
        template_id: str,
        subject: str,
        requests: list,
    ) -> dict:
        """
        Send batch template emails using personalizations. Max 1000 per API call.

        Each chunk of up to 1000 recipients is sent as a single Mail object with
        multiple Personalization entries — equivalent to the Rails pattern.

        Args:
            template_id: SendGrid template ID
            subject: Email subject
            requests: List of dicts with 'to' and optional 'dynamic_data' keys

        Returns:
            dict with 'success', 'total', 'sent', and 'failed' keys
        """
        total = len(requests)

        if not cls.enabled():
            logger.warning("SendGrid is not configured. Skipping batch email send.")
            return {"success": False, "total": total, "sent": 0, "failed": total}

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Email, Mail, Personalization
        except ImportError as e:
            logger.error("sendgrid package not available: %s", e)
            return {"success": False, "total": total, "sent": 0, "failed": total}

        sent = 0
        failed = 0
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        from_email = (
            getattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com"),
            getattr(settings, "SENDGRID_FROM_NAME", "Template"),
        )

        for batch_start in range(0, total, cls.MAX_BATCH_SIZE):
            batch = requests[batch_start : batch_start + cls.MAX_BATCH_SIZE]

            mail = Mail()
            mail.from_email = from_email
            mail.template_id = template_id

            for req in batch:
                personalization = Personalization()
                personalization.add_to(Email(req["to"]))
                personalization.subject = subject
                personalization.dynamic_template_data = req.get("dynamic_data") or {}
                mail.add_personalization(personalization)

            try:
                response = sg.send(mail)
                if response.status_code in (200, 201, 202):
                    sent += len(batch)
                    logger.info("Batch sent: %d recipients, status: %s", len(batch), response.status_code)
                else:
                    failed += len(batch)
                    logger.error("Batch failed: %d recipients, status: %s", len(batch), response.status_code)
            except Exception as e:
                failed += len(batch)
                logger.error("Batch send error (%d recipients): %s", len(batch), e)

        return {
            "success": failed == 0,
            "total": total,
            "sent": sent,
            "failed": failed,
        }
