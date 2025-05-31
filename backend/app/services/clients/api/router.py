from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, UploadFile, File
from pydantic import EmailStr

from app.services.clients.models.client import Client, ClientDocument
from app.services.clients.schemas.client import ClientCreate, ClientUpdate
from app.services.clients.services.client_service import client_service
from app.services.clients.services.document_service import document_service
from app.utils.ocr import ocr_service

router = APIRouter()

@router.post("/", response_model=Client, status_code=201)
async def create_client_endpoint(client: ClientCreate):
    """Create a new client."""
    return await client_service.create_client(client)

@router.get("/", response_model=List[Client])
async def get_clients_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    industry: Optional[str] = None,
    kyc_verified: Optional[bool] = None
):
    """Get a list of clients with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if industry:
        filters["industry"] = industry
    if kyc_verified is not None:
        filters["kyc_verified"] = kyc_verified
    
    return await client_service.get_clients(skip=skip, limit=limit, filters=filters)

@router.get("/{client_id}", response_model=Client)
async def get_client_endpoint(client_id: int = Path(..., gt=0)):
    """Get a client by ID."""
    client = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=Client)
async def update_client_endpoint(
    client_id: int = Path(..., gt=0),
    client_update: ClientUpdate = Body(...)
):
    """Update a client."""
    client = await client_service.update_client(client_id, client_update)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.delete("/{client_id}", response_model=Dict[str, bool])
async def delete_client_endpoint(client_id: int = Path(..., gt=0)):
    """Delete a client."""
    result = await client_service.delete_client(client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found or has associated contracts")
    return {"success": True}

@router.post("/extract-id", response_model=Dict[str, Any])
async def extract_id_endpoint(file: UploadFile = File(...)):
    """Extract identification data from uploaded document using OCR."""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        result = await ocr_service.extract_id_data(file)
        
        if result["success"]:
            return result["data"]
        else:
            return {
                "name": None,
                "dob": None,
                "id_number": None,
                "error": result.get("error", "OCR processing failed")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@router.post("/{client_id}/documents", response_model=ClientDocument, status_code=201)
async def upload_document_endpoint(
    client_id: int = Path(..., gt=0),
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Type of document (e.g., passport, id_card, incorporation_certificate)"),
    expiry_date: Optional[str] = Query(None, description="Document expiry date in YYYY-MM-DD format")
):
    """Upload a document for a client."""
    from datetime import datetime
    
    client = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    parsed_expiry_date = None
    if expiry_date:
        try:
            parsed_expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry date format. Use YYYY-MM-DD")
    
    return await document_service.upload_document(client_id, file, document_type, parsed_expiry_date)

@router.get("/{client_id}/documents", response_model=List[ClientDocument])
async def get_client_documents_endpoint(client_id: int = Path(..., gt=0)):
    """Get all documents for a specific client."""
    client = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return await document_service.get_client_documents(client_id)

@router.get("/documents/{document_id}", response_model=ClientDocument)
async def get_document_endpoint(document_id: int = Path(..., gt=0)):
    """Get a specific document by ID."""
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/documents/{document_id}/validate", response_model=ClientDocument)
async def validate_document_endpoint(
    document_id: int = Path(..., gt=0),
    is_valid: bool = Body(..., description="Whether the document is valid")
):
    """Mark a document as validated or invalid."""
    document = await document_service.validate_document(document_id, is_valid)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/documents/{document_id}", response_model=Dict[str, bool])
async def delete_document_endpoint(document_id: int = Path(..., gt=0)):
    """Delete a document."""
    result = await document_service.delete_document(document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True}

@router.get("/expiring-documents", response_model=List[ClientDocument])
async def get_expiring_documents_endpoint(
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to look ahead for expiring documents")
):
    """Get documents that are expiring within the specified number of days."""
    return await document_service.get_expiring_documents(days_ahead)
