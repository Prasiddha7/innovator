import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning_service.settings')
django.setup()

from elearning.models import Course, VendorProfile
print("COURSES:")
for c in Course.objects.all():
    print(c.id, c.title, "vendor:", c.vendor_id)
print("VENDORS:")
for v in VendorProfile.objects.all():
    print(v.id, v.user.username)
