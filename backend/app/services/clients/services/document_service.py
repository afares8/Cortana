import os
import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException
import shutil

from app.services.clients.models.client import ClientDocument
from app.db.in_memory import InMemoryDB

logger = logging.getLogger(__name__)

class DocumentService:
    """
    Service for managing client documents including upload, storage, and validation.
    """
    
    def __init__(self):
        self.base_upload_dir = Path.home() / "repos" / "Cortana" / "backend" / "uploads" / "clients"
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)
        self.documents_db = InMemoryDB("client_documents")
    
    async def upload_document(
        self,
        client_id: int,
        file: UploadFile,
        document_type: str,
        expiry_date: Optional[date] = None
    ) -> ClientDocument:
        """
        Upload and store a client document.
        
        Args:
            client_id: ID of the client
            file: Uploaded file
            document_type: Type of document (e.g., 'passport', 'id_card', 'incorporation_certificate')
            expiry_date: Optional expiry date for the document
            
        Returns:
            ClientDocument: Created document record
        """
        try:
            client_dir = self.base_upload_dir / str(client_id)
            client_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(file.filename).suffix if file.filename else ""
            filename = f"{document_type}_{timestamp}{file_extension}"
            file_path = client_dir / filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            document = ClientDocument(
                id=self._generate_id(),
                client_id=client_id,
                type=document_type,
                file_path=str(file_path),
                received_date=date.today(),
                expiry_date=expiry_date,
                is_validated=False
            )
            
            document_id = self.documents_db.create(document)
            document.id = document_id
            
            logger.info(f"Document uploaded for client {client_id}: {filename}")
            return document
            
        except Exception as e:
            logger.error(f"Error uploading document for client {client_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")
    
    async def get_client_documents(self, client_id: int) -> List[ClientDocument]:
        """
        Get all documents for a specific client.
        
        Args:
            client_id: ID of the client
            
        Returns:
            List[ClientDocument]: List of client documents
        """
        try:
            all_documents = self.documents_db.get_all()
            client_documents = [doc for doc in all_documents if doc.client_id == client_id]
            return client_documents
        except Exception as e:
            logger.error(f"Error retrieving documents for client {client_id}: {str(e)}")
            return []
    
    async def get_document(self, document_id: int) -> Optional[ClientDocument]:
        """
        Get a specific document by ID.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Optional[ClientDocument]: Document if found, None otherwise
        """
        try:
            return self.documents_db.get(document_id)
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            return None
    
    async def validate_document(self, document_id: int, is_valid: bool) -> Optional[ClientDocument]:
        """
        Mark a document as validated or invalid.
        
        Args:
            document_id: ID of the document
            is_valid: Whether the document is valid
            
        Returns:
            Optional[ClientDocument]: Updated document if found, None otherwise
        """
        try:
            document = self.documents_db.get(document_id)
            if not document:
                return None
            
            document.is_validated = is_valid
            self.documents_db.update(document_id, document)
            
            logger.info(f"Document {document_id} validation status updated to: {is_valid}")
            return document
            
        except Exception as e:
            logger.error(f"Error validating document {document_id}: {str(e)}")
            return None
    
    async def delete_document(self, document_id: int) -> bool:
        """
        Delete a document and its file.
        
        Args:
            document_id: ID of the document
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            document = self.documents_db.get(document_id)
            if not document:
                return False
            
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            
            self.documents_db.delete(document_id)
            
            logger.info(f"Document {document_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    async def get_expiring_documents(self, days_ahead: int = 30) -> List[ClientDocument]:
        """
        Get documents that are expiring within the specified number of days.
        
        Args:
            days_ahead: Number of days to look ahead for expiring documents
            
        Returns:
            List[ClientDocument]: List of expiring documents
        """
        try:
            all_documents = self.documents_db.get_all()
            expiring_documents = []
            
            cutoff_date = date.today()
            future_date = date.fromordinal(cutoff_date.toordinal() + days_ahead)
            
            for doc in all_documents:
                if doc.expiry_date and cutoff_date <= doc.expiry_date <= future_date:
                    expiring_documents.append(doc)
            
            return expiring_documents
            
        except Exception as e:
            logger.error(f"Error retrieving expiring documents: {str(e)}")
            return []
    
    def _generate_id(self) -> int:
        """Generate a unique ID for documents."""
        existing_docs = self.documents_db.get_all()
        if not existing_docs:
            return 1
        return max(doc.id for doc in existing_docs) + 1

document_service = DocumentService()
