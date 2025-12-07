# app/api/internal/leads.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_internal_token
from app.schemas.lead import LeadResponse, LeadStateUpdate
from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/leads",
    tags=["Internal Leads"],
    dependencies=[Depends(require_internal_token)],
)


@router.get("/ping", status_code=status.HTTP_200_OK)
def internal_ping():
    return {"message": "internal leads endpoint"}


@router.get("", response_model=list[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(
    db: Session = Depends(get_db),
):
    try:
        return LeadService.get_all_leads(db)
    except Exception as e:
        logger.error(
            f"Error fetching all leads: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leads"
        )


@router.get("/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
):
    try:
        lead = LeadService.get_lead_by_id(db=db, lead_id=lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching lead {lead_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch lead"
        )


@router.patch("/{lead_id}/state", response_model=LeadResponse, status_code=status.HTTP_200_OK)
def update_lead_state(
    lead_id: str,
    update: LeadStateUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated = LeadService.update_state(db=db, lead_id=lead_id, new_state=update.state)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating lead {lead_id} state: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lead state"
        )
