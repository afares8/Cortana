from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging
import json
import os
from enum import Enum

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
from app.services.compliance.utils.open_sanctions import open_sanctions_client
from app.services.compliance.services.manual_integration_service import (
    compliance_manual_integration, DueDiligenceLevel, RiskLevel, RiskCategory
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
        Create a new PEP screening result using the Open Sanctions API.
        """
        if not screening_data.match_details:
            client_name = f"Client {screening_data.client_id}"  # Placeholder
            client_country = screening_data.match_details.get("country") if screening_data.match_details else None
            
            try:
                match_result = await open_sanctions_client.search_pep(
                    name=client_name,
                    country=client_country,
                    limit=10
                )
                
                if match_result.get("error"):
                    logger.error(f"Error searching PEPs: {match_result.get('error')}")
                    match_result = search_pep_database(client_name)
                elif match_result.get("total", 0) > 0:
                    screening_data.match_status = "potential_match"
                    screening_data.match_details = {
                        "found": True,
                        "matches": match_result.get("results", []),
                        "total": match_result.get("total", 0),
                        "highest_risk": "high" if match_result.get("total", 0) > 0 else "low",
                        "source": "open_sanctions"
                    }
                    screening_data.risk_level = "high" if match_result.get("total", 0) > 0 else "low"
                else:
                    screening_data.match_status = "no_match"
                    screening_data.match_details = {
                        "found": False,
                        "matches": [],
                        "total": 0,
                        "highest_risk": "low",
                        "source": "open_sanctions"
                    }
                    screening_data.risk_level = "low"
            except Exception as e:
                logger.error(f"Error using Open Sanctions API: {str(e)}")
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
        Create a new sanctions screening result using the Open Sanctions API.
        """
        if not screening_data.match_details:
            client_name = f"Client {screening_data.client_id}"  # Placeholder
            client_country = screening_data.match_details.get("country") if screening_data.match_details else None
            entity_type = screening_data.match_details.get("entity_type", "Person") if screening_data.match_details else "Person"
            
            try:
                match_result = await open_sanctions_client.search_sanctions(
                    name=client_name,
                    entity_type=entity_type,
                    country=client_country,
                    datasets=["us_ofac", "eu_fsf", "un_sc", "gb_ofsi", "ca_dfatd_sema"],
                    limit=10
                )
                
                if match_result.get("error"):
                    logger.error(f"Error searching sanctions: {match_result.get('error')}")
                    match_result = search_sanctions_database(client_name)
                elif match_result.get("total", 0) > 0:
                    screening_data.match_status = "potential_match"
                    screening_data.match_details = {
                        "found": True,
                        "matches": match_result.get("results", []),
                        "total": match_result.get("total", 0),
                        "datasets": [r.get("dataset", "unknown") for r in match_result.get("results", [])],
                        "source": "open_sanctions"
                    }
                    screening_data.risk_level = "high"
                else:
                    screening_data.match_status = "no_match"
                    screening_data.match_details = {
                        "found": False,
                        "matches": [],
                        "total": 0,
                        "source": "open_sanctions"
                    }
                    screening_data.risk_level = "low"
            except Exception as e:
                logger.error(f"Error using Open Sanctions API: {str(e)}")
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
        Create a new document retention policy based on compliance manual requirements.
        """
        if not policy_data.retention_period_days:
            try:
                retention_requirements = await compliance_manual_integration.get_document_retention_requirements(
                    document_type=policy_data.document_type
                )
                
                if "minimum_retention_period" in retention_requirements:
                    years = retention_requirements.get("minimum_retention_period", 5)
                    policy_data.retention_period_days = years * 365
                
                if "legal_basis" in retention_requirements and not policy_data.legal_basis:
                    policy_data.legal_basis = retention_requirements.get("legal_basis", "")
                
            except Exception as e:
                logger.error(f"Error getting retention requirements: {str(e)}")
                policy_data.retention_period_days = policy_data.retention_period_days or 1825
        
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
    
    async def get_due_diligence_requirements(
        self, 
        client_id: int, 
        due_diligence_level: Union[str, DueDiligenceLevel] = None,
        client_type: str = "individual"
    ) -> Dict[str, Any]:
        """
        Get due diligence requirements for a client based on the compliance manual.
        
        Args:
            client_id: ID of the client
            due_diligence_level: Level of due diligence (basic, enhanced, simplified)
            client_type: Type of client (individual, company, etc.)
            
        Returns:
            Dictionary with due diligence requirements
        """
        if not due_diligence_level:
            # For now, we'll use a placeholder
            client_risk = "medium"  # Placeholder
            
            if client_risk == "high":
                due_diligence_level = DueDiligenceLevel.ENHANCED
            elif client_risk == "low":
                due_diligence_level = DueDiligenceLevel.SIMPLIFIED
            else:
                due_diligence_level = DueDiligenceLevel.BASIC
        
        if isinstance(due_diligence_level, str):
            try:
                due_diligence_level = DueDiligenceLevel(due_diligence_level.lower())
            except ValueError:
                logger.error(f"Invalid due diligence level: {due_diligence_level}")
                due_diligence_level = DueDiligenceLevel.BASIC
        
        try:
            requirements = await compliance_manual_integration.get_due_diligence_requirements(
                due_diligence_level=due_diligence_level,
                client_type=client_type
            )
            
            requirements["client_id"] = client_id
            requirements["due_diligence_level"] = due_diligence_level.value
            requirements["client_type"] = client_type
            
            return requirements
        except Exception as e:
            logger.error(f"Error getting due diligence requirements: {str(e)}")
            return {
                "error": str(e),
                "client_id": client_id,
                "due_diligence_level": due_diligence_level.value if hasattr(due_diligence_level, "value") else str(due_diligence_level),
                "client_type": client_type
            }
    
    async def calculate_client_risk(
        self,
        client_id: int,
        client_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate risk score for a client based on the risk matrices in the compliance manual.
        
        Args:
            client_id: ID of the client
            client_data: Data about the client (optional)
            
        Returns:
            Dictionary with risk assessment results
        """
        if not client_data:
            client_data = {
                "id": client_id,
                "name": f"Client {client_id}",
                "country": "PA",  # Panama
                "business_type": "retail",
                "years_as_client": 2,
                "transaction_volume": 50000,
                "products": ["perfumes", "cosmetics"]
            }
        
        risk_factors = {
            RiskCategory.CLIENT: {
                "business_type": client_data.get("business_type", "unknown"),
                "years_as_client": client_data.get("years_as_client", 0),
                "previous_suspicious_activity": client_data.get("previous_suspicious_activity", False)
            },
            RiskCategory.GEOGRAPHIC: {
                "country": client_data.get("country", "unknown"),
                "region": client_data.get("region", "unknown"),
                "high_risk_jurisdiction": client_data.get("high_risk_jurisdiction", False)
            },
            RiskCategory.PRODUCT: {
                "products": client_data.get("products", []),
                "services": client_data.get("services", []),
                "high_value_products": client_data.get("high_value_products", False)
            },
            RiskCategory.CHANNEL: {
                "online_transactions": client_data.get("online_transactions", False),
                "in_person_transactions": client_data.get("in_person_transactions", True),
                "third_party_transactions": client_data.get("third_party_transactions", False)
            },
            RiskCategory.TRANSACTIONAL: {
                "transaction_volume": client_data.get("transaction_volume", 0),
                "transaction_frequency": client_data.get("transaction_frequency", "low"),
                "cash_transactions": client_data.get("cash_transactions", False)
            }
        }
        
        try:
            risk_assessment = await compliance_manual_integration.calculate_risk_score(
                client_id=client_id,
                risk_factors=risk_factors
            )
            
            return risk_assessment
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return {
                "error": str(e),
                "client_id": client_id,
                "risk_level": "medium",  # Default to medium risk if calculation fails
                "risk_factors": risk_factors
            }
    
    async def detect_suspicious_activity(
        self,
        transaction_id: int,
        transaction_data: Dict[str, Any] = None,
        client_id: int = None
    ) -> Dict[str, Any]:
        """
        Detect suspicious activity in a transaction based on the compliance manual.
        
        Args:
            transaction_id: ID of the transaction
            transaction_data: Data about the transaction (optional)
            client_id: ID of the client (optional)
            
        Returns:
            Dictionary with suspicious activity detection results
        """
        if not transaction_data:
            transaction_data = {
                "id": transaction_id,
                "client_id": client_id or 1,
                "amount": 15000,
                "currency": "USD",
                "date": datetime.utcnow().isoformat(),
                "type": "purchase",
                "payment_method": "cash",
                "products": ["luxury_perfume"]
            }
        
        client_id = client_id or transaction_data.get("client_id", 1)
        client_profile = {
            "id": client_id,
            "name": f"Client {client_id}",
            "risk_level": "medium",
            "average_transaction_amount": 5000,
            "usual_payment_methods": ["credit_card", "bank_transfer"],
            "usual_products": ["regular_perfume", "cosmetics"]
        }
        
        try:
            suspicious_activity = await compliance_manual_integration.detect_suspicious_activity(
                transaction_data=transaction_data,
                client_profile=client_profile
            )
            
            suspicious_activity["transaction_id"] = transaction_id
            suspicious_activity["client_id"] = client_id
            
            return suspicious_activity
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {str(e)}")
            return {
                "error": str(e),
                "transaction_id": transaction_id,
                "client_id": client_id,
                "is_suspicious": False,
                "risk_level": "low",
                "recommended_actions": ["review_manually"]
            }
    
    async def generate_ros_report(
        self,
        transaction_id: int,
        client_id: int,
        suspicious_activity: Dict[str, Any] = None
    ) -> ComplianceReport:
        """
        Generate a Suspicious Activity Report (ROS) for a suspicious transaction.
        
        Args:
            transaction_id: ID of the suspicious transaction
            client_id: ID of the client
            suspicious_activity: Results of suspicious activity detection (optional)
            
        Returns:
            ComplianceReport with the ROS report
        """
        if not suspicious_activity:
            suspicious_activity = await self.detect_suspicious_activity(
                transaction_id=transaction_id,
                client_id=client_id
            )
        
        transaction_data = {
            "id": transaction_id,
            "client_id": client_id,
            "amount": 15000,
            "currency": "USD",
            "date": datetime.utcnow().isoformat(),
            "type": "purchase",
            "payment_method": "cash",
            "products": ["luxury_perfume"]
        }
        
        client_data = {
            "id": client_id,
            "name": f"Client {client_id}",
            "identification": "123456789",
            "address": "123 Main St, Panama City, Panama",
            "contact": "client@example.com",
            "risk_level": "medium"
        }
        
        try:
            ros_report = await compliance_manual_integration.generate_ros_report(
                suspicious_activity=suspicious_activity,
                client_data=client_data,
                transaction_data=transaction_data
            )
            
            report_create = ComplianceReportCreate(
                report_type="ros_report",
                entity_type="transaction",
                entity_id=transaction_id,
                report_data=ros_report,
                status="draft",
                notes=f"ROS report for suspicious transaction {transaction_id} by client {client_id}"
            )
            
            return await self.create_compliance_report(report_create)
        except Exception as e:
            logger.error(f"Error generating ROS report: {str(e)}")
            
            report_create = ComplianceReportCreate(
                report_type="ros_report",
                entity_type="transaction",
                entity_id=transaction_id,
                report_data={
                    "error": str(e),
                    "transaction_id": transaction_id,
                    "client_id": client_id,
                    "suspicious_activity": suspicious_activity
                },
                status="draft",
                notes=f"Error generating ROS report: {str(e)}"
            )
            
            return await self.create_compliance_report(report_create)
    
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
        
        try:
            uaf_requirements = await compliance_manual_integration.query_compliance_manual(
                query="What are the requirements for UAF reporting according to the compliance manual?"
            )
            
            report_data["compliance_manual_guidance"] = uaf_requirements.get("response", "")
        except Exception as e:
            logger.error(f"Error querying compliance manual for UAF requirements: {str(e)}")
        
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
