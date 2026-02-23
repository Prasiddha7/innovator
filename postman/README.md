Coordinator API curl examples

Replace `{{BASE_URL}}` with your service base URL (e.g. http://localhost:8000) and `{{TOKEN}}` with a valid JWT for a coordinator user.

Assign teacher to a classroom:

```bash
curl -X POST "{{BASE_URL}}/api/coordinator/assignments/" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"teacher_id": 5, "classroom_id": 3}'
```

List assignments:

```bash
curl -X GET "{{BASE_URL}}/api/coordinator/assignments/" \
  -H "Authorization: Bearer {{TOKEN}}"
```

Delete assignment (replace ASSIGN_ID):

```bash
curl -X DELETE "{{BASE_URL}}/api/coordinator/assignments/ASSIGN_ID/" \
  -H "Authorization: Bearer {{TOKEN}}"
```

List pending attendance:

```bash
curl -X GET "{{BASE_URL}}/api/coordinator/attendance/pending/" \
  -H "Authorization: Bearer {{TOKEN}}"
```

Approve a single attendance (replace ATT_ID):

```bash
curl -X PUT "{{BASE_URL}}/api/coordinator/attendance/ATT_ID/approve/" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "notes": "Verified"}'
```

Bulk approve attendance:

```bash
curl -X PUT "{{BASE_URL}}/api/coordinator/attendance/bulk-approve/" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "attendance_ids": [10,11,12], "notes": "Batch approved"}'
```
