# app/schemas/lead.py

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.lead_state import LeadState


class LeadCreate(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr


class LeadResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    resume_path: str
    state: LeadState
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadStateUpdate(BaseModel):
    state: LeadState
