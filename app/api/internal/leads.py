# app/api/internal/leads.py

from fastapi import APIRouter, Depends
from app.api.deps import require_internal_token


router = APIRouter(
    prefix="/leads",
    tags=["internal"],
    dependencies=[Depends(require_internal_token)],
)


@router.get("/ping")
def internal_ping():
    return {"message": "internal leads endpoint"}
