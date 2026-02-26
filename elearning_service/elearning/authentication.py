from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from elearning.models import AdminProfile, VendorProfile, StudentProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads JWT token issued by auth_service,
    and returns the local User instance from DB.
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            if not user_id:
                raise exceptions.AuthenticationFailed("Token missing user_id field")

            # Try to get the user from the local DB. It should have been synced via internal/sync-user/
            user = User.objects.filter(id=user_id).first()
            if not user:
                # If completely missing, fallback: try to create a basic user record from token
                username = validated_token.get("username", str(user_id))
                full_name = validated_token.get("full_name", "")
                email = validated_token.get("email", "")
                role = validated_token.get("role", "student")

                user, created = User.objects.get_or_create(
                    id=user_id,
                    defaults={
                        "username": username,
                        "full_name": full_name,
                        "email": email,
                        "role": role,
                        "is_active": True,
                    }
                )
                if created:
                    if role == "admin":
                        AdminProfile.objects.get_or_create(user=user)
                    elif role == "vendor" or role == "elearning_vendor":
                        VendorProfile.objects.get_or_create(user=user)
                    elif role == "student":
                        StudentProfile.objects.get_or_create(user=user)

            return user

        except exceptions.AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"AuthServiceJWTAuthentication error: {str(e)}", exc_info=True)
            raise exceptions.AuthenticationFailed("Authentication failed.")
