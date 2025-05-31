from typing import List, Optional, Dict, Any
import logging
from app.services.clients.models.client import Client
from app.services.clients.schemas.client import ClientCreate, ClientUpdate
from app.db.in_memory import InMemoryDB
from app.services.compliance.services.unified_verification_service import unified_verification_service
from app.services.compliance.models.models import CustomerVerifyRequest, Entity

logger = logging.getLogger(__name__)

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
            notes=getattr(legal_client, 'notes', None),
            dob=getattr(legal_client, 'dob', None),
            nationality=getattr(legal_client, 'nationality', None),
            registration_number=getattr(legal_client, 'registration_number', None),
            incorporation_date=getattr(legal_client, 'incorporation_date', None),
            incorporation_country=getattr(legal_client, 'incorporation_country', None),
            directors=getattr(legal_client, 'directors', []),
            ubos=getattr(legal_client, 'ubos', [])
        )
        
        await self._trigger_compliance_verification(client)
        
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
                notes=getattr(legal_client, 'notes', None),
                dob=getattr(legal_client, 'dob', None),
                nationality=getattr(legal_client, 'nationality', None),
                registration_number=getattr(legal_client, 'registration_number', None),
                incorporation_date=getattr(legal_client, 'incorporation_date', None),
                incorporation_country=getattr(legal_client, 'incorporation_country', None),
                directors=getattr(legal_client, 'directors', []),
                ubos=getattr(legal_client, 'ubos', [])
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
            notes=getattr(legal_client, 'notes', None),
            dob=getattr(legal_client, 'dob', None),
            nationality=getattr(legal_client, 'nationality', None),
            registration_number=getattr(legal_client, 'registration_number', None),
            incorporation_date=getattr(legal_client, 'incorporation_date', None),
            incorporation_country=getattr(legal_client, 'incorporation_country', None),
            directors=getattr(legal_client, 'directors', []),
            ubos=getattr(legal_client, 'ubos', [])
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
            notes=getattr(legal_client, 'notes', None),
            dob=getattr(legal_client, 'dob', None),
            nationality=getattr(legal_client, 'nationality', None),
            registration_number=getattr(legal_client, 'registration_number', None),
            incorporation_date=getattr(legal_client, 'incorporation_date', None),
            incorporation_country=getattr(legal_client, 'incorporation_country', None),
            directors=getattr(legal_client, 'directors', []),
            ubos=getattr(legal_client, 'ubos', [])
        )
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Delete a client.
        """
        from app.legal.services import delete_client
        
        return delete_client(client_id)
    
    async def _trigger_compliance_verification(self, client: Client) -> None:
        """
        Trigger compliance verification for a client including directors and UBOs.
        """
        try:
            logger.info(f"Triggering compliance verification for client: {client.name}")
            
            customer_entity = Entity(
                name=client.name,
                country=getattr(client, 'country', ''),
                type='individual' if getattr(client, 'client_type') == 'individual' else 'legal',
                dob=client.dob,
                id_number=getattr(client, 'registration_number', None) or str(client.id)
            )
            
            directors_entities = []
            for director_data in client.directors:
                if isinstance(director_data, dict):
                    director_entity = Entity(
                        name=director_data.get('name', ''),
                        country=director_data.get('country', ''),
                        type='individual',
                        dob=director_data.get('dob')
                    )
                    directors_entities.append(director_entity)
            
            ubos_entities = []
            for ubo_data in client.ubos:
                if isinstance(ubo_data, dict):
                    ubo_entity = Entity(
                        name=ubo_data.get('name', ''),
                        country=ubo_data.get('country', ''),
                        type='individual',
                        dob=ubo_data.get('dob')
                    )
                    ubos_entities.append(ubo_entity)
            
            verification_request = CustomerVerifyRequest(
                customer=customer_entity,
                directors=directors_entities,
                ubos=ubos_entities
            )
            
            verification_result = await unified_verification_service.verify_customer(verification_request)
            
            logger.info(f"Compliance verification completed for client {client.name}. "
                       f"Report ID: {verification_result.get('report', {}).get('id')}")
            
        except Exception as e:
            logger.error(f"Error during compliance verification for client {client.name}: {str(e)}")

client_service = ClientService()
