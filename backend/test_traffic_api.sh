
echo "Getting token from login endpoint..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin&grant_type=password")

echo "Login response: $TOKEN_RESPONSE"

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//g')

if [ -z "$TOKEN" ]; then
  echo "Failed to get token. Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Token obtained successfully."

echo -e "\nTesting GET /api/v1/traffic/records endpoint (should be empty)..."
curl -s -X GET "http://localhost:8000/api/v1/traffic/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\nTesting POST /api/v1/traffic/upload endpoint (first invoice)..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/traffic/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "invoice_number": "INV-001",
      "invoice_date": "2025-05-01T00:00:00",
      "client_name": "Test Client",
      "client_id": "TC001",
      "movement_type": "Exit",
      "total_value": 1000.0,
      "total_weight": 500.0,
      "items": [
        {
          "tariff_code": "8471.30.00",
          "description": "Laptop computers",
          "quantity": 10,
          "unit": "units",
          "weight": 50.0,
          "value": 100.0
        }
      ]
    }
  }')

echo "Upload response (first invoice): $UPLOAD_RESPONSE"

RECORD_ID=$(python3 -c "
import json, sys
try:
    data = json.loads('$UPLOAD_RESPONSE'.replace('\n', ''))
    if isinstance(data, list) and len(data) > 0:
        print(data[0]['id'])
    else:
        print(data['id'] if 'id' in data else '')
except Exception as e:
    print('')
")

if [ -z "$RECORD_ID" ]; then
  echo "Failed to get record ID from upload response. Using default ID 1."
  RECORD_ID=1
else
  echo "Successfully extracted record ID: $RECORD_ID"
fi

echo -e "\nTesting POST /api/v1/traffic/upload endpoint (second invoice)..."
UPLOAD_RESPONSE2=$(curl -s -X POST "http://localhost:8000/api/v1/traffic/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "invoice_number": "INV-002",
      "invoice_date": "2025-05-02T00:00:00",
      "client_name": "Test Client",
      "client_id": "TC001",
      "movement_type": "Exit",
      "total_value": 2000.0,
      "total_weight": 800.0,
      "items": [
        {
          "tariff_code": "8471.30.00",
          "description": "Desktop computers",
          "quantity": 5,
          "unit": "units",
          "weight": 160.0,
          "value": 400.0
        }
      ]
    }
  }')

echo "Upload response (second invoice): $UPLOAD_RESPONSE2"

RECORD_ID2=$(python3 -c "
import json, sys
try:
    data = json.loads('$UPLOAD_RESPONSE2'.replace('\n', ''))
    if isinstance(data, list) and len(data) > 0:
        print(data[0]['id'])
    else:
        print(data['id'] if 'id' in data else '')
except Exception as e:
    print('')
")

if [ -z "$RECORD_ID2" ]; then
  echo "Failed to get second record ID. Using ID 2."
  RECORD_ID2=2
else
  echo "Successfully extracted second record ID: $RECORD_ID2"
fi

echo -e "\nTesting GET /api/v1/traffic/records endpoint (should have records now)..."
curl -s -X GET "http://localhost:8000/api/v1/traffic/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\nTesting GET /api/v1/traffic/record/$RECORD_ID endpoint..."
curl -s -X GET "http://localhost:8000/api/v1/traffic/record/$RECORD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\nTesting POST /api/v1/traffic/consolidate endpoint..."
CONSOLIDATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/traffic/consolidate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"invoice_record_ids\": [$RECORD_ID, $RECORD_ID2]}")

echo -e "\nConsolidation response: $CONSOLIDATE_RESPONSE"

CONSOLIDATED_ID=$(python3 -c "
import json, sys
try:
    data = json.loads('$CONSOLIDATE_RESPONSE'.replace('\n', ''))
    if 'consolidated_record' in data and 'id' in data['consolidated_record']:
        print(data['consolidated_record']['id'])
    else:
        print('')
except Exception as e:
    print('')
")

if [ -z "$CONSOLIDATED_ID" ]; then
  echo "Failed to get consolidated record ID. Using ID 3."
  CONSOLIDATED_ID=3
else
  echo "Successfully extracted consolidated record ID: $CONSOLIDATED_ID"
fi

echo -e "\nTesting POST /api/v1/traffic/submit endpoint..."
SUBMIT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/traffic/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"record_id\": $CONSOLIDATED_ID}")

echo -e "\nSubmission response: $SUBMIT_RESPONSE"

SUBMISSION_ID=$(python3 -c "
import json, sys
try:
    data = json.loads('$SUBMIT_RESPONSE'.replace('\n', ''))
    if 'submission_id' in data:
        print(data['submission_id'])
    else:
        print('')
except Exception as e:
    print('')
")

if [ -z "$SUBMISSION_ID" ]; then
  echo "Failed to get submission ID. Using ID 1."
  SUBMISSION_ID=1
else
  echo "Successfully extracted submission ID: $SUBMISSION_ID"
fi

echo -e "\nTesting GET /api/v1/traffic/logs endpoint..."
curl -s -X GET "http://localhost:8000/api/v1/traffic/logs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\nTesting GET /api/v1/traffic/logs/$SUBMISSION_ID endpoint..."
curl -s -X GET "http://localhost:8000/api/v1/traffic/logs/$SUBMISSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\nAPI testing completed."
