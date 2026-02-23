import uuid
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from kms.models import (
    School, ClassRoom, Course, TeacherKYC, TeacherClassAssignment, TeacherCourseAssignment,
    Teacher, TeacherSalary, Student, StudentAttendance,
    TeacherCompensationRule, TeacherSalarySlip, PaymentType, SalarySlipStatus
)
from kms.serializers import (
    ClassRoomSerializer,
    CourseSerializer,
    SchoolSerializer,
    TeacherClassAssignmentSerializer,
    TeacherKYCSerializer,
    TeacherCompensationRuleSerializer,
    TeacherSalarySlipSerializer
    # SchoolSerializer, ClassRoomSerializer, CourseSerializer,
    # TeacherClassAssignmentSerializer, TeacherCourseAssignmentSerializer, TeacherKYCSerializer,
    # AdminTeacherAssignmentSerializer, BulkTeacherAssignmentSerializer
)
from kms.permissions import IsAdmin
from kms.authentication import CustomJWTAuthentication
from django.db import transaction


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def resolve_teacher(value):
    # If UUID
    if is_valid_uuid(value):
        # 1️⃣ Try Teacher ID
        teacher = Teacher.objects.filter(id=value).first()
        if teacher:
            return teacher

        # 2️⃣ Try User ID
        teacher = Teacher.objects.filter(user__id=value).first()
        if teacher:
            return teacher

        return None

    # If not UUID → try username or teacher name
    return Teacher.objects.filter(
        Q(name=value) | Q(user__username=value)
    ).first()



def resolve_classroom(value):
    if is_valid_uuid(value):
        return ClassRoom.objects.filter(id=value).first()
    return ClassRoom.objects.filter(name=value).first()


def resolve_course(value):
    if is_valid_uuid(value):
        return Course.objects.filter(id=value).first()
    return Course.objects.filter(title=value).first()


# ============================================================================
# SCHOOL MANAGEMENT
# ============================================================================

