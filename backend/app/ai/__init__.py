# Import AI functions from services module
from app.services.ai.contract_intelligence import (
    extract_text_from_file,
    extract_clauses,
    calculate_risk_score,
    detect_anomalies,
    process_contract
)

from app.services.ai.mistral_client import mistral_client
