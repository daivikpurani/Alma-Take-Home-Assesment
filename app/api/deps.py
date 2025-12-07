# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.storage.local_storage_service import LocalStorageService
from app.db.session import get_db  # <-- re-export


# STORAGE DEPENDENCY
def get_storage():
    return LocalStorageService()


# AUTH FOR INTERNAL ROUTES
bearer_scheme = HTTPBearer()

def require_internal_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings = Depends(get_settings),
):
    if credentials.credentials != settings.internal_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal API token",
        )
