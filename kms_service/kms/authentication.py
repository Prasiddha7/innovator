from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.db import transaction
from kms.models import Teacher
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    pass
    """
    Custom JWT Authentication that:
    - Syncs user from Auth service into local KMS DB
    - Assigns Django Group based on role
    - Creates role-specific profile (Teacher, Coordinator, Admin)
    """

    # def get_user(self, validated_token):
    #     try:
    #         # 🔹 Extract required fields from token
    #         user_id = validated_token.get("user_id")
    #         username = validated_token.get("username")
    #         email = validated_token.get("email")
    #         role = validated_token.get("role")

    #         if not all([user_id, username, email, role]):
    #             raise exceptions.AuthenticationFailed(
    #                 "Token missing required fields"
    #             )

    #         with transaction.atomic():

    #             # 🔹 Sync or Update KMS User
    #             user, created = User.objects.get_or_create(
    #                 id=user_id,
    #                 defaults={
    #                     "username": username,
    #                     "email": email,
    #                     "is_active": True,
    #                 },
    #             )

    #             if not created:
    #                 # Keep local data synced
    #                 updated = False

    #                 if user.username != username:
    #                     user.username = username
    #                     updated = True

    #                 if user.email != email:
    #                     user.email = email
    #                     updated = True

    #                 if not user.is_active:
    #                     user.is_active = True
    #                     updated = True

    #                 if updated:
    #                     user.save()

    #             # 🔹 Assign Group
    #             group, _ = Group.objects.get_or_create(name=role)
    #             user.groups.add(group)

    #             # 🔹 Admin staff permission
    #             if role == "admin" and not user.is_staff:
    #                 user.is_staff = True
    #                 user.save()

    #             # 🔹 Sync Role-specific models
    #             full_name = user.get_full_name() or user.username

    #             if role == "teacher":
    #                 Teacher.objects.get_or_create(
    #                     user=user,
    #                     defaults={
    #                         "name": full_name,
    #                         "email": user.email,
    #                     },
    #                 )

    #             elif role == "coordinator":
    #                 Coordinator.objects.get_or_create(
    #                     user=user,
    #                     defaults={
    #                         "name": full_name,
    #                         "school": None,
    #                     },
    #                 )

    #             elif role == "admin":
    #                 Admin.objects.get_or_create(
    #                     user=user,
    #                     defaults={
    #                         "name": full_name,
    #                     },
    #                 )

    #         return user

    #     except exceptions.AuthenticationFailed:
    #         raise

    #     except Exception as e:
    #         logger.error(
    #             f"CustomJWTAuthentication error: {str(e)}",
    #             exc_info=True
    #         )
    #         raise exceptions.AuthenticationFailed(
    #             "Authentication failed. Please try again."
    #         )

    # def authenticate(self, request):
    #     """
    #     Override to return (user, validated_token)
    #     """
    #     result = super().authenticate(request)
    #     if result:
    #         user, validated_token = result
    #         return user, validated_token
    #     return None