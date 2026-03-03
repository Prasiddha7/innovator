from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Check both request.auth (from JWT) and group membership
        is_admin_role = request.auth and request.auth.get('role') == 'admin'
        is_admin_group = request.user.groups.filter(name='admin').exists()
        return is_admin_role or is_admin_group

class IsVendorUser(permissions.BasePermission):
    """Allow access to vendors and admins"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get('role') if request.auth else None
        is_vendor_or_admin = role in ['ecommerce_vendor', 'admin']
        has_vendor_group = request.user.groups.filter(name__in=['ecommerce_vendor', 'admin']).exists()
        return is_vendor_or_admin or has_vendor_group

class IsCustomerUser(permissions.BasePermission):
    """Allow access to customers and admins"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get('role') if request.auth else None
        is_customer_or_admin = role in ['customer', 'admin']
        has_customer_group = request.user.groups.filter(name__in=['customer', 'admin']).exists()
        return is_customer_or_admin or has_customer_group

class IsVendorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.auth.get('role') if request.auth else None

        is_vendor = role == "ecommerce_vendor" or request.user.groups.filter(name='ecommerce_vendor').exists()
        is_admin = role == "admin" or request.user.groups.filter(name='admin').exists()

        return is_vendor or is_admin