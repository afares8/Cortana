from typing import Dict, Any, Optional
import json
from app.services.ai.utils.intent_classifier import IntentType

class PromptBuilder:
    """
    Builds enhanced prompts for the Mistral model by incorporating context data.
    """
    
    def build_prompt(self, query: str, intent: IntentType, context_data: Dict[str, Any], language: str = "es") -> str:
        """
        Build an enhanced prompt for the Mistral model.
        
        Args:
            query: The original user query
            intent: The classified intent
            context_data: The retrieved context data
            language: The language of the query (default: Spanish)
            
        Returns:
            An enhanced prompt string
        """
        system_instruction = self._get_system_instruction(language)
        
        context_section = self._format_context_data(intent, context_data, language)
        
        user_query = f"Usuario: {query}"
        
        prompt = f"{system_instruction}\n\n{context_section}\n\n{user_query}\n\nAsistente:"
        
        return prompt
    
    def _get_system_instruction(self, language: str = "es") -> str:
        """Get the system instruction based on language."""
        if language == "es":
            return """Eres un asistente legal inteligente para el Departamento Legal de una empresa de perfumería en la Zona Libre de Colón. 
Tu tarea es proporcionar respuestas precisas y útiles basadas en los datos internos de la aplicación.
Debes responder en español, de manera concisa y profesional.
A continuación se te proporcionará información contextual de los sistemas internos para ayudarte a responder.
Utiliza esta información para dar respuestas específicas y relevantes."""
        else:
            return """You are an intelligent legal assistant for the Legal Department of a perfumery business in the Colon Free Zone.
Your task is to provide accurate and helpful responses based on the internal application data.
You should respond in a concise and professional manner.
Contextual information from internal systems will be provided below to help you answer.
Use this information to give specific and relevant responses."""
    
    def _format_context_data(self, intent: IntentType, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format the context data based on intent and language."""
        if intent == IntentType.TASKS:
            return self._format_tasks_context(context_data, language)
        elif intent == IntentType.CONTRACTS:
            return self._format_contracts_context(context_data, language)
        elif intent == IntentType.CLIENTS:
            return self._format_clients_context(context_data, language)
        elif intent == IntentType.COMPLIANCE:
            return self._format_compliance_context(context_data, language)
        elif intent == IntentType.WORKFLOWS:
            return self._format_workflows_context(context_data, language)
        else:
            return self._format_general_context(context_data, language)
    
    def _format_tasks_context(self, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format tasks context data."""
        if "error" in context_data:
            return f"Información de contexto: Error al recuperar datos de tareas: {context_data['error']}"
        
        tasks = context_data.get("tasks", [])
        count = context_data.get("count", 0)
        is_mock = context_data.get("is_mock_data", False)
        
        if language == "es":
            header = f"Información de contexto: Tareas ({count} en total)"
            if is_mock:
                header += " [DATOS DE EJEMPLO]"
            
            if not tasks:
                return f"{header}\nNo se encontraron tareas con los criterios especificados."
            
            tasks_text = "\n".join([
                f"- Tarea #{task['id']}: {task['title']} (Prioridad: {self._translate_priority(task['priority'], 'es')}, " +
                f"Vencimiento: {task['due_date']}, Estado: {self._translate_status(task['status'], 'es')})"
                for task in tasks
            ])
            
            return f"{header}\n{tasks_text}"
        else:
            header = f"Context information: Tasks ({count} total)"
            if is_mock:
                header += " [SAMPLE DATA]"
            
            if not tasks:
                return f"{header}\nNo tasks found matching the specified criteria."
            
            tasks_text = "\n".join([
                f"- Task #{task['id']}: {task['title']} (Priority: {task['priority']}, " +
                f"Due date: {task['due_date']}, Status: {task['status']})"
                for task in tasks
            ])
            
            return f"{header}\n{tasks_text}"
    
    def _format_contracts_context(self, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format contracts context data."""
        if "error" in context_data:
            return f"Información de contexto: Error al recuperar datos de contratos: {context_data['error']}"
        
        contracts = context_data.get("contracts", [])
        count = context_data.get("count", 0)
        is_mock = context_data.get("is_mock_data", False)
        
        if language == "es":
            header = f"Información de contexto: Contratos ({count} en total)"
            if is_mock:
                header += " [DATOS DE EJEMPLO]"
            
            if not contracts:
                return f"{header}\nNo se encontraron contratos con los criterios especificados."
            
            contracts_text = "\n".join([
                f"- Contrato #{contract['id']}: {contract['title']} (Cliente: {contract['client_name']}, " +
                f"Tipo: {self._translate_contract_type(contract['contract_type'], 'es')}, " +
                f"Estado: {self._translate_contract_status(contract['status'], 'es')}, " +
                f"Vencimiento: {contract['expiration_date']})"
                for contract in contracts
            ])
            
            return f"{header}\n{contracts_text}"
        else:
            header = f"Context information: Contracts ({count} total)"
            if is_mock:
                header += " [SAMPLE DATA]"
            
            if not contracts:
                return f"{header}\nNo contracts found matching the specified criteria."
            
            contracts_text = "\n".join([
                f"- Contract #{contract['id']}: {contract['title']} (Client: {contract['client_name']}, " +
                f"Type: {contract['contract_type']}, Status: {contract['status']}, " +
                f"Expiration: {contract['expiration_date']})"
                for contract in contracts
            ])
            
            return f"{header}\n{contracts_text}"
    
    def _format_clients_context(self, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format clients context data."""
        if "error" in context_data:
            return f"Información de contexto: Error al recuperar datos de clientes: {context_data['error']}"
        
        clients = context_data.get("clients", [])
        count = context_data.get("count", 0)
        is_mock = context_data.get("is_mock_data", False)
        
        if language == "es":
            header = f"Información de contexto: Clientes/Proveedores ({count} en total)"
            if is_mock:
                header += " [DATOS DE EJEMPLO]"
            
            if not clients:
                return f"{header}\nNo se encontraron clientes con los criterios especificados."
            
            clients_text = "\n".join([
                f"- {self._translate_client_type(client['type'], 'es')} #{client['id']}: {client['name']} " +
                f"(Contacto: {client['contact_name']}, {client['contact_email']})"
                for client in clients
            ])
            
            return f"{header}\n{clients_text}"
        else:
            header = f"Context information: Clients/Vendors ({count} total)"
            if is_mock:
                header += " [SAMPLE DATA]"
            
            if not clients:
                return f"{header}\nNo clients found matching the specified criteria."
            
            clients_text = "\n".join([
                f"- {client['type'].capitalize()} #{client['id']}: {client['name']} " +
                f"(Contact: {client['contact_name']}, {client['contact_email']})"
                for client in clients
            ])
            
            return f"{header}\n{clients_text}"
    
    def _format_compliance_context(self, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format compliance context data."""
        if "error" in context_data:
            return f"Información de contexto: Error al recuperar datos de cumplimiento: {context_data['error']}"
        
        reports = context_data.get("reports", [])
        count = context_data.get("count", 0)
        dashboard = context_data.get("dashboard")
        is_mock = context_data.get("is_mock_data", False)
        
        if language == "es":
            header = f"Información de contexto: Reportes de Cumplimiento ({count} en total)"
            if is_mock:
                header += " [DATOS DE EJEMPLO]"
            
            if not reports:
                return f"{header}\nNo se encontraron reportes de cumplimiento con los criterios especificados."
            
            reports_text = "\n".join([
                f"- Reporte #{report['id']}: Tipo: {self._translate_report_type(report['report_type'], 'es')}, " +
                f"Entidad: {report['entity_name']}, Estado: {self._translate_report_status(report['status'], 'es')}, " +
                f"Creado: {report['created_at']}"
                for report in reports
            ])
            
            result = f"{header}\n{reports_text}"
            
            if dashboard:
                dashboard_text = self._format_compliance_dashboard(dashboard, language)
                result += f"\n\n{dashboard_text}"
            
            return result
        else:
            header = f"Context information: Compliance Reports ({count} total)"
            if is_mock:
                header += " [SAMPLE DATA]"
            
            if not reports:
                return f"{header}\nNo compliance reports found matching the specified criteria."
            
            reports_text = "\n".join([
                f"- Report #{report['id']}: Type: {report['report_type']}, " +
                f"Entity: {report['entity_name']}, Status: {report['status']}, " +
                f"Created: {report['created_at']}"
                for report in reports
            ])
            
            result = f"{header}\n{reports_text}"
            
            if dashboard:
                dashboard_text = self._format_compliance_dashboard(dashboard, language)
                result += f"\n\n{dashboard_text}"
            
            return result
    
    def _format_compliance_dashboard(self, dashboard: Dict[str, Any], language: str = "es") -> str:
        """Format compliance dashboard data."""
        if language == "es":
            header = "Resumen del Panel de Cumplimiento:"
            
            reports_data = dashboard.get("reports", {})
            screenings_data = dashboard.get("screenings", {})
            
            reports_text = (
                f"Total de reportes: {reports_data.get('total', 0)}\n" +
                f"Pendientes: {reports_data.get('pending', 0)}\n" +
                f"Enviados: {reports_data.get('submitted', 0)}\n" +
                f"Aprobados: {reports_data.get('approved', 0)}\n" +
                f"Rechazados: {reports_data.get('rejected', 0)}"
            )
            
            screenings_text = (
                f"Revisiones PEP: {screenings_data.get('pep', {}).get('total', 0)} " +
                f"(Coincidencias: {screenings_data.get('pep', {}).get('matches', 0)})\n" +
                f"Revisiones de Sanciones: {screenings_data.get('sanctions', {}).get('total', 0)} " +
                f"(Coincidencias: {screenings_data.get('sanctions', {}).get('matches', 0)})"
            )
            
            return f"{header}\n{reports_text}\n\n{screenings_text}"
        else:
            header = "Compliance Dashboard Summary:"
            
            reports_data = dashboard.get("reports", {})
            screenings_data = dashboard.get("screenings", {})
            
            reports_text = (
                f"Total reports: {reports_data.get('total', 0)}\n" +
                f"Pending: {reports_data.get('pending', 0)}\n" +
                f"Submitted: {reports_data.get('submitted', 0)}\n" +
                f"Approved: {reports_data.get('approved', 0)}\n" +
                f"Rejected: {reports_data.get('rejected', 0)}"
            )
            
            screenings_text = (
                f"PEP Screenings: {screenings_data.get('pep', {}).get('total', 0)} " +
                f"(Matches: {screenings_data.get('pep', {}).get('matches', 0)})\n" +
                f"Sanctions Screenings: {screenings_data.get('sanctions', {}).get('total', 0)} " +
                f"(Matches: {screenings_data.get('sanctions', {}).get('matches', 0)})"
            )
            
            return f"{header}\n{reports_text}\n\n{screenings_text}"
    
    def _format_workflows_context(self, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format workflows context data."""
        if "error" in context_data:
            return f"Información de contexto: Error al recuperar datos de flujos de trabajo: {context_data['error']}"
        
        workflows = context_data.get("workflows", [])
        count = context_data.get("count", 0)
        is_mock = context_data.get("is_mock_data", False)
        
        if language == "es":
            header = f"Información de contexto: Flujos de Trabajo ({count} en total)"
            if is_mock:
                header += " [DATOS DE EJEMPLO]"
            
            if not workflows:
                return f"{header}\nNo se encontraron flujos de trabajo con los criterios especificados."
            
            workflows_text = "\n".join([
                f"- Flujo #{workflow['id']}: {workflow['title']} (Tipo: {self._translate_workflow_type(workflow['workflow_type'], 'es')}, " +
                f"Estado: {self._translate_workflow_status(workflow['status'], 'es')}, " +
                f"Etapa actual: {self._translate_workflow_stage(workflow['current_stage'], 'es')})"
                for workflow in workflows
            ])
            
            return f"{header}\n{workflows_text}"
        else:
            header = f"Context information: Workflows ({count} total)"
            if is_mock:
                header += " [SAMPLE DATA]"
            
            if not workflows:
                return f"{header}\nNo workflows found matching the specified criteria."
            
            workflows_text = "\n".join([
                f"- Workflow #{workflow['id']}: {workflow['title']} (Type: {workflow['workflow_type']}, " +
                f"Status: {workflow['status']}, Current stage: {workflow['current_stage']})"
                for workflow in workflows
            ])
            
            return f"{header}\n{workflows_text}"
    
    def _format_general_context(self, context_data: Dict[str, Any], language: str = "es") -> str:
        """Format general context data."""
        if "error" in context_data:
            return f"Información de contexto: Error al recuperar datos: {context_data['error']}"
        
        if "message" in context_data:
            if language == "es":
                return f"Información de contexto: {context_data['message']}"
            else:
                return f"Context information: {context_data['message']}"
        
        return ""
    
    def _translate_priority(self, priority: str, language: str = "es") -> str:
        """Translate priority values to the target language."""
        if language == "es":
            translations = {
                "high": "Alta",
                "medium": "Media",
                "low": "Baja"
            }
            return translations.get(priority.lower(), priority)
        return priority
    
    def _translate_status(self, status: str, language: str = "es") -> str:
        """Translate status values to the target language."""
        if language == "es":
            translations = {
                "pending": "Pendiente",
                "in_progress": "En progreso",
                "completed": "Completado",
                "cancelled": "Cancelado",
                "overdue": "Vencido"
            }
            return translations.get(status.lower(), status)
        return status
    
    def _translate_contract_type(self, contract_type: str, language: str = "es") -> str:
        """Translate contract type values to the target language."""
        if language == "es":
            translations = {
                "lease": "Arrendamiento",
                "service": "Servicio",
                "purchase": "Compra",
                "sale": "Venta",
                "nda": "Confidencialidad",
                "license": "Licencia",
                "employment": "Empleo"
            }
            return translations.get(contract_type.lower(), contract_type)
        return contract_type
    
    def _translate_contract_status(self, status: str, language: str = "es") -> str:
        """Translate contract status values to the target language."""
        if language == "es":
            translations = {
                "active": "Activo",
                "expired": "Vencido",
                "expiring": "Por vencer",
                "terminated": "Terminado",
                "draft": "Borrador",
                "pending_approval": "Pendiente de aprobación"
            }
            return translations.get(status.lower(), status)
        return status
    
    def _translate_client_type(self, client_type: str, language: str = "es") -> str:
        """Translate client type values to the target language."""
        if language == "es":
            translations = {
                "client": "Cliente",
                "vendor": "Proveedor",
                "partner": "Socio",
                "distributor": "Distribuidor"
            }
            return translations.get(client_type.lower(), client_type)
        return client_type
    
    def _translate_report_type(self, report_type: str, language: str = "es") -> str:
        """Translate report type values to the target language."""
        if language == "es":
            translations = {
                "uaf": "UAF",
                "pep": "PEP",
                "sanctions": "Sanciones",
                "audit": "Auditoría",
                "compliance": "Cumplimiento"
            }
            return translations.get(report_type.lower(), report_type)
        return report_type
    
    def _translate_report_status(self, status: str, language: str = "es") -> str:
        """Translate report status values to the target language."""
        if language == "es":
            translations = {
                "pending": "Pendiente",
                "submitted": "Enviado",
                "approved": "Aprobado",
                "rejected": "Rechazado",
                "in_review": "En revisión"
            }
            return translations.get(status.lower(), status)
        return status
    
    def _translate_workflow_type(self, workflow_type: str, language: str = "es") -> str:
        """Translate workflow type values to the target language."""
        if language == "es":
            translations = {
                "contract_approval": "Aprobación de contrato",
                "vendor_review": "Revisión de proveedor",
                "uaf_report_approval": "Aprobación de reporte UAF",
                "document_review": "Revisión de documento",
                "legal_review": "Revisión legal"
            }
            return translations.get(workflow_type.lower(), workflow_type)
        return workflow_type
    
    def _translate_workflow_status(self, status: str, language: str = "es") -> str:
        """Translate workflow status values to the target language."""
        if language == "es":
            translations = {
                "pending": "Pendiente",
                "in_progress": "En progreso",
                "completed": "Completado",
                "cancelled": "Cancelado",
                "on_hold": "En espera"
            }
            return translations.get(status.lower(), status)
        return status
    
    def _translate_workflow_stage(self, stage: str, language: str = "es") -> str:
        """Translate workflow stage values to the target language."""
        if language == "es":
            translations = {
                "legal_review": "Revisión legal",
                "compliance_review": "Revisión de cumplimiento",
                "management_approval": "Aprobación de gerencia",
                "document_preparation": "Preparación de documentos",
                "completed": "Completado"
            }
            return translations.get(stage.lower(), stage)
        return stage

prompt_builder = PromptBuilder()
