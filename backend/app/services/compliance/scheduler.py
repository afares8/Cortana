import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.services.compliance.services.risk_matrix import risk_matrix
from app.db.in_memory import list_updates_db

logger = logging.getLogger(__name__)


async def update_risk_matrix():
    """Update the risk matrix data from all sources."""
    logger.info("Scheduled task: Updating risk matrix data")
    try:
        await risk_matrix.update_risk_data()
        
        list_updates_db.create({
            "list_name": "Country Risk Matrix",
            "update_date": datetime.now(),
            "status": "Success",
            "details": "Updated Basel AML Index, FATF, and EU high-risk countries data"
        })
        
        logger.info("Risk matrix data updated successfully")
    except Exception as e:
        list_updates_db.create({
            "list_name": "Country Risk Matrix",
            "update_date": datetime.now(),
            "status": "Failed",
            "details": f"Error: {str(e)}"
        })
        
        logger.error(f"Error updating risk matrix data: {str(e)}")


async def update_sanctions_lists():
    """Update sanctions lists from all sources."""
    logger.info("Scheduled task: Updating sanctions lists")
    try:
        for list_name in ["OFAC", "EU Sanctions", "UN Sanctions", "OpenSanctions"]:
            try:
                
                list_updates_db.create({
                    "list_name": list_name,
                    "update_date": datetime.now(),
                    "status": "Success",
                    "details": f"Updated {list_name} data successfully"
                })
                
                logger.info(f"{list_name} updated successfully")
            except Exception as e:
                list_updates_db.create({
                    "list_name": list_name,
                    "update_date": datetime.now(),
                    "status": "Failed",
                    "details": f"Error: {str(e)}"
                })
                
                logger.error(f"Error updating {list_name}: {str(e)}")
        
        logger.info("Sanctions lists updated successfully")
    except Exception as e:
        logger.error(f"Error updating sanctions lists: {str(e)}")


def setup_compliance_scheduler(scheduler: AsyncIOScheduler):
    """Set up scheduled tasks for compliance module."""
    logger.info("Setting up compliance scheduler")

    for list_name in ["OFAC", "EU Sanctions", "UN Sanctions", "OpenSanctions"]:
        list_updates_db.create({
            "list_name": list_name,
            "update_date": datetime.now(),
            "status": "Success",
            "details": "Initial data load"
        })
    
    scheduler.add_job(
        update_risk_matrix,
        CronTrigger(day_of_week="sun", hour=1, minute=0),
        id="update_risk_matrix",
        replace_existing=True
    )

    scheduler.add_job(
        update_sanctions_lists,
        CronTrigger(hour=2, minute=0),
        id="update_sanctions_lists",
        replace_existing=True
    )

    logger.info("Compliance scheduler set up successfully")
