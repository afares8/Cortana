from datetime import date
from typing import List, Optional, Dict, Any
import os
import shutil
from fastapi import UploadFile, HTTPException

from app.db.init_db import contracts_db
from app.services.contracts.models.contract import Contract, ContractInDB
from app.services.contracts.schemas.contract import ContractCreate, ContractUpdate

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ContractService:
    """
    Service for contract operations.
    """
    
    async def get_contracts(
        self,
        client_name: Optional[str] = None,
        contract_type: Optional[str] = None,
        responsible_lawyer: Optional[str] = None,
        expiration_before: Optional[date] = None,
        expiration_after: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Contract]:
        """
        Get contracts with optional filtering.
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
    
    async def create_contract(
        self,
        contract_data: ContractCreate,
        file: UploadFile,
    ) -> Contract:
        """
        Create a new contract with uploaded file.
        """
        file_path = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        contract = contracts_db.create(
            obj_in=ContractInDB(
                **contract_data.model_dump(),
                file_path=file_path,
            )
        )
        
        return contract
    
    async def get_contract(self, contract_id: int) -> Optional[Contract]:
        """
        Get a specific contract by ID.
        """
        contract = contracts_db.get(contract_id)
        if not contract:
            return None
        return contract
    
    async def update_contract(
        self,
        contract_id: int,
        contract_data: ContractUpdate,
    ) -> Optional[Contract]:
        """
        Update a contract.
        """
        contract = contracts_db.get(contract_id)
        if not contract:
            return None
        
        updated_contract = contracts_db.update(id=contract_id, obj_in=contract_data)
        return updated_contract
    
    async def delete_contract(self, contract_id: int) -> Optional[Contract]:
        """
        Delete a contract.
        """
        contract = contracts_db.remove(id=contract_id)
        if not contract:
            return None
        
        if os.path.exists(contract.file_path):
            os.remove(contract.file_path)
        
        return contract
    
    async def get_dashboard_stats(self) -> Dict[str, int]:
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

contract_service = ContractService()
