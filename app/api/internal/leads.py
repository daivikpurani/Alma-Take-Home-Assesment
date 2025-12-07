# app/api/internal/leads.py

from fastapi import APIRouter, Depends
from app.api.deps import get_current_internal_user

router = APIRouter(
    prefix="/leads",
    tags=["internal"],
    dependencies=[Depends(get_current_internal_user)],
)


@router.get("/ping")
def internal_ping():
    return {"message": "internal leads endpoint"}
