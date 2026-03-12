from django.utils import timezone
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from kms.serializers import (
    MarkAttendanceSerializer, StudentAttendanceSerializer, 
    TeacherAttendanceSerializer, TeacherKYCUploadSerializer, 
    TeacherSalarySlipSerializer
)

from kms.authentication import CustomJWTAuthentication
from kms.permissions import IsAdmin, IsTeacherUser

class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomJWTAuthentication]
    serializer_class = TeacherAttendanceSerializer
    permission_classes = [IsAuthenticated,IsTeacherUser]

    def get_queryset(self):
        from kms.models import Teacher, TeacherAttendance
        teacher = Teacher.objects.get(user=self.request.user)
        return TeacherAttendance.objects.filter(teacher=teacher)

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        from kms.models import Teacher, TeacherAttendance
        teacher = Teacher.objects.get(user=request.user)

        att = TeacherAttendance.objects.create(
            teacher=teacher,
            school_id=request.data['school'],
            check_in=timezone.now()
        )

        serializer = self.get_serializer(att)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        from kms.models import TeacherAttendance
        att = self.get_object()
        att.check_out = timezone.now()
        att.save()

        serializer = self.get_serializer(att)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TeacherProfileView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from kms.models import (
            Teacher, TeacherSalarySlip, SalarySlipStatus, 
            School, TeacherClassAssignment, TeacherCompensationRule
        )
        user = request.user
        teacher = Teacher.objects.filter(user=user).first()
        if not teacher:
            return Response({"detail": "Teacher profile not found"}, status=404)
        
        slips = TeacherSalarySlip.objects.filter(teacher=teacher)
        valid_slips = slips.filter(status__in=[SalarySlipStatus.LOCKED, SalarySlipStatus.PAID])
        
        total_earnings = valid_slips.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        total_paid = slips.filter(status=SalarySlipStatus.PAID).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        total_pending = valid_slips.filter(status=SalarySlipStatus.LOCKED).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        total_commission = valid_slips.aggregate(Sum('commission'))['commission__sum'] or 0
        projected_earnings = slips.filter(status=SalarySlipStatus.DRAFT).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        
        salary_breakdown = []
        
        school_ids = set()
        school_ids.update(teacher.schools.values_list('id', flat=True))
        school_ids.update(TeacherClassAssignment.objects.filter(teacher=teacher).values_list('school_id', flat=True))
        school_ids.update(TeacherCompensationRule.objects.filter(teacher=teacher).values_list('school_id', flat=True))
        school_ids.update(slips.values_list('school_id', flat=True))
        
        assigned_schools = School.objects.filter(id__in=school_ids)
        
        for school in assigned_schools:
            school_slips = valid_slips.filter(school=school)
            school_total = school_slips.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
            school_commission = school_slips.aggregate(Sum('commission'))['commission__sum'] or 0
            school_projected = slips.filter(school=school, status=SalarySlipStatus.DRAFT).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
            
            # Count distinct classes taught in this school from TeacherClassAssignment
            classes_count = TeacherClassAssignment.objects.filter(teacher=teacher, school=school).count()
            
            salary_breakdown.append({
                'school_id': str(school.id),
                'school_name': school.name,
                'total_earnings': float(school_total),
                'total_commission': float(school_commission),
                'projected_earnings': float(school_projected),
                'classes_count': classes_count,
            })

        return Response({
            "id": str(teacher.user.id),
            "name": teacher.name,
            "email": teacher.email,
            "phone_number": teacher.phone_number,
            "earnings": {
                "total_earnings": float(total_earnings),
                "total_paid": float(total_paid),
                "total_pending": float(total_pending),
                "total_commission": float(total_commission),
                "projected_earnings": float(projected_earnings),
                "schools": salary_breakdown
            }
        })


