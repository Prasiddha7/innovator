#!/bin/bash

# Comprehensive Teacher API Integration Test
# This script tests all teacher API endpoints with realistic workflows

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="http://localhost:8002"
AUTH_API="http://localhost:8000"
TEACHER_EMAIL="testuser@example.com"
TEACHER_PASSWORD="TestPassword123"

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_test() {
  echo -e "${BLUE}▶ $1${NC}"
}

log_success() {
  echo -e "${GREEN}✓ $1${NC}"
  ((TESTS_PASSED++))
}

log_error() {
  echo -e "${RED}✗ $1${NC}"
  ((TESTS_FAILED++))
}

log_info() {
  echo -e "${YELLOW}ℹ $1${NC}"
}

check_status() {
  local status=$1
  local expected=$2
  local message=$3
  
  if [ "$status" == "$expected" ]; then
    log_success "$message (HTTP $status)"
    return 0
  else
    log_error "$message (Expected $expected, got $status)"
    return 1
  fi
}

# Extract response body and HTTP code
extract_response() {
  local response=$1
  # Get last line (HTTP code)
  echo "$response" | tail -1
}

extract_body() {
  local response=$1
  # Get everything except last line
  echo "$response" | sed '$d'
}

# Main test suite
echo -e "${YELLOW}════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}   Teacher API Integration Test Suite${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════${NC}\n"

# Test 1: Get JWT Token
echo -e "\n${YELLOW}=== Section 1: Authentication ===${NC}\n"
log_test "Getting JWT token..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$AUTH_API/api/auth/sso/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEACHER_EMAIL\",\"password\":\"$TEACHER_PASSWORD\"}")

HTTP_CODE=$(extract_response "$LOGIN_RESPONSE")
RESPONSE_BODY=$(extract_body "$LOGIN_RESPONSE")

if check_status "$HTTP_CODE" "200" "JWT Token obtained"; then
  ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  TEACHER_ID=$(echo "$RESPONSE_BODY" | grep -o '"user":{"id":[0-9]*' | grep -o '[0-9]*')
  log_info "Access Token: ${ACCESS_TOKEN:0:20}..."
  log_info "Teacher ID: $TEACHER_ID"
else
  log_error "Failed to obtain token. Response: $RESPONSE_BODY"
  exit 1
fi

# Test 2: Get Teacher Profile
echo -e "\n${YELLOW}=== Section 2: Teacher Profile ===${NC}\n"
log_test "Getting teacher profile..."
PROFILE_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/profile/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$PROFILE_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$PROFILE_RESPONSE" | head -n-1)

if check_status "$HTTP_CODE" "200" "Teacher profile retrieved"; then
  CLASSES_COUNT=$(echo "$RESPONSE_BODY" | grep -o '"classes_count":[0-9]*' | cut -d':' -f2)
  TOTAL_EARNINGS=$(echo "$RESPONSE_BODY" | grep -o '"total_earnings":"[^"]*' | cut -d'"' -f4)
  log_info "Classes Assigned: $CLASSES_COUNT"
  log_info "Total Earnings: $TOTAL_EARNINGS"
else
  log_error "Failed to retrieve profile. Response: $RESPONSE_BODY"
fi

# Test 3: Get Teacher Classes
echo -e "\n${YELLOW}=== Section 3: Class Management ===${NC}\n"
log_test "Getting teacher classes..."
CLASSES_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/classes/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$CLASSES_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$CLASSES_RESPONSE" | head -n-1)

if check_status "$HTTP_CODE" "200" "Classes retrieved"; then
  TOTAL_CLASSES=$(echo "$RESPONSE_BODY" | grep -o '"total_classes":[0-9]*' | cut -d':' -f2)
  log_info "Total Classes: $TOTAL_CLASSES"
  
  # Extract classroom ID for further tests
  CLASSROOM_ID=$(echo "$RESPONSE_BODY" | grep -o '"classroom_id":"[^"]*' | head -1 | cut -d'"' -f4)
  if [ ! -z "$CLASSROOM_ID" ]; then
    log_info "First Classroom ID: $CLASSROOM_ID"
  else
    log_info "No classrooms assigned yet"
  fi
else
  log_error "Failed to retrieve classes. Response: $RESPONSE_BODY"
fi

# Test 4: Get KYC Status
echo -e "\n${YELLOW}=== Section 4: KYC Management ===${NC}\n"
log_test "Checking KYC status..."
KYC_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/kyc/status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$KYC_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$KYC_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" == "200" ]; then
  log_success "KYC found"
  KYC_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
  log_info "KYC Status: $KYC_STATUS"
elif [ "$HTTP_CODE" == "404" ]; then
  log_success "KYC not yet submitted (expected)"
  log_info "Teacher needs to upload KYC documents"
else
  log_error "Unexpected response. HTTP $HTTP_CODE"
fi

# Test 5: Get Earnings
echo -e "\n${YELLOW}=== Section 5: Earnings & Salary ===${NC}\n"
log_test "Getting teacher earnings..."
EARNINGS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/earnings/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$EARNINGS_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$EARNINGS_RESPONSE" | head -n-1)

