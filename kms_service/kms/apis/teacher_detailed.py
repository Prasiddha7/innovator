from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime, timedelta
from django.db.models import Q, Count
from django.utils import timezone

from kms.models import (
    Teacher, TeacherKYC, Student, StudentAttendance, ClassRoom,
    TeacherClassAssignment, TeacherSalary, User, TeacherSalarySlip, SalarySlipStatus
)
from kms.serializers import (
    TeacherDetailedSerializer, TeacherProfileSerializer, TeacherKYCUploadSerializer, 
    TeacherKYCSerializer, ClassRoomSerializer, StudentAttendanceDetailSerializer,
    MarkAttendanceSerializer, BulkMarkAttendanceSerializer, AttendanceReportSerializer,
    TeacherSalarySlipSerializer
)
from kms.authentication import CustomJWTAuthentication


class TeacherProfileView(APIView):
    """Get complete teacher profile with UUID ID, earnings, classes, and salary."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            # Auto-create teacher profile on first access
            try:
                teacher = Teacher.objects.create(
                    user=request.user,
                    name=request.user.username,
                    email=request.user.email
                )
            except Exception:
                return Response(
                    {"detail": "Unable to create teacher profile"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        serializer = TeacherProfileSerializer(teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherKYCUploadView(APIView):
    """Upload or update teacher KYC documents."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TeacherKYCUploadSerializer(
            data=request.data,
            context={"request": request}
        )
        
        if serializer.is_valid():
            kyc = serializer.save()
            return Response(
                {
                    "message": "KYC submitted successfully",
                    "kyc": TeacherKYCSerializer(kyc).data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Get current KYC status."""
        try:
            teacher = Teacher.objects.get(user=request.user)
            kyc = TeacherKYC.objects.get(teacher=teacher)
            serializer = TeacherKYCSerializer(kyc)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeacherKYC.DoesNotExist:
            return Response(
                {"detail": "KYC not found. Please submit your KYC first."},
                status=status.HTTP_404_NOT_FOUND
            )


class TeacherClassesView(APIView):
    """View all classes/classrooms assigned to a teacher."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response(
                {"detail": "Teacher profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        assignments = TeacherClassAssignment.objects.filter(
            teacher=teacher
        ).select_related('classroom', 'classroom__school')
        
        classes_data = []
        for assignment in assignments:
            classes_data.append({
                'classroom_id': str(assignment.classroom.id),
                'classroom_name': assignment.classroom.name,
                'school_id': str(assignment.classroom.school.id),
                'school_name': assignment.classroom.school.name,
                'assigned_at': assignment.assigned_at,
                'students_count': Student.objects.filter(school=assignment.classroom.school).count()
            })
        
        return Response({
            'total_classes': len(classes_data),
            'classes': classes_data
        }, status=status.HTTP_200_OK)


class StudentAttendanceListView(APIView):
    """View students and their attendance for a specific classroom."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classroom_id = request.query_params.get('classroom_id')
        date = request.query_params.get('date')
        
        if not classroom_id:
            return Response(
                {"detail": "classroom_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
        except ClassRoom.DoesNotExist:
            return Response(
                {"detail": "Classroom not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify teacher is assigned to this classroom
        try:
            teacher = Teacher.objects.get(user=request.user)
            TeacherClassAssignment.objects.get(teacher=teacher, classroom=classroom)
        except (Teacher.DoesNotExist, TeacherClassAssignment.DoesNotExist):
            return Response(
                {"detail": "You don't have access to this classroom"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all students in the school
        students = Student.objects.filter(school=classroom.school)
        
        attendance_data = []
        query_date = datetime.strptime(date, '%Y-%m-%d').date() if date else timezone.now().date()
        
        for student in students:
            attendance_record = StudentAttendance.objects.filter(
                student=student,
                classroom=classroom,
                date=query_date
            ).first()
            
            attendance_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'attendance_id': attendance_record.id if attendance_record else None,
                'status': attendance_record.status if attendance_record else None,
                'marked_at': attendance_record.marked_at if attendance_record else None,
                'date': query_date
            })
        
        return Response({
            'classroom': classroom.name,
            'date': query_date,
            'total_students': len(attendance_data),
            'students': attendance_data
        }, status=status.HTTP_200_OK)


class MarkAttendanceView(APIView):
    """Mark attendance for a student."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MarkAttendanceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response(
                {"detail": "Teacher profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify teacher is assigned to this classroom
        classroom = serializer.validated_data['classroom']
        try:
            TeacherClassAssignment.objects.get(teacher=teacher, classroom=classroom)
        except TeacherClassAssignment.DoesNotExist:
            return Response(
                {"detail": "You don't have access to this classroom"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = serializer.validated_data['student']
        
        # Create or update attendance record
        attendance, created = StudentAttendance.objects.update_or_create(
            student=student,
            classroom=classroom,
            date=serializer.validated_data['date'],
            defaults={
                'status': serializer.validated_data['status'],
                'marked_by': teacher,
                'notes': serializer.validated_data.get('notes', '')
            }
        )
        
        return Response({
            'message': 'Attendance marked successfully',
            'attendance': StudentAttendanceDetailSerializer(attendance).data
        }, status=status.HTTP_201_CREATED)


class BulkMarkAttendanceView(APIView):
    """Mark attendance for multiple students at once."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BulkMarkAttendanceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response(
                {"detail": "Teacher profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        classroom_id = serializer.validated_data['classroom_id']
        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
        except ClassRoom.DoesNotExist:
            return Response(
                {"detail": "Classroom not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify teacher is assigned to this classroom
        try:
            TeacherClassAssignment.objects.get(teacher=teacher, classroom=classroom)
        except TeacherClassAssignment.DoesNotExist:
            return Response(
                {"detail": "You don't have access to this classroom"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        attendance_records = []
        date = serializer.validated_data['date']
        
        for attendance_data in serializer.validated_data['attendances']:
            student = attendance_data['student']
            
            attendance, created = StudentAttendance.objects.update_or_create(
                student=student,
                classroom=classroom,
                date=date,
                defaults={
                    'status': attendance_data['status'],
                    'marked_by': teacher,
                    'notes': attendance_data.get('notes', '')
                }
            )
            attendance_records.append(StudentAttendanceDetailSerializer(attendance).data)
        
        return Response({
            'message': f'Attendance marked for {len(attendance_records)} students',
            'count': len(attendance_records),
            'date': date,
            'attendances': attendance_records
        }, status=status.HTTP_201_CREATED)


class AttendanceReportView(APIView):
    """Get attendance report for a classroom."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classroom_id = request.query_params.get('classroom_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not classroom_id:
            return Response(
                {"detail": "classroom_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
        except ClassRoom.DoesNotExist:
            return Response(
                {"detail": "Classroom not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify teacher is assigned to this classroom
        try:
            teacher = Teacher.objects.get(user=request.user)
            TeacherClassAssignment.objects.get(teacher=teacher, classroom=classroom)
        except (Teacher.DoesNotExist, TeacherClassAssignment.DoesNotExist):
            return Response(
                {"detail": "You don't have access to this classroom"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Date range filtering
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        # Get attendance records
        attendance_records = StudentAttendance.objects.filter(
            classroom=classroom,
            date__range=[start_date, end_date]
        )
        
        # Calculate stats
        total_records = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        late_count = attendance_records.filter(status='late').count()
        leave_count = attendance_records.filter(
            status__in=['sick_leave', 'casual_leave']
        ).count()
        
        attendance_percentage = (
            (present_count / total_records * 100) if total_records > 0 else 0
        )
        
        return Response({
            'classroom': classroom.name,
            'start_date': start_date,
            'end_date': end_date,
            'total_records': total_records,
            'present': present_count,
            'absent': absent_count,
            'late': late_count,
            'leave': leave_count,
            'attendance_percentage': round(attendance_percentage, 2),
            'daily_breakdown': self._get_daily_breakdown(classroom, start_date, end_date)
        }, status=status.HTTP_200_OK)
    
    def _get_daily_breakdown(self, classroom, start_date, end_date):
        """Get day-wise attendance breakdown."""
        daily_data = {}
        current_date = start_date
        
        while current_date <= end_date:
            daily_attendance = StudentAttendance.objects.filter(
                classroom=classroom,
                date=current_date
            )
            
            total = daily_attendance.count()
            present = daily_attendance.filter(status='present').count()
            percentage = (present / total * 100) if total > 0 else 0
            
            daily_data[str(current_date)] = {
                'total': total,
                'present': present,
                'percentage': round(percentage, 2)
            }
            
            current_date += timedelta(days=1)
        
        return daily_data


class TeacherEarningsView(APIView):
    """View teacher earnings based on generated salary slips."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        slips = TeacherSalarySlip.objects.filter(teacher=teacher)
        
        # Calculate totals from locked and paid slips
        valid_slips = slips.filter(status__in=[SalarySlipStatus.LOCKED, SalarySlipStatus.PAID])
        
        from django.db.models import Sum
        total_earnings = valid_slips.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        total_paid = slips.filter(status=SalarySlipStatus.PAID).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        total_pending = valid_slips.filter(status=SalarySlipStatus.LOCKED).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        
        # Breakdown by school
        schools = set([slip.school for slip in valid_slips])
        salary_breakdown = []
        for school in schools:
            school_slips = valid_slips.filter(school=school)
            school_total = school_slips.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
            salary_breakdown.append({
                'school_id': str(school.id),
                'school_name': school.name,
                'total_earnings': float(school_total),
                'slips_count': school_slips.count()
            })
            
        return Response({
            'teacher_name': teacher.name,
            'total_earnings': float(total_earnings),
            'total_paid': float(total_paid),
            'total_pending': float(total_pending),
            'total_schools': len(schools),
            'total_classes': teacher.get_classes_count(),
            'salary_breakdown': salary_breakdown,
        }, status=status.HTTP_200_OK)


class TeacherSalarySlipsView(APIView):
    """View individual monthly salary slips."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        school_id = request.query_params.get('school_id')
        
        slips = TeacherSalarySlip.objects.filter(teacher=teacher).order_by('-year', '-month')
        
        if month: slips = slips.filter(month=month)
        if year: slips = slips.filter(year=year)
        if school_id: slips = slips.filter(school_id=school_id)
        
        serializer = TeacherSalarySlipSerializer(slips, many=True)
        return Response({
            'total': len(serializer.data),
            'slips': serializer.data
        }, status=status.HTTP_200_OK)

