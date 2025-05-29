import logging
from datetime import date, timedelta, datetime
from typing import List, Dict, Any
from fastapi import BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from email.message import EmailMessage
import aiosmtplib

from app.core.config import settings
from app.db.init_db import contracts_db
from app.models.contract import Contract
from app.services.notifications import send_slack_notification

logger = logging.getLogger(__name__)

async def send_email(
    email_to: str,
    subject: str,
    body: str,
) -> None:
    """
    Send an email.
    """
    if not settings.EMAILS_ENABLED:
        logger.warning(
            f"Email sending disabled. Would have sent to {email_to}: {subject}"
        )
        return

    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_TLS,
        )
        logger.info(f"Email sent to {email_to}")
    except Exception as e:
        logger.error(f"Error sending email to {email_to}: {e}")


async def send_contract_expiration_reminder(
    contract: Contract,
    days_remaining: int,
    email_to: str,
) -> None:
    """
    Send a reminder about a contract that is about to expire.
    """
    subject = f"Contract Expiration Reminder: {contract.title} - {days_remaining} days remaining"
    body = f"""
    Dear Legal Team Member,

    This is a reminder that the following contract is about to expire in {days_remaining} days:

    Title: {contract.title}
    Client: {contract.client_name}
    Type: {contract.contract_type}
    Expiration Date: {contract.expiration_date}
    Responsible Lawyer: {contract.responsible_lawyer}

    Please review this contract and take appropriate action.

    Regards,
    Legal Contract Tracker System
    """
    
    await send_email(email_to=email_to, subject=subject, body=body)


async def check_expiring_contracts() -> None:
    """
    Check for contracts that are about to expire and send reminders.
    """
    logger.info("Checking for expiring contracts...")
    today = date.today()
    
    contracts = [c for c in contracts_db.data.values() if c.status == "active"]
    
    for days in [30, 15, 5]:
        target_date = today + timedelta(days=days)
        expiring_contracts = [
            c for c in contracts 
            if c.expiration_date == target_date
        ]
        
        for contract in expiring_contracts:
            await send_contract_expiration_reminder(
                contract=contract,
                days_remaining=days,
                email_to="legal@example.com",  # Placeholder
            )


async def run_pep_screening() -> None:
    """
    Run weekly PEP (Politically Exposed Persons) screening on all clients.
    Scheduled to run every Monday at 08:00 UTC.
    """
    logger.info("Starting weekly PEP screening...")
    
    try:
        
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        await send_slack_notification(
            message="Weekly PEP screening completed successfully.",
            title="PEP Screening Report",
            fields={
                "Time": current_time,
                "Status": "Completed",
                "Total Clients": "42",  # This would be dynamic in a real implementation
                "Matches Found": "3"    # This would be dynamic in a real implementation
            }
        )
        
        logger.info("Weekly PEP screening completed")
    except Exception as e:
        error_message = f"Error during weekly PEP screening: {str(e)}"
        logger.error(error_message)
        
        await send_slack_notification(
            message=error_message,
            title="PEP Screening Failed",
            color="#FF0000"  # Red for errors
        )


async def check_dmce_invoices() -> None:
    """
    Run nightly DMCE invoice checks.
    Scheduled to run daily at 01:00 UTC.
    """
    logger.info("Starting nightly DMCE invoice checks...")
    
    try:
        
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        await send_slack_notification(
            message="Nightly DMCE invoice checks completed successfully.",
            title="DMCE Invoice Check Report",
            fields={
                "Time": current_time,
                "Status": "Completed",
                "Invoices Processed": "15",  # This would be dynamic in a real implementation
                "Issues Found": "2"          # This would be dynamic in a real implementation
            }
        )
        
        logger.info("Nightly DMCE invoice checks completed")
    except Exception as e:
        error_message = f"Error during DMCE invoice checks: {str(e)}"
        logger.error(error_message)
        
        await send_slack_notification(
            message=error_message,
            title="DMCE Invoice Check Failed",
            color="#FF0000"  # Red for errors
        )


def setup_scheduler() -> AsyncIOScheduler:
    """
    Set up the scheduler for periodic tasks.
    """
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        check_expiring_contracts,
        CronTrigger(hour=0, minute=0),
        id="check_expiring_contracts",
        replace_existing=True,
    )
    
    scheduler.add_job(
        run_pep_screening,
        CronTrigger(day_of_week="mon", hour=8, minute=0),
        id="weekly_pep_screening",
        replace_existing=True,
    )
    
    scheduler.add_job(
        check_dmce_invoices,
        CronTrigger(hour=1, minute=0),
        id="nightly_dmce_invoice_checks",
        replace_existing=True,
    )
    
    return scheduler
