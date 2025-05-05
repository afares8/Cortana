from datetime import datetime, timedelta
import logging
from apscheduler.triggers.cron import CronTrigger

from app.accounting.services import obligations_db, get_obligations, update_obligation

logger = logging.getLogger(__name__)

async def check_obligation_due_dates():
    """
    Check for obligations that are approaching due date or are overdue and update their status.
    """
    logger.info("Checking obligation due dates...")
    today = datetime.utcnow().date()
    
    pending_obligations = get_obligations(filters={"status": "pending"})
    
    overdue_count = 0
    for obligation in pending_obligations:
        due_date = obligation.next_due_date.date() if isinstance(obligation.next_due_date, datetime) else obligation.next_due_date
        if due_date < today:
            update_obligation(obligation.id, {"status": "overdue"})
            overdue_count += 1
            
    if overdue_count > 0:
        logger.info(f"Marked {overdue_count} obligations as overdue")
    
    upcoming_count = 0
    for obligation in pending_obligations:
        due_date = obligation.next_due_date.date() if isinstance(obligation.next_due_date, datetime) else obligation.next_due_date
        reminder_date = due_date - timedelta(days=obligation.reminder_days)
        if reminder_date <= today < due_date:
            upcoming_count += 1
            
    if upcoming_count > 0:
        logger.info(f"Found {upcoming_count} upcoming obligations within reminder window")

def setup_accounting_scheduler(scheduler):
    """
    Set up the scheduler for the accounting module.
    """
    scheduler.add_job(
        check_obligation_due_dates,
        CronTrigger(hour=0, minute=0),  # Run at midnight
        id="check_obligation_due_dates",
        replace_existing=True,
    )
    
    logger.info("Accounting scheduler set up")
    return scheduler
