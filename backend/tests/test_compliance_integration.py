from fastapi.testclient import TestClient
from app.main import app
from app.services.compliance.services.excel_risk_evaluator import excel_risk_evaluator

client = TestClient(app)


def test_risk_evaluation_endpoint():
    """Test the risk evaluation endpoint."""
    response = client.post(
        "/api/v1/compliance/risk-evaluation",
        json={
            "client_data": {
                "client_type": "individual",
                "country": "PA",
                "industry": "finance",
                "channel": "presencial",
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_score" in data
    assert "risk_level" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]


def test_legal_verify_client_endpoint():
    """Test the legal client verification endpoint."""
    from app.legal.models import Client
    from app.legal.services import clients_db

    test_client = Client(
        id=999,  # Provide ID explicitly for testing
        name="Test Client",
        contact_email="test@example.com",
        industry="finance",
        client_type="individual",
        country="PA",
    )

    clients_db.data[test_client.id] = test_client

    print(f"Created test client with ID: {test_client.id}")

    assert clients_db.get(test_client.id) is not None

    response = client.post(
        "/api/v1/legal/verify-client",
        json={
            "client_id": test_client.id,
            "name": "Test Client",
            "country": "PA",
            "type": "natural",
        },
    )
    print(f"Verify client response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "verification_date" in data


def test_contract_analysis_endpoint():
    """Test the contract analysis endpoint."""
    from app.legal.models import Client, Contract
    from app.legal.services import clients_db, contracts_db
    from datetime import datetime
    import unittest.mock

    with open("/tmp/test_contract.pdf", "w") as f:
        f.write("Test contract content for analysis")

    with unittest.mock.patch(
        "app.services.ai.contract_intelligence.process_contract"
    ) as mock_process:
        mock_process.return_value = {
            "summary": "This is a test contract",
            "key_clauses": ["Test clause 1", "Test clause 2"],
            "risk_factors": ["No significant risks identified"],
            "recommendations": ["Contract appears to be standard"],
        }

        test_client = Client(
            id=888,  # Provide ID explicitly for testing
            name="Test Client for Contract",
            contact_email="test@example.com",
            industry="finance",
            client_type="individual",
            country="PA",
        )

        clients_db.data[test_client.id] = test_client

        print(f"Created test client with ID: {test_client.id}")

        test_contract = Contract(
            id=777,  # Provide ID explicitly for testing
            title="Test Contract",
            client_id=test_client.id,
            contract_type="Service Agreement",
            start_date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
            expiration_date=datetime.strptime("2024-12-31", "%Y-%m-%d"),
            responsible_lawyer="Test Lawyer",
            status="draft",
            file_path="/tmp/test_contract.pdf",
            metadata={},
        )

        contracts_db.data[test_contract.id] = test_contract

        print(f"Created test contract with ID: {test_contract.id}")

        response = client.post(f"/api/v1/legal/contracts/{test_contract.id}/analyze")
        print(f"Contract analysis response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data

        mock_process.assert_called_once()


def test_uaf_report_generation_endpoint():
    """Test the UAF report generation endpoint."""
    response = client.post(
        "/api/v1/compliance/uaf-reports",
        json={"client_id": 999, "start_date": "2024-01-01", "end_date": "2024-12-31"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "status" in data


def test_excel_risk_evaluator():
    """Test the Excel risk evaluator directly."""
    risk_result = excel_risk_evaluator.calculate_risk(
        {
            "client_type": "individual",
            "country": "PA",
            "industry": "finance",
            "channel": "presencial",
        }
    )

    assert "total_score" in risk_result
    assert "risk_level" in risk_result
    assert "components" in risk_result
    assert risk_result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]

    high_risk_result = excel_risk_evaluator.calculate_risk(
        {
            "client_type": "pep",
            "country": "VE",
            "industry": "finance",
            "channel": "no_presencial",
        }
    )
    assert high_risk_result["risk_level"] == "HIGH"

    low_risk_result = excel_risk_evaluator.calculate_risk(
        {
            "client_type": "individual",
            "country": "US",
            "industry": "technology",
            "channel": "presencial",
        }
    )
    assert low_risk_result["risk_level"] in ["LOW", "MEDIUM"]  # Depending on the matrix
