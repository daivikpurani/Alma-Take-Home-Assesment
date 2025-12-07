# app/storage/local_storage_service.py

import os
import uuid
import logging
from fastapi import UploadFile
from app.storage.storage_service import StorageService

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"


class LocalStorageService(StorageService):
    async def save(self, file: UploadFile, filename: str | None = None) -> str:
        """
        Save uploaded file to local storage.
        """
        try:
            # Create upload directory if missing
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # Use unique name if not provided
            if filename is None:
                extension = file.filename.split(".")[-1] if "." in file.filename else ""
                filename = f"{uuid.uuid4()}.{extension}" if extension else str(uuid.uuid4())

            path = os.path.join(UPLOAD_DIR, filename)

            # Save file
            with open(path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            logger.info(f"File saved successfully: {path}")
            return path
        except OSError as e:
            logger.error(
                f"OS error saving file {file.filename}: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error saving file {file.filename}: {str(e)}",
                exc_info=True
            )
            raise
