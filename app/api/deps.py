# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.storage.local_storage_service import LocalStorageService
from app.core.config import get_settings, Settings


security = HTTPBearer()


def get_current_internal_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
):
    """
    Validate Bearer token for internal UI routes.
    """
    if credentials.credentials != settings.internal_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return {"role": "attorney"}  # placeholder user object





def get_storage():
    return LocalStorageService()
