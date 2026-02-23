# Teacher API Quick Start Guide

## 5-Minute Setup

### Prerequisites
- JWT token from login
- Teacher account with role='teacher'
- Access to microservices (running on Docker)

---

## Step 1: Get Your JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "your_password"
  }'
```

**Save the `access_token` from response**

---

## Step 2: Check Your Profile

```bash
curl -X GET http://localhost:8002/api/teacher/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected response: Your profile with classes, earnings, and KYC status

---

## Step 3: Upload KYC (If Not Already Done)

```bash
curl -X POST http://localhost:8002/api/teacher/kyc/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "id_doc=@/path/to/your_id.pdf" \
  -F "cv=@/path/to/your_cv.pdf" \
  -F "address=Your Street Address" \
  -F "phone=+1234567890"
```

Wait for admin approval before marking attendance

---

## Step 4: View Your Classes

```bash
curl -X GET http://localhost:8002/api/teacher/classes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Save the `classroom_id` for marking attendance**

---

## Step 5: Mark Student Attendance (Quick Method - Bulk)

```bash
curl -X POST http://localhost:8002/api/teacher/attendance/bulk-mark/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_id": "YOUR_CLASSROOM_ID",
    "date": "2024-02-18",
    "attendances": [
      {"student_id": "student_uuid_1", "status": "present"},
      {"student_id": "student_uuid_2", "status": "absent"},
      {"student_id": "student_uuid_3", "status": "late", "notes": "15 minutes late"}
    ]
  }'
```

---

## Common Operations

### Get Student List Before Marking Attendance

```bash
curl -X GET "http://localhost:8002/api/teacher/attendance/students/?classroom_id=YOUR_CLASSROOM_ID&date=2024-02-18" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response includes all students - use their IDs in bulk-mark request

---

### Mark Single Student Attendance

```bash
curl -X POST http://localhost:8002/api/teacher/attendance/mark/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_uuid",
    "classroom_id": "classroom_uuid",
    "date": "2024-02-18",
    "status": "present",
    "notes": "Optional notes"
  }'
```

---

### Get Attendance Report (Analytics)

```bash
curl -X GET "http://localhost:8002/api/teacher/attendance/report/?classroom_id=YOUR_CLASSROOM_ID&start_date=2024-02-01&end_date=2024-02-18" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Shows: Total attendance rate, daily breakdown, absence trends

---

### View Your Earnings

```bash
curl -X GET http://localhost:8002/api/teacher/earnings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Shows: Monthly salary per school, total classes, cumulative earnings

---

## Attendance Status Quick Reference

| Status | Code | When to Use |
|--------|------|-------------|
| Present | `present` | Student attended class |
| Absent | `absent` | Student did not come |
| Late | `late` | Student arrived after class started |
| Sick Leave | `sick_leave` | Student has valid medical excuse |
| Casual Leave | `casual_leave` | Student has prior permission to be absent |

---

## Troubleshooting

### "Given token not valid for any token type"
→ Token expired or invalid. Get a new token using Step 1

### "You don't have access to this classroom"
→ You're not assigned to this classroom. Check your classes list

### "KYC not found. Please submit your KYC first."
→ Upload your KYC documents first. Use Step 3

### "Teacher profile not found"
→ Contact admin. Issue with teacher account setup

### 404 Errors on Endpoints
→ Check classroom_id and student_id match your classes/students

---

## API Endpoints Summary

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Get Profile | GET | `/api/teacher/profile/` |
| Upload KYC | POST | `/api/teacher/kyc/upload/` |
| View Classes | GET | `/api/teacher/classes/` |
| Get Students | GET | `/api/teacher/attendance/students/` |
| Mark Single | POST | `/api/teacher/attendance/mark/` |
| Mark Bulk | POST | `/api/teacher/attendance/bulk-mark/` |
| Get Report | GET | `/api/teacher/attendance/report/` |
| View Earnings | GET | `/api/teacher/earnings/` |

---

## Daily Workflow

**Morning:**
1. Login and get new token (if old one expired)
2. Check your classes: `GET /api/teacher/classes/`
3. For each class, get student list: `GET /api/teacher/attendance/students/`
4. Mark attendance: `POST /api/teacher/attendance/bulk-mark/`

**Weekly:**
1. Review attendance reports: `GET /api/teacher/attendance/report/`
2. Check earnings: `GET /api/teacher/earnings/`

**Monthly:**
1. Review salary breakdown in earnings endpoint
2. Check total cumulative earnings

---

## Postman Collection

Import the provided Postman collection for easy API testing:
- File: `Innovator_Microservices_JWT.postman_collection.json`
- Pre-configured with all endpoints
- Automatic JWT token handling

---

## Support

For issues or feature requests:
1. Check TEACHER_API_DOCUMENTATION.md for detailed API specs
2. Verify token validity
3. Check error message and error codes section
4. Contact administrator if account issues persist

---
