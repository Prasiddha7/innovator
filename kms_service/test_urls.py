import os
import django
from django.urls import resolve, Resolver404

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kms_service.settings.local')
django.setup()

paths_to_test = [
    '/api/kms/students/attendance/bulk/',
    '/api/kms/students/attendance/',
    '/api/kms/student/attendance/',
]

for path in paths_to_test:
    try:
        match = resolve(path)
        print(f"Path '{path}' matches view: {match.view_name}")
    except Resolver404:
        print(f"Path '{path}' did NOT match any view.")
