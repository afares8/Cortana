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
from app.modules.admin.permissions.models import Permission, PermissionGroup
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
permissions_db = InMemoryDB[Permission](Permission)
permission_groups_db = InMemoryDB[PermissionGroup](PermissionGroup)
functions_db = InMemoryDB[Function](Function)
ai_profiles_db = InMemoryDB[AIProfile](AIProfile)
admin_audit_logs_db = InMemoryDB[AdminAuditLog](AdminAuditLog)
insights_db = InMemoryDB[ArturInsight](ArturInsight)

def init_db() -> None:
    """Initialize the database with some sample data."""
    if not users_db.get_multi(filters={"email": "admin@example.com"}):
        users_db.create(
            obj_in=UserInDB(
                email="admin@example.com",
                hashed_password=get_password_hash("password"),
                full_name="Admin User",
                is_superuser=True,
            )
        )
        
    from app.modules.admin.departments.services import department_service
    department_service.sync_with_global_db(departments_db)
    
    from app.modules.admin.permissions.services import sync_with_global_db
    sync_with_global_db(permissions_db)
    
    if not permissions_db.get_multi():
        permission_categories = {
            "contract": "Legal contract management permissions",
            "financial": "Financial and accounting permissions",
            "compliance": "Regulatory compliance permissions",
            "logistics": "Logistics and shipping permissions",
            "hr": "Human resources permissions",
            "marketing": "Marketing and content permissions",
            "sales": "Sales and client management permissions",
            "system": "System and IT permissions"
        }
        
        permissions_list = [
            {"id": 1, "name": "create_contract", "description": "Create new legal contracts", "category": "contract"},
            {"id": 2, "name": "approve_contract", "description": "Approve legal contracts", "category": "contract"},
            {"id": 3, "name": "view_all_contracts", "description": "View all contracts in the system", "category": "contract"},
            
            {"id": 4, "name": "create_invoice", "description": "Create new invoices", "category": "financial"},
            {"id": 5, "name": "approve_payment", "description": "Approve financial payments", "category": "financial"},
            {"id": 6, "name": "view_financial_reports", "description": "View financial reports", "category": "financial"},
            
            {"id": 7, "name": "run_compliance_check", "description": "Run compliance verification checks", "category": "compliance"},
            {"id": 8, "name": "approve_policy", "description": "Approve compliance policies", "category": "compliance"},
            {"id": 9, "name": "view_audit_logs", "description": "View system audit logs", "category": "compliance"},
            
            {"id": 10, "name": "create_shipment", "description": "Create new shipments", "category": "logistics"},
            {"id": 11, "name": "approve_invoice", "description": "Approve shipping invoices", "category": "logistics"},
            {"id": 12, "name": "view_logistics_reports", "description": "View logistics reports", "category": "logistics"},
            
            {"id": 13, "name": "create_employee", "description": "Create new employee records", "category": "hr"},
            {"id": 14, "name": "approve_leave", "description": "Approve employee leave requests", "category": "hr"},
            {"id": 15, "name": "view_personnel_records", "description": "View personnel records", "category": "hr"},
            
            {"id": 16, "name": "create_campaign", "description": "Create marketing campaigns", "category": "marketing"},
            {"id": 17, "name": "approve_content", "description": "Approve marketing content", "category": "marketing"},
            {"id": 18, "name": "view_analytics", "description": "View marketing analytics", "category": "marketing"},
            
            {"id": 19, "name": "create_opportunity", "description": "Create sales opportunities", "category": "sales"},
            {"id": 20, "name": "approve_discount", "description": "Approve sales discounts", "category": "sales"},
            {"id": 21, "name": "view_sales_reports", "description": "View sales reports", "category": "sales"},
            
            {"id": 22, "name": "create_user", "description": "Create system users", "category": "system"},
            {"id": 23, "name": "approve_access", "description": "Approve system access requests", "category": "system"},
            {"id": 24, "name": "view_system_logs", "description": "View system logs", "category": "system"}
        ]
        
        for perm_data in permissions_list:
            permissions_db.data[perm_data["id"]] = Permission(**perm_data)
        
        permission_groups_list = [
            {"id": 1, "name": "Contract Management", "permissions": ["create_contract", "approve_contract", "view_all_contracts"]},
            {"id": 2, "name": "Financial Management", "permissions": ["create_invoice", "approve_payment", "view_financial_reports"]},
            {"id": 3, "name": "Compliance Management", "permissions": ["run_compliance_check", "approve_policy", "view_audit_logs"]},
            {"id": 4, "name": "Logistics Management", "permissions": ["create_shipment", "approve_invoice", "view_logistics_reports"]},
            {"id": 5, "name": "HR Management", "permissions": ["create_employee", "approve_leave", "view_personnel_records"]},
            {"id": 6, "name": "Marketing Management", "permissions": ["create_campaign", "approve_content", "view_analytics"]},
            {"id": 7, "name": "Sales Management", "permissions": ["create_opportunity", "approve_discount", "view_sales_reports"]},
            {"id": 8, "name": "System Management", "permissions": ["create_user", "approve_access", "view_system_logs"]}
        ]
        
        for group_data in permission_groups_list:
            permission_groups_db.data[group_data["id"]] = PermissionGroup(**group_data)
    
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
        
        traffic_dept = Department(
            id=4,
            name="Traffic",
            type="traffic",
            ai_enabled=True,
            ai_profile="logistics_assistant",
            country="US",
            timezone="America/New_York",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[traffic_dept.id] = traffic_dept
        
        hr_dept = Department(
            id=5,
            name="HR",
            type="hr",
            ai_enabled=True,
            ai_profile="hr_assistant",
            country="US",
            timezone="America/Chicago",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[hr_dept.id] = hr_dept
        
        marketing_dept = Department(
            id=6,
            name="Marketing",
            type="marketing",
            ai_enabled=True,
            ai_profile="marketing_assistant",
            country="US",
            timezone="America/Los_Angeles",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[marketing_dept.id] = marketing_dept
        
        sales_dept = Department(
            id=7,
            name="Sales",
            type="sales",
            ai_enabled=True,
            ai_profile="sales_assistant",
            country="US",
            timezone="America/Denver",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[sales_dept.id] = sales_dept
        
        it_dept = Department(
            id=8,
            name="IT",
            type="it",
            ai_enabled=True,
            ai_profile="tech_assistant",
            country="US",
            timezone="America/Phoenix",
            company_id=str(uuid.uuid4())
        )
        departments_db.data[it_dept.id] = it_dept
        
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
        
        roles_db.data[4] = Role(
            id=4,
            name="Traffic Manager",
            description="Manages logistics and shipping operations",
            department_id=4,
            permissions=["create_shipment", "approve_invoice", "view_logistics_reports"]
        )
        
        roles_db.data[5] = Role(
            id=5,
            name="HR Manager",
            description="Manages human resources operations",
            department_id=5,
            permissions=["create_employee", "approve_leave", "view_personnel_records"]
        )
        
        roles_db.data[6] = Role(
            id=6,
            name="Marketing Director",
            description="Manages marketing campaigns and strategies",
            department_id=6,
            permissions=["create_campaign", "approve_content", "view_analytics"]
        )
        
        roles_db.data[7] = Role(
            id=7,
            name="Sales Manager",
            description="Manages sales team and client relationships",
            department_id=7,
            permissions=["create_opportunity", "approve_discount", "view_sales_reports"]
        )
        
        roles_db.data[8] = Role(
            id=8,
            name="IT Administrator",
            description="Manages technology infrastructure",
            department_id=8,
            permissions=["create_user", "approve_access", "view_system_logs"]
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
        
        functions_db.data[4] = Function(
            id=4,
            name="Shipment Processing",
            description="Automated shipment documentation and tracking",
            input_schema={"shipment_data": "object", "destination": "string"},
            output_schema={"tracking_id": "string", "estimated_arrival": "date", "documents": "array"},
            department_id=4
        )
        
        functions_db.data[5] = Function(
            id=5,
            name="Employee Onboarding",
            description="Automated employee onboarding workflow",
            input_schema={"employee_data": "object", "position_id": "string"},
            output_schema={"status": "string", "tasks": "array", "completion_date": "date"},
            department_id=5
        )
        
        functions_db.data[6] = Function(
            id=6,
            name="Campaign Analysis",
            description="Automated marketing campaign performance analysis",
            input_schema={"campaign_id": "string", "date_range": "object"},
            output_schema={"performance": "object", "insights": "array", "recommendations": "array"},
            department_id=6
        )
        
        functions_db.data[7] = Function(
            id=7,
            name="Sales Forecasting",
            description="Automated sales prediction and analysis",
            input_schema={"product_id": "string", "period": "string"},
            output_schema={"forecast": "number", "confidence": "number", "factors": "array"},
            department_id=7
        )
        
        functions_db.data[8] = Function(
            id=8,
            name="System Health Check",
            description="Automated IT infrastructure monitoring",
            input_schema={"system_id": "string", "check_type": "string"},
            output_schema={"status": "string", "issues": "array", "recommendations": "array"},
            department_id=8
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
        
        ai_profiles_db.data[4] = AIProfile(
            id=4,
            name="Logistics Assistant",
            model="mistral-7b",
            embedding_id="logistics-embeddings",
            temperature=0.4,
            top_p=0.9,
            context_type="logistics",
            department_id=4
        )
        
        ai_profiles_db.data[5] = AIProfile(
            id=5,
            name="HR Assistant",
            model="mistral-7b",
            embedding_id="hr-embeddings",
            temperature=0.6,
            top_p=0.9,
            context_type="hr",
            department_id=5
        )
        
        ai_profiles_db.data[6] = AIProfile(
            id=6,
            name="Marketing Assistant",
            model="mistral-7b",
            embedding_id="marketing-embeddings",
            temperature=0.7,
            top_p=0.95,
            context_type="marketing",
            department_id=6
        )
        
        ai_profiles_db.data[7] = AIProfile(
            id=7,
            name="Sales Assistant",
            model="mistral-7b",
            embedding_id="sales-embeddings",
            temperature=0.8,
            top_p=0.95,
            context_type="sales",
            department_id=7
        )
        
        ai_profiles_db.data[8] = AIProfile(
            id=8,
            name="IT Assistant",
            model="mistral-7b",
            embedding_id="it-embeddings",
            temperature=0.5,
            top_p=0.9,
            context_type="it",
            department_id=8
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
        
        insights_db.data[4] = ArturInsight(
            id=4,
            category=InsightCategory.FUNCTION_USAGE,
            entity_type=EntityType.FUNCTION,
            entity_id=4,
            department_id=4,
            metrics={
                "total_executions": 22,
                "success_rate": 0.82,
                "error_rate": 0.18
            },
            context={
                "period_days": 30,
                "threshold": 0.3
            },
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        
        insights_db.data[5] = ArturInsight(
            id=5,
            category=InsightCategory.AI_CONSUMPTION,
            entity_type=EntityType.DEPARTMENT,
            entity_id=5,
            department_id=5,
            metrics={
                "prompt_count": 65,
                "response_count": 62,
                "token_count": 28000,
                "days_monitored": 30
            },
            context={
                "period_days": 30,
                "threshold": 5
            },
            created_at=datetime.utcnow() - timedelta(days=4)
        )
        
        insights_db.data[6] = ArturInsight(
            id=6,
            category=InsightCategory.FUNCTION_USAGE,
            entity_type=EntityType.FUNCTION,
            entity_id=6,
            department_id=6,
            metrics={
                "total_executions": 15,
                "success_rate": 0.90,
                "error_rate": 0.10
            },
            context={
                "period_days": 30,
                "threshold": 0.3
            },
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        
        insights_db.data[7] = ArturInsight(
            id=7,
            category=InsightCategory.AI_CONSUMPTION,
            entity_type=EntityType.DEPARTMENT,
            entity_id=7,
            department_id=7,
            metrics={
                "prompt_count": 85,
                "response_count": 82,
                "token_count": 36000,
                "days_monitored": 30
            },
            context={
                "period_days": 30,
                "threshold": 5
            },
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        insights_db.data[8] = ArturInsight(
            id=8,
            category=InsightCategory.FUNCTION_USAGE,
            entity_type=EntityType.FUNCTION,
            entity_id=8,
            department_id=8,
            metrics={
                "total_executions": 30,
                "success_rate": 0.85,
                "error_rate": 0.15
            },
            context={
                "period_days": 30,
                "threshold": 0.3
            },
            created_at=datetime.utcnow() - timedelta(days=3)
        )
