from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that:
    - Syncs user from Auth service into local DB if missing
    - Creates role-specific profile (Student, Vendor, Admin)
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            username = validated_token.get("username")
            email = validated_token.get("email")
            role = validated_token.get("role")
            full_name = validated_token.get("full_name") or validated_token.get("name") or username

            if not user_id:
                raise exceptions.AuthenticationFailed("Token missing user_id")

            with transaction.atomic():
                # 🔹 Sync or Create User
                user, created = User.objects.get_or_create(
                    id=user_id,
                    defaults={
                        "username": username or f"user_{user_id[:8]}",
                        "email": email,
                        "role": role,
                        "full_name": full_name,
                        "is_active": True,
                    }
                )

                if not created:
                    updated = False
                    if username and user.username != username:
                        user.username = username
                        updated = True
                    if email and user.email != email:
                        user.email = email
                        updated = True
                    if role and user.role != role:
                        user.role = role
                        updated = True
                    if updated:
                        user.save()

                # 🔹 Sync Profiles
                if role:
                    from elearning.models import AdminProfile, VendorProfile, StudentProfile
                    if role == "admin":
                        AdminProfile.objects.get_or_create(user=user, defaults={"id": user.id, "full_name": full_name})
                    elif role in ["vendor", "elearning_vendor"]:
                        VendorProfile.objects.get_or_create(user=user, defaults={"id": user.id})
                    elif role == "student":
                        StudentProfile.objects.get_or_create(user=user, defaults={"id": user.id})

            return user

        except Exception as e:
            logger.error(f"CustomJWTAuthentication error: {str(e)}", exc_info=True)
            return super().get_user(validated_token)
