
API_URL="http://localhost:8000/api/v1/compliance/verify-customer"

echo "=== Testing Natural Person Verification ==="
echo "POST $API_URL"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{
    "customer": { "name":"John Doe","dob":"1970-01-01","country":"US","type":"natural" },
    "directors": [], "ubos": []
  }'

echo -e "\n\n"

echo "=== Testing Legal Entity Verification ==="
echo "POST $API_URL"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{
    "customer": { "name":"Acme Corp","country":"US","type":"legal" },
    "directors":[{"name":"Jane Doe","dob":"1980-05-15","country":"US","type":"natural"}],
    "ubos":[{"name":"Jim Smith","dob":"1965-09-30","country":"US","type":"natural"}]
  }'

echo -e "\n\n"

echo "=== Testing with Known PEP Name ==="
echo "POST $API_URL"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{
    "customer": { "name":"Vladimir Putin","dob":"1952-10-07","country":"RU","type":"natural" },
    "directors": [], "ubos": []
  }'

echo -e "\n\n"

echo "=== Testing with Known Sanctions Entity ==="
echo "POST $API_URL"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{
    "customer": { "name":"North Korea Ministry of Defense","country":"KP","type":"legal" },
    "directors": [], "ubos": []
  }'

echo -e "\n\nTests completed."
