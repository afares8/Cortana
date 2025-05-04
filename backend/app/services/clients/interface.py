from typing import List, Optional, Dict, Any
from app.services.clients.models.client import Client
from app.services.clients.schemas.client import ClientCreate, ClientUpdate

class ClientsServiceInterface:
    """
    Interface for client operations.
    """
    
    async def create_client(self, client_data: ClientCreate) -> Client:
        """
        Create a new client.
        """
        pass
    
    async def get_clients(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Client]:
        """
        Get clients with optional filtering.
        """
        pass
    
    async def get_client(self, client_id: int) -> Optional[Client]:
        """
        Get a client by ID.
        """
        pass
    
    async def update_client(
        self,
        client_id: int,
        client_data: ClientUpdate
    ) -> Optional[Client]:
        """
        Update a client.
        """
        pass
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Delete a client.
        """
        pass
