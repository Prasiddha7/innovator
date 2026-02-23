
from django.contrib import admin
from .models import Enrollment, School, ClassRoom,Course, Student, StudentAttendance, Teacher, TeacherAttendance, TeacherClassAssignment, TeacherCourseAssignment, TeacherKYC, TeacherSalary

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'created_by', 'status', 'created_at')


@admin.register(ClassRoom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'school','created_at')
    
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'total_earnings', 'is_active', 'created_at')

@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school', 'monthly_salary', 'created_at')

@admin.register(TeacherClassAssignment)
class TeacherClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'classroom', 'assigned_at')

@admin.register(TeacherCourseAssignment)
class TeacherCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'course', 'assigned_at')

@admin.register(TeacherKYC)
class TeacherKYCAdmin(admin.ModelAdmin):        
    list_display = ('teacher', 'id_doc', 'cv', 'status', 'submitted_at')

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school', 'check_in', 'check_out', 'status', 'total_hours', 'supervised_by', 'supervised_at')    

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'created_at') 

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at') 

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'teacher', 'date', 'status', 'marked_by', 'marked_at')   

    