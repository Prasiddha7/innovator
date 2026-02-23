from rest_framework.permissions import BasePermission

class IsRole(BasePermission):
    def __init__(self, role):
        self.role = role

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == self.role

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "admin"

class IsElearningVendor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "elearning_vendor"

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "student"
