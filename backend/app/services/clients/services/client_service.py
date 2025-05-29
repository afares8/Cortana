from typing import List, Optional, Dict, Any
from app.services.clients.models.client import Client
from app.services.clients.schemas.client import ClientCreate, ClientUpdate
from app.db.in_memory import InMemoryDB

class ClientService:
    """
    Service for client operations using in-memory database.
    """
    
    async def create_client(self, client_data: ClientCreate) -> Client:
        """
        Create a new client with automatic compliance verification.
        """
        from app.legal.services import create_client
        
        client_dict = client_data.model_dump()
        legal_client = create_client(client_dict)
        
        client = Client(
            id=legal_client.id,
            name=legal_client.name,
            contact_email=legal_client.contact_email,
            contact_phone=getattr(legal_client, 'contact_phone', None),
            address=getattr(legal_client, 'address', None),
            industry=getattr(legal_client, 'industry', None),
            kyc_verified=getattr(legal_client, 'kyc_verified', False),
            notes=getattr(legal_client, 'notes', None)
        )
        
        return client
    
    async def get_clients(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Client]:
        """
        Get clients with optional filtering.
        """
        from app.legal.services import get_clients
        
        legal_clients = get_clients(skip=skip, limit=limit, filters=filters or {})
        
        clients = []
        for legal_client in legal_clients:
            client = Client(
                id=legal_client.id,
                name=legal_client.name,
                contact_email=legal_client.contact_email,
                contact_phone=getattr(legal_client, 'contact_phone', None),
                address=getattr(legal_client, 'address', None),
                industry=getattr(legal_client, 'industry', None),
                kyc_verified=getattr(legal_client, 'kyc_verified', False),
                notes=getattr(legal_client, 'notes', None)
            )
            clients.append(client)
        
        return clients
    
    async def get_client(self, client_id: int) -> Optional[Client]:
        """
        Get a client by ID.
        """
        from app.legal.services import get_client
        
        legal_client = get_client(client_id)
        if not legal_client:
            return None
            
        return Client(
            id=legal_client.id,
            name=legal_client.name,
            contact_email=legal_client.contact_email,
            contact_phone=getattr(legal_client, 'contact_phone', None),
            address=getattr(legal_client, 'address', None),
            industry=getattr(legal_client, 'industry', None),
            kyc_verified=getattr(legal_client, 'kyc_verified', False),
            notes=getattr(legal_client, 'notes', None)
        )
    
    async def update_client(
        self,
        client_id: int,
        client_data: ClientUpdate
    ) -> Optional[Client]:
        """
        Update a client.
        """
        from app.legal.services import update_client
        
        update_dict = client_data.model_dump(exclude_unset=True)
        legal_client = update_client(client_id, update_dict)
        
        if not legal_client:
            return None
            
        return Client(
            id=legal_client.id,
            name=legal_client.name,
            contact_email=legal_client.contact_email,
            contact_phone=getattr(legal_client, 'contact_phone', None),
            address=getattr(legal_client, 'address', None),
            industry=getattr(legal_client, 'industry', None),
            kyc_verified=getattr(legal_client, 'kyc_verified', False),
            notes=getattr(legal_client, 'notes', None)
        )
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Delete a client.
        """
        from app.legal.services import delete_client
        
        return delete_client(client_id)

client_service = ClientService()
