from typing import Dict, Any, List, Optional
import logging
import httpx
from fastapi import HTTPException

from app.services.ai.utils.intent_classifier import IntentType

logger = logging.getLogger(__name__)

class ContextRetriever:
    """
    Retrieves context data from internal services based on the classified intent.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)
    
    async def retrieve_context(self, intent: IntentType, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve context data from the appropriate service based on the intent.
        
        Args:
            intent: The classified intent
            params: Parameters extracted from the query
            user_id: Optional user ID for personalized context
            
        Returns:
            A dictionary containing the retrieved context data
        """
        try:
            if intent == IntentType.TASKS:
                return await self._retrieve_tasks_context(params, user_id)
            elif intent == IntentType.CONTRACTS:
                return await self._retrieve_contracts_context(params, user_id)
            elif intent == IntentType.CLIENTS:
                return await self._retrieve_clients_context(params, user_id)
            elif intent == IntentType.COMPLIANCE:
                return await self._retrieve_compliance_context(params, user_id)
            elif intent == IntentType.WORKFLOWS:
                return await self._retrieve_workflows_context(params, user_id)
            else:
                return {"message": "No specific context data available for this query."}
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return {"error": f"Failed to retrieve context: {str(e)}"}
    
    async def _retrieve_tasks_context(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve tasks context from the Tasks Service."""
        try:
            query_params = {}
            if user_id:
                query_params["assigned_to"] = user_id
            
            if "status" in params:
                query_params["status"] = params["status"]
            else:
                query_params["status"] = "pending"
                
            if "priority" in params:
                query_params["priority"] = params["priority"]
                
            if "timeframe" in params:
                query_params["timeframe"] = params["timeframe"]
            
            response = await self.client.get("/api/v1/tasks", params=query_params)
            response.raise_for_status()
            tasks = response.json()
            
            if not tasks:
                return {"tasks": [], "count": 0, "message": "No tasks found matching the criteria."}
            
            tasks = sorted(tasks, key=lambda x: x.get("due_date", "9999-12-31"))
            
            return {
                "tasks": tasks[:10],  # Limit to 10 tasks for context
                "count": len(tasks),
                "filters_applied": query_params
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error retrieving tasks: {e.response.status_code} - {e.response.text}")
            return self._get_mock_tasks_data(params, user_id)
        except Exception as e:
            logger.error(f"Error retrieving tasks context: {str(e)}")
            return self._get_mock_tasks_data(params, user_id)
    
    async def _retrieve_contracts_context(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve contracts context from the Contracts Service."""
        try:
            query_params = {}
            if "status" in params:
                query_params["status"] = params["status"]
            
            if "type" in params:
                query_params["contract_type"] = params["type"]
            
            response = await self.client.get("/api/v1/contracts", params=query_params)
            response.raise_for_status()
            contracts = response.json()
            
            if not contracts:
                return {"contracts": [], "count": 0, "message": "No contracts found matching the criteria."}
            
            contracts = sorted(contracts, key=lambda x: x.get("expiration_date", "9999-12-31"))
            
            return {
                "contracts": contracts[:10],  # Limit to 10 contracts for context
                "count": len(contracts),
                "filters_applied": query_params
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error retrieving contracts: {e.response.status_code} - {e.response.text}")
            return self._get_mock_contracts_data(params, user_id)
        except Exception as e:
            logger.error(f"Error retrieving contracts context: {str(e)}")
            return self._get_mock_contracts_data(params, user_id)
    
    async def _retrieve_clients_context(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve clients context from the Clients Service."""
        try:
            query_params = {}
            if "status" in params:
                query_params["status"] = params["status"]
            
            if "type" in params:
                query_params["entity_type"] = params["type"]
            
            response = await self.client.get("/api/v1/clients", params=query_params)
            response.raise_for_status()
            clients = response.json()
            
            if not clients:
                return {"clients": [], "count": 0, "message": "No clients found matching the criteria."}
            
            clients = sorted(clients, key=lambda x: x.get("name", ""))
            
            return {
                "clients": clients[:10],  # Limit to 10 clients for context
                "count": len(clients),
                "filters_applied": query_params
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error retrieving clients: {e.response.status_code} - {e.response.text}")
            return self._get_mock_clients_data(params, user_id)
        except Exception as e:
            logger.error(f"Error retrieving clients context: {str(e)}")
            return self._get_mock_clients_data(params, user_id)
    
    async def _retrieve_compliance_context(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve compliance context from the Compliance Service."""
        try:
            query_params = {}
            if "report_type" in params:
                query_params["report_type"] = params["report_type"]
            
            if "status" in params:
                query_params["status"] = params["status"]
            
            response = await self.client.get("/api/v1/compliance/reports", params=query_params)
            response.raise_for_status()
            reports = response.json()
            
            if not reports:
                return {"reports": [], "count": 0, "message": "No compliance reports found matching the criteria."}
            
            reports = sorted(reports, key=lambda x: x.get("created_at", ""), reverse=True)
            
            try:
                dashboard_response = await self.client.get("/api/v1/compliance/dashboard")
                dashboard_response.raise_for_status()
                dashboard_data = dashboard_response.json()
            except Exception:
                dashboard_data = None
            
            return {
                "reports": reports[:10],  # Limit to 10 reports for context
                "count": len(reports),
                "filters_applied": query_params,
                "dashboard": dashboard_data
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error retrieving compliance reports: {e.response.status_code} - {e.response.text}")
            return self._get_mock_compliance_data(params, user_id)
        except Exception as e:
            logger.error(f"Error retrieving compliance context: {str(e)}")
            return self._get_mock_compliance_data(params, user_id)
    
    async def _retrieve_workflows_context(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve workflows context from the Workflows Service."""
        try:
            query_params = {}
            if user_id:
                query_params["user_id"] = user_id
            
            response = await self.client.get("/api/v1/workflows", params=query_params)
            response.raise_for_status()
            workflows = response.json()
            
            if not workflows:
                return {"workflows": [], "count": 0, "message": "No workflows found matching the criteria."}
            
            workflows = sorted(workflows, key=lambda x: (0 if x.get("status") == "pending" else 1, x.get("created_at", "")))
            
            return {
                "workflows": workflows[:10],  # Limit to 10 workflows for context
                "count": len(workflows),
                "filters_applied": query_params
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error retrieving workflows: {e.response.status_code} - {e.response.text}")
            return self._get_mock_workflows_data(params, user_id)
        except Exception as e:
            logger.error(f"Error retrieving workflows context: {str(e)}")
            return self._get_mock_workflows_data(params, user_id)
    
    def _get_mock_tasks_data(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get mock tasks data for development/testing."""
        mock_tasks = [
            {
                "id": 1,
                "title": "Revisión del contrato de arrendamiento con Global Fragrances Ltd.",
                "description": "Revisar términos y condiciones del contrato de arrendamiento para la nueva tienda en Albrook Mall.",
                "status": "pending",
                "priority": "high",
                "assigned_to": 1,
                "due_date": "2025-05-20",
                "created_at": "2025-05-01"
            },
            {
                "id": 2,
                "title": "Envío de recordatorio de NDA a TechStart Inc.",
                "description": "Enviar recordatorio sobre la renovación del acuerdo de confidencialidad que vence el próximo mes.",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1,
                "due_date": "2025-05-15",
                "created_at": "2025-05-02"
            },
            {
                "id": 3,
                "title": "Renovación del acuerdo de licencia con Acme Corp.",
                "description": "Preparar documentación para la renovación del acuerdo de licencia de marca.",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1,
                "due_date": "2025-05-25",
                "created_at": "2025-05-03"
            }
        ]
        
        filtered_tasks = mock_tasks
        if "status" in params:
            filtered_tasks = [task for task in filtered_tasks if task["status"] == params["status"]]
        
        if "priority" in params:
            filtered_tasks = [task for task in filtered_tasks if task["priority"] == params["priority"]]
        
        return {
            "tasks": filtered_tasks,
            "count": len(filtered_tasks),
            "filters_applied": params,
            "is_mock_data": True
        }
    
    def _get_mock_contracts_data(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get mock contracts data for development/testing."""
        mock_contracts = [
            {
                "id": 1,
                "title": "Contrato de Arrendamiento - Albrook Mall",
                "client_id": 2,
                "client_name": "Global Fragrances Ltd.",
                "contract_type": "lease",
                "status": "active",
                "start_date": "2025-01-15",
                "expiration_date": "2026-01-14",
                "responsible_lawyer": "Carlos Mendoza"
            },
            {
                "id": 2,
                "title": "Acuerdo de Confidencialidad",
                "client_id": 3,
                "client_name": "TechStart Inc.",
                "contract_type": "nda",
                "status": "expiring",
                "start_date": "2024-06-10",
                "expiration_date": "2025-06-09",
                "responsible_lawyer": "Maria Rodriguez"
            },
            {
                "id": 3,
                "title": "Licencia de Uso de Marca",
                "client_id": 4,
                "client_name": "Acme Corp.",
                "contract_type": "license",
                "status": "active",
                "start_date": "2024-12-01",
                "expiration_date": "2025-11-30",
                "responsible_lawyer": "Carlos Mendoza"
            }
        ]
        
        filtered_contracts = mock_contracts
        if "status" in params:
            filtered_contracts = [contract for contract in filtered_contracts if contract["status"] == params["status"]]
        
        if "type" in params:
            filtered_contracts = [contract for contract in filtered_contracts if contract["contract_type"] == params["type"]]
        
        return {
            "contracts": filtered_contracts,
            "count": len(filtered_contracts),
            "filters_applied": params,
            "is_mock_data": True
        }
    
    def _get_mock_clients_data(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get mock clients data for development/testing."""
        mock_clients = [
            {
                "id": 1,
                "name": "Zona Libre de Colón",
                "type": "client",
                "status": "active",
                "contact_name": "Juan Perez",
                "contact_email": "jperez@zlc.gob.pa",
                "contact_phone": "+507 123-4567",
                "created_at": "2024-01-10"
            },
            {
                "id": 2,
                "name": "Global Fragrances Ltd.",
                "type": "client",
                "status": "active",
                "contact_name": "Sarah Johnson",
                "contact_email": "sjohnson@globalfragrances.com",
                "contact_phone": "+44 20 1234 5678",
                "created_at": "2024-02-15"
            },
            {
                "id": 3,
                "name": "TechStart Inc.",
                "type": "vendor",
                "status": "active",
                "contact_name": "Miguel Torres",
                "contact_email": "mtorres@techstart.com",
                "contact_phone": "+1 305 987-6543",
                "created_at": "2024-03-20"
            },
            {
                "id": 4,
                "name": "Acme Corp.",
                "type": "client",
                "status": "active",
                "contact_name": "Lisa Wong",
                "contact_email": "lwong@acmecorp.com",
                "contact_phone": "+1 212 555-1234",
                "created_at": "2024-04-05"
            }
        ]
        
        filtered_clients = mock_clients
        if "status" in params:
            filtered_clients = [client for client in filtered_clients if client["status"] == params["status"]]
        
        if "type" in params:
            filtered_clients = [client for client in filtered_clients if client["type"] == params["type"]]
        
        return {
            "clients": filtered_clients,
            "count": len(filtered_clients),
            "filters_applied": params,
            "is_mock_data": True
        }
    
    def _get_mock_compliance_data(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get mock compliance data for development/testing."""
        mock_reports = [
            {
                "id": 1,
                "report_type": "uaf",
                "entity_type": "client",
                "entity_id": 2,
                "entity_name": "Global Fragrances Ltd.",
                "status": "submitted",
                "created_at": "2025-04-15",
                "submitted_at": "2025-04-16",
                "created_by": 1
            },
            {
                "id": 2,
                "report_type": "pep",
                "entity_type": "client",
                "entity_id": 3,
                "entity_name": "TechStart Inc.",
                "status": "pending",
                "created_at": "2025-05-01",
                "submitted_at": None,
                "created_by": 1
            },
            {
                "id": 3,
                "report_type": "sanctions",
                "entity_type": "vendor",
                "entity_id": 5,
                "entity_name": "Distribuidora XYZ",
                "status": "approved",
                "created_at": "2025-04-10",
                "submitted_at": "2025-04-10",
                "approved_at": "2025-04-12",
                "created_by": 1
            }
        ]
        
        filtered_reports = mock_reports
        if "report_type" in params:
            filtered_reports = [report for report in filtered_reports if report["report_type"] == params["report_type"]]
        
        if "status" in params:
            filtered_reports = [report for report in filtered_reports if report["status"] == params["status"]]
        
        mock_dashboard = {
            "reports": {
                "total": 15,
                "pending": 5,
                "submitted": 8,
                "approved": 2,
                "rejected": 0,
                "by_type": {
                    "uaf": 8,
                    "pep": 5,
                    "sanctions": 2
                }
            },
            "screenings": {
                "pep": {
                    "total": 25,
                    "matches": 3,
                    "match_percentage": 12
                },
                "sanctions": {
                    "total": 25,
                    "matches": 1,
                    "match_percentage": 4
                }
            }
        }
        
        return {
            "reports": filtered_reports,
            "count": len(filtered_reports),
            "filters_applied": params,
            "dashboard": mock_dashboard,
            "is_mock_data": True
        }
    
    def _get_mock_workflows_data(self, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get mock workflows data for development/testing."""
        mock_workflows = [
            {
                "id": 1,
                "title": "Aprobación de Contrato - Global Fragrances",
                "workflow_type": "contract_approval",
                "status": "pending",
                "current_stage": "legal_review",
                "entity_type": "contract",
                "entity_id": 1,
                "created_at": "2025-05-01",
                "updated_at": "2025-05-02"
            },
            {
                "id": 2,
                "title": "Revisión de Proveedor - TechStart Inc.",
                "workflow_type": "vendor_review",
                "status": "completed",
                "current_stage": "completed",
                "entity_type": "client",
                "entity_id": 3,
                "created_at": "2025-04-15",
                "updated_at": "2025-04-20",
                "completed_at": "2025-04-20"
            },
            {
                "id": 3,
                "title": "Aprobación de Reporte UAF - Acme Corp.",
                "workflow_type": "uaf_report_approval",
                "status": "pending",
                "current_stage": "compliance_review",
                "entity_type": "report",
                "entity_id": 1,
                "created_at": "2025-05-03",
                "updated_at": "2025-05-03"
            }
        ]
        
        return {
            "workflows": mock_workflows,
            "count": len(mock_workflows),
            "filters_applied": params,
            "is_mock_data": True
        }

context_retriever = ContextRetriever()
