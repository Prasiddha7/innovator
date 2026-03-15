from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
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
                # 🔹 Step 1: Try to find user by ID
                user = User.objects.filter(id=user_id).first()
                created = False

                if not user:
                    # 🔹 Step 2: If not found by ID, check by username
                    user = User.objects.filter(username=username).first()
                    if user:
                        # Conflict found! Update the existing user's ID
                        logger.warning(f"Conflict found in Social Media: User '{username}' exists with ID {user.id}. Updating to {user_id}")
                        User.objects.filter(id=user.id).update(id=user_id)
                        user = User.objects.get(id=user_id)
                    else:
                        # 🔹 Step 3: Create new user
                        user = User.objects.create(
                            id=user_id,
                            username=username or f"user_{user_id[:8]}",
                            email=email,
                            role=role,
                            full_name=full_name,
                            is_active=True,
                        )
                        created = True

                if not created:
                    # Update fields if changed
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

                # 🔹 Sync Profile
                from social_media.models import Profile
                Profile.objects.get_or_create(user=user)

            return user

        except Exception as e:
            logger.error(f"CustomJWTAuthentication error: {str(e)}", exc_info=True)
            return super().get_user(validated_token)
