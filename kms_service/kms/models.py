import datetime
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Custom User model with UUID primary key for microservice sync
class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, role=None, **extra_fields):
        if role:
            extra_fields['role'] = role
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        # Sync to KMS models
        if role == "teacher":
            from kms.models import Teacher
            Teacher.objects.get_or_create(user=user, defaults={'id': user.id, 'name': username})
        elif role == "coordinator":
            from kms.models import Coordinator
            Coordinator.objects.get_or_create(user=user, defaults={'id': user.id, 'name': username})
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, role="admin", **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        app_label = 'kms'
    
    def __str__(self):
        return self.username


class ApprovalStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "Approve", "Approved"
    REJECTED = "Reject", "Rejected"

class CourseStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    RUNNING = "RUNNING", "Running"
    COMPLETED = "COMPLETED", "Completed"




class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,blank=False, unique=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
   
    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
   
    def __str__(self):
        return f"{self.name} ({self.school.name})"


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    created_by = models.UUIDField()  # teacher or coordinator

    # Approval workflow
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        db_index=True
    )

    # Lifecycle tracking
    status = models.CharField(
        max_length=20,
        choices=CourseStatus.choices,
        default=CourseStatus.DRAFT,
        db_index=True
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    schools = models.ManyToManyField(School, related_name='teachers', through='TeacherSalary')
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_classes_count(self):
        return self.teacherclassassignment_set.count()
    
    def get_total_earnings(self):
        return self.total_earnings
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"

class TeacherSalary(models.Model):
    """Fixed salary per school for each teacher"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('teacher', 'school')
    
    def __str__(self):
        return f"{self.teacher.name} - {self.school.name}: {self.monthly_salary}"

class PaymentType(models.TextChoices):
    FIXED_MONTHLY = "FIXED_MONTHLY", "Fixed Monthly"
    HOURLY = "HOURLY", "Hourly Rate"
    PER_CLASS = "PER_CLASS", "Per Class Rate"

class TeacherCompensationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.FIXED_MONTHLY
    )
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount per month, hour, or class")
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Commission % (e.g., 5.00 for 5%)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('teacher', 'school')

    def __str__(self):
        return f"{self.teacher.name} - {self.get_payment_type_display()} at {self.school.name}"

class SalarySlipStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    LOCKED = "LOCKED", "Locked"
    PAID = "PAID", "Paid"

class TeacherSalarySlip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    total_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_classes = models.IntegerField(default=0)
    
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adjustments = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Manual additions/deductions")
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(
        max_length=20,
        choices=SalarySlipStatus.choices,
        default=SalarySlipStatus.DRAFT
    )
    
    admin_override = models.BooleanField(default=False)
    override_notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('teacher', 'school', 'month', 'year')

    def __str__(self):
        return f"Slip: {self.teacher.name} - {self.month}/{self.year} ({self.status})"


class Coordinator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinators')
    name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class TeacherClassAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('teacher', 'classroom', 'school')

class TeacherCourseAssignment(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

#Student and Enrollment
class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,null=True,blank=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')


#Attendance
class TeacherAttendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        db_index=True
    )
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    supervised_by = models.CharField(max_length=255, null=True, blank=True) 
    supervised_at = models.DateTimeField(default=timezone.now) 


class StudentAttendance(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('sick_leave', 'Sick Leave'),
        ('casual_leave', 'Casual Leave'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='present'
    )
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    marked_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    
    approved = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        db_index=True
    )
    approved_by = models.CharField(max_length=255, null=True, blank=True)  # auth_user_id of coordinator
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'classroom', 'date')
        indexes = [
            models.Index(fields=['teacher', 'date']),
            models.Index(fields=['classroom', 'date']),
        ]


#Teacher KYC and Profile
class TeacherKYC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.OneToOneField("Teacher", on_delete=models.CASCADE, related_name='kyc')
    id_doc = models.FileField(upload_to="kyc/id_docs/")
    cv = models.FileField(upload_to="kyc/cv/", null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    document_verified = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )
    rejection_reason = models.TextField(null=True, blank=True)
    kyc_status_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_classes = models.IntegerField(default=0)
    total_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.teacher.name} - KYC ({self.status})"

