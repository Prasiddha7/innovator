#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Testing Coordinator Profile Auto-Creation Flow ===${NC}\n"

# 1. Login via SSO
echo -e "${BLUE}1. Login coordinator1@example.com via SSO...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"coordinator1@example.com","password":"pass123"}')

echo "Response: $LOGIN_RESPONSE"
JWT_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$JWT_TOKEN" ]; then
  echo -e "${BLUE}Getting token from response...${NC}"
  JWT_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access // .token // ""' 2>/dev/null)
fi

echo -e "${GREEN}JWT Token: ${JWT_TOKEN:0:50}...${NC}\n"

if [ -z "$JWT_TOKEN" ] || [ "$JWT_TOKEN" == "null" ]; then
  echo "Failed to get JWT token"
  exit 1
fi

# 2. Call coordinator endpoint to trigger auto-creation
echo -e "${BLUE}2. Call coordinator endpoint (this triggers auto-creation)...${NC}"
COORDINATOR_RESPONSE=$(curl -s -X GET http://localhost:8002/api/coordinator/teacher-invoices/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')

echo "Response: $COORDINATOR_RESPONSE"
echo ""

# 3. Check if profiles were created in kms_service
echo -e "${BLUE}3. Checking if profiles were created in kms_service...${NC}"
docker compose exec kms_service python manage.py shell << 'INNER_EOF' 2>&1 | grep -A 5 "Coordinator\|Teacher"
from kms.models import Coordinator, Teacher
from accounts.models import User
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.local')

# Find the coordinator user
try:
    # We need to get the user_id from auth_service first
    print("Checking coordinator profiles in kms_service...")
    coordinators = Coordinator.objects.all()
    print(f"Total coordinators: {coordinators.count()}")
    for coord in coordinators:
        print(f"  - Coordinator: {coord.name} (auth_user_id: {coord.auth_user_id}, school: {coord.school})")
    
    # Check teachers too
    teachers = Teacher.objects.all()
    print(f"Total teachers: {teachers.count()}")
    for teacher in teachers[:3]:
        print(f"  - Teacher: {teacher.name}")
except Exception as e:
    print(f"Error: {e}")
INNER_EOF

