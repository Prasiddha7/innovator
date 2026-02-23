# Administrator APIs for Teacher Management

## Overview
Administrator APIs provide comprehensive management capabilities for teacher verification, assignment, and oversight.

---

## Authentication
All admin endpoints require JWT Bearer token with `admin` role:
```
Authorization: Bearer <admin_token>
```

---

## Teacher KYC Approval (Admin)

### Endpoint: Get All KYC Applications
**GET** `/api/admin/teacher-kyc/`

**Description:** Retrieve all teacher KYC applications with their verification status.

**Query Parameters:**
- `status` (optional): Filter by status - `pending`, `approved`, `rejected`
- `verified` (optional): Filter by verification stage - `phone`, `document`

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8002/api/admin/teacher-kyc/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "teacher": {
        "id": 2,
        "name": "John Teacher",
        "email": "john@example.com",
        "phone_number": "+1234567890"
      },
      "id_doc": "/media/kyc/id_doc_12345.pdf",
      "cv": "/media/kyc/cv_12345.pdf",
      "address": "123 Main Street",
      "status": "pending",
      "submitted_at": "2024-02-18T10:00:00Z",
      "phone_verified": false,
      "document_verified": false,
      "approval_date": null,
      "rejection_reason": null
    }
  ]
}
```

### Endpoint: Update KYC Status
**PUT** `/api/admin/teacher-kyc/<kyc_id>/`

**Description:** Approve or reject a KYC application.

**Request Body:**
```json
{
  "status": "approved",  // Can be: pending, approved, rejected
  "phone_verified": true,
  "document_verified": true,
  "rejection_reason": null  // Required if status is 'rejected'
}
```

**Example cURL - Approve:**
```bash
curl -X PUT http://localhost:8002/api/admin/teacher-kyc/uuid/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "phone_verified": true,
    "document_verified": true
  }'
```

**Example cURL - Reject:**
```bash
curl -X PUT http://localhost:8002/api/admin/teacher-kyc/uuid/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "rejection_reason": "Invalid documents. Please resubmit with clear copies."
  }'
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "teacher": 2,
  "id_doc": "/media/kyc/id_doc.pdf",
  "cv": "/media/kyc/cv.pdf",
  "address": "123 Main Street",
  "status": "approved",
  "submitted_at": "2024-02-18T10:00:00Z",
  "phone_verified": true,
  "document_verified": true,
  "approval_date": "2024-02-18T14:30:00Z",
  "rejection_reason": null
}
```

---

## Teacher Class Assignment (Admin)

### Endpoint: Assign Teacher to Classroom
**POST** `/api/admin/teacher-assignments/`

**Description:** Assign a teacher to teach a specific classroom.

**Request Body:**
```json
{
  "teacher_id": "uuid-of-teacher",
  "classroom_id": "uuid-of-classroom"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "teacher": {
    "id": "uuid",
    "name": "John Teacher",
    "email": "john@example.com"
  },
  "classroom": {
    "id": "uuid",
    "name": "Class 10-A",
    "school": {
      "id": "uuid",
      "name": "Delhi Public School"
    }
  },
  "assigned_at": "2024-02-18T14:30:00Z"
}
```

### Endpoint: Get All Teacher Assignments
**GET** `/api/admin/teacher-assignments/`

**Description:** View all teacher assignments.

**Query Parameters:**
- `teacher_id`: Filter by specific teacher
- `classroom_id`: Filter by specific classroom
- `school_id`: Filter by specific school

**Response (200 OK):**
```json
{
  "count": 50,
  "results": [
    {
      "id": "uuid",
      "teacher": "John Teacher",
      "classroom": "Class 10-A",
      "school": "Delhi Public School",
      "assigned_at": "2024-02-15T09:00:00Z",
      "students_count": 45
    }
  ]
}
```

---

## Teacher Salary Management (Admin)

### Endpoint: Set Teacher Salary for School
**POST** `/api/admin/teacher-salary/`

**Description:** Set monthly salary for a teacher at a specific school.

**Request Body:**
```json
{
  "teacher_id": "uuid",
  "school_id": "uuid",
  "monthly_salary": "50000.00"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "teacher": "John Teacher",
  "school": "Delhi Public School",
  "monthly_salary": "50000.00",
  "created_at": "2024-02-18T14:30:00Z",
  "updated_at": "2024-02-18T14:30:00Z"
}
```

### Endpoint: Update Teacher Salary
**PUT** `/api/admin/teacher-salary/<salary_id>/`

**Description:** Update an existing teacher salary record.

**Request Body:**
```json
{
  "monthly_salary": "55000.00"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "teacher": "John Teacher",
  "school": "Delhi Public School",
  "monthly_salary": "55000.00",
  "updated_at": "2024-02-18T15:00:00Z"
}
```

---

## School Management (Admin)

### Endpoint: Create/List Schools
**POST/GET** `/api/admin/schools/`

**POST - Create New School:**
```bash
curl -X POST http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Delhi Public School",
    "address": "123 Main Street, Delhi"
  }'
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Delhi Public School",
  "address": "123 Main Street, Delhi",
  "created_at": "2024-02-18T14:30:00Z"
}
```

**GET - List All Schools:**
```bash
curl -X GET http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer <admin_token>"
```

**Response (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid-1",
      "name": "Delhi Public School",
      "address": "123 Main Street, Delhi",
      "created_at": "2024-02-18T14:30:00Z"
    }
  ]
}
```

