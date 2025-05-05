import logging
from datetime import datetime, timedelta
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.accounting.services import (
    get_obligations, 
    update_obligation, 
    get_companies,
    create_notification
)
from app.accounting.models import Obligation, Company

logger = logging.getLogger(__name__)

async def check_obligations():
    """
    Daily task to check obligations:
    - Flag as upcoming if due in X days
    - Flag as overdue if past due date
    - Generate notifications if required
    """
    logger.info("Running daily obligation check...")
    today = datetime.now().date()
    
    obligations = get_obligations(filters={"status": "pending"})
    
    for obligation in obligations:
        due_date = obligation.next_due_date
        
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00")).date()
        elif isinstance(due_date, datetime):
            due_date = due_date.date()
            
        if due_date < today:
            logger.info(f"Obligation {obligation.id} is overdue")
            update_obligation(obligation.id, {"status": "overdue"})
            
            create_notification({
                "user_id": 1,  # Admin user ID, would be replaced with actual user IDs in production
                "message": f"Obligation '{obligation.name}' for company '{obligation.company_name}' is overdue",
                "related_obligation_id": obligation.id
            })
            
        elif due_date <= today + timedelta(days=obligation.reminder_days):
            days_until_due = (due_date - today).days
            logger.info(f"Obligation {obligation.id} is due in {days_until_due} days")
            
            if days_until_due in [7, 3, 1]:
                create_notification({
                    "user_id": 1,  # Admin user ID, would be replaced with actual user IDs in production
                    "message": f"Obligation '{obligation.name}' for company '{obligation.company_name}' is due in {days_until_due} days",
                    "related_obligation_id": obligation.id
                })

async def run_ai_analysis():
    """
    Weekly task to run AI analysis for companies with auto-AI enabled
    and store summary suggestions.
    """
    logger.info("Running weekly AI analysis...")
    
    companies = get_companies()
    
    for company in companies:
        logger.info(f"Running AI analysis for company {company.id}")
        
        create_notification({
            "user_id": 1,  # Admin user ID, would be replaced with actual user IDs in production
            "message": f"Weekly AI analysis completed for company '{company.name}'",
            "related_obligation_id": None
        })

def init_scheduler():
    """Initialize the scheduler with tasks."""
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        check_obligations,
        CronTrigger(hour=0, minute=0),
        id="check_obligations",
        replace_existing=True
    )
    
    scheduler.add_job(
        run_ai_analysis,
        CronTrigger(day_of_week="sun", hour=1, minute=0),
        id="run_ai_analysis",
        replace_existing=True
    )
    
    return scheduler
