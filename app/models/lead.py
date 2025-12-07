# app/models/lead.py

import uuid
from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.lead_state import LeadState


class Lead(Base):   # <— DO NOT CHANGE THIS LINE
    __tablename__ = "leads"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)

    # Path to stored resume (file will be saved separately)
    resume_path = Column(String(500), nullable=False)

    state = Column(
        Enum(LeadState, name="lead_state"),
        nullable=False,
        default=LeadState.PENDING,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
