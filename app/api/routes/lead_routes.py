# app/api/routes/lead_routes.py

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_storage, require_internal_token
from app.schemas.lead import LeadCreate, LeadResponse, LeadStateUpdate
from app.services.lead_service import LeadService
from app.services.email_service import EmailService
from app.storage.storage_service import StorageService
import asyncio

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage),
):
    # Validate input via Pydantic schema
    lead_create = LeadCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )

    # Save file locally, get path
    resume_path = await storage.save(resume)

    # Persist lead in DB
    lead = LeadService.create_lead(db=db, data=lead_create, resume_path=resume_path)

    # send prospect email + attorney email
    asyncio.create_task(EmailService.send_email(
        to=lead.email,
        subject="Thank you for your submission!",
        body="We have received your information."
    ))

    asyncio.create_task(EmailService.send_email(
        to="attorney@example.com",
        subject="New lead submitted",
        body=f"Lead {lead.first_name} {lead.last_name} has submitted information."
    ))

    return lead


@router.get("", response_model=list[LeadResponse], tags=["Internal Leads"])
def list_leads(
    db: Session = Depends(get_db),
    _ = Depends(require_internal_token),
):
    return LeadService.get_all_leads(db)


@router.patch("/{lead_id}/state", response_model=LeadResponse, tags=["Internal Leads"])
def update_lead_state(
    lead_id: str,
    update: LeadStateUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_internal_token),
):
    updated = LeadService.update_state(db=db, lead_id=lead_id, new_state=update.state)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return updated
