import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

async def analyze_trends(component: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze historical data to predict future issues for a component.
    
    Args:
        component: Name of the component
        history: Historical diagnostic data for the component
        
    Returns:
        Dict[str, Any]: Prediction results
    """
    try:
        if len(history) < 3:
            return {
                "prediction": "Insufficient historical data for trend analysis",
                "confidence": 0.0,
                "trend": "unknown"
            }
        
        sorted_history = sorted(history, key=lambda x: x.get("timestamp", datetime.min))
        
        status_counts = {"healthy": 0, "warning": 0, "error": 0}
        
        for item in sorted_history:
            status = item.get("status", "unknown")
            if status in status_counts:
                status_counts[status] += 1
        
        deteriorating = False
        latest_statuses = [item.get("status", "unknown") for item in sorted_history[-3:]]
        
        if latest_statuses == ["healthy", "warning", "error"] or \
           latest_statuses == ["healthy", "healthy", "warning"] or \
           latest_statuses == ["warning", "warning", "error"]:
            deteriorating = True
        
        improving = False
        if latest_statuses == ["error", "warning", "healthy"] or \
           latest_statuses == ["warning", "healthy", "healthy"] or \
           latest_statuses == ["error", "error", "warning"]:
            improving = True
        
        latest_status = latest_statuses[-1] if latest_statuses else "unknown"
        
        prediction = ""
        confidence = 0.0
        trend = "stable"
        
        if deteriorating:
            if latest_status == "warning":
                prediction = "Component may experience errors soon based on deteriorating trend"
                confidence = 0.7
                trend = "deteriorating"
            elif latest_status == "error":
                prediction = "Component likely to continue experiencing errors"
                confidence = 0.8
                trend = "critical"
        elif improving:
            if latest_status == "healthy":
                prediction = "Component should remain stable based on improvement trend"
                confidence = 0.8
                trend = "improving"
            elif latest_status == "warning":
                prediction = "Component may recover soon based on improvement trend"
                confidence = 0.6
                trend = "recovering"
        else: # stable
            if latest_status == "healthy":
                prediction = "Component should remain stable"
                confidence = 0.9
                trend = "stable"
            elif latest_status == "warning":
                prediction = "Component may continue to experience warnings"
                confidence = 0.7
                trend = "unstable"
            elif latest_status == "error":
                prediction = "Component likely to continue experiencing errors without intervention"
                confidence = 0.8
                trend = "critical"
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "trend": trend,
            "status_distribution": status_counts,
            "latest_status": latest_status
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trends for component {component}: {e}")
        return {
            "prediction": f"Error analyzing trends: {str(e)}",
            "confidence": 0.0,
            "trend": "unknown",
            "error": str(e)
        }
