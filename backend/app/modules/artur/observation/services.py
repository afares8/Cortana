from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.modules.artur.observation.models import ArturInsight, InsightCategory, EntityType
from app.modules.admin.audit.models import AuditLog, ActionType, TargetType
from app.db.base import InMemoryDB

class ObservationService:
    def __init__(self):
        self.db = InMemoryDB(ArturInsight)
        self.audit_db = InMemoryDB(AuditLog)  # For accessing audit logs
        
    async def create_insight(self, insight_data: Dict[str, Any]) -> ArturInsight:
        """Create a new insight from observation"""
        insight = ArturInsight(**insight_data)
        insight.id = self.db.get_next_id(ArturInsight)
        self.db.add(ArturInsight, insight)
        return insight
        
    async def get_insights(
        self, 
        skip: int = 0, 
        limit: int = 100,
        category: Optional[str] = None,
        entity_type: Optional[str] = None,
        department_id: Optional[int] = None
    ) -> List[ArturInsight]:
        """Get insights with optional filtering"""
        insights = self.db.get_multi()
        
        if category:
            insights = [i for i in insights if i.category == category]
        if entity_type:
            insights = [i for i in insights if i.entity_type == entity_type]
        if department_id:
            insights = [i for i in insights if i.department_id == department_id]
            
        return insights[skip:skip + limit]
    
    async def get_insight_by_id(self, insight_id: int) -> Optional[ArturInsight]:
        """Get a specific insight by ID"""
        return self.db.get_by_id(ArturInsight, insight_id)
    
    async def monitor_function_usage(self, days: int = 30) -> List[ArturInsight]:
        """Monitor function usage patterns and create insights"""
        audit_logs = self.audit_db.get_multi()
        function_logs = [
            log for log in audit_logs 
            if log.action_type == ActionType.FUNCTION_EXECUTION
            and log.created_at >= datetime.utcnow() - timedelta(days=days)
        ]
        
        function_usage = {}
        for log in function_logs:
            key = f"{log.target_id}_{log.payload.get('department_id')}"
            if key not in function_usage:
                function_usage[key] = {
                    "function_id": log.target_id,
                    "department_id": log.payload.get("department_id"),
                    "count": 0,
                    "success_count": 0,
                    "error_count": 0
                }
            
            function_usage[key]["count"] += 1
            if log.success:
                function_usage[key]["success_count"] += 1
            else:
                function_usage[key]["error_count"] += 1
        
        insights = []
        for key, usage in function_usage.items():
            if usage["count"] > 10 and usage["error_count"] / usage["count"] > 0.3:
                insight = await self.create_insight({
                    "category": InsightCategory.FUNCTION_USAGE,
                    "entity_type": EntityType.FUNCTION,
                    "entity_id": usage["function_id"],
                    "department_id": usage["department_id"],
                    "metrics": {
                        "total_executions": usage["count"],
                        "success_rate": usage["success_count"] / usage["count"],
                        "error_rate": usage["error_count"] / usage["count"]
                    },
                    "context": {
                        "period_days": days,
                        "threshold": 0.3
                    }
                })
                insights.append(insight)
                
            if usage["count"] < 3 and days >= 30:
                insight = await self.create_insight({
                    "category": InsightCategory.INACTIVE_ENTITY,
                    "entity_type": EntityType.FUNCTION,
                    "entity_id": usage["function_id"],
                    "department_id": usage["department_id"],
                    "metrics": {
                        "total_executions": usage["count"],
                        "days_monitored": days
                    },
                    "context": {
                        "period_days": days,
                        "threshold": 3
                    }
                })
                insights.append(insight)
                
        return insights
    
    async def monitor_ai_consumption(self, days: int = 30) -> List[ArturInsight]:
        """Monitor AI token consumption patterns and create insights"""
        audit_logs = self.audit_db.get_multi()
        ai_logs = [
            log for log in audit_logs 
            if log.action_type in [ActionType.AI_PROMPT, ActionType.AI_RESPONSE]
            and log.created_at >= datetime.utcnow() - timedelta(days=days)
        ]
        
        ai_usage = {}
        for log in ai_logs:
            dept_id = log.payload.get("department_id")
            if not dept_id:
                continue
                
            if dept_id not in ai_usage:
                ai_usage[dept_id] = {
                    "prompt_count": 0,
                    "response_count": 0,
                    "token_count": 0
                }
            
            if log.action_type == ActionType.AI_PROMPT:
                ai_usage[dept_id]["prompt_count"] += 1
            else:
                ai_usage[dept_id]["response_count"] += 1
                
            tokens = log.payload.get("token_count", 0)
            ai_usage[dept_id]["token_count"] += tokens
        
        insights = []
        for dept_id, usage in ai_usage.items():
            if usage["prompt_count"] < 5 and days >= 30:
                insight = await self.create_insight({
                    "category": InsightCategory.AI_CONSUMPTION,
                    "entity_type": EntityType.DEPARTMENT,
                    "entity_id": dept_id,
                    "department_id": dept_id,
                    "metrics": {
                        "prompt_count": usage["prompt_count"],
                        "response_count": usage["response_count"],
                        "token_count": usage["token_count"],
                        "days_monitored": days
                    },
                    "context": {
                        "period_days": days,
                        "threshold": 5
                    }
                })
                insights.append(insight)
                
        return insights
    
    async def run_all_monitors(self) -> List[ArturInsight]:
        """Run all monitoring functions and return combined insights"""
        insights = []
        
        function_insights = await self.monitor_function_usage()
        insights.extend(function_insights)
        
        ai_insights = await self.monitor_ai_consumption()
        insights.extend(ai_insights)
        
        
        return insights

observation_service = ObservationService()
