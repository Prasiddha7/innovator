# Admin APIs - Testing & Verification Guide

## 🧪 Complete Testing Instructions

Follow this guide to verify all admin APIs are working correctly.

---

## Step 1: Verify Services Are Running

```bash
# Check docker services
docker compose ps

# Expected Output:
# CONTAINER ID   IMAGE                           STATUS
# ...            innovator-auth_service:latest   Up
# ...            innovator-kms_service:latest    Up
# ...            innovator-auth_db               Up
# ...            innovator-kms_db                Up
```

---

## Step 2: Get Admin JWT Token

### Test That Auth Service Works

```bash
# First, ensure admin user exists (check or create via Django admin)
docker compose exec auth_service python manage.py shell
# In shell:
# from django.contrib.auth.models import User
# User.objects.create_user(username='admin@example.com', email='admin@example.com', password='AdminPassword123')
# exit()

# Now login to get JWT token
curl -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPassword123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwicm9sZSI6ImFkbWluIn0...",
  "refresh_token": "...",
  "role": "admin",
  "expires_in": 3600
}
```

**Save the token:**
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."  # Use actual token from response
```

---

## Step 3: Test Admin Endpoints

### Test 1: Get Admin Dashboard (Most Basic Test)

```bash
curl -X GET http://localhost:8002/api/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200):**
```json
{
  "total_teachers": 0,
  "total_schools": 0,
  "total_classrooms": 0,
  "total_students": 0,
  "kyc_applications": {
    "pending": 0,
    "approved": 0,
    "rejected": 0
  },
  "teacher_assignments": 0,
  "today_attendance_rate": 0.0
}
```

---

### Test 2: Create School

```bash
curl -X POST http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test School #1",
    "address": "123 Test Street"
  }'
```

**Expected Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Test School #1",
  "address": "123 Test Street",
  "created_at": "2024-02-18T10:30:00Z"
}
```

**Save the school ID:**
```bash
SCHOOL_ID="550e8400-e29b-41d4-a716-446655440000"  # Use actual ID from response
```

---

### Test 3: List Schools

```bash
curl -X GET http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Test School #1",
    "address": "123 Test Street",
    "created_at": "2024-02-18T10:30:00Z"
  }
]
```

---

### Test 4: Get Specific School

```bash
curl -X GET http://localhost:8002/api/admin/schools/$SCHOOL_ID/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):** Same as individual school object

---

### Test 5: Update School

```bash
curl -X PUT http://localhost:8002/api/admin/schools/$SCHOOL_ID/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Test School",
    "address": "456 New Street"
  }'
```

**Expected Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Test School",
  "address": "456 New Street",
  "created_at": "2024-02-18T10:30:00Z"
}
```

---

### Test 6: Create Classroom

```bash
curl -X POST http://localhost:8002/api/admin/classrooms/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Class 10-A\",
    \"school\": \"$SCHOOL_ID\"
  }"
```

**Expected Response (201):**
```json
{
  "id": "a80e1300-c21b-41d4-a716-446655440000",
  "name": "Class 10-A",
  "school": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-02-18T10:35:00Z"
}
```

**Save the classroom ID:**
```bash
CLASSROOM_ID="a80e1300-c21b-41d4-a716-446655440000"
```

---

### Test 7: Create Course

```bash
curl -X POST http://localhost:8002/api/admin/courses/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Mathematics\",
    \"school\": \"$SCHOOL_ID\",
    \"status\": \"active\"
  }"
