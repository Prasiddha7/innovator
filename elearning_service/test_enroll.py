import os
import django
import sys

# Add both settings directories physically to sys.path just in case
sys.path.append('/Users/prasiddhasubedi/innovator/elearning_service')
sys.path.append('/Users/prasiddhasubedi/innovator/auth_service')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning_service.settings')
django.setup()

from elearning.models import Course, Enrollment, StudentProfile
from elearning.serializers import EnrollmentSerializer

print("COURSES:")
qs = Course.objects.all()
if not qs:
    print("NO COURSES FOUND")
for c in qs:
    print(c.id, c.title, "published:", c.is_published, type(c.id))

