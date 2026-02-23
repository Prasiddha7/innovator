# Admin APIs - Complete URL Reference

## **Authentication**
All admin endpoints require:
1. **Login as admin user via SSO**
2. **Use role="admin" in JWT token**
3. **Include JWT token in Authorization header**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPassword123"}'

# Response includes token with role: "admin"
# Then use: Authorization: Bearer <token>
```

---

## **ADMIN MANAGEMENT ENDPOINTS**

### **1. SCHOOL MANAGEMENT**

#### List All Schools
```
GET /api/admin/schools/
```

#### Get Specific School
```
GET /api/admin/schools/{school_id}/
```

#### Create School
```
POST /api/admin/schools/

Body:
{
  "name": "Delhi Public School",
  "address": "123 Main Street, Delhi"
}
```

#### Update School
```
PUT /api/admin/schools/{school_id}/

Body:
{
  "name": "Updated School Name",
  "address": "New Address"
}
```

#### Delete School
```
DELETE /api/admin/schools/{school_id}/
```

---

### **2. CLASSROOM MANAGEMENT**

#### List All Classrooms
```
GET /api/admin/classrooms/
```

#### Get Specific Classroom
```
GET /api/admin/classrooms/{classroom_id}/
```

#### Create Classroom
```
POST /api/admin/classrooms/

Body:
{
  "name": "Class 10-A",
  "school": "school_id_uuid"
}
```

#### Update Classroom
```
PUT /api/admin/classrooms/{classroom_id}/

Body:
{
  "name": "Class 10-B"
}
```

#### Delete Classroom
```
DELETE /api/admin/classrooms/{classroom_id}/
```

---

### **3. COURSE MANAGEMENT**

#### List All Courses
```
GET /api/admin/courses/
```

#### Get Specific Course
```
GET /api/admin/courses/{course_id}/
```

#### Create Course
```
POST /api/admin/courses/

Body:
{
  "title": "Mathematics",
  "school": "school_id_uuid",
  "status": "active"
}
```

#### Update Course
```
PUT /api/admin/courses/{course_id}/

Body:
{
  "title": "Advanced Mathematics",
  "status": "active"
}
```

#### Delete Course
```
DELETE /api/admin/courses/{course_id}/
```

---

### **4. TEACHER TO CLASSROOM ASSIGNMENT**

#### List All Teacher Assignments
```
GET /api/admin/teacher-assignments/

Query Parameters (optional):
- ?teacher_id=uuid      (filter by teacher)
- ?classroom_id=uuid    (filter by classroom)
```

#### Assign Teacher to Classroom
```
POST /api/admin/teacher-assignments/

Body:
{
  "teacher": "teacher_uuid",
  "classroom": "classroom_uuid"
}
```

#### Remove Teacher from Classroom
```
DELETE /api/admin/teacher-assignments/{assignment_id}/
```

---

### **5. TEACHER KYC VERIFICATION**

#### List All KYC Applications
```
GET /api/admin/teacher-kyc/

Query Parameters (optional):
- ?status=pending       (pending, approved, rejected)
```

#### Get Specific KYC
```
GET /api/admin/teacher-kyc/{kyc_id}/
```

#### Approve KYC Application
```
PUT /api/admin/teacher-kyc/{kyc_id}/

Body:
{
  "action": "approve",
  "phone_verified": true,
  "document_verified": true
}
```

#### Reject KYC Application
```
PUT /api/admin/teacher-kyc/{kyc_id}/

Body:
{
  "action": "reject",
  "rejection_reason": "Invalid documents. Please resubmit with clearer copies."
}
```

---

### **6. TEACHER SALARY MANAGEMENT**

#### View All Salaries
```
GET /api/admin/teacher-salary/

Query Parameters (optional):
- ?teacher_id=uuid     (filter by teacher)
- ?school_id=uuid      (filter by school)
```

#### Set Teacher Salary for School
```
POST /api/admin/teacher-salary/

Body:
{
  "teacher_id": "teacher_uuid",
  "school_id": "school_uuid",
  "monthly_salary": "50000.00"
}
```

---

### **7. ADMIN DASHBOARD**

#### Get Dashboard Statistics
```
GET /api/admin/dashboard/

Response includes:
{
  "total_teachers": 25,
  "total_schools": 5,
  "total_classrooms": 20,
  "total_students": 500,
  "kyc_applications": {
    "pending": 3,
    "approved": 20,
    "rejected": 2
  },
  "teacher_assignments": 45,
  "today_attendance_rate": 92.5
}
```

---

## **COMPLETE CURL EXAMPLES**

### **Create School**
```bash
curl -X POST http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "St. Xavier School",
    "address": "Delhi"
  }'
