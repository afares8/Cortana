from typing import Dict, Any
from app.db.base import InMemoryDB
from app.services.compliance.models.compliance import (
    ComplianceReport, PEPScreeningResult, 
    SanctionsScreeningResult, DocumentRetentionPolicy
)

compliance_reports_db = InMemoryDB[ComplianceReport](ComplianceReport)
pep_screenings_db = InMemoryDB[PEPScreeningResult](PEPScreeningResult)
sanctions_screenings_db = InMemoryDB[SanctionsScreeningResult](SanctionsScreeningResult)
retention_policies_db = InMemoryDB[DocumentRetentionPolicy](DocumentRetentionPolicy)

SAMPLE_PEP_DATA = [
    {
        "id": 1,
        "name": "Juan Carlos Varela",
        "position": "Former President",
        "country": "Panama",
        "risk_level": "medium",
        "active": True
    },
    {
        "id": 2,
        "name": "Ricardo Martinelli",
        "position": "Former President",
        "country": "Panama",
        "risk_level": "high",
        "active": True
    },
    {
        "id": 3,
        "name": "Laurentino Cortizo",
        "position": "Current President",
        "country": "Panama",
        "risk_level": "medium",
        "active": True
    }
]

SAMPLE_SANCTIONS_DATA = [
    {
        "id": 1,
        "entity_name": "Grupo Wisa",
        "entity_type": "company",
        "country": "Panama",
        "sanction_type": "OFAC",
        "reason": "Money laundering",
        "active": True
    },
    {
        "id": 2,
        "entity_name": "Abdul Waked",
        "entity_type": "individual",
        "country": "Panama",
        "sanction_type": "OFAC",
        "reason": "Money laundering",
        "active": True
    }
]

def search_pep_database(name: str, country: str = None) -> Dict[str, Any]:
    """
    Search the PEP database for matches.
    Returns match details if found, empty dict otherwise.
    """
    matches = []
    name = name.lower()
    
    for pep in SAMPLE_PEP_DATA:
        if name in pep["name"].lower():
            if country is None or country.lower() == pep["country"].lower():
                matches.append(pep)
    
    if matches:
        return {
            "found": True,
            "matches": matches,
            "match_count": len(matches),
            "highest_risk": max(match["risk_level"] for match in matches)
        }
    
    return {"found": False, "matches": [], "match_count": 0}

def search_sanctions_database(name: str, entity_type: str = None) -> Dict[str, Any]:
    """
    Search the sanctions database for matches.
    Returns match details if found, empty dict otherwise.
    """
    matches = []
    name = name.lower()
    
    for sanction in SAMPLE_SANCTIONS_DATA:
        if name in sanction["entity_name"].lower():
            if entity_type is None or entity_type.lower() == sanction["entity_type"].lower():
                matches.append(sanction)
    
    if matches:
        return {
            "found": True,
            "matches": matches,
            "match_count": len(matches),
            "sanction_types": list(set(match["sanction_type"] for match in matches))
        }
    
    return {"found": False, "matches": [], "match_count": 0}
