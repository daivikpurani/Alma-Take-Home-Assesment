# app/db/base.py

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import models here so create_all can see them
from app.models.lead import Lead  # noqa: E402, F401
