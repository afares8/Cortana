from app.db.base import InMemoryDB
from app.models.user import UserInDB
from app.models.contract import ContractInDB
from app.models.settings import SystemSettingInDB
from app.models.ai_models import ExtractedClause, RiskScore, ComplianceCheck, AuditLog, AIQuery, ContractAnomaly
from app.core.security import get_password_hash

users_db = InMemoryDB[UserInDB](UserInDB)
contracts_db = InMemoryDB[ContractInDB](ContractInDB)
system_settings_db = InMemoryDB[SystemSettingInDB](SystemSettingInDB)

extracted_clauses_db = InMemoryDB[ExtractedClause](ExtractedClause)
risk_scores_db = InMemoryDB[RiskScore](RiskScore)
compliance_checks_db = InMemoryDB[ComplianceCheck](ComplianceCheck)
audit_logs_db = InMemoryDB[AuditLog](AuditLog)
ai_queries_db = InMemoryDB[AIQuery](AIQuery)
contract_anomalies_db = InMemoryDB[ContractAnomaly](ContractAnomaly)

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