if check_status "$HTTP_CODE" "200" "Earnings retrieved"; then
  MONTHLY_EARNINGS=$(echo "$RESPONSE_BODY" | grep -o '"total_monthly_earnings":[0-9.]*' | cut -d':' -f2)
  TOTAL_SCHOOLS=$(echo "$RESPONSE_BODY" | grep -o '"total_schools":[0-9]*' | cut -d':' -f2)
  CUMULATIVE=$(echo "$RESPONSE_BODY" | grep -o '"cumulative_earnings":[0-9.]*' | cut -d':' -f2)
  log_info "Monthly Earnings: $$MONTHLY_EARNINGS"
  log_info "Schools: $TOTAL_SCHOOLS"
  log_info "Cumulative Earnings: $$CUMULATIVE"
else
  log_error "Failed to retrieve earnings. Response: $RESPONSE_BODY"
fi

# Test 6: Attendance - Get Student List (if classroom assigned)
if [ ! -z "$CLASSROOM_ID" ]; then
  echo -e "\n${YELLOW}=== Section 6: Attendance Management ===${NC}\n"
  
  log_test "Getting student list for attendance..."
  STUDENTS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/attendance/students/?classroom_id=$CLASSROOM_ID&date=2024-02-18" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  
  HTTP_CODE=$(echo "$STUDENTS_RESPONSE" | tail -1)
  RESPONSE_BODY=$(echo "$STUDENTS_RESPONSE" | head -n-1)
  
  if check_status "$HTTP_CODE" "200" "Student list retrieved"; then
    TOTAL_STUDENTS=$(echo "$RESPONSE_BODY" | grep -o '"total_students":[0-9]*' | cut -d':' -f2)
    log_info "Total Students: $TOTAL_STUDENTS"
  else
    log_error "Failed to retrieve students. Response: $RESPONSE_BODY"
  fi
  
  # Test 7: Mark Single Attendance
  log_test "Testing single student attendance marking..."
  FIRST_STUDENT=$(echo "$RESPONSE_BODY" | grep -o '"student_id":"[^"]*' | head -1 | cut -d'"' -f4)
  
  if [ ! -z "$FIRST_STUDENT" ]; then
    MARK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/teacher/attendance/mark/" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"student_id\": \"$FIRST_STUDENT\",
        \"classroom_id\": \"$CLASSROOM_ID\",
        \"date\": \"2024-02-18\",
        \"status\": \"present\",
        \"notes\": \"Test attendance mark\"
      }")
    
    HTTP_CODE=$(echo "$MARK_RESPONSE" | tail -1)
    RESPONSE_BODY=$(echo "$MARK_RESPONSE" | head -n-1)
    
    if check_status "$HTTP_CODE" "201" "Single attendance marked"; then
      ATTENDANCE_ID=$(echo "$RESPONSE_BODY" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
      log_info "Attendance ID: $ATTENDANCE_ID"
    else
      log_error "Failed to mark attendance. Response: $RESPONSE_BODY"
    fi
  fi
  
  # Test 8: Test Invalid Token
  echo -e "\n${YELLOW}=== Section 7: Error Handling ===${NC}\n"
  
  log_test "Testing with invalid token..."
  INVALID_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/profile/" \
    -H "Authorization: Bearer invalid_token_12345")
  
  HTTP_CODE=$(echo "$INVALID_RESPONSE" | tail -1)
  if check_status "$HTTP_CODE" "401" "Invalid token correctly rejected"; then
    true
  fi
  
  # Test 9: Test without token
  log_test "Testing without authentication token..."
  NO_AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/profile/")
  
  HTTP_CODE=$(echo "$NO_AUTH_RESPONSE" | tail -1)
  if check_status "$HTTP_CODE" "401" "Missing token correctly rejected"; then
    true
  fi
  
  # Test 10: Get Attendance Report
  log_test "Getting attendance report..."
  REPORT_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/teacher/attendance/report/?classroom_id=$CLASSROOM_ID&start_date=2024-02-01&end_date=2024-02-18" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  
  HTTP_CODE=$(echo "$REPORT_RESPONSE" | tail -1)
  RESPONSE_BODY=$(echo "$REPORT_RESPONSE" | head -n-1)
  
  if check_status "$HTTP_CODE" "200" "Attendance report generated"; then
    ATTENDANCE_PCT=$(echo "$RESPONSE_BODY" | grep -o '"attendance_percentage":[0-9.]*' | cut -d':' -f2)
    TOTAL_RECORDS=$(echo "$RESPONSE_BODY" | grep -o '"total_records":[0-9]*' | cut -d':' -f2)
    log_info "Attendance %: $ATTENDANCE_PCT"
    log_info "Total Records: $TOTAL_RECORDS"
  else
    log_error "Failed to generate report. Response: $RESPONSE_BODY"
  fi
else
  log_info "Skipping attendance tests (no classroom assigned)"
fi

# Final Summary
echo -e "\n${YELLOW}════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}                 Test Summary${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════${NC}\n"

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed! ($TESTS_PASSED/$((TESTS_PASSED + TESTS_FAILED)))${NC}\n"
  exit 0
else
  echo -e "${RED}✗ Some tests failed!${NC}"
  echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
  echo -e "${RED}Failed: $TESTS_FAILED${NC}\n"
  exit 1
fi
