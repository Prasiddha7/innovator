from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The default AbstractUser has first_name and last_name.
    # To satisfy the specific 'use full name in user model' requirement, we add an explicit full_name field or property.
    full_name = models.CharField(max_length=255, blank=True, null=True)
    
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("coordinator", "Coordinator"),
        ("teacher", "Teacher"),
        ("student", "Student"),
        ("elearning_vendor", "Elearning Vendor"),
        ("ecommerce_vendor", "Ecommerce Vendor"),
        ("customer", "Customer"),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set', 
        blank=True,
        help_text='The groups this user belongs to',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set', 
        blank=True,
        help_text='Specific permissions for this user',
        verbose_name='user permissions'
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
