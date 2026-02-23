#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Teacher API Comprehensive Tests ===${NC}\n"

# Get JWT token
echo -e "${YELLOW}Step 1: Get JWT Token${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"TestPassword123"}')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}✗ Failed to get token${NC}"
  echo $LOGIN_RESPONSE
  exit 1
fi

echo -e "${GREEN}✓ Token obtained${NC}\n"

# Test 1: Teacher Profile
echo -e "${YELLOW}Test 1: Get Teacher Profile${NC}"
PROFILE=$(curl -s -X GET http://localhost:8002/api/teacher/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response: $PROFILE"
echo ""

# Test 2: Teacher Classes
echo -e "${YELLOW}Test 2: Get Teacher Classes${NC}"
CLASSES=$(curl -s -X GET http://localhost:8002/api/teacher/classes/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response: $CLASSES"
echo ""

# Test 3: Teacher Earnings
echo -e "${YELLOW}Test 3: Get Teacher Earnings${NC}"
EARNINGS=$(curl -s -X GET http://localhost:8002/api/teacher/earnings/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response: $EARNINGS"
echo ""

# Test 4: Get KYC Status (should be 404 if not uploaded)
echo -e "${YELLOW}Test 4: Get KYC Status${NC}"
KYC=$(curl -s -X GET http://localhost:8002/api/teacher/kyc/status/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response: $KYC"
echo ""

echo -e "${GREEN}=== Tests Complete ===${NC}"
