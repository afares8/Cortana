from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from pydantic import EmailStr

from app.services.clients.models.client import Client
from app.services.clients.schemas.client import ClientCreate, ClientUpdate
from app.services.clients.services.client_service import client_service

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
