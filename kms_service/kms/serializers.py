from django.utils import timezone
from rest_framework import serializers
import uuid
from .models import School, ClassRoom, Course, StudentAttendance, Student, Teacher, TeacherAttendance, TeacherCourseAssignment, TeacherClassAssignment, Enrollment, TeacherKYC, TeacherSalary, TeacherCompensationRule, TeacherSalarySlip, TeacherInvoice, CoordinatorInvoice

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class ClassRoomSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    school = serializers.CharField(write_only=True, help_text="School name or UUID")
    
    class Meta:
        model = ClassRoom
        fields = ['id', 'name', 'school', 'school_name', 'created_at']
    
    def validate_school(self, value):
        """Convert school name or UUID to School instance"""
        try:
            # Try UUID lookup
            school = School.objects.get(id=value)
            return school
        except (School.DoesNotExist, ValueError):
            pass
        
        try:
            # Try converting string to UUID
            lookup_uuid = uuid.UUID(str(value))
            school = School.objects.get(id=lookup_uuid)
            return school
        except (ValueError, School.DoesNotExist):
            pass
        
        try:
            # Try name lookup
            school = School.objects.get(name=value)
            return school
        except School.DoesNotExist:
            raise serializers.ValidationError(f"School '{value}' not found. Use school name or UUID.")

class CourseSerializer(serializers.ModelSerializer):
    # Accept school by id or name
    school = serializers.CharField(write_only=True, help_text="School name or UUID")
    school_name = serializers.CharField(source='school.name', read_only=True)

    # created_by should not be provided by frontend; show it as read-only
    created_by = serializers.UUIDField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'school', 'school_name', 'created_by', 'approval_status',
            'status', 'start_date', 'end_date', 'created_at'
        ]

    def validate_school(self, value):
        """Convert school name or UUID to School instance"""
        try:
            school = School.objects.get(id=value)
            return school
        except (School.DoesNotExist, ValueError):
            pass
        
        try:
            lookup_uuid = uuid.UUID(str(value))
            school = School.objects.get(id=lookup_uuid)
            return school
        except (ValueError, School.DoesNotExist):
            pass
        
        try:
            school = School.objects.get(name=value)
            return school
        except School.DoesNotExist:
            raise serializers.ValidationError(f"School '{value}' not found. Use school name or UUID.")

    def validate(self, attrs):
        # Resolve school either from provided `school` (id) or `school_name`
        request = self.context.get('request')
        school_name = None
        if not attrs.get('school'):
            # read raw input to check for school_name
            if request and hasattr(request, 'data'):
                school_name = request.data.get('school_name')

        if school_name:
            try:
                school_obj = School.objects.get(name=school_name)
            except School.DoesNotExist:
                raise serializers.ValidationError({'school_name': 'School with this name not found'})
            attrs['school'] = school_obj

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        # Pop any helper key if present
        validated_data.pop('school_name', None)

        # Auto-fill created_by from authenticated token or request.user
        auth = None
        if request is not None:
            auth = getattr(request, 'auth', None)

        user_id = None
        if isinstance(auth, dict):
            user_id = auth.get('user_id')
        elif request and getattr(request, 'user', None):
            user_id = getattr(request.user, 'id', None)

        if user_id is None:
            # fallback to None — model expects a UUID, but let DB raise if required
            pass
        else:
            validated_data['created_by'] = user_id

        return super().create(validated_data)

    def validate_status(self, value):
        """Normalize friendly status inputs (case-insensitive) to CourseStatus choices."""
        if value is None:
            return value
        # Accept already-correct values
        valid = {"DRAFT", "RUNNING", "COMPLETED"}
        if value in valid:
            return value

        v = str(value).strip().upper()
        if v in valid:
            return v

        raise serializers.ValidationError("Invalid status. Valid values: DRAFT, RUNNING, COMPLETED")

class TeacherSalarySerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    school = serializers.CharField(write_only=True, help_text="School name or UUID")
    teacher = serializers.CharField(write_only=True, help_text="Teacher name or UUID")
    
    class Meta:
        model = TeacherSalary
        fields = ['id', 'school', 'school_name', 'teacher', 'teacher_name', 'monthly_salary', 'created_at']
    
    def validate_school(self, value):
        """Convert school name or UUID to School instance"""
        try:
            school = School.objects.get(id=value)
            return school
        except (School.DoesNotExist, ValueError):
            pass
        
        try:
            school = School.objects.get(id=uuid.UUID(str(value)))
            return school
        except (ValueError, School.DoesNotExist):
            pass
        
        try:
            school = School.objects.get(name=value)
            return school
        except School.DoesNotExist:
            raise serializers.ValidationError(f"School '{value}' not found. Use school name or UUID.")
    
    def validate_teacher(self, value):
        """Convert teacher name or UUID to Teacher instance"""
        from kms.apis.administrator import resolve_teacher
        teacher = resolve_teacher(value)
        if not teacher:
            raise serializers.ValidationError(f"Teacher '{value}' not found. Use teacher name or UUID.")
        return teacher

class TeacherCompensationRuleSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    school = serializers.CharField(write_only=True, help_text="School name or UUID")
    teacher = serializers.CharField(write_only=True, help_text="Teacher name or UUID")
    
    class Meta:
        model = TeacherCompensationRule
        fields = ['id', 'school', 'school_name', 'teacher', 'teacher_name', 'payment_type', 'base_rate', 'commission_percentage', 'is_active', 'created_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure the teacher ID returned is the User ID (Auth ID)
        if instance.teacher and instance.teacher.user:
            data['teacher'] = str(instance.teacher.user.id)
        return data
    
    def validate_school(self, value):
        from kms.apis.administrator import resolve_classroom, resolve_course # Using custom resolve if needed, but we can do UUID/Name parsing
        # (Assuming the same logic as TeacherSalarySerializer above)
        try:
            school = School.objects.get(id=value)
            return school
        except (School.DoesNotExist, ValueError):
            pass
        try:
            school = School.objects.get(id=uuid.UUID(str(value)))
            return school
        except (ValueError, School.DoesNotExist):
            pass
        try:
            school = School.objects.get(name=value)
            return school
        except School.DoesNotExist:
            raise serializers.ValidationError(f"School '{value}' not found. Use school name or UUID.")
    
    def validate_teacher(self, value):
        from kms.apis.administrator import resolve_teacher
        teacher = resolve_teacher(value)
        if not teacher:
             raise serializers.ValidationError(f"Teacher '{value}' not found. Use teacher name or UUID.")
        return teacher

class TeacherSalarySlipSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    
    class Meta:
        model = TeacherSalarySlip
        fields = [
            'id', 'teacher', 'teacher_name', 'school', 'school_name', 
            'month', 'year', 'total_hours', 'total_classes', 
            'base_salary', 'commission', 'adjustments', 'net_salary', 
            'status', 'admin_override', 'override_notes', 'created_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure the teacher ID returned is the User ID (Auth ID)
        if instance.teacher and instance.teacher.user:
            data['teacher'] = str(instance.teacher.user.id)
        return data

class CoordinatorInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoordinatorInvoice
        fields = [
            'id', 'school_id', 'invoice_number', 'total_amount', 
            'paid_amount', 'due_amount', 'description', 
            'issue_date', 'due_date', 'status', 'bank_qr_code', 'created_at'
        ]
        read_only_fields = ['id', 'due_amount', 'created_at']

class TeacherKYCSerializer(serializers.ModelSerializer):
    bank_account_number = serializers.CharField(required=True, allow_blank=False)
    class Meta:
        model = TeacherKYC
        fields = [
            'id', 'id_doc', 'cv', 'bank_account_number', 'bank_name', 
            'citizenship', 'n_id_number', 'photo', 'address', 'status', 
            'phone_verified', 'document_verified', 'submitted_at', 
            'updated_at', 'approved_at', 'rejection_reason'
        ]

class TeacherDetailedSerializer(serializers.ModelSerializer):
    """Detailed teacher profile with earnings, classes, and salary info"""
    classes_count = serializers.SerializerMethodField()
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    salaries = TeacherSalarySerializer(many=True, source='teachersalary_set', read_only=True)
    kyc = TeacherKYCSerializer(read_only=True)
    classes = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'email', 'phone_number', 'is_active', 
                  'classes_count', 'classes', 'total_earnings', 'salaries', 'kyc']
    
    def get_classes_count(self, obj):
        return obj.get_classes_count()
    
    def get_classes(self, obj):
        assignments = TeacherClassAssignment.objects.filter(teacher=obj).select_related('classroom', 'classroom__school')
        return [
            {
                'classroom_id': a.classroom.id,
                'classroom_name': a.classroom.name,
                'school_id': a.classroom.school.id,
                'school_name': a.classroom.school.name,
                'assigned_at': a.assigned_at
            } for a in assignments
        ]

class TeacherProfileSerializer(serializers.ModelSerializer):
    """Teacher profile with UUID ID and user info"""
    user_id = serializers.CharField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'user_id', 'name', 'email', 'username', 'phone_number', 'is_active']

class StudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False)
    school = serializers.CharField(write_only=True, help_text="School name or UUID")
    school_name = serializers.CharField(source='school.name', read_only=True)
    classroom = serializers.CharField(write_only=True, required=False, allow_null=True, help_text="Classroom UUID")
    classroom_name = serializers.CharField(source='classroom.name', read_only=True, default=None)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'school', 'school_name',
            'classroom', 'classroom_name',
            'address', 'phone_number', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_school(self, value):
        """Convert school name or UUID to School instance"""
        if not value:
            raise serializers.ValidationError("School is required.")
        try:
            return School.objects.get(id=value)
        except (School.DoesNotExist, ValueError):
            pass
        try:
            lookup_uuid = uuid.UUID(str(value))
            return School.objects.get(id=lookup_uuid)
        except (ValueError, School.DoesNotExist):
            pass
        try:
            return School.objects.get(name=value)
        except School.DoesNotExist:
            raise serializers.ValidationError(f"School '{value}' not found. Use school name or UUID.")

    def validate_classroom(self, value):
        """Convert classroom UUID to ClassRoom instance"""
        if not value:
            return None
        try:
            return ClassRoom.objects.get(id=value)
        except (ClassRoom.DoesNotExist, ValueError):
            pass
        try:
            lookup_uuid = uuid.UUID(str(value))
            return ClassRoom.objects.get(id=lookup_uuid)
        except (ValueError, ClassRoom.DoesNotExist):
            raise serializers.ValidationError(f"Classroom '{value}' not found.")

class StudentAttendanceDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    class Meta:
        model = StudentAttendance
        fields = ['id', 'student', 'student_name', 'classroom', 'classroom_name', 
                  'date', 'status', 'marked_at', 'notes', 'approved']

