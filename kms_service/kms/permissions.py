from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Check both request.auth (from JWT) and group membership
        is_admin_role = request.auth and request.auth.get('role') == 'admin'
        is_admin_group = request.user.groups.filter(name='admin').exists()
        return is_admin_role or is_admin_group

class IsCoordinatorUser(permissions.BasePermission):
    """Allow access to coordinators and admins"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get('role') if request.auth else None
        is_coordinator_or_admin = role in ['coordinator', 'admin']
        has_coordinator_group = request.user.groups.filter(name__in=['coordinator', 'admin']).exists()
        return is_coordinator_or_admin or has_coordinator_group

class IsTeacherUser(permissions.BasePermission):
    """Allow access to teachers, coordinators, and admins"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get('role') if request.auth else None
        is_teacher_role = role in ['teacher', 'coordinator', 'admin']
        has_teacher_group = request.user.groups.filter(name__in=['teacher', 'coordinator', 'admin']).exists()
        return is_teacher_role or has_teacher_group

class IsPrincipal(permissions.BasePermission):
    """Allow access only to principals"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get('role') if request.auth else None
        is_principal_role = role == 'principal'
        has_principal_group = request.user.groups.filter(name='principal').exists()
        return is_principal_role or has_principal_group