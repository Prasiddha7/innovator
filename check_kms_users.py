#!/usr/bin/env python
import os
import sys
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kms_service.settings.local')

import django
django.setup()

from kms.models import User, Teacher, Coordinator, Admin

print("=== Users in KMS Database ===")
users = User.objects.all()
print(f"Total users: {users.count()}")
for user in users:
    print(f"  - {user.username} (email: {user.email}, id: {user.id})")

print("\n=== Teachers in KMS Database ===")
teachers = Teacher.objects.all()
print(f"Total teachers: {teachers.count()}")
for teacher in teachers:
    print(f"  - {teacher.name} (user: {teacher.user.username if teacher.user else 'Unknown'})")

print("\n=== Coordinators in KMS Database ===")
coordinators = Coordinator.objects.all()
print(f"Total coordinators: {coordinators.count()}")
for coord in coordinators:
    print(f"  - {coord.name} (auth_user_id: {coord.auth_user_id}, school: {coord.school})")

print("\n=== Admins in KMS Database ===")
admins = Admin.objects.all()
print(f"Total admins: {admins.count()}")
for admin in admins:
    print(f"  - {admin.name} (auth_user_id: {admin.auth_user_id})")
