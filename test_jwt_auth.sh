#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== JWT Authentication Test ===${NC}\n"

# Test credentials
EMAIL="testuser@example.com"
PASSWORD="TestPassword123"
AUTH_URL="http://localhost:8000"
KMS_URL="http://localhost:8002"

echo -e "${BLUE}1. Registering test user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$AUTH_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"testuser\",\"password\":\"$PASSWORD\",\"role\":\"teacher\"}")

echo "Response: $REGISTER_RESPONSE"
echo ""

echo -e "${BLUE}2. Logging in to get JWT token...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/api/auth/sso/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Response: $LOGIN_RESPONSE"
echo ""

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}❌ Failed to get access token${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Access Token obtained: ${ACCESS_TOKEN:0:50}...${NC}\n"

echo -e "${BLUE}3. Testing KMS Service APIs with JWT token...${NC}\n"

# Test admin APIs (These require IsAdmin permission)
echo -e "${BLUE}Testing: GET /api/admin/schools/${NC}"
SCHOOLS_RESPONSE=$(curl -s -X GET "$KMS_URL/api/admin/schools/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Response: $SCHOOLS_RESPONSE"
if echo "$SCHOOLS_RESPONSE" | grep -q "detail\|error"; then
  echo -e "${RED}❌ Failed (Check if user has IsAdmin permission or if endpoint exists)${NC}"
else
  echo -e "${GREEN}✓ Success (Empty list is OK for first test)${NC}"
fi
echo ""

echo -e "${BLUE}Testing: GET /api/teacher/profile/${NC}"
PROFILE_RESPONSE=$(curl -s -X GET "$KMS_URL/api/teacher/profile/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Response: $PROFILE_RESPONSE"
if echo "$PROFILE_RESPONSE" | grep -q "error\|detail"; then
  echo -e "${RED}❌ Failed${NC}"
else
  echo -e "${GREEN}✓ Success${NC}"
fi
echo ""

# Test without token (should fail)
echo -e "${BLUE}4. Testing without JWT token (should fail)...${NC}"
NOTAUTH_RESPONSE=$(curl -s -X GET "$KMS_URL/api/admin/schools/" \
  -H "Content-Type: application/json")

echo "Response: $NOTAUTH_RESPONSE"
if echo "$NOTAUTH_RESPONSE" | grep -q "detail"; then
  echo -e "${GREEN}✓ Correctly rejected unauthenticated request${NC}"
else
  echo -e "${RED}❌ Should have rejected request${NC}"
fi
echo ""

# Test with invalid token (should fail)
echo -e "${BLUE}5. Testing with invalid JWT token (should fail)...${NC}"
INVALID_RESPONSE=$(curl -s -X GET "$KMS_URL/api/admin/schools/" \
  -H "Authorization: Bearer invalid.token.here" \
  -H "Content-Type: application/json")

echo "Response: $INVALID_RESPONSE"
if echo "$INVALID_RESPONSE" | grep -q "detail"; then
  echo -e "${GREEN}✓ Correctly rejected invalid token${NC}"
else
  echo -e "${RED}❌ Should have rejected invalid token${NC}"
fi
echo ""

echo -e "${GREEN}=== Test Complete ===${NC}"
