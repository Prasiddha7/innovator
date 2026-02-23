# Postman Testing Guide - Innovator Microservices JWT

## Quick Start

### 1. Import Collection
1. Open **Postman**
2. Click **Import** (top left)
3. Select **Upload Files**
4. Choose: `Innovator_Microservices_JWT.postman_collection.json`
5. Click **Import**

### 2. Verify Environment Variables
The collection includes pre-configured variables:
- `auth_url`: `http://localhost:8000` (Auth Service)
- `kms_url`: `http://localhost:8002` (KMS Service)
- `access_token`: (auto-populated after login)
- `refresh_token`: (auto-populated after login)

---

## API Flow

### Step 1: Register User (Optional)
**If user doesn't exist yet**

- **Method**: POST
- **URL**: `{{auth_url}}/api/auth/register/`
- **Body** (JSON):
```json
{
  "username": "teacher1",
  "email": "teacher1@example.com",
  "password": "SecurePass123",
  "role": "teacher"
}
```
- **Expected Response**: 201 Created with user data

---

### Step 2: Login (Get JWT Token)
**REQUIRED - Do this first!**

- **Method**: POST
- **URL**: `{{auth_url}}/api/auth/sso/login/`
- **Body** (JSON):
```json
{
  "email": "teacher1@example.com",
  "password": "SecurePass123"
}
```
- **Expected Response**: 200 OK with `access_token`
- ✅ **Auto-saves token** to environment variable

---

### Step 3: Use Token for Protected APIs

After login, use any protected endpoint. The token is automatically used:

#### Option A: Bearer Token (Automatic)
All endpoints in the collection use `Bearer {{access_token}}`

#### Option B: Manual Bearer Token
If testing manually, set header:
```
Authorization: Bearer <your_access_token>
```

---

## Available Endpoints

### KMS Service - Teacher APIs

#### Get Teacher Profile
- **Method**: GET
- **URL**: `{{kms_url}}/api/teacher/profile/`
- **Auth**: Bearer Token (required)
- **Expected Response**: 200 OK
```json
{
  "id": "2",
  "name": "teacher1@example.com",
  "email": "teacher1@example.com",
  "phone_number": null
}
```

---

### KMS Service - Admin APIs

#### Get Schools (Admin Only)
- **Method**: GET
- **URL**: `{{kms_url}}/api/admin/schools/`
- **Auth**: Bearer Token (required) + Admin role
- **Expected Response**: 
  - 200 OK if user is admin
  - 403 Forbidden if user is not admin

#### Create School
- **Method**: POST
- **URL**: `{{kms_url}}/api/admin/schools/`
- **Auth**: Bearer Token (required) + Admin role
- **Body** (JSON):
```json
{
  "name": "Central High School",
  "address": "123 Main Street"
}
```
- **Expected Response**: 201 Created

#### Get Classrooms
- **Method**: GET
- **URL**: `{{kms_url}}/api/admin/classrooms/`
- **Auth**: Bearer Token (required) + Admin role

#### Create Classroom
- **Method**: POST
- **URL**: `{{kms_url}}/api/admin/classrooms/`
- **Auth**: Bearer Token (required) + Admin role
- **Body** (JSON):
```json
{
  "name": "Class 10A",
  "school": "<school_uuid>"
}
```

---

## Testing Checklist

- [ ] Step 1: Register a new user (if needed)
- [ ] Step 2: Login and get token
- [ ] Step 3: Get Teacher Profile (should work)
- [ ] Step 4: Try Admin endpoint (should get 403 Forbidden)
- [ ] Step 5: Test without token (should get 401)
- [ ] Step 6: Test with invalid token (should get 401)

---

## Common Errors & Solutions

### ❌ 401 Unauthorized
**Problem**: "Authentication credentials were not provided"
- **Solution**: Ensure you've logged in and token is in environment
- Check: Click **Environments** → Select environment → Verify `access_token` is populated

### ❌ 403 Forbidden
**Problem**: "You do not have permission to perform this action"
- **Solution**: Only admins can access `/admin/` endpoints
- Your test user has role `teacher`, not `admin`

### ❌ Token Error
**Problem**: "Given token not valid for any token type"
- **Solution**: 
  1. Token has expired - Login again
  2. Token is malformed - Check you copied it correctly

### ❌ 404 Not Found
**Problem**: Endpoint not found
- **Solution**: 
  1. Check URL spelling
  2. Verify KMS service is running: `docker compose ps`

### ❌ Connection Refused
**Problem**: "Could not connect to server"
- **Solution**: 
  1. Ensure Docker containers are running: `docker compose up -d`
  2. Verify ports: `docker compose ps`
  3. Check: `curl http://localhost:8002/api/teacher/profile/`

---

## Testing Locally Without Docker

If not using Docker, update environment variables:

**Auth Service**:
- Port: 8000 (default Django)
- URL: `http://localhost:8000`

**KMS Service**:
- Port: 8002 (configured in docker-compose)
- URL: `http://localhost:8002`

---

## Advanced: Auto-Login Script

To auto-login when collection runs:

1. In Postman, add a **Pre-request Script** to collection:
```javascript
// Auto-login if token is missing
if (!pm.environment.get('access_token')) {
    console.log('Token missing, logging in...');
    pm.sendRequest({
        url: pm.environment.get('auth_url') + '/api/auth/sso/login/',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                email: 'teacher1@example.com',
                password: 'SecurePass123'
            })
        }
    }, function (err, response) {
        if (!err) {
            var jsonData = response.json();
            pm.environment.set('access_token', jsonData.access_token);
            console.log('Auto-login successful!');
        }
    });
}
```

---

## Microservices Supported

After importing this collection, you can extend it to test:

- ✅ **Auth Service** (ports 8000, DB: 5433)
- ✅ **KMS Service** (port 8002, DB: 5434)
- ❓ **Ecommerce Service** (configure port in environment)
- ❓ **Elearning Service** (configure port in environment)
- ❓ **Social Media Service** (configure port in environment)

All use the same JWT auth mechanism!

---

## Variables Reference

| Variable | Value | Description |
|----------|-------|-------------|
| `auth_url` | `http://localhost:8000` | Auth Service URL |
| `kms_url` | `http://localhost:8002` | KMS Service URL |
| `access_token` | `eyJ...` | JWT access token (auto-populated) |
| `refresh_token` | `eyJ...` | JWT refresh token (auto-populated) |

---

## Tips

1. **Run Login first**: Every testing session requires you to login first
2. **Token expires**: Token lasts 1 hour, then you need to login again
3. **Check Tests tab**: Click **Tests** to see auto-validation results
4. **Save responses**: Click **Save Response** to save example responses
5. **Use collections**: Organize requests by service/feature

---

**Happy Testing! 🚀**
