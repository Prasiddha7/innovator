# # kms/views.py
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from .models import TeacherKYC
# from .serializers import TeacherKYCUploadSerializer
# from .authentication import AuthServiceJWTAuthentication

# class TeacherProfileView(APIView):
#     authentication_classes = [AuthServiceJWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         teacher = request.user  # returned from AuthServiceJWTAuthentication
#         kyc = TeacherKYC.objects.filter(teacher=teacher).first()
#         return Response({
#             "teacher_id": teacher.id,
#             "auth_user_id": teacher.auth_user_id,
#             "schools": [s.name for s in teacher.schools.all()],
#             "kyc_status": kyc.status if kyc else "not submitted",
#         })

# class TeacherKYCView(APIView):
#     authentication_classes = [AuthServiceJWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         teacher = request.user
#         serializer = TeacherKYCUploadSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(teacher=teacher, status='pending')
#             return Response({"message":"KYC submitted successfully"})
#         return Response(serializer.errors, status=400)


# kms/accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSyncSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveAPIView

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
                    "gender": user_data.get("gender"),
                    "date_of_birth": user_data.get("date_of_birth"),
                    "address": user_data.get("address"),
                    "phone_number": user_data.get("phone_number"),
                }
            )

            # Sync to corresponding profile if applicable
            role = user_data.get("role")
            if role == "teacher":
                from kms.models import Teacher
                Teacher.objects.get_or_create(user=user, defaults={'id': user.id, 'name': user.username})
            elif role == "coordinator":
                from kms.models import Coordinator
                Coordinator.objects.get_or_create(user=user, defaults={'id': user.id, 'name': user.username})

            return Response({
                "message": "User synced successfully",
                "created": created
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(RetrieveAPIView):
    """
    Returns details of the currently authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import UserDetailSerializer
        return UserDetailSerializer
    
    def get_object(self):
        return self.request.user