"""
Unit tests for the legal module endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_verify_client_endpoint():
    """Test the verify-client endpoint."""
    response = client.post(
        "/api/v1/legal/verify-client",
        json={
            "full_name": "John Doe",
            "passport": "A123456",
            "country": "US",
            "type": "natural"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "full_name" in data
    assert "passport" in data
    assert "country" in data
    assert "results" in data
    assert "status" in data
    assert "risk_score" in data

def test_legal_qa_endpoint():
    """Test the legal QA endpoint."""
    response = client.post(
        "/api/v1/legal/ask",
        json={"prompt": "What is a confidentiality clause?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0

def test_analyze_contract_endpoint():
    """Test the contract analysis endpoint."""
    sample_contract = """
    CONFIDENTIALITY AGREEMENT
    
    This Confidentiality Agreement (the "Agreement") is entered into as of January 1, 2023 (the "Effective Date") by and between Company A and Company B.
    
    1. CONFIDENTIAL INFORMATION
    "Confidential Information" means any information disclosed by either party to the other party, either directly or indirectly, in writing, orally or by inspection of tangible objects.
    
    2. NON-DISCLOSURE
    Each party shall not disclose any Confidential Information to third parties.
    
    3. TERM
    This Agreement shall terminate three (3) years from the Effective Date.
    """
    
    response = client.post(
        "/api/v1/legal/contracts/analyze",
        json={
            "contract_text": sample_contract,
            "analysis_type": "extract_clauses"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "clauses" in data
    
    response = client.post(
        "/api/v1/legal/contracts/analyze",
        json={
            "contract_text": sample_contract,
            "analysis_type": "calculate_risk"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    
    response = client.post(
        "/api/v1/legal/contracts/analyze",
        json={
            "contract_text": sample_contract,
            "analysis_type": "detect_anomalies"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    
    response = client.post(
        "/api/v1/legal/contracts/analyze",
        json={
            "contract_text": sample_contract,
            "analysis_type": "suggest_rewrites"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "rewrites" in data
    
    response = client.post(
        "/api/v1/legal/contracts/analyze",
        json={
            "contract_text": "This Agreement shall terminate immediately upon breach by either party.",
            "analysis_type": "simulate_impact",
            "specific_query": "This Agreement shall terminate immediately upon breach by either party."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "impact" in data
