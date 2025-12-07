# app/services/email_service.py

import logging
import asyncio

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    async def send_email(to: str, subject: str, body: str):
        # simulate I/O delay
        await asyncio.sleep(0.1)
        logger.info(f"[EMAIL SENT] to={to} subject={subject} body={body}")
