import logging
from typing import Dict, Any, Optional
from uuid import UUID

from app.services.ai.mistral_client import MistralClient
from app.services.ai.spanish_input_pipeline import process_spanish_input
from app.accounting.services import get_company, get_obligation, get_payment

logger = logging.getLogger(__name__)

mistral_client = MistralClient()

async def generate_email_draft(
    company_id: int,
    recipient: str,
    context: str,
    obligation_id: Optional[int] = None,
    payment_id: Optional[int] = None,
    language: str = "es"
) -> Dict[str, Any]:
    """
    Generate an email draft using Mistral AI.
    
    Args:
        company_id: ID of the company
        recipient: Recipient of the email (e.g., "CSS", "DGI", "Municipio")
        context: Context of the email (e.g., "Declaración fuera de tiempo")
        obligation_id: Optional ID of the related obligation
        payment_id: Optional ID of the related payment
        language: Language of the email (default: "es")
        
    Returns:
        Dictionary with the generated email draft
    """
    company = get_company(company_id)
    if not company:
        logger.error(f"Company {company_id} not found")
        return {"error": "Company not found"}
        
    context_info = {
        "company_name": company.name,
        "company_location": company.location,
        "is_zona_libre": company.is_zona_libre,
        "recipient": recipient,
        "context": context
    }
    
    if obligation_id:
        obligation = get_obligation(obligation_id)
        if obligation:
            context_info["obligation_name"] = obligation.name
            context_info["obligation_amount"] = obligation.amount
            context_info["obligation_due_date"] = obligation.next_due_date
                
    if payment_id:
        payment = get_payment(payment_id)
        if payment:
            context_info["payment_amount"] = payment.amount
            context_info["payment_date"] = payment.payment_date
            context_info["payment_receipt"] = payment.receipt_number
                
    prompt = f"""
    Eres un asistente especializado en redactar correos electrónicos profesionales para comunicaciones con entidades gubernamentales en Panamá.
    
    INFORMACIÓN:
    - Empresa: {context_info['company_name']}
    - Ubicación: {context_info['company_location']}
    - Zona Libre: {"Sí" if context_info['is_zona_libre'] else "No"}
    - Destinatario: {context_info['recipient']}
    - Contexto: {context_info['context']}
    """
    
    if "obligation_name" in context_info:
        prompt += f"""
        - Obligación: {context_info['obligation_name']}
        - Monto: ${context_info['obligation_amount']}
        - Fecha de vencimiento: {context_info['obligation_due_date']}
        """
            
    if "payment_amount" in context_info:
        prompt += f"""
        - Monto pagado: ${context_info['payment_amount']}
        - Fecha de pago: {context_info['payment_date']}
        - Número de recibo: {context_info['payment_receipt']}
        """
            
    prompt += f"""
    TAREA:
    Redacta un correo electrónico profesional en español para enviar a {context_info['recipient']} relacionado con "{context_info['context']}".
    
    El correo debe incluir:
    1. Saludo formal
    2. Introducción clara del propósito
    3. Detalles relevantes
    4. Solicitud o acción específica
    5. Despedida formal
    
    Formato del correo:
    - Asunto: [Asunto apropiado]
    - Cuerpo: [Contenido del correo]
    """
    
    if language == "es":
        prompt = process_spanish_input(prompt)
    
    try:
        response = await mistral_client.generate(prompt, temperature=0.7)
        
        lines = response.strip().split('\n')
        subject = ""
        body = ""
        
        for i, line in enumerate(lines):
            if line.startswith("Asunto:"):
                subject = line.replace("Asunto:", "").strip()
                body = "\n".join(lines[i+1:]).replace("Cuerpo:", "").strip()
                break
        
        return {
            "subject": subject,
            "body": body,
            "recipient": recipient,
            "company_id": company_id,
            "is_fallback": getattr(mistral_client, "fallback_mode", False)
        }
        
    except Exception as e:
        logger.error(f"Error generating email draft: {e}")
        
        fallback_subject = f"Comunicación sobre {context} - {company.name}"
        fallback_body = f"""
        Estimados señores de {recipient},
        
        Por medio de la presente, nos comunicamos con ustedes en relación a {context} para la empresa {company.name}.
        
        Agradecemos su atención a este asunto y quedamos a la espera de su respuesta.
        
        Atentamente,
        {company.name}
        """
        
        return {
            "subject": fallback_subject,
            "body": fallback_body,
            "recipient": recipient,
            "company_id": company_id,
            "is_fallback": True,
            "error": str(e)
        }
