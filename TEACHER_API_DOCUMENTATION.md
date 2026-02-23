# Teacher API Comprehensive Documentation

## Overview
The Teacher API provides complete functionality for teacher role management in the Innovator microservices architecture. Teachers can manage their KYC verification, supervise student attendance, view their assigned classes, and track earnings.

---

## Authentication
All endpoints require JWT Bearer token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Teacher Profile Endpoints

### 1. Get Teacher Profile
**Endpoint:** `GET /api/teacher/profile/`

**Description:** Retrieve the complete teacher profile including classes, earnings, and KYC status.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "2",
  "name": "testuser@example.com",
  "email": "testuser@example.com",
  "phone_number": "+1234567890",
  "is_active": true,
  "classes_count": 3,
  "classes": [
    {
      "classroom_id": "uuid",
      "classroom_name": "Class 10-A",
      "school_id": "uuid",
      "school_name": "School Name"
    }
  ],
  "total_earnings": "50000.00",
  "salaries": [
    {
      "school_id": "uuid",
      "school_name": "School Name",
      "monthly_salary": "25000.00",
      "classes_in_school": 2
    }
  ],
  "kyc": {
    "id": "uuid",
    "status": "approved",
    "phone_verified": true,
    "document_verified": true
  }
}
```

---

## KYC Management Endpoints

### 2. Upload/Update KYC
**Endpoint:** `POST /api/teacher/kyc/upload/`

**Description:** Upload teacher KYC documents (ID document, CV, Address).

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
id_doc: <file>        # Identity document (PDF, JPG, PNG)
cv: <file>            # Curriculum Vitae (PDF, DOC, DOCX)
address: <string>     # Address text
phone: <string>       # Phone number (optional)
```

**Example cURL:**
```bash
curl -X POST http://localhost:8002/api/teacher/kyc/upload/ \
  -H "Authorization: Bearer <token>" \
  -F "id_doc=@/path/to/id.pdf" \
  -F "cv=@/path/to/cv.pdf" \
  -F "address=123 Main Street" \
  -F "phone=+1234567890"
```

**Response (201 Created):**
```json
{
  "message": "KYC submitted successfully",
  "kyc": {
    "id": "uuid",
    "teacher": 2,
    "id_doc": "/media/kyc/id_doc_filename.pdf",
    "cv": "/media/kyc/cv_filename.pdf",
    "address": "123 Main Street",
    "status": "pending",
    "submitted_at": "2024-02-18T10:00:00Z"
  }
}
```

### 3. Get KYC Status
**Endpoint:** `GET /api/teacher/kyc/status/`

**Description:** Check the current KYC application status.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "teacher": 2,
  "id_doc": "/media/kyc/id_doc_filename.pdf",
  "cv": "/media/kyc/cv_filename.pdf",
  "address": "123 Main Street",
  "status": "approved",
  "submitted_at": "2024-02-18T10:00:00Z",
  "phone_verified": true,
  "document_verified": true,
  "approval_date": "2024-02-18T15:00:00Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "KYC not found. Please submit your KYC first."
}
```

---

## Class Management Endpoints

### 4. Get Teacher's Classes
**Endpoint:** `GET /api/teacher/classes/`

**Description:** View all classes/classrooms assigned to the teacher.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "total_classes": 3,
  "classes": [
    {
      "classroom_id": "uuid-1",
      "classroom_name": "Class 10-A",
      "school_id": "uuid-school-1",
      "school_name": "Delhi Public School",
      "assigned_at": "2024-02-15T09:00:00Z",
      "students_count": 45
    },
    {
      "classroom_id": "uuid-2",
      "classroom_name": "Class 10-B",
      "school_id": "uuid-school-1",
      "school_name": "Delhi Public School",
      "assigned_at": "2024-02-15T09:00:00Z",
      "students_count": 42
    }
  ]
}
```

---

## Student Attendance Endpoints

### 5. Get Student List with Attendance Status
**Endpoint:** `GET /api/teacher/attendance/students/?classroom_id=<id>&date=<YYYY-MM-DD>`

