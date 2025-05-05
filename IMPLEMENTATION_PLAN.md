# Architecture Refactoring Implementation Plan

## Overview

This document outlines the step-by-step implementation plan for refactoring the LegalContractTracker application into a modular microservice architecture. The plan is designed to minimize disruption to existing functionality while establishing clear service boundaries.

## Phase 1: Service Module Separation

### Step 1: Create Service Module Directory Structure

Create the following directory structure for each service:

```
backend/
  app/
    services/
      contracts/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
      clients/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
      compliance/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
      workflows/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
      tasks/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
      audit/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
      ai/
        api/
        models/
        schemas/
        services/
        utils/
        __init__.py
```

### Step 2: Move Existing Code to Service Modules

Move existing code to the appropriate service modules:

1. **Contracts Service**:
   - Move contract models from `app/models/contract.py` to `app/services/contracts/models/`
   - Move contract schemas from `app/schemas/contract.py` to `app/services/contracts/schemas/`
   - Move contract routers from `app/routers/contracts.py` to `app/services/contracts/api/`
   - Move contract services from `app/legal/services.py` (contract-related functions) to `app/services/contracts/services/`

2. **Clients Service**:
   - Move client models from `app/legal/models.py` to `app/services/clients/models/`
   - Move client schemas from `app/legal/schemas.py` to `app/services/clients/schemas/`
   - Move client routers from `app/legal/routers.py` to `app/services/clients/api/`
   - Move client services from `app/legal/services.py` (client-related functions) to `app/services/clients/services/`

3. **Workflow Service**:
   - Move workflow models from `app/legal/models.py` to `app/services/workflows/models/`
   - Move workflow schemas from `app/legal/schemas.py` to `app/services/workflows/schemas/`
   - Move workflow routers from `app/legal/routers.py` to `app/services/workflows/api/`
   - Move workflow services from `app/legal/services.py` (workflow-related functions) to `app/services/workflows/services/`

4. **Tasks Service**:
   - Move task models from `app/legal/models.py` to `app/services/tasks/models/`
   - Move task schemas from `app/legal/schemas.py` to `app/services/tasks/schemas/`
   - Move task routers from `app/legal/routers.py` to `app/services/tasks/api/`
   - Move task services from `app/legal/services.py` (task-related functions) to `app/services/tasks/services/`

5. **Audit Service**:
   - Move audit models from `app/legal/models.py` to `app/services/audit/models/`
   - Move audit schemas from `app/legal/schemas.py` to `app/services/audit/schemas/`
   - Move audit routers from `app/legal/routers.py` to `app/services/audit/api/`
   - Move audit services from `app/legal/services.py` (audit-related functions) to `app/services/audit/services/`

6. **AI Service**:
   - Move AI models from `app/models/ai_models.py` to `app/services/ai/models/`
   - Move AI schemas from `app/schemas/ai_schemas.py` to `app/services/ai/schemas/`
   - Move AI routers from `app/routers/ai.py` to `app/services/ai/api/`
   - Move AI services from `app/services/ai/` to `app/services/ai/services/`

### Step 3: Create Service Initialization Files

Create `__init__.py` files for each service that expose the service's API:

```python
# app/services/contracts/__init__.py
from app.services.contracts.api.router import router as contracts_router

__all__ = ["contracts_router"]
```

### Step 4: Update Main Application

Update `app/main.py` to use the new service modules:

```python
from app.services.contracts import contracts_router
from app.services.clients import clients_router
from app.services.compliance import compliance_router
from app.services.workflows import workflows_router
from app.services.tasks import tasks_router
from app.services.audit import audit_router
from app.services.ai import ai_router

# Include routers with appropriate prefixes
app.include_router(contracts_router, prefix=f"{settings.API_V1_STR}/contracts", tags=["contracts"])
app.include_router(clients_router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
app.include_router(compliance_router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])
app.include_router(workflows_router, prefix=f"{settings.API_V1_STR}/workflows", tags=["workflows"])
app.include_router(tasks_router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(audit_router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])
app.include_router(ai_router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
```

## Phase 2: API Contract Implementation

### Step 1: Define API Contracts

For each service, define clear API contracts in OpenAPI format:

1. Create API documentation in each service's `api` directory
2. Implement proper request/response models
3. Implement proper error handling

### Step 2: Implement Service Interfaces

For each service, implement a service interface that other services can use:

