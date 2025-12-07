# app/api/public/leads.py

from fastapi import APIRouter

router = APIRouter(prefix="/leads", tags=["public"])


@router.get("/ping")
def public_ping():
    return {"message": "public leads endpoint"}