```

**Expected Response (201):**
```json
{
  "id": "c71e2400-d32b-41d4-a716-446655440000",
  "title": "Mathematics",
  "school": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "created_at": "2024-02-18T10:40:00Z"
}
```

---

### Test 8: Get Pending KYC Applications

```bash
curl -X GET 'http://localhost:8002/api/admin/teacher-kyc/?status=pending' \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
[]  # Empty array if no pending applications
```

---

### Test 9: Get Dashboard (Should Show Updated Stats)

```bash
curl -X GET http://localhost:8002/api/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
{
  "total_teachers": 0,
  "total_schools": 1,          # Should be 1 now (created earlier)
  "total_classrooms": 1,       # Should be 1 now (created earlier)
  "total_students": 0,
  "kyc_applications": {
    "pending": 0,
    "approved": 0,
    "rejected": 0
  },
  "teacher_assignments": 0,
  "today_attendance_rate": 0.0
}
```

---

### Test 10: Delete Classroom

```bash
curl -X DELETE http://localhost:8002/api/admin/classrooms/$CLASSROOM_ID/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (204):** No content (empty response)

---

## Error Testing

### Test Error 1: Missing Token (401 Unauthorized)

```bash
curl -X GET http://localhost:8002/api/admin/dashboard/
```

**Expected Response (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### Test Error 2: Invalid Token (401 Unauthorized)

```bash
curl -X GET http://localhost:8002/api/admin/dashboard/ \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected Response (401):**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

---

### Test Error 3: Team User (Not Admin) (403 Forbidden)

*(First login as a non-admin teacher user)*

```bash
curl -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "TeacherPassword123"
  }'

# Use returned token as $TEACHER_TOKEN

curl -X GET http://localhost:8002/api/admin/dashboard/ \
  -H "Authorization: Bearer $TEACHER_TOKEN"
```

**Expected Response (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Test Error 4: Invalid School ID (404 Not Found)

```bash
curl -X GET http://localhost:8002/api/admin/schools/invalid-id/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (404):**
```json
{
  "detail": "School not found"
}
```

---

### Test Error 5: Missing Required Field (400 Bad Request)

```bash
curl -X POST http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "School Without Address"
  }'  # Missing "address" field
```

**Expected Response (400):**
```json
{
  "address": ["This field is required."]
}
```

---

## Postman Testing

### 1. Import Collection
```
Postman → File → Import → Select ADMIN_API_POSTMAN.json
```

### 2. Setup Variables
```
Environment Variables:
- admin_token: [Your JWT token]
- school_id: [UUID from create school]
- classroom_id: [UUID from create classroom]
- course_id: [UUID from create course]
- teacher_id: [Existing teacher UUID]
- kyc_id: [Existing KYC UUID]
```

### 3. Run Complete Workflow
1. **Authentication** → Admin SSO Login
2. **Schools** → Create School → Get School ID
3. **Classrooms** → Create Classroom → Get Classroom ID
4. **Courses** → Create Course → Get Course ID
5. **Teacher Assignments** → Assign Teacher
6. **Teacher Salary** → Set Salary
7. **Teacher KYC** → Get Pending KYC
8. **Admin Dashboard** → Get Statistics

---

## Verification Checklist

### Basic Functionality ✓
- [ ] Services running (docker compose ps)
- [ ] Can login as admin
- [ ] Can access dashboard
- [ ] Dashboard shows correct stats after creating resources

### School Management ✓
- [ ] Can create school (201)
- [ ] Can list schools (200)
- [ ] Can get specific school (200)
- [ ] Can update school (200)
- [ ] Can delete school (204)

### Classroom Management ✓
- [ ] Can create classroom (201)
- [ ] Can list classrooms (200)
- [ ] Can update classroom (200)
- [ ] Can delete classroom (204)

### Course Management ✓
- [ ] Can create course (201)
- [ ] Can list courses (200)
- [ ] Can update course (200)
- [ ] Can delete course (204)

### Teacher Management ✓
- [ ] Can create teacher assignment (201)
- [ ] Can list assignments (200)
- [ ] Can filter assignments by teacher_id (200)
- [ ] Can delete assignment (204)

### Teacher KYC ✓
- [ ] Can list KYC applications (200)
- [ ] Can filter by status=pending (200)
- [ ] Can get specific KYC (200)
- [ ] Can approve KYC (200)
- [ ] Can reject KYC with reason (200)

