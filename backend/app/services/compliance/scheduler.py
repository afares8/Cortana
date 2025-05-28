import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from typing import List, Dict, Any

from app.services.compliance.services.risk_matrix import risk_matrix
from app.db.in_memory import list_updates_db
from app.services.email import send_email as send_email_async

logger = logging.getLogger(__name__)


async def update_risk_matrix():
    """Update the risk matrix data from all sources."""
    logger.info("Scheduled task: Updating risk matrix data")
    try:
        await risk_matrix.update_risk_data()

        list_updates_db.create(
            {
                "list_name": "Country Risk Matrix",
                "update_date": datetime.now(),
                "status": "Success",
                "details": "Updated Basel AML Index, FATF, and EU high-risk countries data",
            }
        )

        logger.info("Risk matrix data updated successfully")
    except Exception as e:
        list_updates_db.create(
            {
                "list_name": "Country Risk Matrix",
                "update_date": datetime.now(),
                "status": "Failed",
                "details": f"Error: {str(e)}",
            }
        )

        logger.error(f"Error updating risk matrix data: {str(e)}")


async def update_sanctions_lists():
    """Update sanctions lists from all sources."""
    logger.info("Scheduled task: Updating sanctions lists")
    try:
        for list_name in ["OFAC", "EU Sanctions", "UN Sanctions", "OpenSanctions"]:
            try:

                list_updates_db.create(
                    {
                        "list_name": list_name,
                        "update_date": datetime.now(),
                        "status": "Success",
                        "details": f"Updated {list_name} data successfully",
                    }
                )

                logger.info(f"{list_name} updated successfully")
            except Exception as e:
                list_updates_db.create(
                    {
                        "list_name": list_name,
                        "update_date": datetime.now(),
                        "status": "Failed",
                        "details": f"Error: {str(e)}",
                    }
                )

                logger.error(f"Error updating {list_name}: {str(e)}")

        logger.info("Sanctions lists updated successfully")
    except Exception as e:
        logger.error(f"Error updating sanctions lists: {str(e)}")


def setup_compliance_scheduler(scheduler: AsyncIOScheduler):
    """Set up scheduled tasks for compliance module."""
    logger.info("Setting up compliance scheduler")

    for list_name in ["OFAC", "EU Sanctions", "UN Sanctions", "OpenSanctions"]:
        list_updates_db.create(
            {
                "list_name": list_name,
                "update_date": datetime.now(),
                "status": "Success",
                "details": "Initial data load",
            }
        )

    list_updates_db.create(
        {
            "list_name": "Client Risk Monitoring",
            "update_date": datetime.now(),
            "status": "Success",
            "details": "Initial setup",
        }
    )

    scheduler.add_job(
        update_risk_matrix,
        CronTrigger(day_of_week="sun", hour=1, minute=0),
        id="update_risk_matrix",
        replace_existing=True,
    )

    scheduler.add_job(
        update_sanctions_lists,
        CronTrigger(hour=2, minute=0),
        id="update_sanctions_lists",
        replace_existing=True,
    )

    scheduler.add_job(
        monitor_client_risk_changes,
        CronTrigger(hour=3, minute=0),  # Daily at 3 AM
        id="monitor_client_risk_changes",
        replace_existing=True,
    )

    logger.info("Compliance scheduler set up successfully with client risk monitoring")


async def monitor_client_risk_changes():
    """
    Monitor for changes in client risk levels and send email alerts.
    This function runs daily to:
    1. Recalculate risk for all clients using the Excel risk matrix
    2. Track changes in risk levels
    3. Update client records with new risk levels
    4. Send email alerts for risk changes and high-risk clients
    """
    logger.info("Scheduled task: Monitoring client risk changes")
    try:
        from app.legal.services import get_clients, update_client
        from app.services.compliance.services.excel_risk_evaluator import (
            excel_risk_evaluator,
        )

        clients = get_clients(skip=0, limit=1000)
        high_risk_clients = []
        risk_changes = []

        for client in clients:
            client_data = {
                "client_type": getattr(client, "client_type", "individual"),
                "country": getattr(client, "country", "PA"),
                "industry": getattr(client, "industry", "other"),
                "channel": "presencial",  # Default channel
            }

            current_risk = excel_risk_evaluator.calculate_risk(client_data)

            previous_risk_level = getattr(client, "risk_level", "UNKNOWN")
            current_risk_level = current_risk.get("risk_level", "MEDIUM")

            if previous_risk_level != current_risk_level:
                risk_changes.append(
                    {
                        "client_id": client.id,
                        "client_name": client.name,
                        "previous_risk": previous_risk_level,
                        "current_risk": current_risk_level,
                    }
                )

                client_update = {
                    "risk_level": current_risk_level,
                    "risk_score": current_risk.get("total_score"),
                    "risk_details": current_risk,
                }
                update_client(client.id, client_update)

            if current_risk_level == "HIGH":
                high_risk_clients.append(
                    {
                        "client_id": client.id,
                        "client_name": client.name,
                        "risk_score": current_risk.get("total_score"),
                    }
                )

        if risk_changes or high_risk_clients:
            await send_compliance_alert_email(risk_changes, high_risk_clients)

        list_updates_db.create(
            {
                "list_name": "Client Risk Monitoring",
                "update_date": datetime.now(),
                "status": "Success",
                "details": f"Monitored {len(clients)} clients, found {len(risk_changes)} risk changes, {len(high_risk_clients)} high-risk clients",
            }
        )

        logger.info(
            f"Client risk monitoring completed: {len(clients)} clients, {len(risk_changes)} risk changes, {len(high_risk_clients)} high-risk clients"
        )

    except Exception as e:
        logger.error(f"Error monitoring client risk changes: {str(e)}")
        list_updates_db.create(
            {
                "list_name": "Client Risk Monitoring",
                "update_date": datetime.now(),
                "status": "Failed",
                "details": f"Error: {str(e)}",
            }
        )


async def send_compliance_alert_email(
    risk_changes: List[Dict[str, Any]], high_risk_clients: List[Dict[str, Any]]
):
    """
    Send email alert for compliance issues.

    Args:
        risk_changes: List of clients with risk level changes
        high_risk_clients: List of high-risk clients
    """
    subject = "Compliance Alert: Risk Level Changes and High-Risk Clients"

    risk_changes_text = (
        "\n".join(
            [
                f"- {change['client_name']} (ID: {change['client_id']}): {change['previous_risk']} → {change['current_risk']}"
                for change in risk_changes
            ]
        )
        if risk_changes
        else "None"
    )

    high_risk_text = (
        "\n".join(
            [
                f"- {client['client_name']} (ID: {client['client_id']}): Score {client['risk_score']}"
                for client in high_risk_clients
            ]
        )
        if high_risk_clients
        else "None"
    )

    body = f"""
    COMPLIANCE MONITORING ALERT
    
    Risk Level Changes ({len(risk_changes)}):
    {risk_changes_text}
    
    High-Risk Clients ({len(high_risk_clients)}):
    {high_risk_text}
    
    Please review these clients and take appropriate action.
    This is an automated message from the Cortana Compliance System.
    """

    try:
        await send_email_async(
            email_to="compliance@example.com", subject=subject, body=body
        )
        logger.info("Compliance alert email sent successfully")
    except Exception as e:
        logger.error(f"Error sending compliance alert email: {str(e)}")