class SchoolView(APIView):
    """Create, list, retrieve, update schools"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, school_id=None):
        """List all schools or get specific school"""
        if school_id:
            try:
                school = School.objects.get(id=school_id)
                serializer = SchoolSerializer(school)
                return Response(serializer.data)
            except School.DoesNotExist:
                return Response({"detail": "School not found"}, status=status.HTTP_404_NOT_FOUND)
        
        schools = School.objects.all()
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create new school"""
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, school_id):
        """Update school"""
        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            return Response({"detail": "School not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SchoolSerializer(school, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, school_id):
        """Delete school"""
        try:
            school = School.objects.get(id=school_id)
            school.delete()
            return Response({"message": "School deleted"}, status=status.HTTP_204_NO_CONTENT)
        except School.DoesNotExist:
            return Response({"detail": "School not found"}, status=status.HTTP_404_NOT_FOUND)


# ============================================================================
# CLASSROOM MANAGEMENT
# ============================================================================

class ClassRoomView(APIView):
    """Create, list, retrieve, update classrooms"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, classroom_id=None):
        """List all classrooms or get specific classroom"""
        if classroom_id:
            try:
                classroom = ClassRoom.objects.get(id=classroom_id)
                serializer = ClassRoomSerializer(classroom)
                return Response(serializer.data)
            except ClassRoom.DoesNotExist:
                return Response({"detail": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)
        
        classrooms = ClassRoom.objects.all()
        serializer = ClassRoomSerializer(classrooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create new classroom"""
        serializer = ClassRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, classroom_id):
        """Update classroom"""
        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
        except ClassRoom.DoesNotExist:
            return Response({"detail": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClassRoomSerializer(classroom, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, classroom_id):
        """Delete classroom"""
        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
            classroom.delete()
            return Response({"message": "Classroom deleted"}, status=status.HTTP_204_NO_CONTENT)
        except ClassRoom.DoesNotExist:
            return Response({"detail": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)


# ============================================================================
# COURSE MANAGEMENT
# ============================================================================

class CourseView(APIView):
    """Create, list, retrieve, update courses"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, course_id=None):
        """List all courses or get specific course"""
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                serializer = CourseSerializer(course)
                return Response(serializer.data)
            except Course.DoesNotExist:
                return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create new course"""
        serializer = CourseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, course_id):
        """Update course"""
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, course_id):
        """Partial update course (use PATCH for approval/status changes)"""
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id):
        """Delete course"""
        try:
            course = Course.objects.get(id=course_id)
            course.delete()
            return Response({"message": "Course deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)


# ============================================================================
# TEACHER CLASS/COURSE ASSIGNMENT
# ============================================================================

class TeacherClassAssignmentView(APIView):
    """
    Assign teacher to multiple classrooms and courses.

    Payload:
    {
        "teacher": "teacher_username_or_uuid",
        "classrooms": ["Class 1", "Class 2"],
        "courses": ["Python Basics"]
    }
    """

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    @transaction.atomic
    def post(self, request):

        teacher_value = request.data.get("teacher")
        classroom_values = request.data.get("classrooms", [])
        course_values = request.data.get("courses", [])

        if not teacher_value:
            return Response(
                {"error": "Teacher field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------
        # Resolve Teacher
        # ---------------------------
        teacher = resolve_teacher(teacher_value)

        if not teacher:
            return Response(
                {"error": f"Teacher '{teacher_value}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        results = {
            "teacher": teacher.name,
            "classroom_assignments": [],
            "course_assignments": []
        }

        # ---------------------------
        # Assign Classrooms
        # ---------------------------
        for value in classroom_values:
            classroom = resolve_classroom(value)

            if not classroom:
                return Response(
                    {"error": f"Classroom '{value}' not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            assignment, created = TeacherClassAssignment.objects.get_or_create(
                teacher=teacher,
                classroom=classroom
            )

            results["classroom_assignments"].append({
                "id": str(assignment.id),
                "classroom": classroom.name,
                "school": classroom.school.name,
                "created": created,
                "assigned_at": assignment.assigned_at
            })

        # ---------------------------
        # Assign Courses
        # ---------------------------
        for value in course_values:
            course = resolve_course(value)

            if not course:
                return Response(
                    {"error": f"Course '{value}' not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            assignment, created = TeacherCourseAssignment.objects.get_or_create(
                teacher=teacher,
                course=course
            )

            results["course_assignments"].append({
                "id": str(assignment.id),
                "course": course.title,
                "created": created,
                "assigned_at": assignment.assigned_at
            })

        return Response(results, status=status.HTTP_201_CREATED)


# ============================================================================
# KYC VERIFICATION & MANAGEMENT
# ============================================================================

class TeacherKYCView(APIView):
    """Verify and manage teacher KYC applications"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, kyc_id=None):
        """List all KYC applications or filter by status"""
        status_filter = request.query_params.get('status')  # pending, approved, rejected
        
        if kyc_id:
            try:
                kyc = TeacherKYC.objects.get(id=kyc_id)
                serializer = TeacherKYCSerializer(kyc)
                return Response(serializer.data)
            except TeacherKYC.DoesNotExist:
                return Response({"detail": "KYC not found"}, status=status.HTTP_404_NOT_FOUND)
        
        kycs = TeacherKYC.objects.all()
        
        if status_filter:
            kycs = kycs.filter(status=status_filter)
        
        serializer = TeacherKYCSerializer(kycs, many=True)
        return Response(serializer.data)

    def put(self, request, kyc_id):
        """Approve or reject KYC application"""
        try:
            kyc = TeacherKYC.objects.get(id=kyc_id)
        except TeacherKYC.DoesNotExist:
            return Response({"detail": "KYC not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'approve' or 'reject'
        
        if action == 'approve':
            kyc.status = 'approved'
            kyc.phone_verified = request.data.get('phone_verified', True)
            kyc.document_verified = request.data.get('document_verified', True)
            kyc.approved_at = timezone.now()
            kyc.rejection_reason = None
        elif action == 'reject':
            kyc.status = 'rejected'
            kyc.rejection_reason = request.data.get('rejection_reason', '')
        else:
            return Response(
                {"error": "Invalid action. Use 'approve' or 'reject'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        kyc.save()
        serializer = TeacherKYCSerializer(kyc)
        return Response(serializer.data)


# ============================================================================
# TEACHER SALARY MANAGEMENT
# ============================================================================

class TeacherSalaryView(APIView):
    """Manage teacher salaries per school"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """Get salary information"""
        teacher_id = request.query_params.get('teacher_id')
        school_id = request.query_params.get('school_id')
        
        salaries = TeacherSalary.objects.all()
        
        if teacher_id:
            salaries = salaries.filter(Q(teacher_id=teacher_id) | Q(teacher__user__id=teacher_id))
        if school_id:
            salaries = salaries.filter(school_id=school_id)
        
        data = []
        for salary in salaries:
            data.append({
                'id': str(salary.id),
                'teacher_id': str(salary.teacher.user.id),
                'teacher_name': salary.teacher.name,
                'school_id': str(salary.school.id),
                'school_name': salary.school.name,
                'monthly_salary': float(salary.monthly_salary),
                'created_at': salary.created_at,
                'updated_at': salary.updated_at,
            })
        
        return Response(data)

    def post(self, request):
        """Set salary for teacher at school"""
        teacher_id = request.data.get('teacher_id')
        school_id = request.data.get('school_id')
        monthly_salary = request.data.get('monthly_salary')
        
        if not all([teacher_id, school_id, monthly_salary]):
            return Response(
                {"error": "teacher_id, school_id, and monthly_salary are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            school = School.objects.get(id=school_id)
        except (Teacher.DoesNotExist, School.DoesNotExist):
            return Response(
                {"error": "Teacher or School not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        salary, created = TeacherSalary.objects.get_or_create(
            teacher=teacher,
            school=school,
            defaults={'monthly_salary': monthly_salary}
        )
        
        if not created:
            salary.monthly_salary = monthly_salary
            salary.save()
        
        return Response({
            'id': str(salary.id),
            'teacher_name': salary.teacher.name,
            'school_name': salary.school.name,
            'monthly_salary': float(salary.monthly_salary),
            'message': 'Salary created' if created else 'Salary updated'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# ============================================================================
# ADMIN DASHBOARD STATS
# ============================================================================

class AdminDashboardView(APIView):
    """Get admin dashboard statistics"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """Get dashboard metrics"""
        return Response({
            'total_teachers': Teacher.objects.filter(is_active=True).count(),
            'total_schools': School.objects.count(),
            'total_classrooms': ClassRoom.objects.count(),
            'total_students': Student.objects.count(),
            'kyc_applications': {
                'pending': TeacherKYC.objects.filter(status='pending').count(),
                'approved': TeacherKYC.objects.filter(status='approved').count(),
                'rejected': TeacherKYC.objects.filter(status='rejected').count(),
            },
            'teacher_assignments': TeacherClassAssignment.objects.count(),
            'today_attendance_rate': self._get_today_attendance_rate(),
        })
    
    def _get_today_attendance_rate(self):
        """Calculate today's attendance percentage"""
        today = timezone.now().date()
        today_records = StudentAttendance.objects.filter(date=today)
        
        if not today_records.exists():
            return 0
        
        present = today_records.filter(status='present').count()
        total = today_records.count()
        
        return round((present / total * 100) if total > 0 else 0, 2)

class AssignTeacherView(APIView):
    """Assign teacher to classroom or course"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        teacher = request.data.get("teacher")
        classroom = request.data.get("classroom")
        school = request.data.get("school")
        
        if not teacher or not classroom or not school:
            return Response(
                {"error": "Teacher, Classroom, and School fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teacher_obj = resolve_teacher(teacher)
        classroom_obj = resolve_classroom(classroom)
        school_obj = School.objects.filter(id=school).first()   
        if not teacher_obj or not classroom_obj or not school_obj:
            return Response(
                {"error": "Invalid Teacher, Classroom, or School"},
                status=status.HTTP_404_NOT_FOUND
            )   
        assignment, created = TeacherClassAssignment.objects.get_or_create(
            teacher=teacher_obj,
            classroom=classroom_obj
        )
        return Response({
            "teacher": teacher_obj.name,
            "classroom": classroom_obj.name,
            "school": school_obj.name,
            "assigned_at": assignment.assigned_at,
            "created": created                  
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class TeacherClassAssignmentAPIView(APIView):

    def get(self, request):
        assignments = TeacherClassAssignment.objects.all()
        serializer = TeacherClassAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeacherClassAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Teacher assigned successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherSchoolAssignmentView(APIView):
    """Assign schools to teachers with salary"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        """Assign a teacher to a school with salary
        
        Request body:
        {
            "teacher": "teacher_uuid_or_name",
            "school": "school_uuid_or_name",
            "monthly_salary": 50000
        }
        """
        teacher_input = request.data.get('teacher')
        school_input = request.data.get('school')
        monthly_salary = request.data.get('monthly_salary')
        
        if not all([teacher_input, school_input, monthly_salary]):
            return Response(
                {"error": "teacher, school, and monthly_salary are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find teacher by UUID or name
        teacher = resolve_teacher(teacher_input)
        if not teacher:
            return Response(
                {"error": f"Teacher '{teacher_input}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find school by UUID or name
        try:
            school = School.objects.get(id=school_input)
        except (School.DoesNotExist, ValueError):
            try:
                school = School.objects.get(id=uuid.UUID(str(school_input)))
            except (ValueError, School.DoesNotExist):
                try:
                    school = School.objects.get(name=school_input)
                except School.DoesNotExist:
                    return Response(
                        {"error": f"School '{school_input}' not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        # Create or update TeacherSalary (which represents the assignment)
        salary, created = TeacherSalary.objects.get_or_create(
            teacher=teacher,
            school=school,
            defaults={'monthly_salary': monthly_salary}
        )
        
        if not created:
            salary.monthly_salary = monthly_salary
            salary.save()
        
        return Response({
            'id': str(salary.id),
            'teacher_id': str(teacher.user.id),
            'teacher_name': teacher.name,
            'school_id': str(school.id),
            'school_name': school.name,
            'monthly_salary': float(monthly_salary),
            'message': 'School assigned to teacher successfully' if created else 'School assignment updated',
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class TeacherCompensationRuleView(APIView):
    """Admin APIs to manage flexible compensation rules"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        """Create or update a compensation rule for a teacher at a school"""
        teacher_input = request.data.get('teacher')
        school_input = request.data.get('school')
        payment_type = request.data.get('payment_type', PaymentType.FIXED_MONTHLY)
        base_rate = request.data.get('base_rate')
        commission = request.data.get('commission_percentage', 0.0)
        
        if not all([teacher_input, school_input, base_rate]):
            return Response(
                {"error": "teacher, school, and base_rate are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        teacher = resolve_teacher(teacher_input)
        if not teacher:
            return Response({"error": f"Teacher '{teacher_input}' not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            school = School.objects.get(id=school_input)
        except (School.DoesNotExist, ValueError):
            try:
                school = School.objects.get(id=uuid.UUID(str(school_input)))
            except (ValueError, School.DoesNotExist):
                try:
                    school = School.objects.get(name=school_input)
                except School.DoesNotExist:
                    return Response({"error": f"School '{school_input}' not found"}, status=status.HTTP_404_NOT_FOUND)
        
        rule, created = TeacherCompensationRule.objects.update_or_create(
            teacher=teacher,
            school=school,
            defaults={
                'payment_type': payment_type,
                'base_rate': base_rate,
                'commission_percentage': commission,
                'is_active': request.data.get('is_active', True)
            }
        )
        
        serializer = TeacherCompensationRuleSerializer(rule)
        return Response({
            'message': 'Compensation rule created' if created else 'Compensation rule updated',
            'rule': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get(self, request):
        """Get compensation rules"""
        teacher_id = request.query_params.get('teacher_id')
        school_id = request.query_params.get('school_id')
        
        rules = TeacherCompensationRule.objects.all()
        
        if teacher_id:
            rules = rules.filter(Q(teacher_id=teacher_id) | Q(teacher__user__id=teacher_id))
        if school_id:
            rules = rules.filter(school_id=school_id)
            
        serializer = TeacherCompensationRuleSerializer(rules, many=True)
        return Response({
            'total': len(serializer.data),
            'rules': serializer.data
        })

class GenerateSalarySlipsView(APIView):
    """Auto-calculate and generate draft salary slips for a given month and year"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        month = request.data.get('month')
        year = request.data.get('year')
        school_id = request.data.get('school')
        
        if not month or not year:
            return Response({"error": "month and year are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            month = int(month)
            year = int(year)
            if not (1 <= month <= 12):
                raise ValueError("Invalid month")
        except ValueError:
             return Response({"error": "Invalid month or year format"}, status=status.HTTP_400_BAD_REQUEST)
             
        # Filter rules
        rules = TeacherCompensationRule.objects.filter(is_active=True)
        if school_id:
            try:
                school = School.objects.get(id=school_id)
                rules = rules.filter(school=school)
            except (School.DoesNotExist, ValueError):
                pass # If it fails, we ignore school filter or return error? We'll ignore and continue with all if school_id isn't valid uuid, or maybe filter. Let's just filter.
                rules = rules.filter(school_id=school_id)
                
        generated_slips = []
        for rule in rules:
            # Check if locked slip exists
            existing_slip = TeacherSalarySlip.objects.filter(
                teacher=rule.teacher, school=rule.school, month=month, year=year
            ).first()
            
            if existing_slip and existing_slip.status != SalarySlipStatus.DRAFT:
                continue # Skip locked or paid slips
            
            # Start calculation
            total_hours = 0
            total_classes = 0
            base_salary = 0
            
            from django.db.models.functions import ExtractMonth, ExtractYear
            
            from decimal import Decimal
            
            # 1. FIXED_MONTHLY
            if rule.payment_type == PaymentType.FIXED_MONTHLY:
                base_salary = Decimal(rule.base_rate)
                
            # 2. HOURLY
            elif rule.payment_type == PaymentType.HOURLY:
                # Find approved attendances for the month
                attendances = TeacherAttendance.objects.filter(
                    teacher=rule.teacher,
                    school=rule.school,
                    status='approved',
                    check_in__month=month,
                    check_in__year=year,
                    total_hours__isnull=False
                )
                from django.db.models import Sum
                total_hours = attendances.aggregate(Sum('total_hours'))['total_hours__sum'] or 0
                base_salary = Decimal(total_hours) * Decimal(rule.base_rate)
                
            # 3. PER_CLASS
            elif rule.payment_type == PaymentType.PER_CLASS:
                # Count approved attendances where teacher checked in
                attendances = TeacherAttendance.objects.filter(
                    teacher=rule.teacher,
                    school=rule.school,
                    status='approved',
                    check_in__month=month,
                    check_in__year=year
                )
                total_classes = attendances.count()
                base_salary = Decimal(total_classes) * Decimal(rule.base_rate)
                
            # Commission
            commission = (Decimal(base_salary) * Decimal(rule.commission_percentage)) / Decimal('100.0')
            
            # Preserve existing adjustments if replacing a draft
            adjustments = Decimal(existing_slip.adjustments) if existing_slip else Decimal('0.0')
            
            net_salary = Decimal(base_salary) + Decimal(commission) + Decimal(adjustments)
            
            slip, created = TeacherSalarySlip.objects.update_or_create(
                teacher=rule.teacher,
                school=rule.school,
                month=month,
                year=year,
                defaults={
                    'total_hours': total_hours,
                    'total_classes': total_classes,
                    'base_salary': base_salary,
                    'commission': commission,
                    'adjustments': adjustments,
                    'net_salary': net_salary,
                    'status': SalarySlipStatus.DRAFT,
                }
            )
            generated_slips.append(slip)
            
        serializer = TeacherSalarySlipSerializer(generated_slips, many=True)
        return Response({
            "message": f"Successfully generated/updated {len(generated_slips)} draft salary slips.",
            "slips": serializer.data
        }, status=status.HTTP_200_OK)


class SalarySlipManagementView(APIView):
    """Manage specific salary slips (lock, adjust, export)"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        teacher_id = request.query_params.get('teacher_id')
        school_id = request.query_params.get('school_id')
        status_filter = request.query_params.get('status')
        
        slips = TeacherSalarySlip.objects.all().select_related('teacher', 'school')
        
        if month: slips = slips.filter(month=month)
        if year: slips = slips.filter(year=year)
        if teacher_id: slips = slips.filter(Q(teacher_id=teacher_id) | Q(teacher__user__id=teacher_id))
        if school_id: slips = slips.filter(school_id=school_id)
        if status_filter: slips = slips.filter(status=status_filter)
        
        serializer = TeacherSalarySlipSerializer(slips, many=True)
        return Response({
            "total": len(serializer.data),
            "slips": serializer.data
        })
        
    def put(self, request, slip_id):
        """Update a specific salary slip (Lock, Adjust)"""
        try:
            slip = TeacherSalarySlip.objects.get(id=slip_id)
        except TeacherSalarySlip.DoesNotExist:
            return Response({"error": "Salary slip not found"}, status=status.HTTP_404_NOT_FOUND)
            
        action = request.data.get('action') # 'lock', 'adjust', 'pay'
        
        if action == 'lock':
            slip.status = SalarySlipStatus.LOCKED
            slip.save()
            return Response({"message": "Salary slip locked successfully", "slip": TeacherSalarySlipSerializer(slip).data})
            
        elif action == 'pay':
            slip.status = SalarySlipStatus.PAID
            slip.save()
            return Response({"message": "Salary slip marked as paid", "slip": TeacherSalarySlipSerializer(slip).data})
            
        elif action == 'adjust':
            if slip.status != SalarySlipStatus.DRAFT:
                return Response({"error": "Can only adjust DRAFT salary slips."}, status=status.HTTP_400_BAD_REQUEST)
                
            from decimal import Decimal
            adjustments = Decimal(request.data.get('adjustments', '0'))
            notes = request.data.get('notes', '')
            new_status = request.data.get('status')
            
            slip.adjustments = adjustments
            slip.override_notes = notes
            slip.net_salary = Decimal(slip.base_salary) + Decimal(slip.commission) + adjustments
            slip.admin_override = True
            
            if new_status in [choice[0] for choice in SalarySlipStatus.choices]:
                slip.status = new_status
                
            slip.save()
            return Response({"message": "Salary slip adjusted", "slip": TeacherSalarySlipSerializer(slip).data})
            
        return Response({"error": "Invalid action. Use 'lock', 'pay', or 'adjust'."}, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        """Get teacher school assignments
        
        Query params:
        - teacher_id: Filter by teacher UUID
        - school_id: Filter by school UUID
        """
        teacher_id = request.query_params.get('teacher_id')
        school_id = request.query_params.get('school_id')
        
        assignments = TeacherSalary.objects.all()
        
        if teacher_id:
            assignments = assignments.filter(Q(teacher_id=teacher_id) | Q(teacher__user__id=teacher_id))
        if school_id:
            assignments = assignments.filter(school_id=school_id)
        
        data = []
        for assignment in assignments:
            data.append({
                'id': str(assignment.id),
                'teacher_id': str(assignment.teacher.user.id),
                'teacher_name': assignment.teacher.name,
                'school_id': str(assignment.school.id),
                'school_name': assignment.school.name,
                'monthly_salary': float(assignment.monthly_salary),
                'created_at': assignment.created_at.isoformat(),
                'updated_at': assignment.updated_at.isoformat(),
            })
        
        return Response({
            'total': len(data),
            'assignments': data
        })
    
    def delete(self, request):
        """Remove teacher from a school
        
        Request body:
        {
            "teacher": "teacher_uuid_or_name",
            "school": "school_uuid_or_name"
        }
        """
        teacher_input = request.data.get('teacher')
        school_input = request.data.get('school')
        
        if not all([teacher_input, school_input]):
            return Response(
                {"error": "teacher and school are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find teacher
            teacher = resolve_teacher(teacher_input)
            if not teacher:
                return Response({"error": f"Teacher '{teacher_input}' not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Find school
            try:
                school = School.objects.get(id=school_input)
            except (School.DoesNotExist, ValueError):
                try:
                    school = School.objects.get(id=uuid.UUID(str(school_input)))
                except (ValueError, School.DoesNotExist):
                    school = School.objects.get(name=school_input)
            
            # Delete assignment
            TeacherSalary.objects.filter(teacher=teacher, school=school).delete()
            
            return Response({
                'message': f"Teacher '{teacher.name}' removed from school '{school.name}'"
            }, status=status.HTTP_200_OK)
        
        except (Teacher.DoesNotExist, School.DoesNotExist) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
# class AssignCoordinatorToSchoolView(APIView):
#     authentication_classes = [CustomJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsAdmin]

#     def post(self, request):
#         return self.assign(request)

#     def put(self, request):
#         return self.assign(request)

#     def assign(self, request):
#         auth_user_id = request.data.get("auth_user_id")  # UUID string from Auth service
#         school_id = request.data.get("school_id")        # UUID

#         if not auth_user_id or not school_id:
#             return Response({"detail": "auth_user_id and school_id are required"}, status=400)

#         try:
#             school = School.objects.get(id=school_id)
#         except School.DoesNotExist:
#             return Response({"detail": "School not found"}, status=404)

#         try:
#             # ✅ Lookup by auth_user_id, NOT id
#             coordinator = Coordinator.objects.get(auth_user_id=str(auth_user_id))
#         except Coordinator.DoesNotExist:
#             return Response({"detail": "Coordinator not found"}, status=404)

#         coordinator.school = school
#         coordinator.save()

#         return Response(
#             {
#                 "message": "Coordinator assigned successfully",
#                 "coordinator_name": coordinator.name,
#                 "school_name": school.name
#             },
#             status=200
#         )