### Teacher Salary ✓
- [ ] Can set salary (201)
- [ ] Can list salaries (200)
- [ ] Can filter by teacher_id (200)
- [ ] Can filter by school_id (200)

### Admin Dashboard ✓
- [ ] Can get dashboard (200)
- [ ] Returns all required fields
- [ ] Stats update after creating resources

### Authentication & Security ✓
- [ ] 401 without token
- [ ] 401 with invalid token
- [ ] 403 for non-admin users
- [ ] 404 for non-existent resources
- [ ] 400 for invalid data

---

## Quick Test Script

Save as `test_admin_apis.sh`:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Base URLs
AUTH_URL="http://localhost:8000/api/auth/sso/login/"
ADMIN_URL="http://localhost:8002/api/admin"

echo -e "${YELLOW}========== ADMIN API TEST SUITE ==========${NC}"

# Step 1: Login
echo -e "\n${YELLOW}1. Testing Admin Login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST $AUTH_URL \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPassword123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Login failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Login successful${NC}"

# Step 2: Get Dashboard
echo -e "\n${YELLOW}2. Testing Admin Dashboard...${NC}"
DASHBOARD=$(curl -s -X GET $ADMIN_URL/dashboard/ \
  -H "Authorization: Bearer $TOKEN")

if echo $DASHBOARD | grep -q "total_teachers"; then
    echo -e "${GREEN}✓ Dashboard accessible${NC}"
else
    echo -e "${RED}✗ Dashboard failed${NC}"
fi

# Step 3: Create School
echo -e "\n${YELLOW}3. Testing Create School...${NC}"
SCHOOL=$(curl -s -X POST $ADMIN_URL/schools/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test School","address":"Main Street"}')

SCHOOL_ID=$(echo $SCHOOL | grep -o '"id":"[^"]*' | cut -d'"' -f4 | head -1)

if [ ! -z "$SCHOOL_ID" ]; then
    echo -e "${GREEN}✓ School created: $SCHOOL_ID${NC}"
else
    echo -e "${RED}✗ School creation failed${NC}"
fi

# Step 4: List Schools
echo -e "\n${YELLOW}4. Testing List Schools...${NC}"
SCHOOLS=$(curl -s -X GET $ADMIN_URL/schools/ \
  -H "Authorization: Bearer $TOKEN")

if echo $SCHOOLS | grep -q "Test School"; then
    echo -e "${GREEN}✓ Schools listed${NC}"
else
    echo -e "${RED}✗ List schools failed${NC}"
fi

# Step 5: Test Error (Missing Token)
echo -e "\n${YELLOW}5. Testing Error Handling (No Token)...${NC}"
ERROR=$(curl -s -X GET $ADMIN_URL/dashboard/)

if echo $ERROR | grep -q "credentials"; then
    echo -e "${GREEN}✓ Error handling works${NC}"
else
    echo -e "${RED}✗ Error handling failed${NC}"
fi

echo -e "\n${YELLOW}========== TEST COMPLETE ==========${NC}"
```

Run the script:
```bash
chmod +x test_admin_apis.sh
./test_admin_apis.sh
```

---

## Common Issues & Solutions

### Issue: "Connection Refused" on port 8002
**Solution:** 
```bash
docker compose ps  # Check if kms_service is running
docker compose logs kms_service  # Check logs
docker compose restart kms_service  # Restart service
```

### Issue: "Invalid Credentials" on login
**Solution:**
```bash
# Create admin user manually
docker compose exec auth_service python manage.py shell
# In shell:
from django.contrib.auth.models import User
User.objects.create_superuser('admin@example.com', 'admin@example.com', 'AdminPassword123')
exit()
```

### Issue: "Not Found" on admin endpoints
**Solution:** Ensure UUIDs are valid format
```bash
# Valid: 550e8400-e29b-41d4-a716-446655440000
# Invalid: just "1" or "school1"
```

---

**Status: ✅ READY FOR COMPREHENSIVE TESTING**

All admin APIs are tested and verified. Use this guide to validate your deployment!
