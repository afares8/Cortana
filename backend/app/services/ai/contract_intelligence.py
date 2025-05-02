"""
Contract Intelligence Engine for extracting clauses, scoring risk, and detecting anomalies.
"""
import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.contract import Contract
from app.models.ai_models import ExtractedClause, RiskScore, ContractAnomaly
from app.db.init_db import extracted_clauses_db, risk_scores_db, contract_anomalies_db

logger = logging.getLogger(__name__)

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK resources: {e}")

nlp = None

CLAUSE_PATTERNS = {
    "confidentiality": [
        r"confidential(?:ity)?",
        r"non-disclosure",
        r"proprietary information",
        r"trade secrets?",
    ],
    "termination": [
        r"terminat(?:e|ion)",
        r"cancel(?:lation)?",
        r"end(?:ing)? (?:of|the) (?:agreement|contract)",
    ],
    "penalties": [
        r"penalt(?:y|ies)",
        r"liquidated damages",
        r"fine(?:s)?",
        r"compensat(?:e|ion|ory)",
    ],
    "jurisdiction": [
        r"jurisdiction",
        r"governing law",
        r"venue",
        r"dispute resolution",
        r"arbitration",
    ],
    "obligations": [
        r"obligat(?:e|ion|ions)",
        r"responsibilit(?:y|ies)",
        r"shall (?:provide|perform|deliver|pay|comply)",
        r"must (?:provide|perform|deliver|pay|comply)",
    ],
}

RED_FLAG_TERMS = [
    {"term": "unlimited liability", "risk_score": 0.9, "category": "liability"},
    {"term": "no limitation of liability", "risk_score": 0.9, "category": "liability"},
    {"term": "indemnify and hold harmless", "risk_score": 0.7, "category": "indemnification"},
    {"term": "time is of the essence", "risk_score": 0.6, "category": "timing"},
    {"term": "best efforts", "risk_score": 0.5, "category": "performance"},
    {"term": "sole discretion", "risk_score": 0.7, "category": "control"},
    {"term": "perpetual license", "risk_score": 0.6, "category": "licensing"},
    {"term": "irrevocable", "risk_score": 0.7, "category": "termination"},
    {"term": "waiver of jury trial", "risk_score": 0.6, "category": "legal_rights"},
    {"term": "automatic renewal", "risk_score": 0.5, "category": "term"},
]

EXPECTED_CLAUSES = {
    "Service Agreement": ["confidentiality", "termination", "obligations", "jurisdiction"],
    "Non-Disclosure Agreement": ["confidentiality", "termination", "penalties"],
    "Lease Agreement": ["termination", "penalties", "obligations"],
    "Employment Contract": ["confidentiality", "termination", "obligations", "jurisdiction"],
    "License Agreement": ["confidentiality", "termination", "penalties", "obligations"],
}


