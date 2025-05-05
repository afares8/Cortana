from app.services.compliance.api.router import router as compliance_router
from app.services.compliance.services.compliance_service import compliance_service

__all__ = ["compliance_router", "compliance_service"]
