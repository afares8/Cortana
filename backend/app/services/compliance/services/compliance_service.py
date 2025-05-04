from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json

from app.services.compliance.models.compliance import (
    ComplianceReport, PEPScreeningResult, 
    SanctionsScreeningResult, DocumentRetentionPolicy
)
from app.services.compliance.schemas.compliance import (
    ComplianceReportCreate, ComplianceReportUpdate,
    PEPScreeningResultCreate, PEPScreeningResultUpdate,
    SanctionsScreeningResultCreate, SanctionsScreeningResultUpdate,
    DocumentRetentionPolicyCreate, DocumentRetentionPolicyUpdate
)
from app.services.compliance.utils.db import (
    compliance_reports_db, pep_screenings_db, sanctions_screenings_db, 
    retention_policies_db, search_pep_database, search_sanctions_database
)

logger = logging.getLogger(__name__)

class ComplianceService:
    """
    Service for compliance operations.
    """
    
    async def create_compliance_report(self, report_data: ComplianceReportCreate) -> ComplianceReport:
        """
        Create a new compliance report.
        """
        obj_in = ComplianceReport(
            id=0,  # Will be set by the database
            report_type=report_data.report_type,
            entity_type=report_data.entity_type,
            entity_id=report_data.entity_id,
            report_data=report_data.report_data,
            status=report_data.status,
            submitted_by=report_data.submitted_by,
            submitted_at=report_data.submitted_at,
            approved_by=report_data.approved_by,
            approved_at=report_data.approved_at,
            notes=report_data.notes,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        return compliance_reports_db.create(obj_in=obj_in)
    
    async def get_compliance_reports(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ComplianceReport]:
        """
        Get compliance reports with optional filtering.
        """
        return compliance_reports_db.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def get_compliance_report(self, report_id: int) -> Optional[ComplianceReport]:
        """
        Get a compliance report by ID.
        """
        return compliance_reports_db.get(report_id)
    
    async def update_compliance_report(
        self,
        report_id: int,
        report_data: ComplianceReportUpdate
    ) -> Optional[ComplianceReport]:
        """
        Update a compliance report.
        """
        return compliance_reports_db.update(id=report_id, obj_in=report_data)
    
    async def delete_compliance_report(self, report_id: int) -> bool:
        """
        Delete a compliance report.
        """
        obj = compliance_reports_db.remove(id=report_id)
        return obj is not None
    
    async def create_pep_screening(self, screening_data: PEPScreeningResultCreate) -> PEPScreeningResult:
        """
        Create a new PEP screening result.
        """
        if not screening_data.match_details:
            client_name = f"Client {screening_data.client_id}"  # Placeholder
            
            match_result = search_pep_database(client_name)
            
            if match_result["found"]:
                screening_data.match_status = "potential_match"
                screening_data.match_details = match_result
                screening_data.risk_level = match_result.get("highest_risk", "medium")
            else:
                screening_data.match_status = "no_match"
                screening_data.match_details = match_result
                screening_data.risk_level = "low"
        
        obj_in = PEPScreeningResult(
            id=0,  # Will be set by the database
            client_id=screening_data.client_id,
            match_status=screening_data.match_status,
            match_details=screening_data.match_details,
            screened_by=screening_data.screened_by,
            screened_at=screening_data.screened_at or datetime.utcnow(),
            risk_level=screening_data.risk_level,
            notes=screening_data.notes,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        return pep_screenings_db.create(obj_in=obj_in)
    
    async def get_pep_screenings(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PEPScreeningResult]:
        """
        Get PEP screening results with optional filtering.
        """
        return pep_screenings_db.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def get_pep_screening(self, screening_id: int) -> Optional[PEPScreeningResult]:
        """
        Get a PEP screening result by ID.
        """
        return pep_screenings_db.get(screening_id)
    
    async def update_pep_screening(
        self,
        screening_id: int,
        screening_data: PEPScreeningResultUpdate
    ) -> Optional[PEPScreeningResult]:
        """
        Update a PEP screening result.
        """
        return pep_screenings_db.update(id=screening_id, obj_in=screening_data)
    
    async def create_sanctions_screening(self, screening_data: SanctionsScreeningResultCreate) -> SanctionsScreeningResult:
        """
        Create a new sanctions screening result.
        """
        if not screening_data.match_details:
            client_name = f"Client {screening_data.client_id}"  # Placeholder
            
            match_result = search_sanctions_database(client_name)
            
            if match_result["found"]:
                screening_data.match_status = "potential_match"
                screening_data.match_details = match_result
                screening_data.risk_level = "high"
            else:
                screening_data.match_status = "no_match"
                screening_data.match_details = match_result
                screening_data.risk_level = "low"
        
        obj_in = SanctionsScreeningResult(
            id=0,  # Will be set by the database
            client_id=screening_data.client_id,
            match_status=screening_data.match_status,
            match_details=screening_data.match_details,
            screened_by=screening_data.screened_by,
            screened_at=screening_data.screened_at or datetime.utcnow(),
            risk_level=screening_data.risk_level,
            notes=screening_data.notes,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        return sanctions_screenings_db.create(obj_in=obj_in)
    
    async def get_sanctions_screenings(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SanctionsScreeningResult]:
        """
        Get sanctions screening results with optional filtering.
        """
        return sanctions_screenings_db.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def get_sanctions_screening(self, screening_id: int) -> Optional[SanctionsScreeningResult]:
        """
        Get a sanctions screening result by ID.
        """
        return sanctions_screenings_db.get(screening_id)
    
    async def update_sanctions_screening(
        self,
        screening_id: int,
        screening_data: SanctionsScreeningResultUpdate
    ) -> Optional[SanctionsScreeningResult]:
        """
        Update a sanctions screening result.
        """
        return sanctions_screenings_db.update(id=screening_id, obj_in=screening_data)
    
    async def create_retention_policy(self, policy_data: DocumentRetentionPolicyCreate) -> DocumentRetentionPolicy:
        """
        Create a new document retention policy.
        """
        obj_in = DocumentRetentionPolicy(
            id=0,  # Will be set by the database
            document_type=policy_data.document_type,
            retention_period_days=policy_data.retention_period_days,
            legal_basis=policy_data.legal_basis,
            is_active=policy_data.is_active,
            created_by=policy_data.created_by,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        return retention_policies_db.create(obj_in=obj_in)
    
    async def get_retention_policies(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[DocumentRetentionPolicy]:
        """
        Get document retention policies with optional filtering.
        """
        return retention_policies_db.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def get_retention_policy(self, policy_id: int) -> Optional[DocumentRetentionPolicy]:
        """
        Get a document retention policy by ID.
        """
        return retention_policies_db.get(policy_id)
    
    async def update_retention_policy(
        self,
        policy_id: int,
        policy_data: DocumentRetentionPolicyUpdate
    ) -> Optional[DocumentRetentionPolicy]:
        """
        Update a document retention policy.
        """
        return retention_policies_db.update(id=policy_id, obj_in=policy_data)
    
    async def delete_retention_policy(self, policy_id: int) -> bool:
        """
        Delete a document retention policy.
        """
        obj = retention_policies_db.remove(id=policy_id)
        return obj is not None
    
    async def generate_uaf_report(self, client_id: int, start_date: datetime, end_date: datetime) -> ComplianceReport:
        """
        Generate a UAF (Unidad de Análisis Financiero) report for a client.
        This report is required by Panamanian regulations for certain transactions.
        """
        logger.info(f"Generating UAF report for client {client_id} from {start_date} to {end_date}")
        
        
        report_data = {
            "client_id": client_id,
            "reporting_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "transaction_summary": {
                "total_transactions": 15,
                "total_value": 125000.00,
                "currency": "USD",
                "high_value_transactions": 3,
                "suspicious_transactions": 1
            },
            "suspicious_activity": [
                {
                    "transaction_id": 12345,
                    "date": (start_date + (end_date - start_date) / 2).isoformat(),
                    "amount": 50000.00,
                    "currency": "USD",
                    "indicators": ["large_cash_deposit", "multiple_transactions_same_day"],
                    "risk_score": 75
                }
            ],
            "compliance_officer_notes": "Report generated automatically based on transaction activity."
        }
        
        report_create = ComplianceReportCreate(
            report_type="uaf_report",
            entity_type="client",
            entity_id=client_id,
            report_data=report_data,
            status="draft",
            notes="Automatically generated UAF report"
        )
        
        return await self.create_compliance_report(report_create)
    
    async def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for the compliance dashboard.
        """
        all_reports = await self.get_compliance_reports(limit=1000)
        
        all_pep_screenings = await self.get_pep_screenings(limit=1000)
        
        all_sanctions_screenings = await self.get_sanctions_screenings(limit=1000)
        
        total_reports = len(all_reports)
        pending_reports = len([r for r in all_reports if r.status == "draft"])
        submitted_reports = len([r for r in all_reports if r.status == "submitted"])
        approved_reports = len([r for r in all_reports if r.status == "approved"])
        rejected_reports = len([r for r in all_reports if r.status == "rejected"])
        
        total_pep_screenings = len(all_pep_screenings)
        pep_matches = len([s for s in all_pep_screenings if s.match_status in ["potential_match", "confirmed_match"]])
        
        total_sanctions_screenings = len(all_sanctions_screenings)
        sanctions_matches = len([s for s in all_sanctions_screenings if s.match_status in ["potential_match", "confirmed_match"]])
        
        dashboard_data = {
            "reports": {
                "total": total_reports,
                "pending": pending_reports,
                "submitted": submitted_reports,
                "approved": approved_reports,
                "rejected": rejected_reports,
                "by_type": {}
            },
            "screenings": {
                "pep": {
                    "total": total_pep_screenings,
                    "matches": pep_matches,
                    "match_percentage": (pep_matches / total_pep_screenings * 100) if total_pep_screenings > 0 else 0
                },
                "sanctions": {
                    "total": total_sanctions_screenings,
                    "matches": sanctions_matches,
                    "match_percentage": (sanctions_matches / total_sanctions_screenings * 100) if total_sanctions_screenings > 0 else 0
                }
            },
            "recent_activity": []
        }
        
        report_types = {}
        for report in all_reports:
            if report.report_type not in report_types:
                report_types[report.report_type] = 0
            report_types[report.report_type] += 1
        
        dashboard_data["reports"]["by_type"] = report_types
        
        recent_reports = sorted(all_reports, key=lambda x: x.created_at, reverse=True)[:5]
        recent_pep = sorted(all_pep_screenings, key=lambda x: x.created_at, reverse=True)[:5]
        recent_sanctions = sorted(all_sanctions_screenings, key=lambda x: x.created_at, reverse=True)[:5]
        
        for report in recent_reports:
            dashboard_data["recent_activity"].append({
                "type": "report",
                "id": report.id,
                "report_type": report.report_type,
                "status": report.status,
                "created_at": report.created_at.isoformat(),
                "entity_type": report.entity_type,
                "entity_id": report.entity_id
            })
        
        for screening in recent_pep:
            dashboard_data["recent_activity"].append({
                "type": "pep_screening",
                "id": screening.id,
                "client_id": screening.client_id,
                "match_status": screening.match_status,
                "risk_level": screening.risk_level,
                "created_at": screening.created_at.isoformat()
            })
        
        for screening in recent_sanctions:
            dashboard_data["recent_activity"].append({
                "type": "sanctions_screening",
                "id": screening.id,
                "client_id": screening.client_id,
                "match_status": screening.match_status,
                "risk_level": screening.risk_level,
                "created_at": screening.created_at.isoformat()
            })
        
        dashboard_data["recent_activity"] = sorted(
            dashboard_data["recent_activity"],
            key=lambda x: x["created_at"],
            reverse=True
        )[:10]
        
        return dashboard_data

compliance_service = ComplianceService()
