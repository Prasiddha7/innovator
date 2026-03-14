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

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser))

class IsElearningVendorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admins and superusers bypass vendor specific checks
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
            
        # Vendors must have the role and be approved
        if request.user.role == 'elearning_vendor':
            return hasattr(request.user, 'vendor_profile') and request.user.vendor_profile.is_approved
            
        return False

class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')
