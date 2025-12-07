# app/services/lead_service.py

import logging
import math
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
        lead = None
        try:
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

            return lead

        except SQLAlchemyError as e:
            # Rollback database transaction on error
            db.rollback()
            logger.error(
                f"Database error while creating lead: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            # Rollback database transaction on any error
            if lead:
                db.rollback()
            logger.error(
                f"Unexpected error while creating lead: {str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def send_prospect_email(lead: Lead):
        """
        Send thank you email to the prospect.
        This method is designed to be called as a background task.
        """
        try:
            settings = get_settings()
            company_name = settings.company_name or "Alma Law Group"
            
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
        except Exception as e:
            # Log email error but don't fail the lead creation
            logger.error(
                f"Failed to send prospect email for lead {lead.id}: {str(e)}",
                exc_info=True
            )

    @staticmethod
    def send_company_notification_email(lead: Lead):
        """
        Send notification email to the company/attorney.
        This method is designed to be called as a background task.
        """
        try:
            settings = get_settings()
            attorney_email = settings.attorney_email
            
            # Format created_at timestamp safely
            submitted_time = "N/A"
            if hasattr(lead, 'created_at') and lead.created_at:
                try:
                    submitted_time = lead.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
                except (AttributeError, ValueError) as e:
                    logger.warning(f"Error formatting timestamp: {str(e)}")
                    submitted_time = str(lead.created_at) if lead.created_at else "N/A"
            
            EmailService.send_email(
                to_email=attorney_email,
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
        except Exception as e:
            # Log email error but don't fail the lead creation
            logger.error(
                f"Failed to send company notification email for lead {lead.id}: {str(e)}",
                exc_info=True
            )

    @staticmethod
    def get_all_leads(db: Session) -> List[Lead]:
        """
        Get all leads ordered by creation date (newest first).
        """
        try:
            return db.query(Lead).order_by(Lead.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching all leads: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching all leads: {str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def get_leads_paginated(db: Session, page: int = 1, page_size: int = 10) -> Tuple[List[Lead], int]:
        """
        Get paginated leads ordered by creation date (newest first).
        Returns a tuple of (leads_list, total_count).
        """
        try:
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get total count
            total = db.query(Lead).count()
            
            # Get paginated results
            leads = (
                db.query(Lead)
                .order_by(Lead.created_at.desc())
                .offset(offset)
                .limit(page_size)
                .all()
            )
            
            return leads, total
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching paginated leads: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching paginated leads: {str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def get_lead_by_id(db: Session, lead_id: str) -> Optional[Lead]:
        """
        Get a lead by its ID.
        Returns None if not found.
        """
        try:
            # Try to convert string to UUID if needed
            import uuid
            lead_uuid = uuid.UUID(lead_id) if isinstance(lead_id, str) else lead_id
            return db.query(Lead).filter(Lead.id == lead_uuid).first()
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid lead_id format: {lead_id} - {str(e)}")
            return None
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching lead {lead_id}: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching lead {lead_id}: {str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def update_state(db: Session, lead_id, new_state: LeadState) -> Optional[Lead]:
        """
        Update the state of a lead.
        Returns None if lead not found.
        """
        try:
            # Convert string to UUID if needed (same logic as get_lead_by_id)
            import uuid
            lead_uuid = uuid.UUID(lead_id) if isinstance(lead_id, str) else lead_id
            
            lead = db.query(Lead).filter(Lead.id == lead_uuid).first()
            if not lead:
                return None

            lead.state = new_state
            db.commit()
            db.refresh(lead)

            logger.info(f"Lead {lead.id} state updated to {new_state}")
            return lead
        except (ValueError, TypeError) as e:
            # Invalid UUID format
            logger.warning(f"Invalid lead_id format: {lead_id} - {str(e)}")
            return None
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error while updating lead {lead_id} state: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error while updating lead {lead_id} state: {str(e)}",
                exc_info=True
            )
            raise
