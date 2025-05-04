from datetime import date
from typing import List, Optional, Dict, Any
from fastapi import UploadFile

from app.services.contracts.models.contract import Contract
from app.services.contracts.schemas.contract import ContractCreate, ContractUpdate

class ContractsServiceInterface:
    """
    Interface for contract operations.
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
        pass
    
    async def create_contract(
        self,
        contract_data: ContractCreate,
        file: UploadFile,
    ) -> Contract:
        """
        Create a new contract with uploaded file.
        """
        pass
    
    async def get_contract(self, contract_id: int) -> Optional[Contract]:
        """
        Get a specific contract by ID.
        """
        pass
    
    async def update_contract(
        self,
        contract_id: int,
        contract_data: ContractUpdate,
    ) -> Optional[Contract]:
        """
        Update a contract.
        """
        pass
    
    async def delete_contract(self, contract_id: int) -> Optional[Contract]:
        """
        Delete a contract.
        """
        pass
    
    async def get_dashboard_stats(self) -> Dict[str, int]:
        """
        Get dashboard statistics.
        """
        pass