**Description:** View all students in a classroom with their attendance status for a specific date.

**Query Parameters:**
- `classroom_id` (required): UUID of the classroom
- `date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Request Headers:**
```
Authorization: Bearer <token>
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8002/api/teacher/attendance/students/?classroom_id=uuid&date=2024-02-18" \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "classroom": "Class 10-A",
  "date": "2024-02-18",
  "total_students": 45,
  "students": [
    {
      "student_id": "uuid-1",
      "student_name": "Raj Kumar",
      "attendance_id": "uuid-att-1",
      "status": "present",
      "marked_at": "2024-02-18T09:00:00Z",
      "date": "2024-02-18"
    },
    {
      "student_id": "uuid-2",
      "student_name": "Priya Singh",
      "attendance_id": null,
      "status": null,
      "marked_at": null,
      "date": "2024-02-18"
    }
  ]
}
```

### 6. Mark Single Student Attendance
**Endpoint:** `POST /api/teacher/attendance/mark/`

**Description:** Mark attendance status for a single student.

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "student_id": "uuid",
  "classroom_id": "uuid",
  "date": "2024-02-18",
  "status": "present",  // Can be: present, absent, late, sick_leave, casual_leave
  "notes": "Student was late but participated."
}
```

**Response (201 Created):**
```json
{
  "message": "Attendance marked successfully",
  "attendance": {
    "id": "uuid",
    "student": "Raj Kumar",
    "classroom": "Class 10-A",
    "teacher": "testuser@example.com",
    "date": "2024-02-18",
    "status": "present",
    "marked_by": "testuser@example.com",
    "marked_at": "2024-02-18T09:00:00Z",
    "notes": "Student was late but participated."
  }
}
```

**Response (400 Bad Request):**
```json
{
  "student_id": ["This field may not be null."],
  "classroom_id": ["This field may not be null."],
  "date": ["Invalid date format. Use YYYY-MM-DD."]
}
```

### 7. Mark Bulk Student Attendance
**Endpoint:** `POST /api/teacher/attendance/bulk-mark/`

**Description:** Mark attendance for multiple students in a single request.

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "classroom_id": "uuid",
  "date": "2024-02-18",
  "attendances": [
    {
      "student_id": "uuid-1",
      "status": "present",
      "notes": ""
    },
    {
      "student_id": "uuid-2",
      "status": "absent",
      "notes": "Did not come to school"
    },
    {
      "student_id": "uuid-3",
      "status": "late",
      "notes": "Late by 15 minutes"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "message": "Attendance marked for 3 students",
  "count": 3,
  "date": "2024-02-18",
  "attendances": [
    {
      "id": "uuid-1",
      "student": "Raj Kumar",
      "status": "present",
      "marked_at": "2024-02-18T09:00:00Z"
    },
    {
      "id": "uuid-2",
      "student": "Priya Singh",
      "status": "absent",
      "marked_at": "2024-02-18T09:00:00Z"
    }
  ]
}
```

### 8. Get Attendance Report
**Endpoint:** `GET /api/teacher/attendance/report/?classroom_id=<id>&start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>`

**Description:** Get detailed attendance analytics for a classroom over a date range.

**Query Parameters:**
- `classroom_id` (required): UUID of the classroom
- `start_date` (optional): Start date in YYYY-MM-DD format (defaults to 30 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (defaults to today)

**Example cURL:**
```bash
curl -X GET "http://localhost:8002/api/teacher/attendance/report/?classroom_id=uuid&start_date=2024-02-01&end_date=2024-02-18" \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "classroom": "Class 10-A",
  "start_date": "2024-02-01",
  "end_date": "2024-02-18",
  "total_records": 810,
  "present": 750,
  "absent": 40,
  "late": 15,
  "leave": 5,
  "attendance_percentage": 92.59,
  "daily_breakdown": {
    "2024-02-01": {
      "total": 45,
      "present": 42,
      "percentage": 93.33
    },
    "2024-02-02": {
      "total": 45,
      "present": 44,
      "percentage": 97.78
    },
    "2024-02-18": {
      "total": 45,
      "present": 44,
      "percentage": 97.78
    }
  }
}
```

---

## Earnings & Salary Endpoints

### 9. Get Teacher Earnings and Salary
**Endpoint:** `GET /api/teacher/earnings/`

**Description:** View teacher's salary breakdown by school and total earnings.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "teacher_name": "testuser@example.com",
  "total_monthly_earnings": 75000.0,
  "total_classes": 3,
  "total_schools": 2,
  "salary_breakdown": [
    {
      "school_id": "uuid-1",
      "school_name": "Delhi Public School",
      "monthly_salary": 50000.0,
      "classes_in_school": 2
    },
    {
      "school_id": "uuid-2",
      "school_name": "St. Xavier School",
      "monthly_salary": 25000.0,
      "classes_in_school": 1
    }
  ],
  "cumulative_earnings": 525000.0
}
```

