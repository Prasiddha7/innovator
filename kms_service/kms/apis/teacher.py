from django.utils import timezone
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from kms.models import Student, StudentAttendance, Teacher, TeacherAttendance, TeacherKYC
from kms.serializers import MarkAttendanceSerializer, StudentAttendanceSerializer, TeacherAttendanceSerializer, TeacherKYCUploadSerializer
from rest_framework.permissions import IsAuthenticated

from kms.authentication import CustomJWTAuthentication
from kms.permissions import IsTeacherUser

class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomJWTAuthentication]
    serializer_class = TeacherAttendanceSerializer
    permission_classes = [IsAuthenticated,IsTeacherUser]

    def get_queryset(self):
        teacher = Teacher.objects.get(user=self.request.user)
        return TeacherAttendance.objects.filter(teacher=teacher)

    @action(detail=False, methods=['post'])
    def check_in(self, request):
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
        att = self.get_object()
        att.check_out = timezone.now()
        att.save()

        serializer = self.get_serializer(att)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TeacherProfileView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        teacher = Teacher.objects.filter(user=user).first()
        if not teacher:
            return Response({"detail": "Teacher profile not found"}, status=404)
        return Response({
            "id": str(teacher.user.id),
            "name": teacher.name,
            "email": teacher.email,
            "phone_number": teacher.phone_number,
        })


class TeacherKYCView(APIView):
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsAuthenticated]

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
    