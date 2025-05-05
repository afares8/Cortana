from datetime import datetime, timedelta
import logging
from apscheduler.triggers.cron import CronTrigger

from app.accounting.services import (
    obligations_db, 
    get_obligations, 
    update_obligation,
    create_notification,
    get_companies
)
from app.accounting.scheduler import check_obligations, run_ai_analysis, init_scheduler

logger = logging.getLogger(__name__)

async def check_obligation_due_dates():
    """
    Check for obligations that are approaching due date or are overdue and update their status.
    This is the original implementation, kept for backward compatibility.
    The new implementation is in scheduler.py.
    """
    await check_obligations()

def setup_accounting_scheduler(scheduler):
    """
    Set up the scheduler for the accounting module.
    """
    scheduler.add_job(
        check_obligations,
        CronTrigger(hour=0, minute=0),  # Run at midnight
        id="check_obligations",
        replace_existing=True,
    )
    
    scheduler.add_job(
        run_ai_analysis,
        CronTrigger(day_of_week="sun", hour=1, minute=0),  # Run at 1 AM on Sundays
        id="run_ai_analysis",
        replace_existing=True,
    )
    
    logger.info("Accounting scheduler set up with obligation checks and AI analysis")
    return scheduler
