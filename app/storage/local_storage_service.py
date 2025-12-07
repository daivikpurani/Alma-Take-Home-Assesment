# app/storage/local_storage_service.py

import os
import uuid
from fastapi import UploadFile
from app.storage.storage_service import StorageService


UPLOAD_DIR = "uploads"


class LocalStorageService(StorageService):
    async def save(self, file: UploadFile, filename: str | None = None) -> str:
        # Create upload directory if missing
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Use unique name if not provided
        extension = file.filename.split(".")[-1]
        filename = filename or f"{uuid.uuid4()}.{extension}"

        path = os.path.join(UPLOAD_DIR, filename)

        # Save file
        with open(path, "wb") as buffer:
            buffer.write(await file.read())

        return path