class TeacherClassAssignmentView(APIView):
    """
    Allows teachers to assign themselves to classrooms.
    A teacher can only assign themselves to classrooms in schools they are already assigned to by an admin.
    """
    authentication_classes = [CustomJWTAuthentication]
    # Use OR logic: Both Teachers and Admins can access
    permission_classes = [IsAuthenticated, (IsTeacherUser | IsAdmin)]

    def post(self, request):
        from kms.models import Teacher, ClassRoom, TeacherClassAssignment
        teacher = Teacher.objects.filter(user=request.user).first()
        if not teacher:
            return Response({"detail": "Teacher profile not found"}, status=404)

        classroom_id = request.data.get('classroom_id')
        if not classroom_id:
            return Response({"error": "classroom_id is required"}, status=400)

        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
        except (ClassRoom.DoesNotExist, ValueError):
            return Response({"error": "Classroom not found"}, status=404)

        # 🔹 Security Check: Is the teacher assigned to this school?
        if not teacher.schools.filter(id=classroom.school_id).exists():
            return Response(
                {"error": "You can only assign yourself to classes in schools you are assigned to by an admin."},
                status=403
            )

        # 🔹 Create or get assignment
        from kms.models import TeacherClassAssignment
        assignment, created = TeacherClassAssignment.objects.get_or_create(
            teacher=teacher,
            classroom=classroom,
            school=classroom.school
        )

        return Response({
            "message": "Assigned to class successfully" if created else "Algorithm already assigned to this class",
            "classroom": classroom.name,
            "school": classroom.school.name,
            "assigned_at": assignment.assigned_at
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        """Remove self from a classroom"""
        from kms.models import Teacher, TeacherClassAssignment
        teacher = Teacher.objects.filter(user=request.user).first()
        classroom_id = request.data.get('classroom_id')
        TeacherClassAssignment.objects.filter(teacher=teacher, classroom_id=classroom_id).delete()
        return Response({"message": "Successfully unassigned from class"}, status=status.HTTP_204_NO_CONTENT)


class TeacherKYCView(APIView):
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsAuthenticated,IsTeacherUser]

    def post(self, request):
        serializer = TeacherKYCUploadSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "KYC submitted successfully", "status": "pending"},
                status=201
            )

        return Response(serializer.errors, status=400)
    
class StudentAttendanceListView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from kms.models import Student, StudentAttendance
        teacher = request.user.teacher  # Assuming teacher profile exists
        school_id = request.query_params.get("school_id")
        class_id = request.query_params.get("class_id")

        if not teacher.schools.filter(id=school_id).exists():
            return Response({"error": "You are not allowed to access this school"}, status=403)

        students = Student.objects.filter(school_id=school_id, class_id=class_id)
        attendance_data = StudentAttendance.objects.filter(
            student__in=students,
            date=timezone.now().date()
        )
        serializer = StudentAttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)


class MarkStudentAttendanceView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from kms.models import StudentAttendance
        teacher = request.user.teacher
        serializer = MarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        classroom = data.get('classroom')
        student = data.get('student')
        if not classroom or not student:
            return Response({"error": "Invalid classroom or student"}, status=400)

        # Check teacher has access to the school's classroom
        if not teacher.schools.filter(id=classroom.school_id).exists():
            return Response({"error": "You cannot manage this school"}, status=403)

        student_attendance, created = StudentAttendance.objects.update_or_create(
            student=student,
            classroom=classroom,
            date=data.get('date'),
            defaults={
                "status": data.get('status'),
                "marked_by": teacher,
                "marked_at": timezone.now(),
                "notes": data.get('notes', '')
            }
        )
        return Response({"success": True, "attendance_id": student_attendance.id})

class MonthlyAttendanceReportView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from kms.models import Student, StudentAttendance
        teacher = request.user.teacher
        school_id = request.query_params.get("school_id")
        class_id = request.query_params.get("class_id")
        month = int(request.query_params.get("month", timezone.now().month))
        year = int(request.query_params.get("year", timezone.now().year))

        if not teacher.schools.filter(id=school_id).exists():
            return Response({"error": "You cannot access this school"}, status=403)

        students = Student.objects.filter(school_id=school_id, class_id=class_id)
        attendance = StudentAttendance.objects.filter(
            student__in=students,
            date__month=month,
            date__year=year
        )

        serializer = StudentAttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

class TeacherSalarySlipView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def get(self, request):
        from kms.models import TeacherSalarySlip
        teacher = getattr(request.user, "teacher", None)
        if not teacher:
            return Response({"error": "Teacher profile not found"}, status=403)

        queryset = TeacherSalarySlip.objects.filter(teacher=teacher)

        # Optional filters
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        school_id = request.query_params.get('school_id')

        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        serializer = TeacherSalarySlipSerializer(queryset, many=True)
        return Response(serializer.data)
    