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
                # 🔹 Step 1: Try to find user by ID (exact match from Auth service)
                user = User.objects.filter(id=user_id).first()
                created = False

                if not user:
                    # 🔹 Step 2: Check by username for ID conflicts
                    user = User.objects.filter(username=username).first()
                    if user and str(user.id) != str(user_id):
                        # Conflict: local user exists with a different ID
                        old_id = str(user.id)
                        logger.warning(
                            f"Conflict found for '{username}': "
                            f"Existing ID {old_id} vs Auth ID {user_id}. "
                            f"Cascading update..."
                        )
                        try:
                            # Use raw SQL to update the PK.
                            # ON UPDATE CASCADE (from migration 0009) will
                            # automatically propagate to kms_user_groups,
                            # kms_teacher, kms_coordinator, kms_student, etc.
                            from django.db import connection
                            with connection.cursor() as cursor:
                                cursor.execute("SET CONSTRAINTS ALL DEFERRED")
                                cursor.execute(
                                    'UPDATE "kms_user" SET "id" = %s WHERE "id" = %s',
                                    [str(user_id), old_id],
                                )
                            # Refresh the user object with the new ID
                            user = User.objects.get(id=user_id)
                            logger.info(f"Successfully updated User ID for '{username}' to {user_id}")
                        except Exception as e:
                            logger.error(
                                f"Failed to cascade-update User ID for '{username}': {e}",
                                exc_info=True,
                            )
                            # Fallback: just use the existing user as-is
                            user = User.objects.filter(username=username).first()
                    elif not user:
                        # 🔹 Step 3: Truly new user – create
                        user = User.objects.create(
                            id=user_id,
                            username=username or f"user_{str(user_id)[:8]}",
                            email=email,
                            role=role,
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

                # 🔹 Assign Group if role exists
                if role:
                    group, _ = Group.objects.get_or_create(name=role)
                    if not user.groups.filter(pk=group.pk).exists():
                        user.groups.add(group)

                    # 🔹 Handle Staff Status
                    if role in ["admin", "coordinator"] and not user.is_staff:
                        user.is_staff = True
                        user.save()

                    # 🔹 Sync Role-specific models
                    if role == "teacher":
                        from kms.models import Teacher
                        t, t_created = Teacher.objects.get_or_create(
                            user=user,
                            defaults={
                                "id": user.id,
                                "name": user.username,
                                "email": user.email,
                            },
                        )
                        # Ensure Teacher ID matches User ID
                        if not t_created and str(t.id) != str(user.id):
                            logger.info(f"Syncing Teacher ID for {user.username} to {user.id}")
                            from django.db import connection
                            with connection.cursor() as cursor:
                                cursor.execute("SET CONSTRAINTS ALL DEFERRED")
                                cursor.execute(
                                    'UPDATE "kms_teacher" SET "id" = %s WHERE "id" = %s',
                                    [str(user.id), str(t.id)],
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