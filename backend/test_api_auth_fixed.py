"""
Test script to verify API endpoints are accessible without authentication.
This script directly tests the FastAPI application without starting a server.
"""
import asyncio
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_traffic_upload_endpoint():
    """Test the traffic upload endpoint without authentication."""
    data = {
        "data": {
            "data": {
                "invoice_number": "TEST-001",
                "invoice_date": "2025-05-01",
                "client_name": "Test Client",
                "client_id": "TC001",
                "movement_type": "import",
                "total_value": 1000.0,
                "total_weight": 100.0,
                "items": [
                    {
                        "tariff_code": "1234.56.78",
                        "description": "Test Item",
                        "quantity": 10,
                        "unit": "PCS",
                        "weight": 100.0,
                        "value": 1000.0
                    }
                ]
            }
        }
    }
    
    response = client.post("/api/v1/traffic/upload", json=data)
    print(f"Traffic Upload Endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    return response.status_code == 200

def test_traffic_records_endpoint():
    """Test the traffic records endpoint without authentication."""
    response = client.get("/api/v1/traffic/records")
    print(f"Traffic Records Endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    return response.status_code == 200

def test_ai_generate_endpoint():
    """Test the AI generate endpoint without authentication."""
    data = {
        "inputs": "Test input",
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "debug": False
    }
    
    response = client.post("/api/v1/ai/mistral/generate", json=data)
    print(f"AI Generate Endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    return response.status_code == 200

def test_accounting_companies_endpoint():
    """Test the accounting companies endpoint without authentication."""
    response = client.get("/api/v1/accounting/companies")
    print(f"Accounting Companies Endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    return response.status_code == 200

def test_accounting_obligations_endpoint():
    """Test the accounting obligations endpoint without authentication."""
    response = client.get("/api/v1/accounting/obligations")
    print(f"Accounting Obligations Endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    return response.status_code == 200

def run_tests():
    """Run all tests and print a summary."""
    print("Testing API endpoints without authentication...")
    print("=" * 50)
    
    results = {
        "Traffic Upload": test_traffic_upload_endpoint(),
        "Traffic Records": test_traffic_records_endpoint(),
        "AI Generate": test_ai_generate_endpoint(),
        "Accounting Companies": test_accounting_companies_endpoint(),
        "Accounting Obligations": test_accounting_obligations_endpoint()
    }
    
    print("\nTest Results Summary:")
    print("=" * 50)
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\nOverall Result:", "PASS" if all_passed else "FAIL")
    
    return all_passed

if __name__ == "__main__":
    run_tests()