```

### **Create Classroom**
```bash
curl -X POST http://localhost:8002/api/admin/classrooms/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Class 9-A",
    "school": "SCHOOL_UUID"
  }'
```

### **Assign Teacher to Classroom**
```bash
curl -X POST http://localhost:8002/api/admin/teacher-assignments/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher": "TEACHER_UUID",
    "classroom": "CLASSROOM_UUID"
  }'
```

### **Set Teacher Salary**
```bash
curl -X POST http://localhost:8002/api/admin/teacher-salary/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_id": "TEACHER_UUID",
    "school_id": "SCHOOL_UUID",
    "monthly_salary": "50000.00"
  }'
```

### **Approve KYC**
```bash
curl -X PUT http://localhost:8002/api/admin/teacher-kyc/KYC_UUID/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "phone_verified": true,
    "document_verified": true
  }'
```

### **Reject KYC**
```bash
curl -X PUT http://localhost:8002/api/admin/teacher-kyc/KYC_UUID/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "rejection_reason": "Documents not clear"
  }'
```

### **Get Admin Dashboard**
```bash
curl -X GET http://localhost:8002/api/admin/dashboard/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## **ERROR RESPONSES**

### **401 Unauthorized - Invalid/Missing Token**
```json
{
  "detail": "Given token not valid for any token type"
}
```

### **403 Forbidden - Not Admin Role**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### **404 Not Found**
```json
{
  "detail": "Not found."
}
```

### **400 Bad Request**
```json
{
  "field": ["Error message"]
}
```

---

## **ADMIN WORKFLOW EXAMPLE**

### **Step 1: Admin Login**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
```

### **Step 2: Create School**
```bash
SCHOOL=$(curl -s -X POST http://localhost:8002/api/admin/schools/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"DPS Delhi","address":"123 Main St"}' \
  | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
```

### **Step 3: Create Classroom**
```bash
CLASSROOM=$(curl -s -X POST http://localhost:8002/api/admin/classrooms/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Class 10-A\",\"school\":\"$SCHOOL\"}" \
  | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
```

### **Step 4: Assign Teacher**
```bash
curl -X POST http://localhost:8002/api/admin/teacher-assignments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"teacher\":\"TEACHER_UUID\",\"classroom\":\"$CLASSROOM\"}"
```

### **Step 5: Set Teacher Salary**
```bash
curl -X POST http://localhost:8002/api/admin/teacher-salary/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"teacher_id\":\"TEACHER_UUID\",\"school_id\":\"$SCHOOL\",\"monthly_salary\":\"50000\"}"
```

### **Step 6: Approve Teacher KYC**
```bash
curl -X PUT http://localhost:8002/api/admin/teacher-kyc/KYC_UUID/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","phone_verified":true,"document_verified":true}'
```

### **Step 7: View Dashboard**
```bash
curl -X GET http://localhost:8002/api/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## **POSTMAN COLLECTION SETUP**

### **Environment Variables:**
```
admin_token = <JWT token from login>
school_id = <UUID from create school>
classroom_id = <UUID from create classroom>
teacher_id = <Teacher UUID>
kyc_id = <KYC UUID>
```

### **Pre-request Scripts:**
For auto-token refresh, add to Pre-request Script:
```javascript
// Get fresh token before each admin request
if (!pm.environment.get('admin_token')) {
    pm.sendRequest({
        url: 'http://localhost:8000/api/auth/sso/login/',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                email: 'admin@example.com',
                password: 'AdminPassword123'
            })
        }
    }, function (err, response) {
        pm.environment.set('admin_token', response.json().access_token);
    });
}
```

---

## **QUICK REFERENCE TABLE**

| Resource | GET | POST | PUT | DELETE |
|----------|-----|------|-----|--------|
| Schools | List | Create | Update | Delete |
| Classrooms | List | Create | Update | Delete |
| Courses | List | Create | Update | Delete |
| Teacher Assignments | List | Assign | - | Remove |
| KYC Applications | List | - | Approve/Reject | - |
| Salaries | List | Set | - | - |
| Dashboard | Stats | - | - | - |

---

## **IMPORTANT NOTES**

✅ **Admin Login Required:** All endpoints require `role: admin` in JWT token
✅ **School ID Format:** Use UUID format (e.g., `550e8400-e29b-41d4-a716-446655440000`)
✅ **Permissions:** Only admin role can access these endpoints
✅ **Data Validation:** All required fields must be provided
✅ **Unique Constraints:** Cannot assign same teacher to same classroom twice

---