```python
# app/services/contracts/interface.py
from typing import List, Optional
from app.services.contracts.schemas.contract import Contract, ContractCreate, ContractUpdate

class ContractsServiceInterface:
    async def create_contract(self, contract: ContractCreate) -> Contract:
        ...
    
    async def get_contract(self, contract_id: int) -> Optional[Contract]:
        ...
    
    async def get_contracts(self, skip: int = 0, limit: int = 100) -> List[Contract]:
        ...
    
    async def update_contract(self, contract_id: int, contract: ContractUpdate) -> Optional[Contract]:
        ...
    
    async def delete_contract(self, contract_id: int) -> bool:
        ...
```

### Step 3: Implement Service Dependencies

Update services to use other services through their interfaces:

```python
# app/services/tasks/services/task_service.py
from app.services.contracts.interface import ContractsServiceInterface
from app.services.clients.interface import ClientsServiceInterface

class TaskService:
    def __init__(
        self,
        contracts_service: ContractsServiceInterface,
        clients_service: ClientsServiceInterface
    ):
        self.contracts_service = contracts_service
        self.clients_service = clients_service
    
    async def create_task_for_contract(self, contract_id: int, task_data: dict):
        contract = await self.contracts_service.get_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract with ID {contract_id} not found")
        
        # Create task logic
        ...
```

## Phase 3: Database Isolation

### Step 1: Define Database Models

For each service, define database models in the service's `models` directory:

```python
# app/services/contracts/models/contract.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    # Other fields
    
    client = relationship("Client", back_populates="contracts")
```

### Step 2: Implement Database Migrations

Create database migration scripts for each service:

1. Create a migration directory for each service
2. Implement migration scripts using Alembic
3. Update the migration process to handle service-specific migrations

### Step 3: Implement Data Access Layer

For each service, implement a data access layer:

```python
# app/services/contracts/services/contract_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.contracts.models.contract import Contract
from app.services.contracts.schemas.contract import ContractCreate, ContractUpdate

class ContractRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, contract: ContractCreate) -> Contract:
        db_contract = Contract(**contract.dict())
        self.db.add(db_contract)
        self.db.commit()
        self.db.refresh(db_contract)
        return db_contract
    
    def get(self, contract_id: int) -> Optional[Contract]:
        return self.db.query(Contract).filter(Contract.id == contract_id).first()
    
    def list(self, skip: int = 0, limit: int = 100) -> List[Contract]:
        return self.db.query(Contract).offset(skip).limit(limit).all()
    
    def update(self, contract_id: int, contract: ContractUpdate) -> Optional[Contract]:
        db_contract = self.get(contract_id)
        if db_contract:
            for key, value in contract.dict(exclude_unset=True).items():
                setattr(db_contract, key, value)
            self.db.commit()
            self.db.refresh(db_contract)
        return db_contract
    
    def delete(self, contract_id: int) -> bool:
        db_contract = self.get(contract_id)
        if db_contract:
            self.db.delete(db_contract)
            self.db.commit()
            return True
        return False
```

## Phase 4: Error Handling and Resilience

### Step 1: Implement Error Handling

For each service, implement proper error handling:

1. Define service-specific exceptions
2. Implement exception handlers
3. Implement proper error responses

### Step 2: Implement Resilience Patterns

Implement resilience patterns for service communication:

1. Implement retry logic for service calls
2. Implement circuit breakers for service calls
3. Implement fallback mechanisms for service failures

## Phase 5: Observability and Monitoring

### Step 1: Implement Logging

For each service, implement proper logging:

1. Define service-specific loggers
2. Implement structured logging
3. Implement log correlation

### Step 2: Implement Metrics

For each service, implement metrics collection:

1. Define service-specific metrics
2. Implement metrics collection
3. Implement metrics visualization

### Step 3: Implement Tracing

Implement distributed tracing across services:

1. Implement trace context propagation
2. Implement span creation and annotation
3. Implement trace visualization

## Testing Strategy

### Unit Testing

For each service, implement unit tests:

1. Test service logic
2. Test API endpoints
3. Test data access layer

### Integration Testing

Implement integration tests for service interactions:

1. Test service-to-service communication
2. Test end-to-end workflows
3. Test error handling and resilience

### Performance Testing

Implement performance tests:

1. Test service throughput
2. Test service latency
3. Test service scalability

## Deployment Strategy

### Development Environment

Deploy all services as a monolith for development:

1. Use a single database
2. Use a single API gateway
3. Use a single deployment unit

### Production Environment

Deploy services independently for production:

1. Use separate databases
2. Use an API gateway for routing
3. Use separate deployment units

## Migration Strategy

### Data Migration

Implement data migration scripts:

1. Migrate existing data to the new schema
2. Validate data integrity
3. Implement rollback mechanisms

### API Migration

Implement API versioning:

1. Support both old and new API versions
2. Implement API deprecation strategy
3. Implement API migration documentation
