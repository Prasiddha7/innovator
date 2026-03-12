import csv
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from kms.models import School, ClassRoom, Student, StudentAttendance, Teacher
from kms.permissions import IsTeacherUser
from rest_framework.permissions import IsAuthenticated
from kms.serializers import StudentAttendanceSerializer, StudentSerializer

class StudentCSVUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "File is required"}, status=400)

        if not file.name.endswith(".csv"):
            return Response({"error": "Only .csv files are supported"}, status=400)

        teacher = getattr(request.user, "teacher", None)
        if not teacher:
            return Response({"error": "Teacher profile not found"}, status=400)

        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
        except Exception as e:
            return Response({"error": f"Invalid CSV file: {str(e)}"}, status=400)

        created_count = 0
        errors = []

        with transaction.atomic():
            for row_number, row in enumerate(reader, start=2):
                try:
                    name = row.get("student_name") or row.get("Student Name")
                    classroom_name = row.get("class") or row.get("Class Name")
                    school_name = row.get("school") or row.get("School Name")
                    student_id_val = row.get("student_id") or row.get("Student ID")

                    if not name or not classroom_name or not school_name:
                        errors.append(f"Row {row_number}: Missing required data (name, class, or school)")
                        continue

                    school = School.objects.filter(name__iexact=school_name).first()
                    if not school:
                        errors.append(f"Row {row_number}: School '{school_name}' not found")
                        continue

                    classroom = ClassRoom.objects.filter(name__iexact=classroom_name, school=school).first()
                    if not classroom:
                        errors.append(f"Row {row_number}: Classroom '{classroom_name}' for school '{school_name}' not found")
                        continue

                    student_data = {
                        "name": name,
                        "school": school,
                        "classroom": classroom,
                    }

                    # If student_id is a valid UUID, use it as 'id'
                    if student_id_val:
                        try:
                            student_data["id"] = student_id_val
                        except Exception:
                            pass # Let it be auto-generated if it's not a valid UUID

                    Student.objects.create(**student_data)
                    created_count += 1

                except Exception as e:
                    errors.append(f"Row {row_number}: {str(e)}")
        return Response({
            "created": created_count,
            "errors": errors
        }, status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_400_BAD_REQUEST)

class AttendanceListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def get(self, request):
        queryset = StudentAttendance.objects.all()
        
        # Date filters
        date = request.query_params.get('date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if date:
            queryset = queryset.filter(date=date)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Teacher filter (who approved/marked)
        teacher_id = request.query_params.get('teacher_id')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
            
        # Approved by teacher filter
        approved_by = request.query_params.get('approved_by')
        if approved_by:
            queryset = queryset.filter(approved_by=approved_by)

        # Status filter
        status_val = request.query_params.get('status')
        if status_val:
            queryset = queryset.filter(status=status_val)

        serializer = StudentAttendanceSerializer(queryset, many=True)
        return Response(serializer.data)

class AttendanceMarkAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def post(self, request):
        teacher = getattr(request.user, "teacher", None)
        if not teacher:
            return Response({"error": "Teacher profile not found"}, status=403)

        student_id = request.data.get("student_id")
        classroom_id = request.data.get("classroom_id")
        date = request.data.get("date", timezone.now().date())
        status_val = request.data.get("status", "present")
        notes = request.data.get("notes", "")

        try:
            student = Student.objects.get(id=student_id)
            classroom = ClassRoom.objects.get(id=classroom_id)
        except (Student.DoesNotExist, ClassRoom.DoesNotExist):
            return Response({"error": "Student or Classroom not found"}, status=404)

        attendance, created = StudentAttendance.objects.update_or_create(
            student=student,
            classroom=classroom,
            date=date,
            defaults={
                "status": status_val,
                "teacher": teacher,
                "marked_by": teacher,
                "marked_at": timezone.now(),
                "notes": notes
            }
        )

        return Response(StudentAttendanceSerializer(attendance).data, status=201 if created else 200)

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
        # Allow passing 'id' explicitly if needed, but otherwise auto-generate
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data, status=201)

        return Response(serializer.errors, status=400)