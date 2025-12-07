# =============================================
# REPLACE the contents of:
# app/api/public/leads.py
# =============================================

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import os

from app.api.deps import get_db, get_storage
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Public Leads"])


# ---- Health Check for Public API ----
@router.get("/ping")
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
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to store uploaded resume"
        )

    # 2) Validate form into Pydantic model
    lead_data = LeadCreate(
        first_name=first_name,
        last_name=last_name,
        email=email
    )

    # 3) Persist + send emails
    try:
        lead = LeadService.create_lead(db=db, data=lead_data, resume_path=file_path)
        return lead
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
