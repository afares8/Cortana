from app.db.base import InMemoryDB
from app.models.user import UserInDB
from app.models.contract import ContractInDB
from app.models.settings import SystemSettingInDB
from app.models.ai_models import ExtractedClause, RiskScore, ComplianceCheck, AuditLog, AIQuery, ContractAnomaly
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid

from app.modules.admin.departments.models import Department
from app.modules.admin.roles.models import Role
from app.modules.admin.functions.models import Function
from app.modules.ai.models import AIProfile
from app.modules.admin.audit.models import AuditLog as AdminAuditLog, ActionType, TargetType
from app.modules.artur.observation.models import ArturInsight, InsightCategory, EntityType

users_db = InMemoryDB[UserInDB](UserInDB)
contracts_db = InMemoryDB[ContractInDB](ContractInDB)
system_settings_db = InMemoryDB[SystemSettingInDB](SystemSettingInDB)

extracted_clauses_db = InMemoryDB[ExtractedClause](ExtractedClause)
risk_scores_db = InMemoryDB[RiskScore](RiskScore)
compliance_checks_db = InMemoryDB[ComplianceCheck](ComplianceCheck)
audit_logs_db = InMemoryDB[AuditLog](AuditLog)
ai_queries_db = InMemoryDB[AIQuery](AIQuery)
contract_anomalies_db = InMemoryDB[ContractAnomaly](ContractAnomaly)

departments_db = InMemoryDB[Department](Department)
roles_db = InMemoryDB[Role](Role)
functions_db = InMemoryDB[Function](Function)
ai_profiles_db = InMemoryDB[AIProfile](AIProfile)
admin_audit_logs_db = InMemoryDB[AdminAuditLog](AdminAuditLog)
insights_db = InMemoryDB[ArturInsight](ArturInsight)

