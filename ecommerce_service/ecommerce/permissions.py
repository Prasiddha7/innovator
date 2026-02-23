from rest_framework.permissions import BasePermission

class IsRole(BasePermission):
    def __init__(self, role):
        self.role = role

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == self.role

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "admin"

class IsEcommerceVendor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "ecommerce_vendor"

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "customer"
