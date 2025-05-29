import logging
import json
import aiohttp
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_slack_notification(
    message: str,
    title: Optional[str] = None,
    fields: Optional[Dict[str, Any]] = None,
    color: str = "#36a64f"  # Default to green
) -> bool:
    """
    Send a notification to Slack using the configured webhook URL.
    
    Args:
        message: The main text message
        title: Optional title for the message
        fields: Optional dictionary of field name to value for structured data
        color: Color for the message sidebar (default: green)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not settings.SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured. Notification not sent.")
        return False
        
    try:
        attachment = {
            "color": color,
            "text": message,
            "mrkdwn_in": ["text", "fields"]
        }
        
        if title:
            attachment["title"] = title
            
        if fields:
            attachment["fields"] = [
                {"title": key, "value": value, "short": True}
                for key, value in fields.items()
            ]
            
        payload = {
            "attachments": [attachment]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                settings.SLACK_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info("Slack notification sent successfully")
                    return True
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to send Slack notification. Status: {response.status}, Response: {response_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        return False
