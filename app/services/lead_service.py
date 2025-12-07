# app/services/lead_service.py

import logging
from typing import List
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_state import LeadState
from app.schemas.lead import LeadCreate


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
