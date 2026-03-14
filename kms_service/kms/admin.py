
from django.contrib import admin
from .models import (
    User, School, ClassRoom,Teacher, TeacherSalary, 
    TeacherCompensationRule, TeacherSalarySlip, Coordinator, 
    TeacherClassAssignment, Student, Enrollment, TeacherAttendance, StudentAttendance, TeacherKYC, 
    TeacherInvoice, CoordinatorInvoice
)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at')

# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'school', 'created_by', 'approval_status', 'status', 'start_date', 'end_date', 'created_at')

@admin.register(ClassRoom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'created_at')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'phone_number', 'is_active', 'total_earnings', 'created_at')

@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school', 'monthly_salary', 'created_at', 'updated_at')

@admin.register(TeacherClassAssignment)
class TeacherClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'classroom', 'school', 'assigned_at')

# @admin.register(TeacherCourseAssignment)
# class TeacherCourseAssignmentAdmin(admin.ModelAdmin):
#     list_display = ('teacher', 'course', 'assigned_at')

@admin.register(TeacherKYC)
class TeacherKYCAdmin(admin.ModelAdmin):        
    list_display = ('teacher', 'status', 'submitted_at', 'updated_at', 'approved_at', 'kyc_status_percentage')

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school', 'check_in', 'check_out', 'status', 'total_hours', 'supervised_by', 'supervised_at')    

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'school', 'classroom', 'phone_number', 'created_at') 

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at') 

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'classroom', 'teacher', 'date', 'status', 
        'marked_by', 'marked_at', 'approved', 'approved_by', 'approved_at'
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')

@admin.register(TeacherCompensationRule)
class TeacherCompensationRuleAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school', 'payment_type', 'base_rate', 'commission_percentage', 'is_active', 'created_at')

@admin.register(TeacherSalarySlip)
class TeacherSalarySlipAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school', 'month', 'year', 'net_salary', 'status', 'created_at')

@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'school', 'created_at')

@admin.register(TeacherInvoice)
class TeacherInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'teacher', 'school', 'month', 'year', 'net_amount', 'status', 'created_at')

@admin.register(CoordinatorInvoice)
class CoordinatorInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'school_id', 'total_amount', 'paid_amount', 'due_amount', 'status', 'issue_date', 'due_date')

    