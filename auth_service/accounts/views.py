import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

# class RegisterView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 🔥 Call kms_service to sync user
        try:
            kms_url = "http://kms-service:8002/api/internal/sync-user/"  
            # If running via docker use service name
            # If local use: http://localhost:8002/api/internal/sync-user/

            payload = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }

            response = requests.post(kms_url, json=payload, timeout=5)

            if response.status_code != 200:
                print("KMS Sync Failed:", response.text)

        except Exception as e:
            print("Error syncing user to KMS:", str(e))

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import LoginSerializer


class SSOLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]  # get user from serializer

        refresh = RefreshToken.for_user(user)
        
        # Add custom claims - convert UUID to string for JSON serialization
        refresh["user_id"] = str(user.id)
        refresh["username"] = user.username
        refresh["email"] = user.email
        refresh["role"] = user.role

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "token_type": "Bearer",
            "expires_in": 900,  # 15 minutes
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        }, status=status.HTTP_200_OK)
