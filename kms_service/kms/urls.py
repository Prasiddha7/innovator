# from django.urls import path
# from kms.apis.administrator import (
#     # AssignCoordinatorToSchoolView,
#     ClassRoomView,
#     CourseView,
#     SchoolView,
#     TeacherClassAssignmentAPIView,
#     TeacherClassAssignmentView,
#     TeacherKYCView,
#     TeacherSalaryView,
#     TeacherSchoolAssignmentView,
#     AdminDashboardView,
# )
from kms.apis.coordinator_assignment import CoordinatorSchoolAssignmentView
# from kms.apis.teacher_detailed import (
#     TeacherProfileView,
#     TeacherKYCUploadView,
#     TeacherClassesView,
#     StudentAttendanceListView,
#     MarkAttendanceView,
#     BulkMarkAttendanceView,
#     AttendanceReportView,
#     EarningsView
# )
# # from kms.apis.coordinator import (
# #     CoordinatorAssignmentView,
# #     CoordinatorPendingAttendanceView,
# #     CoordinatorApproveAttendanceView,
# #     CoordinatorBulkApproveAttendanceView,
# #     TeacherAttendanceSupervisionView,
# #     TeacherInvoiceView,
# # )

# urlpatterns = [
#     # ============================================================================
#     # ADMIN MANAGEMENT APIs
#     # ============================================================================
    
#     # Schools
#     path('admin/schools/', SchoolView.as_view(), name='school-list-create'),
#     path('admin/schools/<str:school_id>/', SchoolView.as_view(), name='school-detail'),
    
#     # Classrooms
#     path('admin/classrooms/', ClassRoomView.as_view(), name='classroom-list-create'),
#     path('admin/classrooms/<str:classroom_id>/', ClassRoomView.as_view(), name='classroom-detail'),
    
#     # Courses
#     path('admin/courses/', CourseView.as_view(), name='course-list-create'),
#     path('admin/courses/<str:course_id>/', CourseView.as_view(), name='course-detail'),
    
#     # Teacher Assignments
#     path("admin/teacher-assignment/", TeacherClassAssignmentAPIView.as_view()),
#     path('admin/teacher-assignments/', TeacherClassAssignmentView.as_view(), name='teacher-assignment-list-create'),
#     path('admin/teacher-assignments/<str:assignment_id>/', TeacherClassAssignmentView.as_view(), name='teacher-assignment-delete'),
    
#     # Teacher KYC Verification
#     path('admin/teacher-kyc/', TeacherKYCView.as_view(), name='teacher-kyc-list'),
#     path('admin/teacher-kyc/<str:kyc_id>/', TeacherKYCView.as_view(), name='teacher-kyc-detail'),
    
#     # Teacher Salary Management
    
#     # Profile & KYC
#     path('teacher/profile/', TeacherProfileView.as_view(), name='teacher-profile'),
#     path('teacher/kyc/upload/', TeacherKYCUploadView.as_view(), name='teacher-kyc-upload'),
#     path('teacher/kyc/status/', TeacherKYCUploadView.as_view(), name='teacher-kyc-status'),
    
#     # Classes
#     path('teacher/classes/', TeacherClassesView.as_view(), name='teacher-classes'),
    
#     # Attendance
#     path('teacher/attendance/students/', StudentAttendanceListView.as_view(), name='student-attendance-list'),
#     path('teacher/attendance/mark/', MarkAttendanceView.as_view(), name='mark-attendance'),
#     path('teacher/attendance/bulk-mark/', BulkMarkAttendanceView.as_view(), name='bulk-mark-attendance'),
#     path('teacher/attendance/report/', AttendanceReportView.as_view(), name='attendance-report'),
    
#     # Earnings
#     path('teacher/earnings/', EarningsView.as_view(), name='teacher-earnings'),

#     # ============================================================================
#     # COORDINATOR APIs
#     # ============================================================================
#     # Assignments (classroom or course)
#     path('coordinator/assignments/', CoordinatorAssignmentView.as_view(), name='coordinator-assignments'),
#     path('coordinator/assignments/<str:assignment_id>/', CoordinatorAssignmentView.as_view(), name='coordinator-assignment-delete'),

#     # Attendance supervision/approval
#     path('coordinator/attendance/pending/', CoordinatorPendingAttendanceView.as_view(), name='coordinator-attendance-pending'),
#     path('coordinator/attendance/<str:attendance_id>/approve/', CoordinatorApproveAttendanceView.as_view(), name='coordinator-approve-attendance'),
 
