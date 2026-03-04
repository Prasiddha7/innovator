from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that:
    - Syncs user from Auth service into local KMS DB if missing
    - Assigns Django Group based on role
    - Creates role-specific profile (Teacher, Coordinator)
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            username = validated_token.get("username")
            email = validated_token.get("email")
            role = validated_token.get("role")

            if not user_id:
                raise exceptions.AuthenticationFailed("Token missing user_id")

            with transaction.atomic():
                # 🔹 Sync or Create KMS User
                user, created = User.objects.get_or_create(
                    id=user_id,
                    defaults={
                        "username": username or f"user_{user_id[:8]}",
                        "email": email,
                        "role": role,
                        "is_active": True,
                    },
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

                # 🔹 Assign Group if role exists
                if role:
                    group, _ = Group.objects.get_or_create(name=role)
                    user.groups.add(group)

                    # 🔹 Handle Staff Status
                    if role in ["admin", "coordinator"] and not user.is_staff:
                        user.is_staff = True
                        user.save()

                    # 🔹 Sync Role-specific models
                    if role == "teacher":
                        from kms.models import Teacher
                        Teacher.objects.get_or_create(
                            user=user,
                            defaults={
                                "id": user.id,
                                "name": user.username,
                                "email": user.email,
                            },
                        )
                    elif role == "coordinator":
                        from kms.models import Coordinator
                        Coordinator.objects.get_or_create(
                            user=user,
                            defaults={
                                "id": user.id,
                                "name": user.username,
                            },
                        )

            return user

        except Exception as e:
            logger.error(f"CustomJWTAuthentication error: {str(e)}", exc_info=True)
            # Fallback to standard behavior if something fails during sync
            return super().get_user(validated_token)