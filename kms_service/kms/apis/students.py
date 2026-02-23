from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import openpyxl
from kms.models import ClassRoom, Student, StudentAttendance
from kms.permissions import IsTeacherUser
from rest_framework.permissions import IsAuthenticated

from kms.serializers import StudentAttendanceSerializer, StudentSerializer

class AttendanceUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "File is required"}, status=400)

        # Validate file type
        if not file.name.endswith(".xlsx"):
            return Response({"error": "Only .xlsx files are supported"}, status=400)

        try:
            workbook = openpyxl.load_workbook(file)
        except Exception:
            return Response({"error": "Invalid Excel file"}, status=400)

        sheet = workbook.active

        teacher = getattr(request.user, "teacher", None)
        if not teacher:
            return Response({"error": "Teacher profile not found"}, status=400)

        created = 0
        errors = []

        today = timezone.now().date()

        for row_number, row in enumerate(
            sheet.iter_rows(min_row=2, values_only=True), start=2
        ):
            try:
                student_name, classroom_name, status_value = row

                # Validate empty cells
                if not student_name or not classroom_name or not status_value:
                    errors.append(f"Row {row_number}: Missing required data")
                    continue

                status_value = str(status_value).strip().upper()

                # Validate status
                if status_value not in ["PRESENT", "ABSENT"]:
                    errors.append(
                        f"Row {row_number}: Invalid status '{status_value}'"
                    )
                    continue

                # Get classroom
                classroom = ClassRoom.objects.filter(
                    name__iexact=classroom_name
                ).first()

                if not classroom:
                    errors.append(
                        f"Row {row_number}: Classroom '{classroom_name}' not found"
                    )
                    continue

                # Get student within that classroom
                student = Student.objects.filter(
                    name__iexact=student_name,
                    classroom=classroom
                ).first()

                if not student:
                    errors.append(
                        f"Row {row_number}: Student '{student_name}' not found in '{classroom_name}'"
                    )
                    continue

                # Create attendance
                attendance, created_flag = StudentAttendance.objects.get_or_create(
                    student=student,
                    classroom=classroom,
                    date=today,
                    defaults={
                        "status": status_value,
                        "teacher": teacher,
                        "marked_by": teacher,
                        "marked_at": timezone.now(),
                    }
                )

                if created_flag:
                    created += 1

            except Exception as e:
                errors.append(f"Row {row_number}: {str(e)}")

        return Response({
            "created": created,
            "errors": errors
        })
    
class AttendanceListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def get(self, request):
        queryset = StudentAttendance.objects.all()
        serializer = StudentAttendanceSerializer(queryset, many=True)
        return Response(serializer.data)
    
class AttendanceApproveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def post(self, request, attendance_id):
        try:
            attendance = StudentAttendance.objects.get(id=attendance_id)

            attendance.approved = "APPROVED"
            attendance.approved_by = str(request.user.id)
            attendance.approved_at = timezone.now()
            attendance.notes = request.data.get("notes")
            attendance.save()

            return Response({"message": "approved"})

        except StudentAttendance.DoesNotExist:
            return Response({"error": "not found"}, status=404)
        
class StudentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def post(self, request):
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data, status=201)

        return Response(serializer.errors, status=400)