class MarkAttendanceSerializer(serializers.Serializer):
    """Serializer for marking student attendance"""
    student_id = serializers.CharField(help_text="Student name or UUID")
    # Make these optional for use in bulk marking
    classroom_id = serializers.CharField(required=False, help_text="Classroom name or UUID")
    date = serializers.DateField(required=False)
    status = serializers.ChoiceField(
        choices=['present', 'absent', 'late', 'sick_leave', 'casual_leave']
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_classroom_id(self, value):
        """Convert classroom name or UUID to ClassRoom instance"""
        try:
            classroom = ClassRoom.objects.get(id=value)
            return classroom
        except (ClassRoom.DoesNotExist, ValueError):
            pass
        
        try:
            lookup_uuid = uuid.UUID(str(value))
            classroom = ClassRoom.objects.get(id=lookup_uuid)
            return classroom
        except (ValueError, ClassRoom.DoesNotExist):
            pass
        
        try:
            classroom = ClassRoom.objects.get(name=value)
            return classroom
        except ClassRoom.DoesNotExist:
            raise serializers.ValidationError(f"Classroom '{value}' not found. Use classroom name or UUID.")
    
    def validate(self, data):
        student_id = data.get('student_id')
        if not student_id:
            raise serializers.ValidationError({"student_id": "This field is required."})
            
        try:
            student = Student.objects.get(id=student_id)
            data['student'] = student
        except (Student.DoesNotExist, ValueError):
            raise serializers.ValidationError({"student_id": "Student not found"})

        # classroom_id is optional at this level if provided at bulk level
        classroom = data.get('classroom_id')
        if classroom:
            if isinstance(classroom, ClassRoom):
                data['classroom'] = classroom
            else:
                # This should have been handled by validate_classroom_id
                pass

        # remove helper key to keep downstream code consistent
        data.pop('classroom_id', None)
        return data


# class CoordinatorAssignmentSerializer(serializers.Serializer):
#     """Coordinator: Assign teacher to classroom/course by name or ID within their school.
#     Supports assigning teacher to multiple classrooms/courses in a single request.
#     """
#     # Use CharField to accept any string input, convert in validators
#     teacher = serializers.CharField(help_text="Teacher name or UUID")
#     classrooms = serializers.ListField(
#         child=serializers.CharField(),
#         required=False,
#         allow_empty=True,
#         help_text="List of classroom names or UUIDs within coordinator's school"
#     )
#     courses = serializers.ListField(
#         child=serializers.CharField(),
#         required=False,
#         allow_empty=True,
#         help_text="List of course names or UUIDs within coordinator's school"
#     )
    
#     def validate_teacher(self, value):
#         """Convert teacher name or UUID to Teacher instance"""
#         try:
#             teacher = Teacher.objects.get(id=value)
#             return teacher
#         except (Teacher.DoesNotExist, ValueError):
#             pass
        
#         try:
#             lookup_uuid = uuid.UUID(str(value))
#             teacher = Teacher.objects.get(id=lookup_uuid)
#             return teacher
#         except (ValueError, Teacher.DoesNotExist):
#             pass
        
#         try:
#             teacher = Teacher.objects.get(name=value)
#             return teacher
#         except Teacher.DoesNotExist:
#             pass
        
#         try:
#             teacher = Teacher.objects.get(user_id=value)
#             return teacher
#         except Teacher.DoesNotExist:
#             pass
        
#         try:
#             lookup_uuid = uuid.UUID(str(value))
#             teacher = Teacher.objects.get(user_id=lookup_uuid)
#             return teacher
#         except (ValueError, Teacher.DoesNotExist):
#             raise serializers.ValidationError(f"Teacher '{value}' not found. Use teacher name or UUID.")
    
#     def validate_classrooms(self, value):
#         """Convert classroom names/ids to ClassRoom instances"""
#         classrooms = []
#         for item in value:
#             try:
#                 classroom = ClassRoom.objects.get(id=item)
#                 classrooms.append(classroom)
#                 continue
#             except (ClassRoom.DoesNotExist, ValueError):
#                 pass
            
#             try:
#                 lookup_uuid = uuid.UUID(str(item))
#                 classroom = ClassRoom.objects.get(id=lookup_uuid)
#                 classrooms.append(classroom)
#                 continue
#             except (ValueError, ClassRoom.DoesNotExist):
#                 pass
            
#             try:
#                 classroom = ClassRoom.objects.get(name=item)
#                 classrooms.append(classroom)
#             except ClassRoom.DoesNotExist:
#                 raise serializers.ValidationError(f"Classroom '{item}' not found. Use classroom name or UUID.")
        
#         return classrooms
    
#     def validate_courses(self, value):
#         """Convert course names/ids to Course instances"""
#         courses = []
#         for item in value:
#             try:
#                 course = Course.objects.get(id=item)
#                 courses.append(course)
#                 continue
#             except (Course.DoesNotExist, ValueError):
#                 pass
            
#             try:
#                 lookup_uuid = uuid.UUID(str(item))
#                 course = Course.objects.get(id=lookup_uuid)
#                 courses.append(course)
#                 continue
#             except (ValueError, Course.DoesNotExist):
#                 pass
            
#             try:
#                 course = Course.objects.get(title=item)
#                 courses.append(course)
#             except Course.DoesNotExist:
#                 raise serializers.ValidationError(f"Course '{item}' not found. Use course title or UUID.")
        
#         return courses

#     def validate(self, attrs):
#         if not attrs.get('classrooms') and not attrs.get('courses'):
#             raise serializers.ValidationError("Either classroom or course must be provided")
#         return attrs


# class AttendanceApprovalSerializer(serializers.Serializer):
#     action = serializers.ChoiceField(choices=['approve', 'reject'])
#     notes = serializers.CharField(required=False, allow_blank=True)


# class BulkAttendanceApprovalSerializer(serializers.Serializer):
#     attendance_ids = serializers.ListField(child=serializers.CharField())
#     action = serializers.ChoiceField(choices=['approve', 'reject'])
#     notes = serializers.CharField(required=False, allow_blank=True)

class BulkMarkAttendanceSerializer(serializers.Serializer):
    """Mark attendance for multiple students at once"""
    classroom_id = serializers.UUIDField()
    date = serializers.DateField()
    attendances = MarkAttendanceSerializer(many=True, required=True)

class AttendanceReportSerializer(serializers.Serializer):
    """Attendance report for a classroom/teacher"""
    date = serializers.DateField()
    total_students = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    leave = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()

# class TeacherCourseAssignmentSerializer(serializers.ModelSerializer):
#     course_name = serializers.CharField(source='course.title', read_only=True)
#     teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    
#     class Meta:
#         model = TeacherCourseAssignment
#         fields = ['id', 'teacher', 'course', 'teacher_name', 'course_name', 'assigned_at']

class TeacherClassAssignmentSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    school_name = serializers.CharField(source='classroom.school.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    
    class Meta:
        model = TeacherClassAssignment
        fields = ['id', 'teacher', 'classroom', 'teacher_name', 'classroom_name', 'school_name', 'assigned_at']

# class AdminTeacherAssignmentSerializer(serializers.Serializer):
#     """Admin API: Assign teacher to classroom/course by name or ID.
    
#     Supports single or bulk assignments:
#     - {"teacher": "John Doe", "classrooms": ["Class 1", "Class 2"]}
#     - {"teacher": "uuid", "courses": ["course_id_1", "course_id_2"]}
#     """
#     # Use CharField to accept any string input, convert in validators
#     teacher = serializers.CharField(help_text="Teacher name or UUID")
#     classrooms = serializers.ListField(
#         child=serializers.CharField(),
#         required=False,
#         allow_empty=True,
#         help_text="List of classroom names or UUIDs"
#     )
#     courses = serializers.ListField(
#         child=serializers.CharField(),
#         required=False,
#         allow_empty=True,
#         help_text="List of course names or UUIDs"
#     )
    
#     def validate_teacher(self, value):
#         """Convert teacher name or UUID to Teacher instance"""
#         try:
#             # Try UUID lookup
#             teacher = Teacher.objects.get(id=value)
#             return teacher
#         except (Teacher.DoesNotExist, ValueError):
#             pass
        
#         try:
#             # Try converting string to UUID
#             lookup_uuid = uuid.UUID(str(value))
#             teacher = Teacher.objects.get(id=lookup_uuid)
#             return teacher
#         except (ValueError, Teacher.DoesNotExist):
#             pass
        
#         try:
#             # Try lookup by name
#             teacher = Teacher.objects.get(name=value)
#             return teacher
#         except Teacher.DoesNotExist:
#             pass
        
#         # Try lookup by user_id
#         try:
#             teacher = Teacher.objects.get(user_id=value)
#             return teacher
#         except Teacher.DoesNotExist:
#             pass
        
#         try:
#             lookup_uuid = uuid.UUID(str(value))
#             teacher = Teacher.objects.get(user_id=lookup_uuid)
#             return teacher
#         except (ValueError, Teacher.DoesNotExist):
#             raise serializers.ValidationError(f"Teacher '{value}' not found. Use teacher name or UUID.")
    
#     def validate_classrooms(self, value):
#         """Convert classroom names/ids to ClassRoom instances"""
#         classrooms = []
#         for item in value:
#             try:
#                 # Try UUID lookup
#                 classroom = ClassRoom.objects.get(id=item)
#             except (ClassRoom.DoesNotExist, ValueError):
#                 pass
#             else:
#                 classrooms.append(classroom)
#                 continue
            
#             try:
#                 # Try converting string to UUID
#                 lookup_uuid = uuid.UUID(str(item))
#                 classroom = ClassRoom.objects.get(id=lookup_uuid)
#                 classrooms.append(classroom)
#                 continue
#             except (ValueError, ClassRoom.DoesNotExist):
#                 pass
            
#             try:
#                 # Try name lookup
#                 classroom = ClassRoom.objects.get(name=item)
#                 classrooms.append(classroom)
#             except ClassRoom.DoesNotExist:
#                 raise serializers.ValidationError(f"Classroom '{item}' not found. Use classroom name or UUID.")
        
#         return classrooms
    
#     def validate_courses(self, value):
#         """Convert course names/ids to Course instances"""
#         courses = []
#         for item in value:
#             try:
#                 # Try UUID lookup
#                 course = Course.objects.get(id=item)
#             except (Course.DoesNotExist, ValueError):
#                 pass
#             else:
#                 courses.append(course)
#                 continue
            
#             try:
#                 # Try converting string to UUID
#                 lookup_uuid = uuid.UUID(str(item))
#                 course = Course.objects.get(id=lookup_uuid)
#                 courses.append(course)
#                 continue
#             except (ValueError, Course.DoesNotExist):
#                 pass
            
#             try:
#                 # Try title lookup
#                 course = Course.objects.get(title=item)
#                 courses.append(course)
#             except Course.DoesNotExist:
#                 raise serializers.ValidationError(f"Course '{item}' not found. Use course title or UUID.")
        
#         return courses
    
#     def validate(self, attrs):
#         if not attrs.get('classrooms') and not attrs.get('courses'):
#             raise serializers.ValidationError("Either classrooms or courses must be provided")
#         return attrs

# class BulkTeacherAssignmentSerializer(serializers.Serializer):
#     """Bulk assignment: Multiple teachers to multiple classrooms/courses"""
#     assignments = AdminTeacherAssignmentSerializer(many=True)
#     school_id = serializers.UUIDField(required=False, help_text="Optional: filter assignments by school")

# class EnrollmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Enrollment
#         fields = '__all__'

class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_id = serializers.UUIDField(source="teacher.id", read_only=True)
    teacher_name = serializers.CharField(source="teacher.user.username", read_only=True)
    school_id = serializers.UUIDField(source="school.id", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = TeacherAttendance
        fields = [
            "id",
            "teacher_id",
            "teacher_name",
            # "date",
            "check_in",
            "check_out",   
            "school_id",
            "school_name",
            "status",
            "supervised_at",
            "supervised_by",
            "total_hours",    
        ]

class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__'

class TeacherKYCUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherKYC
        fields = [
            "id_doc", "cv", "bank_account_number", "bank_name", 
            "citizenship", "n_id_number", "photo", "address"
        ]
        extra_kwargs = {
            'cv': {'required': False, 'allow_null': True},
            'address': {'required': False, 'allow_blank': True},
            'bank_account_number': {'required': True},
            'bank_name': {'required': True},
            'citizenship': {'required': True},
            'n_id_number': {'required': True},
            'photo': {'required': True},
        }

    def validate(self, attrs):
        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError("Request context is required.")

        # Get Teacher from request user
        user = request.user
        if not user:
            raise serializers.ValidationError("Authentication error.")

        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError("Teacher profile not found.")

        # Check if KYC already approved
        existing_kyc = TeacherKYC.objects.filter(teacher=teacher).first()

        if existing_kyc and existing_kyc.status == "approved":
            raise serializers.ValidationError(
                "KYC already approved. Cannot resubmit."
            )

        self.teacher = teacher
        self.existing_kyc = existing_kyc

        return attrs

    def create(self, validated_data):
        # If KYC already exists → update it instead of creating new
        if self.existing_kyc:
            for attr, value in validated_data.items():
                setattr(self.existing_kyc, attr, value)
            self.existing_kyc.status = "pending"
            self.existing_kyc.updated_at = timezone.now()
            self.existing_kyc.save()
            return self.existing_kyc

        # Create new KYC
        return TeacherKYC.objects.create(
            teacher=self.teacher,
            status="pending",
            **validated_data
        )


# class LoginSerializer(serializers.Serializer):
#     """Handles teacher login and returns JWT token with teacher UUID."""
#     username = serializers.CharField(write_only=True)
#     password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
#     access_token = serializers.CharField(read_only=True)
#     refresh_token = serializers.CharField(read_only=True)
#     token_type = serializers.CharField(read_only=True)
#     expires_in = serializers.IntegerField(read_only=True)
    
#     user_id = serializers.CharField(read_only=True)
#     teacher_uuid = serializers.CharField(read_only=True)
#     username_resp = serializers.CharField(read_only=True, source='username')
#     email = serializers.EmailField(read_only=True)
#     role = serializers.CharField(read_only=True)


# class TeacherClassAssignmentSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = TeacherClassAssignment
#         fields = "__all__"

#     def validate(self, attrs):
#         teacher = attrs.get("teacher")
#         classroom = attrs.get("classroom")
#         school = attrs.get("school")
#         if not teacher or not classroom or not school:
#             raise serializers.ValidationError("Teacher, classroom, and school are required.")
#         # Check classroom belongs to school
#         if classroom.school != school:
#             raise serializers.ValidationError(
#                 "Classroom does not belong to the selected school."
#             )

#         return attrs

from rest_framework import serializers
from .models import User

class UserSyncSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    full_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    role = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    gender = serializers.CharField(max_length=10, required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_null=True)

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'is_staff', 'date_joined']

class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.user.username", read_only=True)

    class Meta:
        model = StudentAttendance
        fields = [
            "id",
            "student",
            "student_name",
            "classroom",
            "classroom_name",
            "teacher",
            "teacher_name",
            "date",
            "status",
            "marked_by",
            "marked_at",
            "approved",
            "approved_by",
            "approved_at",
            "notes",
        ]
        read_only_fields = ["marked_by", "marked_at", "approved_by", "approved_at"]

# StudentSerializer is defined above (near line 285) — do not duplicate here.


class TeacherInvoiceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.username', read_only=True, default=None)

    class Meta:
        model = TeacherInvoice
        fields = [
            'id', 'invoice_number',
            'teacher', 'teacher_name',
            'school', 'school_name',
            'month', 'year',
            'base_salary', 'total_hours', 'total_classes',
            'commission_rate', 'commission_amount',
            'tax_rate', 'tax_amount',
            'adjustments', 'gross_amount', 'net_amount',
            'status', 'notes',
            'generated_by', 'generated_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'teacher', 'school',
            'month', 'year', 'base_salary', 'total_hours', 'total_classes',
            'commission_rate', 'commission_amount',
            'generated_by', 'created_at', 'updated_at',
        ]