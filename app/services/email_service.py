# app/services/email_service.py

import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from app.core.config import get_settings


logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, content: str):
        """
        Send an email via SendGrid, with fallback to console logging
        if API key is missing or if an error occurs.
        """
        settings = get_settings()
        api_key = settings.sendgrid_api_key
        sender_email = settings.company_notification_email

        # Debug: Log what we're reading from config (masked for security)
        api_key_preview = f"{api_key[:8]}..." if api_key and len(api_key) > 8 else "None/Empty"
        print(f"\n{'='*60}")
        print(f"[DEBUG - Config Values]")
        print(f"sendgrid_api_key: {api_key_preview} (type: {type(api_key).__name__}, length: {len(api_key) if api_key else 0})")
        print(f"company_notification_email: {sender_email}")
        print(f"Raw api_key value (first check): {repr(api_key)}")
        print(f"{'='*60}\n")

        # Fallback logging if no API key or sender email configured
        if not api_key:
            logger.warning(
                f"[EMAIL-SIMULATION] To={to_email} | Subject={subject} | Body={content}"
            )
            print(f"\n{'='*60}")
            print(f"[EMAIL-SIMULATION - No API Key Configured]")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body:\n{content}")
            print(f"{'='*60}\n")
            return

        if not sender_email:
            logger.warning(
                f"[EMAIL-SIMULATION] To={to_email} | Subject={subject} | Body={content}"
            )
            print(f"\n{'='*60}")
            print(f"[EMAIL-SIMULATION - No Sender Email Configured]")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body:\n{content}")
            print(f"{'='*60}\n")
            return

        try:
            message = Mail(
                from_email=Email(sender_email, settings.company_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=content,
            )

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            # Log detailed API response
            logger.info(f"Email sent successfully to {to_email} (Status: {response.status_code})")
            print(f"\n{'='*60}")
            print(f"[SENDGRID API RESPONSE]")
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Body: {response.body}")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            # Log full error with stack trace
            logger.error(
                f"SendGrid Email Failure to {to_email}: {str(e)}",
                exc_info=True,  # This includes full stack trace
                extra={
                    "to_email": to_email,
                    "subject": subject,
                }
            )
            # Fallback to console logging on error
            logger.warning(
                f"[EMAIL-SIMULATION - SendGrid Error] To={to_email} | Subject={subject}"
            )
