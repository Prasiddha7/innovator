from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ecommerce.models import VendorProfile
from ecommerce.serializers import VendorProfileSerializer
from ecommerce.permissions import IsAdminUser

class VendorViewSet(ModelViewSet):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]