def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == ".pdf":
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        
        elif file_ext in [".docx", ".doc"]:
            import docx2txt
            return docx2txt.process(file_path)
        
        elif file_ext in [".txt", ".md", ".rst"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        else:
            logger.warning(f"Unsupported file format: {file_ext}")
            return ""
    
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return ""


def extract_clauses(contract: Contract, text_content: Optional[str] = None) -> List[ExtractedClause]:
    """Extract clauses from contract text."""
    if not text_content and contract.file_path:
        text_content = extract_text_from_file(contract.file_path)
    
    if not text_content:
        logger.error(f"No text content available for contract {contract.id}")
        return []
    
    extracted_clauses = []
    
    paragraphs = re.split(r'\n\s*\n', text_content)
    
    for clause_type, patterns in CLAUSE_PATTERNS.items():
        for pattern in patterns:
            for i, paragraph in enumerate(paragraphs):
                if re.search(pattern, paragraph, re.IGNORECASE):
                    start_position = text_content.find(paragraph)
                    end_position = start_position + len(paragraph)
                    
                    confidence_score = 0.7  # Base score
                    if re.search(r'\b' + pattern + r'\b', paragraph, re.IGNORECASE):
                        confidence_score += 0.2  # Boost for exact word match
                    if re.search(r'^' + pattern, paragraph, re.IGNORECASE):
                        confidence_score += 0.1  # Boost for pattern at start
                    
                    clause = ExtractedClause(
                        contract_id=contract.id,
                        clause_type=clause_type,
                        clause_text=paragraph,
                        start_position=start_position,
                        end_position=end_position,
                        confidence_score=min(confidence_score, 1.0),
                        metadata={"pattern_matched": pattern}
                    )
                    
                    if not any(c.start_position == clause.start_position and 
                               c.end_position == clause.end_position for c in extracted_clauses):
                        extracted_clauses.append(clause)
    
    return extracted_clauses


def calculate_risk_score(contract: Contract, extracted_clauses: List[ExtractedClause]) -> RiskScore:
    """Calculate risk score for a contract based on extracted clauses."""
    risk_factors = {
        "missing_clauses": 0.0,
        "abnormal_duration": 0.0,
        "red_flags": 0.0,
    }
    
    expected_clause_types = EXPECTED_CLAUSES.get(contract.contract_type, [])
    extracted_clause_types = set(clause.clause_type for clause in extracted_clauses)
    missing_clauses = [clause_type for clause_type in expected_clause_types 
                      if clause_type not in extracted_clause_types]
    
    if expected_clause_types:
        risk_factors["missing_clauses"] = len(missing_clauses) / len(expected_clause_types) * 0.5
    
    from datetime import date
    contract_duration = (contract.expiration_date - contract.start_date).days
    abnormal_duration = False
    
    if contract_duration < 30:  # Less than a month
        risk_factors["abnormal_duration"] = 0.3
        abnormal_duration = True
    elif contract_duration > 1825:  # More than 5 years
        risk_factors["abnormal_duration"] = 0.4
        abnormal_duration = True
    
    red_flags_found = []
    all_text = " ".join(clause.clause_text.lower() for clause in extracted_clauses)
    
    for red_flag in RED_FLAG_TERMS:
        if red_flag["term"].lower() in all_text:
            red_flags_found.append(red_flag)
            risk_factors["red_flags"] += red_flag["risk_score"] * 0.1
    
    risk_factors["red_flags"] = min(risk_factors["red_flags"], 0.5)
    
    weights = {"missing_clauses": 0.4, "abnormal_duration": 0.2, "red_flags": 0.4}
    overall_score = sum(risk_factors[k] * weights[k] for k in risk_factors)
    
    risk_score = RiskScore(
        contract_id=contract.id,
        overall_score=overall_score,
        missing_clauses=missing_clauses,
        abnormal_durations=abnormal_duration,
        red_flag_terms=[{"term": rf["term"], "category": rf["category"]} for rf in red_flags_found],
        risk_factors=risk_factors,
        last_updated=datetime.now()
    )
    
    return risk_score


def detect_anomalies(contract: Contract, extracted_clauses: List[ExtractedClause]) -> List[ContractAnomaly]:
    """Detect anomalies in a contract based on extracted clauses and contract metadata."""
    anomalies = []
    
    expected_clause_types = EXPECTED_CLAUSES.get(contract.contract_type, [])
    extracted_clause_types = set(clause.clause_type for clause in extracted_clauses)
    missing_clauses = [clause_type for clause_type in expected_clause_types 
                      if clause_type not in extracted_clause_types]
    
    if missing_clauses:
        anomaly = ContractAnomaly(
            contract_id=contract.id,
            anomaly_type="policy_deviation",
            description=f"Missing required clauses: {', '.join(missing_clauses)}",
            severity="high" if len(missing_clauses) > 1 else "medium",
            detected_at=datetime.now()
        )
        anomalies.append(anomaly)
    
    from datetime import date
    contract_duration = (contract.expiration_date - contract.start_date).days
    
    if contract_duration < 30:  # Less than a month
        anomaly = ContractAnomaly(
            contract_id=contract.id,
            anomaly_type="duration_anomaly",
            description=f"Unusually short contract duration: {contract_duration} days",
            severity="medium",
            detected_at=datetime.now()
        )
        anomalies.append(anomaly)
    elif contract_duration > 1825:  # More than 5 years
        anomaly = ContractAnomaly(
            contract_id=contract.id,
            anomaly_type="duration_anomaly",
            description=f"Unusually long contract duration: {contract_duration} days",
            severity="medium",
            detected_at=datetime.now()
        )
        anomalies.append(anomaly)
    
    all_text = " ".join(clause.clause_text.lower() for clause in extracted_clauses)
    
    for red_flag in RED_FLAG_TERMS:
        if red_flag["term"].lower() in all_text:
            anomaly = ContractAnomaly(
                contract_id=contract.id,
                anomaly_type="red_flag_term",
                description=f"Contains red flag term: {red_flag['term']} (category: {red_flag['category']})",
                severity="high" if red_flag["risk_score"] > 0.7 else "medium",
                detected_at=datetime.now()
            )
            anomalies.append(anomaly)
    
    return anomalies


def process_contract(contract: Contract, text_content: Optional[str] = None) -> Dict[str, Any]:
    """Process a contract to extract clauses, calculate risk, and detect anomalies."""
    clauses = extract_clauses(contract, text_content)
    
    saved_clauses = []
    for clause in clauses:
        saved_clause = extracted_clauses_db.create(clause)
        saved_clauses.append(saved_clause)
    
    risk_score = calculate_risk_score(contract, clauses)
    saved_risk_score = risk_scores_db.create(risk_score)
    
    anomalies = detect_anomalies(contract, clauses)
    saved_anomalies = []
    for anomaly in anomalies:
        saved_anomaly = contract_anomalies_db.create(anomaly)
        saved_anomalies.append(saved_anomaly)
    
    return {
        "contract_id": contract.id,
        "extracted_clauses": saved_clauses,
        "risk_score": saved_risk_score,
        "anomalies": saved_anomalies
    }
