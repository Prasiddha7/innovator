import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from drf_spectacular.utils import extend_schema

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(responses={201: UserSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        payload = {
            "id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "gender": user.gender,
            "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
            "address": user.address,
            "phone_number": user.phone_number,
        }

        # Sync to microservices
        self.sync_user(payload)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def sync_user(self, payload):
        # KMS Sync
        try:
            res = requests.post(settings.KMS_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"KMS Sync Failed (Status {res.status_code}): {res.text}")
        except Exception as e:
            print(f"Error syncing user to KMS: {str(e)}")

        # Elearning Sync
        try:
            res = requests.post(settings.ELEARNING_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Elearning Sync Failed (Status {res.status_code}): {res.text}")
        except Exception as e:
            print(f"Error syncing user to Elearning: {str(e)}")

        # Ecommerce Sync
        try:
            res = requests.post(settings.ECOMMERCE_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Ecommerce Sync Failed (Status {res.status_code}): {res.text}")
        except Exception as e:
            print(f"Error syncing user to Ecommerce: {str(e)}")

        # Social Media Sync
        try:
            res = requests.post(settings.SOCIAL_MEDIA_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Social Media Sync Failed (Status {res.status_code}): {res.text}")
        except Exception as e:
            print(f"Error syncing user to Social Media: {str(e)}")


class SSOLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(responses={200: UserSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = str(user.id)
        refresh["username"] = user.username
        refresh["full_name"] = user.full_name
        refresh["email"] = user.email
        refresh["role"] = user.role

        payload = {
            "id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "gender": user.gender,
            "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
            "address": user.address,
            "phone_number": user.phone_number,
        }

        # Sync on login
        try:
            res = requests.post(settings.KMS_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"KMS Sync Failed on Login: {res.text}")
        except Exception: pass
            
        try:
            res = requests.post(settings.ELEARNING_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Elearning Sync Failed on Login: {res.text}")
        except Exception: pass

        try:
            res = requests.post(settings.ECOMMERCE_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Ecommerce Sync Failed on Login: {res.text}")
        except Exception: pass

        try:
            res = requests.post(settings.SOCIAL_MEDIA_SERVICE_SYNC_URL, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Social Media Sync Failed on Login: {res.text}")
        except Exception: pass

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "token_type": "Bearer",
            "expires_in": 900,
            "user": payload
        }, status=status.HTTP_200_OK)


class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import UserSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user