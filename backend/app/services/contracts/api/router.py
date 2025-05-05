from datetime import date
from typing import Any, List, Optional
import os
import shutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from pydantic import EmailStr

from app.auth.token import get_current_active_user
from app.db.init_db import contracts_db
from app.models.user import User
from app.services.contracts.models.contract import Contract, ContractInDB
from app.services.contracts.schemas.contract import ContractCreate, ContractUpdate

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=List[Contract])
async def get_contracts(
    client_name: Optional[str] = None,
    contract_type: Optional[str] = None,
    responsible_lawyer: Optional[str] = None,
    expiration_before: Optional[date] = None,
    expiration_after: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve contracts with optional filtering.
    """
    contracts = list(contracts_db.data.values())
    
    if client_name:
        contracts = [c for c in contracts if client_name.lower() in c.client_name.lower()]
    
    if contract_type:
        contracts = [c for c in contracts if contract_type.lower() in c.contract_type.lower()]
    
    if responsible_lawyer:
        contracts = [c for c in contracts if responsible_lawyer.lower() in c.responsible_lawyer.lower()]
    
    if expiration_before:
        contracts = [c for c in contracts if c.expiration_date <= expiration_before]
    
    if expiration_after:
        contracts = [c for c in contracts if c.expiration_date >= expiration_after]
    
    if status:
        contracts = [c for c in contracts if c.status == status]
    
    return contracts[skip : skip + limit]


@router.post("/", response_model=Contract)
async def create_contract(
    title: str = Form(...),
    client_name: str = Form(...),
    contract_type: str = Form(...),
    start_date: date = Form(...),
    expiration_date: date = Form(...),
    responsible_lawyer: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
) -> Any:
    """
    Create new contract with uploaded file.
    """
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    contract_in = ContractCreate(
        title=title,
        client_name=client_name,
        contract_type=contract_type,
        start_date=start_date,
        expiration_date=expiration_date,
        responsible_lawyer=responsible_lawyer,
        description=description,
    )
    
    contract = contracts_db.create(
        obj_in=ContractInDB(
            **contract_in.model_dump(),
            file_path=file_path,
        )
    )
    
    return contract


@router.get("/{contract_id}", response_model=Contract)
async def get_contract(
    contract_id: int,
) -> Any:
    """
    Get a specific contract by ID.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.put("/{contract_id}", response_model=Contract)
async def update_contract(
    contract_id: int,
    contract_in: ContractUpdate,
) -> Any:
    """
    Update a contract.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    updated_contract = contracts_db.update(id=contract_id, obj_in=contract_in)
    return updated_contract


@router.delete("/{contract_id}", response_model=Contract)
async def delete_contract(
    contract_id: int,
) -> Any:
    """
    Delete a contract.
    """
    contract = contracts_db.remove(id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if os.path.exists(contract.file_path):
        os.remove(contract.file_path)
    
    return contract


@router.get("/dashboard/stats")
async def get_dashboard_stats() -> Any:
    """
    Get dashboard statistics.
    """
    contracts = list(contracts_db.data.values())
    today = date.today()
    
    active_contracts = [c for c in contracts if c.status == "active"]
    
    expiring_soon = [
        c for c in active_contracts 
        if (c.expiration_date - today).days <= 30 and (c.expiration_date - today).days > 0
    ]
    
    overdue_contracts = [
        c for c in active_contracts 
        if c.expiration_date < today
    ]
    
    return {
        "total_active_contracts": len(active_contracts),
        "contracts_expiring_soon": len(expiring_soon),
        "overdue_contracts": len(overdue_contracts),
        "total_contracts": len(contracts),
    }
