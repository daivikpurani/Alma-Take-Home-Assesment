
# app/storage/storage_service.py

from abc import ABC, abstractmethod
from fastapi import UploadFile


class StorageService(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, filename: str) -> str:
        """Save file and return the full path stored in DB"""
        raise NotImplementedError