#     path('coordinator/attendance/bulk-approve/', CoordinatorBulkApproveAttendanceView.as_view(), name='coordinator-bulk-approve-attendance'),

#     # Teacher Attendance Supervision (coordinator supervises teachers)
#     path('coordinator/teacher-attendance/', TeacherAttendanceSupervisionView.as_view(), name='coordinator-teacher-attendance'),
#     path('coordinator/teacher-attendance/<str:attendance_id>/', TeacherAttendanceSupervisionView.as_view(), name='coordinator-teacher-attendance-detail'),

#     # Teacher Invoices (generate invoices for classes taught)
#     path('coordinator/teacher-invoices/', TeacherInvoiceView.as_view(), name='coordinator-teacher-invoices'),
# ]

from django.urls import path
from kms.views import UserSyncView
from kms.apis.coordinator import TeacherAttendanceSupervisionView
from kms.apis.administrator import ClassRoomView, SchoolView, TeacherSchoolAssignmentView, TeacherCompensationRuleView, GenerateSalarySlipsView, SalarySlipManagementView
from kms.apis.teacher import TeacherAttendanceViewSet, TeacherProfileView
from kms.apis.teacher_detailed import TeacherKYCUploadView, TeacherEarningsView, TeacherSalarySlipsView
from kms.apis.students import AttendanceApproveAPIView, AttendanceListAPIView, AttendanceUploadAPIView, StudentCreateAPIView


urlpatterns = [
    path("internal/sync-user/", UserSyncView.as_view(), name="sync-user"),
    # Schools
    path('admin/schools/', SchoolView.as_view(), name='school-list-create'),
    path('admin/schools/<str:school_id>/', SchoolView.as_view(), name='school-detail'),
    path("admin/coordinator-school-assignment/", CoordinatorSchoolAssignmentView.as_view(), name='coordinator-school-assignment'),
    path("admin/coordinator-school-assignment/<str:coordinator_id>/", CoordinatorSchoolAssignmentView.as_view(), name='coordinator-school-assignment-delete'),
    path("admin/teacher-school-assignment/", TeacherSchoolAssignmentView.as_view(), name='teacher-school-assignment'),
    # Classrooms
    path('admin/classrooms/', ClassRoomView.as_view(), name='classroom-list-create'),
    path('admin/classrooms/<str:classroom_id>/', ClassRoomView.as_view(), name='classroom-detail'),
    path("admin/teacher-compensation-rules/", TeacherCompensationRuleView.as_view(), name='teacher-compensation-rules'),
    path("admin/salary-slips/generate/", GenerateSalarySlipsView.as_view(), name='generate-salary-slips'),
    path("admin/salary-slips/", SalarySlipManagementView.as_view(), name='salary-slips-list'),
    path("admin/salary-slips/<str:slip_id>/", SalarySlipManagementView.as_view(), name='salary-slips-detail'),
    

    path("coordinator/teacher-attendance/", TeacherAttendanceSupervisionView.as_view(), name='coordinator-teacher-attendance'),
    path("coordinator/teacher-attendance/<str:attendance_id>/", TeacherAttendanceSupervisionView.as_view(), name='coordinator-teacher-attendance-detail'),
    
    # Teacher Attendance (Check-in/out)
    path("teacher/attendance/", TeacherAttendanceViewSet.as_view({'get': 'list'}), name='teacher-attendance-list'),
    path("teacher/attendance/check-in/", TeacherAttendanceViewSet.as_view({'post': 'check_in'}), name='teacher-attendance-check-in'),
    path("teacher/attendance/<int:pk>/check-out/", TeacherAttendanceViewSet.as_view({'post': 'check_out'}), name='teacher-attendance-check-out'),

    # Profile & KYC
    path('teacher/profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('teacher/kyc/upload/', TeacherKYCUploadView.as_view(), name='teacher-kyc-upload'),
    path('teacher/kyc/status/', TeacherKYCUploadView.as_view(), name='teacher-kyc-status'),
    path('teacher/earnings/', TeacherEarningsView.as_view(), name='teacher-earnings'),
    path('teacher/salary-slips/', TeacherSalarySlipsView.as_view(), name='teacher-salary-slips'),

    #Student Attendance
    path("student/create/", StudentCreateAPIView.as_view()),
    path("attendance/upload/", AttendanceUploadAPIView.as_view()),
    path("attendance/", AttendanceListAPIView.as_view()),
    path("attendance/approve/<uuid:attendance_id>/", AttendanceApproveAPIView.as_view()),

]
