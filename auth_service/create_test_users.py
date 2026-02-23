#!/usr/bin/env python
import os
import sys

# Set up auth_service environment
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accounts.settings.local')

import django
django.setup()

from accounts.models import User

# Test data
test_users = [
    ('teacher1@example.com', 'Teacher One', 'teacher', 'pass123'),
    ('coordinator1@example.com', 'Coordinator One', 'coordinator', 'pass123'),
    ('admin1@example.com', 'Admin One', 'admin', 'pass123'),
]

for email, name, role, password in test_users:
    username = email.split('@')[0]
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'first_name': name.split()[0],
            'last_name': name.split()[1] if len(name.split()) > 1 else '',
            'role': role,
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
    
    status = '✓ Created' if created else '✓ Exists'
    print(f"{status}: {email} (role: {user.role})")

print("\nTest users created successfully!")
