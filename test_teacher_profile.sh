#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Teacher Profile API Test ===${NC}\n"

AUTH_URL="http://localhost:8000"
KMS_URL="http://localhost:8002"

# Test credentials
EMAIL="testuser@example.com"
PASSWORD="TestPassword123"

echo -e "${BLUE}Step 1: Get JWT Token${NC}"
echo "Logging in with: $EMAIL"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/api/auth/sso/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Login Response:"
echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# Extract token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" == "null" ]; then
  echo -e "${RED}❌ Failed to get access token${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Token obtained${NC}"
echo "Token: ${ACCESS_TOKEN:0:50}..."
echo ""

echo -e "${BLUE}Step 2: Call Teacher Profile API${NC}"
echo "GET $KMS_URL/api/teacher/profile/"
echo ""

PROFILE_RESPONSE=$(curl -s -X GET "$KMS_URL/api/teacher/profile/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -w "\nHTTP_STATUS:%{http_code}")

# Extract status and body
HTTP_STATUS=$(echo "$PROFILE_RESPONSE" | grep "HTTP_STATUS:" | cut -d':' -f2)
BODY=$(echo "$PROFILE_RESPONSE" | sed '$d')

echo "Response Status: $HTTP_STATUS"
echo ""
echo "Response Body:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_STATUS" == "200" ]; then
  echo -e "${GREEN}✓ Success!${NC}"
  echo ""
  echo "Teacher Profile Details:"
  echo "$BODY" | jq '{id, name, email, phone_number}' 2>/dev/null || echo "$BODY"
else
  echo -e "${RED}❌ Failed with status $HTTP_STATUS${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Test with Invalid Token${NC}"
INVALID_RESPONSE=$(curl -s -X GET "$KMS_URL/api/teacher/profile/" \
  -H "Authorization: Bearer invalid.token.here" \
  -H "Content-Type: application/json" \
  -w "\nHTTP_STATUS:%{http_code}")

INVALID_STATUS=$(echo "$INVALID_RESPONSE" | grep "HTTP_STATUS:" | cut -d':' -f2)
INVALID_BODY=$(echo "$INVALID_RESPONSE" | sed '$d')

echo "Response Status: $INVALID_STATUS"
echo "Response:"
echo "$INVALID_BODY" | jq '.' 2>/dev/null || echo "$INVALID_BODY"
echo ""

if [ "$INVALID_STATUS" == "401" ]; then
  echo -e "${GREEN}✓ Correctly rejected invalid token${NC}"
else
  echo -e "${YELLOW}⚠ Expected 401, got $INVALID_STATUS${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Test without Token${NC}"
NO_TOKEN_RESPONSE=$(curl -s -X GET "$KMS_URL/api/teacher/profile/" \
  -H "Content-Type: application/json" \
  -w "\nHTTP_STATUS:%{http_code}")

NO_TOKEN_STATUS=$(echo "$NO_TOKEN_RESPONSE" | grep "HTTP_STATUS:" | cut -d':' -f2)
NO_TOKEN_BODY=$(echo "$NO_TOKEN_RESPONSE" | sed '$d')

echo "Response Status: $NO_TOKEN_STATUS"
echo "Response:"
echo "$NO_TOKEN_BODY" | jq '.' 2>/dev/null || echo "$NO_TOKEN_BODY"
echo ""

if [ "$NO_TOKEN_STATUS" == "401" ]; then
  echo -e "${GREEN}✓ Correctly rejected missing token${NC}"
else
  echo -e "${YELLOW}⚠ Expected 401, got $NO_TOKEN_STATUS${NC}"
fi

echo ""
echo -e "${BLUE}=== Test Complete ===${NC}"