def init_db() -> None:
    """Initialize the database with some sample data."""
    if not users_db.get_multi(filters={"email": "admin@legalcontracttracker.com"}):
        users_db.create(
            obj_in=UserInDB(
                email="admin@legalcontracttracker.com",
                hashed_password=get_password_hash("admin"),
                full_name="Admin User",
                is_superuser=True,
            )
        )
        
    from app.modules.admin.departments.services import department_service
    department_service.sync_with_global_db(departments_db)
    
    if not departments_db.get_multi():
        legal_dept = Department(
            id=1,
            name="Legal",
            type="legal",
            ai_enabled=True,
            ai_profile="legal_assistant",
            country="US",
            timezone="America/New_York",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[legal_dept.id] = legal_dept
        
        accounting_dept = Department(
            id=2,
            name="Accounting",
            type="accounting",
            ai_enabled=True,
            ai_profile="finance_assistant",
            country="US",
            timezone="America/Chicago",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[accounting_dept.id] = accounting_dept
        
        compliance_dept = Department(
            id=3,
            name="Compliance",
            type="compliance",
            ai_enabled=True,
            ai_profile="compliance_assistant",
            country="US",
            timezone="America/Los_Angeles",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[compliance_dept.id] = compliance_dept
        
        roles_db.data[1] = Role(
            id=1,
            name="Legal Manager",
            description="Manages legal department operations",
            department_id=1,
            permissions=["create_contract", "approve_contract", "view_all_contracts"]
        )
        
        roles_db.data[2] = Role(
            id=2,
            name="Accounting Manager",
            description="Manages accounting department operations",
            department_id=2,
            permissions=["create_invoice", "approve_payment", "view_financial_reports"]
        )
        
        roles_db.data[3] = Role(
            id=3,
            name="Compliance Officer",
            description="Ensures regulatory compliance",
            department_id=3,
            permissions=["run_compliance_check", "approve_policy", "view_audit_logs"]
        )
        
        functions_db.data[1] = Function(
            id=1,
            name="Contract Review",
            description="Automated contract review and analysis",
            input_schema={"contract_text": "string", "priority": "integer"},
            output_schema={"risk_score": "float", "issues": "array", "recommendations": "array"},
            department_id=1
        )
        
        functions_db.data[2] = Function(
            id=2,
            name="Invoice Processing",
            description="Automated invoice processing and validation",
            input_schema={"invoice_data": "object", "vendor_id": "string"},
            output_schema={"valid": "boolean", "errors": "array", "total": "float"},
            department_id=2
        )
        
        functions_db.data[3] = Function(
            id=3,
            name="Compliance Check",
            description="Automated compliance verification",
            input_schema={"document_id": "string", "regulation_codes": "array"},
            output_schema={"compliant": "boolean", "violations": "array", "risk_level": "string"},
            department_id=3
        )
        
        ai_profiles_db.data[1] = AIProfile(
            id=1,
            name="Legal Assistant",
            model="mistral-7b",
            embedding_id="legal-embeddings",
            temperature=0.7,
            top_p=0.95,
            context_type="legal",
            department_id=1
        )
        
        ai_profiles_db.data[2] = AIProfile(
            id=2,
            name="Finance Assistant",
            model="mistral-7b",
            embedding_id="finance-embeddings",
            temperature=0.5,
            top_p=0.9,
            context_type="finance",
            department_id=2
        )
        
        ai_profiles_db.data[3] = AIProfile(
            id=3,
            name="Compliance Assistant",
            model="mistral-7b",
            embedding_id="compliance-embeddings",
            temperature=0.3,
            top_p=0.85,
            context_type="compliance",
            department_id=3
        )
        
        for i in range(1, 50):
            admin_audit_logs_db.data[i] = AdminAuditLog(
                id=i,
                user_id=1,
                action_type=ActionType.FUNCTION_EXECUTION,
                target_type=TargetType.FUNCTION,
                target_id=1 if i % 3 == 0 else (2 if i % 3 == 1 else 3),
                payload={
                    "department_id": 1 if i % 3 == 0 else (2 if i % 3 == 1 else 3),
                    "success": i % 5 != 0,  # 20% failure rate
                    "execution_time": 0.5 + (i % 10) / 10
                },
                success=i % 5 != 0,
                created_at=datetime.utcnow() - timedelta(days=i % 30, hours=i % 24)
            )
        
        for i in range(50, 100):
            admin_audit_logs_db.data[i] = AdminAuditLog(
                id=i,
                user_id=1,
                action_type=ActionType.AI_PROMPT if i % 2 == 0 else ActionType.AI_RESPONSE,
                target_type=TargetType.AI_MODEL,
                target_id=1 if i % 3 == 0 else (2 if i % 3 == 1 else 3),
                payload={
                    "department_id": 1 if i % 3 == 0 else (2 if i % 3 == 1 else 3),
                    "token_count": 100 + (i % 900),
                    "model": "mistral-7b"
                },
                success=True,
                created_at=datetime.utcnow() - timedelta(days=i % 30, hours=i % 24)
            )
        
        insights_db.data[1] = ArturInsight(
            id=1,
            category=InsightCategory.FUNCTION_USAGE,
            entity_type=EntityType.FUNCTION,
            entity_id=1,
            department_id=1,
            metrics={
                "total_executions": 25,
                "success_rate": 0.85,
                "error_rate": 0.15
            },
            context={
                "period_days": 30,
                "threshold": 0.3
            },
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        
        insights_db.data[2] = ArturInsight(
            id=2,
            category=InsightCategory.AI_CONSUMPTION,
            entity_type=EntityType.DEPARTMENT,
            entity_id=1,
            department_id=1,
            metrics={
                "prompt_count": 80,
                "response_count": 78,
                "token_count": 35000,
                "days_monitored": 30
            },
            context={
                "period_days": 30,
                "threshold": 5
            },
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        insights_db.data[3] = ArturInsight(
            id=3,
            category=InsightCategory.FUNCTION_USAGE,
            entity_type=EntityType.FUNCTION,
            entity_id=2,
            department_id=2,
            metrics={
                "total_executions": 18,
                "success_rate": 0.78,
                "error_rate": 0.22
            },
            context={
                "period_days": 30,
                "threshold": 0.3
            },
            created_at=datetime.utcnow() - timedelta(days=3)
        )
