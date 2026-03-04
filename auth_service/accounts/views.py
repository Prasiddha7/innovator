import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
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

            response = requests.post(kms_url, json=payload, timeout=5)

            if response.status_code != 200:
                print("KMS Sync Failed:", response.text)

        except Exception as e:
            print("Error syncing user to KMS:", str(e))

        # 🔥 Call elearning_service to sync user
        try:
            elearning_url = "http://elearning-service:8003/api/internal/sync-user/"  
            # Defaulting to 8003 based on standard increment, will adapt if different

            response = requests.post(elearning_url, json=payload, timeout=5)

            if response.status_code != 200:
                print("Elearning Sync Failed:", response.text)

        except Exception as e:
            print("Error syncing user to Elearning:", str(e))

        # 🔥 Call ecommerce_service to sync user
        try:
            ecommerce_url = "http://ecommerce-service:8004/api/internal/sync-user/"
            response = requests.post(ecommerce_url, json=payload, timeout=5)
            
            if response.status_code != 200:
                print("Ecommerce Sync Failed:", response.text)
        except Exception as e:
            print("Error syncing user to Ecommerce:", str(e))

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

        # Sync on login as well to ensure latest data is present
        try:
            requests.post("http://kms-service:8002/api/internal/sync-user/", json=payload, timeout=5)
        except Exception:
            pass
            
        try:
            requests.post("http://elearning-service:8003/api/internal/sync-user/", json=payload, timeout=5)
        except Exception:
            pass

        try:
            requests.post("http://ecommerce-service:8004/api/internal/sync-user/", json=payload, timeout=5)
        except Exception:
            pass

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "token_type": "Bearer",
            "expires_in": 900,  # 15 minutes
            "user": payload
        }, status=status.HTTP_200_OK)


class UserDetailView(RetrieveAPIView):
    """
    Returns details of the currently authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import UserSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user