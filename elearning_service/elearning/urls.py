from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserSyncView,
    VendorDashboardView, VendorCourseViewSet, VendorCourseContentViewSet, VendorPayoutViewSet,
    StudentCourseListView, StudentEnrollmentViewSet, StudentCourseContentListView,
    VendorProfileView, PublicCourseListView
)
from .apis.admin import AdminCategoryViewSet, AdminVendorViewSet, AdminCourseViewSet, AdminCourseContentViewSet

router = DefaultRouter()
# Admin Paths
router.register(r'admin/categories', AdminCategoryViewSet, basename='admin-category')
router.register(r'admin/vendors', AdminVendorViewSet, basename='admin-vendor')
router.register(r'admin/courses', AdminCourseViewSet, basename='admin-course')
router.register(r'admin/courses/(?P<course_pk>[^/.]+)/contents', AdminCourseContentViewSet, basename='admin-course-content')

# Vendor Paths
router.register(r'vendor/courses', VendorCourseViewSet, basename='vendor-course')
# Vendor Course Content uses course_pk
router.register(r'vendor/courses/(?P<course_pk>[^/.]+)/contents', VendorCourseContentViewSet, basename='vendor-course-content')
router.register(r'vendor/payouts', VendorPayoutViewSet, basename='vendor-payout')

# Student Paths
router.register(r'student/enrollments', StudentEnrollmentViewSet, basename='student-enrollment')


urlpatterns = [
    # Internal User Sync API
    path('internal/sync-user/', UserSyncView.as_view(), name='sync-user'),
    # path('user/me/', UserDetailView.as_view(), name='user-detail'),

    # Public Catalog
    path('courses/', PublicCourseListView.as_view(), name='public-course-list'),

    # Vendor specific
    path('vendor/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path("vendor/profile/", VendorProfileView.as_view()),

    # Student specific
    path('student/courses/', StudentCourseListView.as_view(), name='student-course-list'),
    path('student/courses/<str:course_pk>/contents/', StudentCourseContentListView.as_view(), name='student-course-content-list'),

    # ViewSet Routes
    path('', include(router.urls)),
]
