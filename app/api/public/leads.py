# app/api/public/leads.py

import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import os

from app.api.deps import get_db, get_storage
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["Public Leads"])


# ---- Health Check for Public API ----
@router.get("/ping", status_code=status.HTTP_200_OK)
def public_ping():
    return {"message": "public leads endpoint"}


# ---- Create a Lead (Prospect Form) ----
@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead_public(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage = Depends(get_storage),
):
    # 1) Save uploaded resume
    try:
        file_extension = os.path.splitext(resume.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = await storage.save(resume, filename)
    except Exception as e:
        logger.error(
            f"Failed to store uploaded resume: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to store uploaded resume"
        )

    # 2) Validate form into Pydantic model
    try:
        lead_data = LeadCreate(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
    except Exception as e:
        logger.error(
            f"Validation error creating lead: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input data: {str(e)}"
        )

    # 3) Persist + send emails
    try:
        lead = LeadService.create_lead(db=db, data=lead_data, resume_path=file_path)
        return lead
    except Exception as e:
        logger.error(
            f"Error creating lead: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to create lead. Please try again later."
        )
