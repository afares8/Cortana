import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.ai.utils.mistral_client import MistralClient
from app.services.traffic.models.traffic import InvoiceRecord, InvoiceItem

logger = logging.getLogger(__name__)

class TrafficAIAnalyzer:
    """
    Utility for analyzing traffic data using Mistral AI.
    """
    
    def __init__(self):
        self.ai_client = MistralClient()
    
    async def analyze_invoice(self, record: InvoiceRecord) -> List[str]:
        """
        Analyze a single invoice record and provide suggestions.
        
        Args:
            record: Invoice record to analyze
            
        Returns:
            List of AI suggestions
        """
        try:
            invoice_data = self._prepare_invoice_data(record)
            
            prompt = self._create_invoice_analysis_prompt(invoice_data)
            
            response = await self.ai_client.generate(prompt)
            
            suggestions = self._parse_ai_suggestions(response)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error analyzing invoice with AI: {str(e)}")
            return ["No se pudieron generar sugerencias debido a un error técnico."]
    
    async def analyze_invoices_batch(self, records: List[InvoiceRecord]) -> Dict[int, List[str]]:
        """
        Analyze multiple invoice records and provide suggestions for each.
        Also identify potential consolidation opportunities.
        
        Args:
            records: List of invoice records to analyze
            
        Returns:
            Dictionary mapping record IDs to lists of suggestions
        """
        try:
            individual_suggestions = {}
            for record in records:
                suggestions = await self.analyze_invoice(record)
                individual_suggestions[record.id] = suggestions
            
            consolidation_suggestions = await self._identify_consolidation_opportunities(records)
            
            for record_id, suggestion in consolidation_suggestions.items():
                if record_id in individual_suggestions:
                    individual_suggestions[record_id].append(suggestion)
                else:
                    individual_suggestions[record_id] = [suggestion]
            
            return individual_suggestions
            
        except Exception as e:
            logger.error(f"Error analyzing invoice batch with AI: {str(e)}")
            return {record.id: ["No se pudieron generar sugerencias debido a un error técnico."] for record in records}
    
    async def _identify_consolidation_opportunities(self, records: List[InvoiceRecord]) -> Dict[int, str]:
        """
        Identify potential consolidation opportunities among multiple records.
        
        Args:
            records: List of invoice records to analyze
            
        Returns:
            Dictionary mapping record IDs to consolidation suggestions
        """
        client_groups = {}
        for record in records:
            key = (record.client_name, record.movement_type)
            if key not in client_groups:
                client_groups[key] = []
            client_groups[key].append(record)
        
        consolidation_suggestions = {}
        for (client_name, movement_type), group in client_groups.items():
            if len(group) > 1:
                invoice_numbers = [r.invoice_number for r in group]
                for record in group:
                    other_invoices = [r.invoice_number for r in group if r.id != record.id]
                    if other_invoices:
                        suggestion = f"Considere consolidar esta factura con {', '.join(other_invoices)} del mismo cliente para reducir el número de declaraciones DMCE."
                        consolidation_suggestions[record.id] = suggestion
        
        return consolidation_suggestions
    
    def _prepare_invoice_data(self, record: InvoiceRecord) -> Dict[str, Any]:
        """
        Prepare invoice data for AI analysis.
        
        Args:
            record: Invoice record to prepare
            
        Returns:
            Dictionary with formatted invoice data
        """
        return {
            "invoice_number": record.invoice_number,
            "invoice_date": record.invoice_date.isoformat() if record.invoice_date else None,
            "client_name": record.client_name,
            "client_id": record.client_id,
            "movement_type": record.movement_type,
            "total_value": record.total_value,
            "total_weight": record.total_weight,
            "items": [
                {
                    "tariff_code": item.tariff_code,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "weight": item.weight,
                    "value": item.value,
                    "volume": item.volume
                }
                for item in record.items
            ]
        }
    
    def _create_invoice_analysis_prompt(self, invoice_data: Dict[str, Any]) -> str:
        """
        Create a prompt for AI analysis of an invoice.
        
        Args:
            invoice_data: Formatted invoice data
            
        Returns:
            Prompt for AI analysis
        """
        items_json = json.dumps(invoice_data["items"], indent=2, ensure_ascii=False)
        
        prompt = f"""
        Analiza la siguiente factura para la Zona Libre de Colón y proporciona sugerencias o identifica posibles problemas:
        
        Factura: {invoice_data["invoice_number"]}
        Cliente: {invoice_data["client_name"]} (ID: {invoice_data["client_id"]})
        Tipo de movimiento: {invoice_data["movement_type"] or "No especificado"}
        Valor total: {invoice_data["total_value"]}
        Peso total: {invoice_data["total_weight"]}
        
        Artículos:
        {items_json}
        
        Por favor, identifica cualquier problema potencial o sugerencia para mejorar esta declaración. 
        Específicamente, verifica:
        1. Si los códigos arancelarios coinciden con las descripciones de los productos
        2. Si hay campos importantes que faltan (como el tipo de movimiento)
        3. Si hay inconsistencias en los valores o pesos
        4. Si hay problemas potenciales para la declaración DMCE
        
        Proporciona sugerencias específicas y claras que ayuden al usuario a mejorar la declaración.
        """
        
        return prompt
    
    def _parse_ai_suggestions(self, ai_response: str) -> List[str]:
        """
        Parse AI response into a list of suggestions.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of formatted suggestions
        """
        cleaned_response = ai_response.replace("Análisis:", "").replace("Sugerencias:", "")
        
        lines = []
        for line in cleaned_response.split("\n"):
            line = line.strip()
            if line:
                if line[0].isdigit() and line[1:3] in [". ", "- ", ") "]:
                    lines.append(line[3:].strip())
                elif line.startswith("- "):
                    lines.append(line[2:].strip())
                elif line.startswith("• "):
                    lines.append(line[2:].strip())
                else:
                    lines.append(line)
        
        suggestions = [line for line in lines if len(line) > 10]
        
        return suggestions[:5]
