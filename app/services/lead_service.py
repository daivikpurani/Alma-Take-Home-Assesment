# app/services/lead_service.py

import logging
from typing import List
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_state import LeadState
from app.schemas.lead import LeadCreate
from app.services.email_service import EmailService
from app.core.config import get_settings


logger = logging.getLogger(__name__)


class LeadService:
    @staticmethod
    def create_lead(db: Session, data: LeadCreate, resume_path: str) -> Lead:
        """
        Create a new lead with a given resume file path.
        The resume file is not saved here, only the path is recorded.
        """
        lead = Lead(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            resume_path=resume_path,
            state=LeadState.PENDING,
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        logger.info(f"Lead created: {lead.id} -> {lead.email}")

        settings = get_settings()
        company_name = settings.company_name or "Alma Law Group"

        # Send email to prospect
        EmailService.send_email(
            to_email=lead.email,
            subject="Thank you for your submission",
            content=f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #2c3e50;">Thank You for Your Submission</h2>
                            <p>Hi {lead.first_name},</p>
                            <p>Thank you for contacting {company_name}. We have received your resume and information, and our team will review your submission shortly.</p>
                            <p>We appreciate your interest in joining our team and will be in touch soon.</p>
                            <p>Best regards,<br>
                            <strong>{company_name}</strong></p>
                        </div>
                    </body>
                </html>
            """
        )

        # Send email to attorney/company - always send to daivikpurani1
        # Format created_at timestamp safely
        submitted_time = "N/A"
        if hasattr(lead, 'created_at') and lead.created_at:
            try:
                submitted_time = lead.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
            except (AttributeError, ValueError):
                submitted_time = str(lead.created_at) if lead.created_at else "N/A"
        
        EmailService.send_email(
            to_email="daivikpurani1@gmail.com",
            subject=f"New Lead Submission - {lead.first_name} {lead.last_name}",
            content=f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #2c3e50;">New Lead Submission</h2>
                            <p>A new lead has been submitted through the application form:</p>
                            <ul style="list-style: none; padding: 0;">
                                <li style="margin: 10px 0;"><strong>Name:</strong> {lead.first_name} {lead.last_name}</li>
                                <li style="margin: 10px 0;"><strong>Email:</strong> <a href="mailto:{lead.email}">{lead.email}</a></li>
                                <li style="margin: 10px 0;"><strong>Resume:</strong> {lead.resume_path}</li>
                                <li style="margin: 10px 0;"><strong>Lead ID:</strong> {lead.id}</li>
                                <li style="margin: 10px 0;"><strong>Submitted:</strong> {submitted_time}</li>
                            </ul>
                            <p>Please review this submission and follow up with the candidate.</p>
                        </div>
                    </body>
                </html>
            """
        )

        return lead

    @staticmethod
    def get_all_leads(db: Session) -> List[Lead]:
        return db.query(Lead).order_by(Lead.created_at.desc()).all()

    @staticmethod
    def update_state(db: Session, lead_id, new_state: LeadState) -> Lead:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        lead.state = new_state
        db.commit()
        db.refresh(lead)

        logger.info(f"Lead {lead.id} state updated to {new_state}")
        return lead
