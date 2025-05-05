def get_upcoming_obligations(days: int = None) -> List[Obligation]:
    """Get obligations that are due within the specified number of days."""
    today = datetime.utcnow().date()
    obligations = get_obligations(filters={"status": "pending"})
    
    upcoming = []
    for obligation in obligations:
        due_date = obligation.next_due_date.date() if isinstance(obligation.next_due_date, datetime) else obligation.next_due_date
        reminder_date = due_date - timedelta(days=obligation.reminder_days if days is None else days)
        if reminder_date <= today < due_date:
            upcoming.append(obligation)
    
    return upcoming

def get_overdue_obligations() -> List[Obligation]:
    """Get obligations that are overdue."""
    return get_obligations(filters={"status": "overdue"})

async def get_obligation_history(company_id: int, months: int = 6) -> Dict[str, Any]:
    """Get obligation and payment history for a company."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    company = get_company(company_id)
    if not company:
        return {"error": "Company not found"}
    
    company_obligations = get_obligations(filters={"company_id": company_id})
    
    obligation_ids = [o.id for o in company_obligations]
    all_payments = []
    for obligation_id in obligation_ids:
        payments = get_payments(filters={"obligation_id": obligation_id})
        payments = [p for p in payments if p.payment_date >= start_date]
        all_payments.extend(payments)
    
    result = {
        "company": company.dict(),
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "months": months
        },
        "obligations": [o.dict() for o in company_obligations],
        "payments": [p.dict() for p in all_payments]
    }
    
    return result

async def analyze_obligation_history(company_id: int, months: int = 6, language: str = "es") -> Dict[str, Any]:
    """Analyze obligation and payment history using Mistral AI."""
    from app.services.ai.mistral_client import mistral_client
    
    history = await get_obligation_history(company_id, months)
    
    if "error" in history:
        return history
    
    company = history["company"]
    
    if language.lower() == "es":
        prompt = f"""
        Eres un asistente contable. Aquí tienes el historial de obligaciones y pagos de la empresa {company['name']} en los últimos {months} meses:
        
        Información de la empresa:
        Nombre: {company['name']}
        Ubicación: {company['location']}
        Zona Libre: {"Sí" if company['is_zona_libre'] else "No"}
        
        Obligaciones fiscales:
        """
        
        for obligation in history["obligations"]:
            prompt += f"""
            - {obligation['name']} ({obligation['frequency']})
              Estado: {obligation['status']}
              Próximo vencimiento: {obligation['next_due_date']}
            """
        
        prompt += """
        
        Pagos realizados:
        """
        
        for payment in history["payments"]:
            prompt += f"""
            - Obligación ID: {payment['obligation_id']}
              Monto: ${payment['amount']}
              Fecha: {payment['payment_date']}
            """
        
        prompt += """
        
        Analiza la información anterior y responde:
        1. ¿Hay obligaciones vencidas o próximas a vencer que requieran atención inmediata?
        2. ¿Identificas alguna anomalía en los montos o frecuencia de pagos?
        3. ¿Qué recomendaciones darías para mejorar el cumplimiento fiscal?
        """
    else:
        prompt = f"""
        You are an accounting assistant. Here is the obligation and payment history for the company {company['name']} for the last {months} months:
        
        Company Information:
        Name: {company['name']}
        Location: {company['location']}
        Free Zone: {"Yes" if company['is_zona_libre'] else "No"}
        
        Tax Obligations:
        """
        
        for obligation in history["obligations"]:
            prompt += f"""
            - {obligation['name']} ({obligation['frequency']})
              Status: {obligation['status']}
              Next due date: {obligation['next_due_date']}
            """
        
        prompt += """
        
        Payments made:
        """
        
        for payment in history["payments"]:
            prompt += f"""
            - Obligation ID: {payment['obligation_id']}
              Amount: ${payment['amount']}
              Date: {payment['payment_date']}
            """
        
        prompt += """
        
        Analyze the information above and answer:
        1. Are there any overdue or upcoming obligations that require immediate attention?
        2. Do you identify any anomalies in the amounts or frequency of payments?
        3. What recommendations would you give to improve tax compliance?
        """
    
    try:
        analysis = await mistral_client.generate(prompt)
        return {
            "company_id": company_id,
            "analysis": analysis,
            "language": language,
            "prompt": prompt
        }
    except Exception as e:
        return {
            "company_id": company_id,
            "error": str(e),
            "language": language
        }
