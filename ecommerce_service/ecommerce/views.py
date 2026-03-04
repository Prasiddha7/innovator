from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import UserSyncSerializer
from .models import User
# Create your views here.

class UserSyncView(APIView):
    """
    Internal API to sync users from auth_service
    """
    permission_classes = [AllowAny]  # Later secure with service token

    def post(self, request):
        serializer = UserSyncSerializer(data=request.data)

        if serializer.is_valid():
            user_data = serializer.validated_data

            # Create or update user
            user, created = User.objects.update_or_create(
                id=user_data["id"],  # UUID from auth_service
                defaults={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "role": user_data.get("role"),
                }
            )

            # Sync to corresponding profile if applicable
            role = user_data.get("role")

            if role == "admin":
                from ecommerce.models import AdminProfile
                AdminProfile.objects.get_or_create(user=user, defaults={'id': user.id})

            elif role == "ecommerce_vendor":
                from ecommerce.models import VendorProfile
                VendorProfile.objects.get_or_create(user=user, defaults={'id': user.id})
            elif role == "customer":
                from ecommerce.models import CustomerProfile
                CustomerProfile.objects.get_or_create(user=user, defaults={'id': user.id})

            return Response({
                "message": "User synced successfully",
                "created": created
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
