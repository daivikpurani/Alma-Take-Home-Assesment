# app/api/internal/leads.py

import logging
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_internal_token
from app.schemas.lead import LeadResponse, LeadStateUpdate, PaginatedLeadResponse
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


@router.get("", status_code=status.HTTP_200_OK)
def list_leads(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    db: Session = Depends(get_db),
):
    """
    List all leads with pagination support.
    Returns paginated results by default.
    """
    try:
        leads, total = LeadService.get_leads_paginated(db, page=page, page_size=page_size)
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return PaginatedLeadResponse(
            items=leads,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(
            f"Error fetching paginated leads: {str(e)}",
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
