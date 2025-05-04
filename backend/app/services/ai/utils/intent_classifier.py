from typing import Dict, Any, List, Tuple, Optional
import re
from enum import Enum

class IntentType(str, Enum):
    TASKS = "tasks"
    CONTRACTS = "contracts"
    CLIENTS = "clients"
    COMPLIANCE = "compliance"
    WORKFLOWS = "workflows"
    GENERAL = "general"

class IntentClassifier:
    """
    Classifies user queries into intents to determine which service to query for data.
    """
    
    def __init__(self):
        self.intent_keywords = {
            IntentType.TASKS: [
                "tarea", "tareas", "pendiente", "pendientes", "asignado", "asignada", 
                "por hacer", "task", "tasks", "pending", "assigned", "to-do", "todo",
                "actividad", "actividades", "vencimiento", "vence", "deadline"
            ],
            IntentType.CONTRACTS: [
                "contrato", "contratos", "acuerdo", "acuerdos", "documento", "documentos",
                "contract", "contracts", "agreement", "agreements", "document", "documents",
                "vencimiento", "expira", "renovación", "renovar", "expiration", "renew"
            ],
            IntentType.CLIENTS: [
                "cliente", "clientes", "proveedor", "proveedores", "empresa", "empresas",
                "client", "clients", "vendor", "vendors", "company", "companies",
                "contacto", "contactos", "contact", "contacts"
            ],
            IntentType.COMPLIANCE: [
                "cumplimiento", "regulación", "regulaciones", "reporte", "reportes",
                "compliance", "regulation", "regulations", "report", "reports",
                "UAF", "PEP", "sanciones", "sanctions", "screening"
            ],
            IntentType.WORKFLOWS: [
                "flujo", "flujos", "proceso", "procesos", "aprobación", "aprobaciones",
                "workflow", "workflows", "process", "processes", "approval", "approvals",
                "etapa", "etapas", "stage", "stages"
            ],
            IntentType.GENERAL: [
                "ayuda", "help", "información", "information", "explicar", "explain",
                "qué es", "what is", "cómo", "how to", "por qué", "why"
            ]
        }
        
        self.task_patterns = [
            r"(?:mis|tengo|hay)?\s*(?:tareas?|tasks?)\s*(?:pendientes?|pending)?",
            r"(?:que|qué)\s*(?:tengo|hay)\s*(?:pendiente|por hacer)",
            r"(?:cuales|cuáles)\s*(?:son)?\s*(?:mis|las)?\s*(?:tareas?|actividades?)\s*(?:pendientes?|por hacer)?",
            r"(?:show|list|display|ver|mostrar|listar)\s*(?:my|mis|the|las|los)?\s*(?:pending|pendientes?)?\s*(?:tasks?|tareas?)",
            r"(?:what|which|cuáles|cuales)\s*(?:tasks?|tareas?)\s*(?:do)?\s*(?:I|yo)?\s*(?:have|tengo)"
        ]
        
        self.contract_patterns = [
            r"(?:contratos?|contracts?)\s*(?:que|por)?\s*(?:vencen?|expiran?|expiring|expire)",
            r"(?:cuales|cuáles)\s*(?:son)?\s*(?:los|mis|the|my)?\s*(?:contratos?|contracts?)\s*(?:que)?\s*(?:vencen?|expiran?|expiring|expire)",
            r"(?:show|list|display|ver|mostrar|listar)\s*(?:the|los|las)?\s*(?:contratos?|contracts?)",
            r"(?:contratos?|contracts?)\s*(?:con|with)\s*(?:cliente|client|proveedor|vendor)"
        ]
        
        self.client_patterns = [
            r"(?:clientes?|clients?|proveedores?|vendors?)\s*(?:activos?|active|nuevos?|new)",
            r"(?:información|information|datos|data)\s*(?:de|sobre|about|on)\s*(?:cliente|client|proveedor|vendor)",
            r"(?:show|list|display|ver|mostrar|listar)\s*(?:the|los|las)?\s*(?:clientes?|clients?|proveedores?|vendors?)"
        ]
        
        self.compliance_patterns = [
            r"(?:reportes?|reports?)\s*(?:de)?\s*(?:UAF|cumplimiento|compliance)",
            r"(?:screening|revisión)\s*(?:de)?\s*(?:PEP|sanciones|sanctions)",
            r"(?:show|list|display|ver|mostrar|listar)\s*(?:the|los|las)?\s*(?:reportes?|reports?)\s*(?:de)?\s*(?:cumplimiento|compliance)"
        ]
        
        self.workflow_patterns = [
            r"(?:flujos?|workflows?|procesos?|processes?)\s*(?:de)?\s*(?:aprobación|approval)",
            r"(?:estado|status)\s*(?:de|del|of)?\s*(?:flujo|workflow|proceso|process)",
            r"(?:show|list|display|ver|mostrar|listar)\s*(?:the|los|las)?\s*(?:flujos?|workflows?|procesos?|processes?)"
        ]
    
    def classify_intent(self, query: str) -> Tuple[IntentType, float]:
        """
        Classify the intent of a user query.
        
        Args:
            query: The user query to classify
            
        Returns:
            A tuple containing the intent type and confidence score
        """
        normalized_query = query.lower().strip()
        
        for pattern in self.task_patterns:
            if re.search(pattern, normalized_query):
                return IntentType.TASKS, 0.9
                
        for pattern in self.contract_patterns:
            if re.search(pattern, normalized_query):
                return IntentType.CONTRACTS, 0.9
                
        for pattern in self.client_patterns:
            if re.search(pattern, normalized_query):
                return IntentType.CLIENTS, 0.9
                
        for pattern in self.compliance_patterns:
            if re.search(pattern, normalized_query):
                return IntentType.COMPLIANCE, 0.9
                
        for pattern in self.workflow_patterns:
            if re.search(pattern, normalized_query):
                return IntentType.WORKFLOWS, 0.9
        
        intent_scores = {intent: 0 for intent in IntentType}
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in normalized_query:
                    intent_scores[intent] += 1
        
        max_score = max(intent_scores.values())
        if max_score > 0:
            max_intents = [intent for intent, score in intent_scores.items() if score == max_score]
            if len(max_intents) == 1:
                return max_intents[0], min(0.7, 0.3 + (0.1 * max_score))
            else:
                for priority_intent in [IntentType.TASKS, IntentType.CONTRACTS, IntentType.CLIENTS, 
                                       IntentType.COMPLIANCE, IntentType.WORKFLOWS, IntentType.GENERAL]:
                    if priority_intent in max_intents:
                        return priority_intent, min(0.6, 0.3 + (0.1 * max_score))
        
        return IntentType.GENERAL, 0.3
    
    def extract_parameters(self, query: str, intent: IntentType) -> Dict[str, Any]:
        """
        Extract parameters from the query based on the intent.
        
        Args:
            query: The user query
            intent: The classified intent
            
        Returns:
            A dictionary of extracted parameters
        """
        params = {}
        normalized_query = query.lower().strip()
        
        if intent == IntentType.TASKS:
            if any(term in normalized_query for term in ["completado", "completed", "terminado", "finished"]):
                params["status"] = "completed"
            elif any(term in normalized_query for term in ["pendiente", "pending", "por hacer", "to do", "todo"]):
                params["status"] = "pending"
            
            if any(term in normalized_query for term in ["alta", "high", "urgente", "urgent"]):
                params["priority"] = "high"
            elif any(term in normalized_query for term in ["media", "medium", "normal"]):
                params["priority"] = "medium"
            elif any(term in normalized_query for term in ["baja", "low"]):
                params["priority"] = "low"
                
            if any(term in normalized_query for term in ["hoy", "today"]):
                params["timeframe"] = "today"
            elif any(term in normalized_query for term in ["semana", "week"]):
                params["timeframe"] = "week"
            elif any(term in normalized_query for term in ["mes", "month"]):
                params["timeframe"] = "month"
        
        elif intent == IntentType.CONTRACTS:
            if any(term in normalized_query for term in ["activo", "active", "vigente", "current"]):
                params["status"] = "active"
            elif any(term in normalized_query for term in ["vencido", "expired", "terminado", "ended"]):
                params["status"] = "expired"
            elif any(term in normalized_query for term in ["por vencer", "expiring", "próximo", "upcoming"]):
                params["status"] = "expiring"
                
            if any(term in normalized_query for term in ["arrendamiento", "lease", "alquiler", "rental"]):
                params["type"] = "lease"
            elif any(term in normalized_query for term in ["servicio", "service"]):
                params["type"] = "service"
            elif any(term in normalized_query for term in ["compra", "purchase", "venta", "sale"]):
                params["type"] = "purchase"
            elif any(term in normalized_query for term in ["confidencialidad", "confidentiality", "nda"]):
                params["type"] = "nda"
        
        elif intent == IntentType.CLIENTS:
            if any(term in normalized_query for term in ["activo", "active"]):
                params["status"] = "active"
            elif any(term in normalized_query for term in ["inactivo", "inactive"]):
                params["status"] = "inactive"
                
            if any(term in normalized_query for term in ["cliente", "client", "customer"]):
                params["type"] = "client"
            elif any(term in normalized_query for term in ["proveedor", "vendor", "supplier"]):
                params["type"] = "vendor"
        
        elif intent == IntentType.COMPLIANCE:
            if any(term in normalized_query for term in ["uaf", "unidad de análisis financiero"]):
                params["report_type"] = "uaf"
            elif any(term in normalized_query for term in ["pep", "persona expuesta políticamente", "politically exposed person"]):
                params["report_type"] = "pep"
            elif any(term in normalized_query for term in ["sanción", "sancion", "sanction"]):
                params["report_type"] = "sanctions"
                
            if any(term in normalized_query for term in ["pendiente", "pending"]):
                params["status"] = "pending"
            elif any(term in normalized_query for term in ["enviado", "submitted"]):
                params["status"] = "submitted"
            elif any(term in normalized_query for term in ["aprobado", "approved"]):
                params["status"] = "approved"
        
        return params

intent_classifier = IntentClassifier()