---

## Classroom Management (Admin)

### Endpoint: Create/List Classrooms
**POST/GET** `/api/admin/classrooms/`

**POST - Create New Classroom:**
```bash
curl -X POST http://localhost:8002/api/admin/classrooms/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Class 10-A",
    "school_id": "uuid"
  }'
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Class 10-A",
  "school": {
    "id": "uuid",
    "name": "Delhi Public School"
  },
  "created_at": "2024-02-18T14:30:00Z"
}
```

---

## Student Management (Admin)

### Endpoint: Create/List Students
**POST/GET** `/api/admin/students/`

**POST - Enroll Student:**
```bash
curl -X POST http://localhost:8002/api/admin/students/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Raj Kumar",
    "school_id": "uuid",
    "classroom_id": "uuid",
    "email": "raj@example.com"
  }'
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Raj Kumar",
  "school": "Delhi Public School",
  "classroom": "Class 10-A",
  "email": "raj@example.com",
  "created_at": "2024-02-18T14:30:00Z"
}
```

---

## Attendance Review (Admin/Principal)

### Endpoint: Get Classroom Attendance Summary
**GET** `/api/admin/attendance/summary/?classroom_id=<id>&date_range=<period>`

**Description:** Get comprehensive attendance summary for a classroom.

**Date Range Options:**
- `daily` - Current day only
- `weekly` - Last 7 days
- `monthly` - Last 30 days
- `custom` - Custom date range (requires start_date and end_date parameters)

**Example cURL:**
```bash
curl -X GET "http://localhost:8002/api/admin/attendance/summary/?classroom_id=uuid&date_range=monthly" \
  -H "Authorization: Bearer <admin_token>"
```

**Response (200 OK):**
```json
{
  "classroom": "Class 10-A",
  "semester_start": "2024-02-01",
  "semester_end": "2024-02-18",
  "total_working_days": 18,
  "class_attendance_rate": 92.5,
  "detailed_breakdown": {
    "present_percentage": 92.5,
    "absent_percentage": 4.2,
    "late_percentage": 2.1,
    "leave_percentage": 1.2
  },
  "students_below_threshold": [
    {
      "student_id": "uuid",
      "student_name": "Priya Singh",
      "attendance_percentage": 70.0,
      "total_absents": 5,
      "total_lates": 2
    }
  ]
}
```

---

## Admin Dashboard Data

### Endpoint: Get Administrator Dashboard Stats
**GET** `/api/admin/dashboard/stats/`

**Description:** Get overview statistics for administrator dashboard.

**Response (200 OK):**
```json
{
  "total_teachers": 50,
  "active_teachers": 48,
  "pending_kyc": 5,
  "approved_kyc": 40,
  "rejected_kyc": 5,
  "total_classrooms": 25,
  "total_students": 1250,
  "average_class_size": 50,
  "last_30_days_metrics": {
    "new_enrollments": 45,
    "new_assignments": 10,
    "attendance_rate": 92.3
  }
}
```

---

## Error Codes

| Code | Status | Message |
|------|--------|---------|
| 401 | Unauthorized | Invalid or missing token |
| 403 | Forbidden | Insufficient permissions (must be admin role) |
| 404 | Not Found | Resource not found |
| 400 | Bad Request | Invalid request data |
| 409 | Conflict | Duplicate assignment or constraint violation |

---

## Admin Workflow Example

### 1. Review Pending KYC Applications
```bash
curl -X GET "http://localhost:8002/api/admin/teacher-kyc/?status=pending" \
  -H "Authorization: Bearer <admin_token>"
```

### 2. Approve KYC Application
```bash
curl -X PUT http://localhost:8002/api/admin/teacher-kyc/kyc-uuid/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "phone_verified": true,
    "document_verified": true
  }'
```

### 3. Assign Teacher to Classroom
```bash
curl -X POST http://localhost:8002/api/admin/teacher-assignments/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_id": "teacher-uuid",
    "classroom_id": "classroom-uuid"
  }'
```

### 4. Set Teacher Salary
```bash
curl -X POST http://localhost:8002/api/admin/teacher-salary/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_id": "teacher-uuid",
    "school_id": "school-uuid",
    "monthly_salary": "50000.00"
  }'
```

### 5. Review Attendance
```bash
curl -X GET "http://localhost:8002/api/admin/attendance/summary/?classroom_id=classroom-uuid&date_range=monthly" \
  -H "Authorization: Bearer <admin_token>"
```

---

## Best Practices

1. **KYC Verification**: Always verify documents before approving
2. **Teacher Assignment**: Ensure teacher has required qualifications for the subject/class
3. **Salary Management**: Set salaries before adding teachers to improve record keeping
4. **Attendance Monitoring**: Review attendance patterns weekly to identify issues early
5. **Multi-School Teachers**: Track salaries separately for each school to ensure accurate billing

---
