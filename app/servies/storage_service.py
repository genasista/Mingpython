"""
Storage Service - Abstraktion för filhantering
Kan bytas mellan lokal lagring och Azure Blob Storage via environment variable
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("Genassista-EDU-pythonAPI.storage")

# Storage provider type
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local").lower()  # 'local' eller 'azure'


class StorageServiceInterface(ABC):
    """Abstract interface för storage service"""
    
    @abstractmethod
    async def upload_file(
        self,
        file_content: bytes,
        path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload file och returnera path/URL
        
        Args:
            file_content: File content som bytes
            path: Relative path (t.ex. "assignments/school_001/assignment_001/submission.pdf")
            metadata: Optional metadata (t.ex. {"content_type": "application/pdf"})
        
        Returns:
            Path eller URL till filen
        """
        pass
    
    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """
        Download file content
        
        Args:
            path: Path eller URL till filen
        
        Returns:
            File content som bytes
        """
        pass
    
    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """
        Delete file
        
        Args:
            path: Path eller URL till filen
        
        Returns:
            True om filen raderades, False annars
        """
        pass
    
    @abstractmethod
    async def file_exists(self, path: str) -> bool:
        """
        Check if file exists
        
        Args:
            path: Path eller URL till filen
        
        Returns:
            True om filen finns, False annars
        """
        pass
    
    @abstractmethod
    async def generate_share_url(
        self,
        path: str,
        expires_in_hours: int = 24
    ) -> str:
        """
        Generera tidsbegränsad delningslänk
        
        Args:
            path: Path eller URL till filen
            expires_in_hours: Timmar tills länken går ut
        
        Returns:
            URL med SAS token eller signed URL
        """
        pass


class LocalStorageService(StorageServiceInterface):
    """
    Lokal filhantering - sparar filer på disk
    Perfekt för utveckling utan kostnader
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize local storage
        
        Args:
            base_path: Base path för filer (default: ./storage)
        """
        self.base_path = Path(base_path or os.getenv("STORAGE_LOCAL_PATH", "./storage"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorageService initialized with base path: {self.base_path}")
    
    async def upload_file(
        self,
        file_content: bytes,
        path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload file lokalt"""
        file_path = self.base_path / path
        
        # Skapa directories om de inte finns
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Skriv fil
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"File uploaded locally: {file_path}")
        return str(file_path.relative_to(self.base_path))
    
    async def download_file(self, path: str) -> bytes:
        """Download file lokalt"""
        file_path = self.base_path / path
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        logger.info(f"File downloaded locally: {file_path}")
        return content
    
    async def delete_file(self, path: str) -> bool:
        """Delete file lokalt"""
        file_path = self.base_path / path
        
        if not file_path.exists():
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        file_path.unlink()
        logger.info(f"File deleted locally: {file_path}")
        return True
    
    async def file_exists(self, path: str) -> bool:
        """Check if file exists lokalt"""
        file_path = self.base_path / path
        exists = file_path.exists()
        logger.debug(f"File exists check: {file_path} = {exists}")
        return exists
    
    async def generate_share_url(
        self,
        path: str,
        expires_in_hours: int = 24
    ) -> str:
        """
        Generera lokal share URL (för utveckling)
        I produktion skulle detta vara en riktig URL med authentication
        """
        # För lokal utveckling: returnera en relativ path
        # I produktion skulle detta vara en riktig URL med SAS token
        # Använd PORT miljövariabel om STORAGE_BASE_URL inte är satt
        if "STORAGE_BASE_URL" in os.environ:
            base_url = os.getenv("STORAGE_BASE_URL")
        else:
            port = os.getenv("PORT", "8001")
            base_url = f"http://localhost:{port}/storage"
        return f"{base_url}/{path}"


class AzureStorageService(StorageServiceInterface):
    """
    Azure Blob Storage - för produktion
    Aktiveras när STORAGE_PROVIDER=azure
    """
    
    def __init__(self):
        """Initialize Azure Storage (kommer implementeras senare)"""
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER", "assignments")
        
        if not connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING must be set for Azure Storage")
        
        # TODO: Implementera Azure Blob Storage när ni är redo
        # from azure.storage.blob import BlobServiceClient
        # self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # self.container_client = self.blob_service_client.get_container_client(container_name)
        
        logger.info("AzureStorageService initialized (not yet implemented)")
        logger.warning("Azure Storage will be implemented when ready for cloud deployment")
    
    async def upload_file(
        self,
        file_content: bytes,
        path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload file till Azure Blob Storage"""
        # TODO: Implementera när ni är redo för moln
        raise NotImplementedError("Azure Storage will be implemented when ready for cloud deployment")
    
    async def download_file(self, path: str) -> bytes:
        """Download file från Azure Blob Storage"""
        # TODO: Implementera när ni är redo för moln
        raise NotImplementedError("Azure Storage will be implemented when ready for cloud deployment")
    
    async def delete_file(self, path: str) -> bool:
        """Delete file från Azure Blob Storage"""
        # TODO: Implementera när ni är redo för moln
        raise NotImplementedError("Azure Storage will be implemented when ready for cloud deployment")
    
    async def file_exists(self, path: str) -> bool:
        """Check if file exists i Azure Blob Storage"""
        # TODO: Implementera när ni är redo för moln
        raise NotImplementedError("Azure Storage will be implemented when ready for cloud deployment")
    
    async def generate_share_url(
        self,
        path: str,
        expires_in_hours: int = 24
    ) -> str:
        """Generera SAS URL för Azure Blob Storage"""
        # TODO: Implementera när ni är redo för moln
        raise NotImplementedError("Azure Storage will be implemented when ready for cloud deployment")


def get_storage_service() -> StorageServiceInterface:
    """
    Factory function för att få rätt storage service
    Väljer implementation baserat på STORAGE_PROVIDER environment variable
    """
    if STORAGE_PROVIDER == "azure":
        logger.info("Using Azure Storage Service")
        return AzureStorageService()
    else:
        logger.info("Using Local Storage Service")
        return LocalStorageService()


# Global instance (lazy initialization)
_storage_service: Optional[StorageServiceInterface] = None


def storage_service() -> StorageServiceInterface:
    """
    Get storage service instance (singleton pattern)
    Använd denna i endpoints för att få storage service
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = get_storage_service()
    return _storage_service


def generate_storage_path(
    school_id: str,
    course_id: str,
    assignment_id: str,
    student_id: Optional[str] = None,
    group_id: Optional[str] = None,
    filename: str = "submission"
) -> str:
    """
    Generera standardiserad storage path
    Fungerar för både lokal och Azure Storage
    
    Args:
        school_id: Skola ID
        course_id: Kurs ID
        assignment_id: Uppgift ID
        student_id: Elev ID (optional, för individuella uppgifter)
        group_id: Grupp ID (optional, för grupparbete)
        filename: Filnamn (utan extension)
    
    Returns:
        Standardiserad path (t.ex. "school_001/course_eng5/assignment_001/student_123/submission.pdf")
    """
    if group_id:
        # Grupparbete
        return f"{school_id}/{course_id}/{assignment_id}/group_{group_id}/{filename}"
    elif student_id:
        # Individuell uppgift
        return f"{school_id}/{course_id}/{assignment_id}/student_{student_id}/{filename}"
    else:
        # Material eller annat
        return f"{school_id}/{course_id}/{assignment_id}/{filename}"

