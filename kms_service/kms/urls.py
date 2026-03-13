from django.urls import path
from kms.views import UserSyncView, UserDetailView
from kms.apis.coordinator import TeacherAttendanceSupervisionView
from kms.apis.coordinator_assignment import CoordinatorSchoolAssignmentView
from kms.apis.administrator import ClassRoomView, SchoolView, TeacherSchoolAssignmentView, TeacherCompensationRuleView, GenerateSalarySlipsView, SalarySlipManagementView
from kms.apis.teacher import TeacherAttendanceViewSet, TeacherProfileView, TeacherClassAssignmentView
from kms.apis.teacher_detailed import TeacherKYCUploadView, TeacherEarningsView, TeacherSalarySlipsView
from kms.apis.students import AttendanceApproveAPIView, AttendanceListAPIView, StudentCSVUploadAPIView, StudentCreateAPIView, AttendanceMarkAPIView, BulkMarkAttendanceAPIView, BulkAttendanceApproveAPIView
from kms.apis.teacher_invoice import GenerateTeacherInvoiceView, TeacherInvoiceManagementView


urlpatterns = [
    path("user/me/", UserDetailView.as_view(), name="user-detail"),
    path("internal/sync-user/", UserSyncView.as_view(), name="sync-user"),

    # Student List (Plural and Singular)
    path('students/list/', StudentCreateAPIView.as_view(), name='student-list-plural'),
    path('student/list/', StudentCreateAPIView.as_view(), name='student-list'),
    path('student/create/', StudentCreateAPIView.as_view(), name='student-create'),
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

    # Teacher Invoices
    path("admin/teacher-invoices/generate/", GenerateTeacherInvoiceView.as_view(), name='generate-teacher-invoices'),
    path("admin/teacher-invoices/", TeacherInvoiceManagementView.as_view(), name='teacher-invoices-list'),
    path("admin/teacher-invoices/<str:invoice_id>/", TeacherInvoiceManagementView.as_view(), name='teacher-invoice-detail'),

    path("coordinator/teacher-attendance/", TeacherAttendanceSupervisionView.as_view(), name='coordinator-teacher-attendance'),
    path("coordinator/teacher-attendance/<str:attendance_id>/", TeacherAttendanceSupervisionView.as_view(), name='coordinator-teacher-attendance-detail'),
    
    # Teacher Attendance (Check-in/out)
    path("teacher/attendance/", TeacherAttendanceViewSet.as_view({'get': 'list'}), name='teacher-attendance-list'),
    path("teacher/attendance/check-in/", TeacherAttendanceViewSet.as_view({'post': 'check_in'}), name='teacher-attendance-check-in'),
    path("teacher/attendance/<uuid:pk>/check-out/", TeacherAttendanceViewSet.as_view({'post': 'check_out'}), name='teacher-attendance-check-out'),

    # Profile & KYC
    path('teacher/profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('teacher/class-assignment/', TeacherClassAssignmentView.as_view(), name='teacher-class-assignment'),
    path('teacher/kyc/upload/', TeacherKYCUploadView.as_view(), name='teacher-kyc-upload'),
    path('teacher/kyc/status/', TeacherKYCUploadView.as_view(), name='teacher-kyc-status'),
    path('teacher/earnings/', TeacherEarningsView.as_view(), name='teacher-earnings'),
    path('teacher/salary-slips/', TeacherSalarySlipsView.as_view(), name='teacher-salary-slips'),

    # Student Attendance
    path("student/attendance/", AttendanceListAPIView.as_view(), name='student-attendance-self'),
    path("students/attendance/", AttendanceListAPIView.as_view(), name='student-attendance-list'),
    path("students/attendance/bulk/", BulkMarkAttendanceAPIView.as_view(), name='student-attendance-bulk'),
    path("students/attendance/bulk-approve/", BulkAttendanceApproveAPIView.as_view(), name='student-attendance-bulk-approve'),
    path("attendance/mark/", AttendanceMarkAPIView.as_view(), name='attendance-mark'),
    path("attendance/approve/<uuid:attendance_id>/", AttendanceApproveAPIView.as_view(), name='attendance-approve'),
]
