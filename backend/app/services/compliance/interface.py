from typing import List, Optional, Dict, Any
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

class ComplianceServiceInterface:
    """
    Interface for compliance operations.
    """
    
    async def create_compliance_report(self, report_data: ComplianceReportCreate) -> ComplianceReport:
        """
        Create a new compliance report.
        """
        pass
    
    async def get_compliance_reports(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ComplianceReport]:
        """
        Get compliance reports with optional filtering.
        """
        pass
    
    async def get_compliance_report(self, report_id: int) -> Optional[ComplianceReport]:
        """
        Get a compliance report by ID.
        """
        pass
    
    async def update_compliance_report(
        self,
        report_id: int,
        report_data: ComplianceReportUpdate
    ) -> Optional[ComplianceReport]:
        """
        Update a compliance report.
        """
        pass
    
    async def delete_compliance_report(self, report_id: int) -> bool:
        """
        Delete a compliance report.
        """
        pass
    
    async def create_pep_screening(self, screening_data: PEPScreeningResultCreate) -> PEPScreeningResult:
        """
        Create a new PEP screening result.
        """
        pass
    
    async def get_pep_screenings(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PEPScreeningResult]:
        """
        Get PEP screening results with optional filtering.
        """
        pass
    
    async def get_pep_screening(self, screening_id: int) -> Optional[PEPScreeningResult]:
        """
        Get a PEP screening result by ID.
        """
        pass
    
    async def update_pep_screening(
        self,
        screening_id: int,
        screening_data: PEPScreeningResultUpdate
    ) -> Optional[PEPScreeningResult]:
        """
        Update a PEP screening result.
        """
        pass
    
    async def create_sanctions_screening(self, screening_data: SanctionsScreeningResultCreate) -> SanctionsScreeningResult:
        """
        Create a new sanctions screening result.
        """
        pass
    
    async def get_sanctions_screenings(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SanctionsScreeningResult]:
        """
        Get sanctions screening results with optional filtering.
        """
        pass
    
    async def get_sanctions_screening(self, screening_id: int) -> Optional[SanctionsScreeningResult]:
        """
        Get a sanctions screening result by ID.
        """
        pass
    
    async def update_sanctions_screening(
        self,
        screening_id: int,
        screening_data: SanctionsScreeningResultUpdate
    ) -> Optional[SanctionsScreeningResult]:
        """
        Update a sanctions screening result.
        """
        pass
    
    async def create_retention_policy(self, policy_data: DocumentRetentionPolicyCreate) -> DocumentRetentionPolicy:
        """
        Create a new document retention policy.
        """
        pass
    
    async def get_retention_policies(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[DocumentRetentionPolicy]:
        """
        Get document retention policies with optional filtering.
        """
        pass
    
    async def get_retention_policy(self, policy_id: int) -> Optional[DocumentRetentionPolicy]:
        """
        Get a document retention policy by ID.
        """
        pass
    
    async def update_retention_policy(
        self,
        policy_id: int,
        policy_data: DocumentRetentionPolicyUpdate
    ) -> Optional[DocumentRetentionPolicy]:
        """
        Update a document retention policy.
        """
        pass
    
    async def delete_retention_policy(self, policy_id: int) -> bool:
        """
        Delete a document retention policy.
        """
        pass