---

## Error Responses

### 401 Unauthorized - Invalid/Missing Token
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid"
    }
  ]
}
```

### 403 Forbidden - No Access to Classroom
```json
{
  "detail": "You don't have access to this classroom"
}
```

### 404 Not Found - Teacher/Classroom Not Found
```json
{
  "detail": "Teacher profile not found" 
}
```

---

## Attendance Status Values
- `present` - Student was present
- `absent` - Student was absent
- `late` - Student arrived late
- `sick_leave` - Student was on sick leave
- `casual_leave` - Student was on casual leave

---

## Example Workflow

### 1. Teacher Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@example.com","password":"password"}'
```

### 2. Check Teacher Profile
```bash
curl -X GET http://localhost:8002/api/teacher/profile/ \
  -H "Authorization: Bearer <token>"
```

### 3. Upload KYC Documents
```bash
curl -X POST http://localhost:8002/api/teacher/kyc/upload/ \
  -H "Authorization: Bearer <token>" \
  -F "id_doc=@id.pdf" \
  -F "cv=@cv.pdf" \
  -F "address=My Street Address"
```

### 4. View Assigned Classes
```bash
curl -X GET http://localhost:8002/api/teacher/classes/ \
  -H "Authorization: Bearer <token>"
```

### 5. Mark Student Attendance (Bulk)
```bash
curl -X POST http://localhost:8002/api/teacher/attendance/bulk-mark/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_id": "uuid",
    "date": "2024-02-18",
    "attendances": [
      {"student_id": "uuid1", "status": "present"},
      {"student_id": "uuid2", "status": "absent"},
      {"student_id": "uuid3", "status": "late"}
    ]
  }'
```

### 6. Get Attendance Report
```bash
curl -X GET "http://localhost:8002/api/teacher/attendance/report/?classroom_id=uuid&start_date=2024-02-01&end_date=2024-02-18" \
  -H "Authorization: Bearer <token>"
```

### 7. View Earnings
```bash
curl -X GET http://localhost:8002/api/teacher/earnings/ \
  -H "Authorization: Bearer <token>"
```

---

## Features Summary

✅ **Teacher Profile Management**
- View complete profile with classes and earnings
- Track cumulative earnings across schools
- Monitor number of classes per school

✅ **KYC Verification**
- Upload identity documents and CV
- Document verification status tracking
- Phone number verification support

✅ **Class Management**
- View all assigned classrooms
- See student count per class
- Track assignment dates

✅ **Student Attendance**
- Mark individual student attendance
- Bulk attendance marking for efficiency
- Multiple attendance statuses (present, absent, late, leave)
- Add notes for each attendance record

✅ **Attendance Analytics**
- Daily attendance breakdown
- Overall attendance percentage
- Date range filtering
- Attendance statistics by status type

✅ **Salary Tracking**
- Per-school salary information
- Multiple enrollment support
- Cumulative earnings calculation

---

## Database Operations Features
- Automatic database indices on frequently queried fields (teacher+date, classroom+date)
- Unique constraints to prevent duplicate attendance records
- Transaction support for bulk operations
- Timestamp tracking for all operations
