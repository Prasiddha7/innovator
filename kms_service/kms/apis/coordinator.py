from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q, Sum
from decimal import Decimal
from datetime import datetime, timedelta

from kms.authentication import CustomJWTAuthentication
from kms.permissions import IsCoordinatorUser
from kms.models import (
     Coordinator, Teacher, TeacherAttendance, TeacherSalary, 
     CoordinatorInvoice, StudentAttendance
)
from kms.serializers import CoordinatorInvoiceSerializer


class TeacherNotesApprovalView(APIView):
    """
    Coordinator approves teaching sessions (grouped student attendance with notes)
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCoordinatorUser]

    def get(self, request):
        try:
            coord = Coordinator.objects.get(user=request.user)
            if not coord.school:
                return Response({"detail": "Coordinator not assigned to a school."}, status=403)
            
            # Group by teacher, classroom, date, and notes to show "Sessions"
            sessions = StudentAttendance.objects.filter(
                classroom__school=coord.school,
                approved="PENDING"
            ).values(
                'teacher__id', 'teacher__name', 
                'classroom__id', 'classroom__name', 
                'date', 'notes'
            ).annotate(
                student_count=Count('id')
            ).order_by('-date')

            return Response({
                "total_sessions": len(sessions),
                "sessions": sessions
            })
        except Coordinator.DoesNotExist:
            return Response({"detail": "Coordinator profile not found."}, status=404)

    def post(self, request):
        try:
            coord = Coordinator.objects.get(user=request.user)
            if not coord.school:
                return Response({"detail": "Coordinator not assigned to a school."}, status=403)
            
            teacher_id = request.data.get("teacher_id")
            classroom_id = request.data.get("classroom_id")
            date = request.data.get("date")
            notes = request.data.get("notes") # Identifying notes
            action = request.data.get("action", "approve")
            
            if not all([teacher_id, classroom_id, date]):
                return Response({"detail": "teacher_id, classroom_id, and date are required."}, status=400)

            status_val = "APPROVED" if action == "approve" else "REJECTED"

            # Bulk update all students in that session
            updated_count = StudentAttendance.objects.filter(
                teacher_id=teacher_id,
                classroom_id=classroom_id,
                classroom__school=coord.school,
                date=date,
                notes=notes,
                approved="PENDING"
            ).update(
                approved=status_val,
                approved_by=str(request.user.id),
                approved_at=timezone.now(),
                notes=f"{notes}\n\n[Coordinator Note]: {request.data.get('coordinator_notes', '')}" if request.data.get('coordinator_notes') else notes
            )

            return Response({
                "message": f"Successfully {action}d {updated_count} student attendance records for this session.",
                "updated_count": updated_count,
                "action": action
            })
        except Coordinator.DoesNotExist:
            return Response({"detail": "Coordinator profile not found."}, status=404)


class TeacherAttendanceSupervisionView(APIView):
    """
    Coordinator supervises and approves teacher attendance
    """

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCoordinatorUser]

    def get_coordinator(self, request):
        try:
            coord = Coordinator.objects.get(
                user=request.user
            )

            if not coord.school:
                return {
                    "error": "Coordinator not assigned to a school.",
                    "code": "NO_SCHOOL_ASSIGNED",
                }

            return coord

        except Coordinator.DoesNotExist:
            return {
                "error": "Coordinator profile not found.",
                "code": "PROFILE_NOT_FOUND",
            }

    def get(self, request):
        coord = self.get_coordinator(request)

        if isinstance(coord, dict):
            return Response({"detail": coord["error"]}, status=403)

        teachers = Teacher.objects.filter(
            teachersalary__school=coord.school
        ).distinct()

        attendances = TeacherAttendance.objects.filter(
            school=coord.school
        )

        # Filters
        teacher_id = request.query_params.get("teacher_id")
        if teacher_id:
            attendances = attendances.filter(Q(teacher_id=teacher_id) | Q(teacher__user__id=teacher_id))

        status_filter = request.query_params.get("status")
        if status_filter:
            attendances = attendances.filter(status=status_filter)
        else:
            attendances = attendances.filter(status="PENDING")

        start_date = request.query_params.get("start_date")
        if start_date:
            attendances = attendances.filter(check_in__gte=start_date)

        end_date = request.query_params.get("end_date")
        if end_date:
            attendances = attendances.filter(check_in__lte=end_date)

        attendances = attendances.select_related(
            "teacher", "school"
        ).order_by("-check_in")

        data = [
            {
                "id": str(att.id),
                "teacher_id": str(att.teacher.user.id),
                "teacher_name": att.teacher.name,
                "date": att.check_in.isoformat() if att.check_in else None,
                "school_id": str(att.school.id) if att.school else None,
                "school_name": att.school.name if att.school else None,
                "status": att.status,
                "approved_at": att.supervised_at.isoformat() if att.supervised_at else None,
            }
            for att in attendances
        ]

        return Response(
            {
                "total": len(data),
                "pending": sum(1 for x in data if x["status"] == "PENDING"),
                "attendances": data,
            }
        )

    def put(self, request, attendance_id):
        coord = self.get_coordinator(request)

        if isinstance(coord, dict):
            return Response({"detail": coord["error"]}, status=403)

        from kms.models import TeacherAttendance, TeacherSalary
        try:
            attendance = TeacherAttendance.objects.get(id=attendance_id)
        except TeacherAttendance.DoesNotExist:
            return Response({"detail": "Attendance not found"}, status=404)

        # Check if coordinator school matches attendance school
        if attendance.school != coord.school:
            return Response({"detail": "Not authorized: School mismatch"}, status=403)

        action = request.data.get("action")

        if action not in ["approve", "reject"]:
            return Response(
                {"detail": 'Action must be "approve" or "reject"'},
                status=400,
            )

        attendance.status = "APPROVED" if action == "approve" else "REJECTED"
        attendance.supervised_at = timezone.now()
        attendance.supervised_by = f"Coordinator: {coord.user.username} ({coord.user.id})"
        attendance.save()

        return Response(
            {
                "id": str(attendance.id),
                "status": attendance.status,
                "message": f"Attendance {action}d successfully",
                "supervised_by": attendance.supervised_by,
                "supervised_at": attendance.supervised_at
            }
        )


class CoordinatorInvoiceListView(APIView):
    """
    Coordinator retrieves invoices sent by Admin for their assigned school.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCoordinatorUser]

    def get(self, request):
        try:
            coord = Coordinator.objects.get(user=request.user)
            if not coord.school:
                return Response({"detail": "Coordinator not assigned to a school."}, status=403)
            
            invoices = CoordinatorInvoice.objects.filter(school_id=coord.school.id).order_by('-created_at')
            serializer = CoordinatorInvoiceSerializer(invoices, many=True)
            return Response(serializer.data)
        except Coordinator.DoesNotExist:
            return Response({"detail": "Coordinator profile not found."}, status=404)


class CoordinatorStudentAttendanceApprovalView(APIView):
    """
    Coordinator approves student attendance marked by teachers.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCoordinatorUser]

    def get(self, request):
        """List PENDING student attendance for coordinator's school"""
        try:
            coord = Coordinator.objects.get(user=request.user)
            if not coord.school:
                return Response({"detail": "Coordinator not assigned to a school."}, status=403)
            
            # Find all student attendance for this school that is PENDING
            attendances = StudentAttendance.objects.filter(
                classroom__school=coord.school,
                approved="PENDING"
            ).select_related('student', 'classroom', 'teacher', 'marked_by').order_by('-date', '-marked_at')

            data = [
                {
                    "id": str(att.id),
                    "student_id": str(att.student.id),
                    "student_name": att.student.name,
                    "classroom_id": str(att.classroom.id),
                    "classroom_name": att.classroom.name,
                    "teacher_id": str(att.teacher.id),
                    "teacher_name": att.teacher.name,
                    "date": att.date.isoformat(),
                    "status": att.status,
                    "marked_by": str(att.marked_by.id) if att.marked_by else None,
                    "marked_at": att.marked_at.isoformat() if att.marked_at else None,
                    "notes": att.notes
                } for att in attendances
            ]
            return Response({"total": len(data), "attendances": data})
        except Coordinator.DoesNotExist:
            return Response({"detail": "Coordinator profile not found."}, status=404)

    def post(self, request):
        try:
            coord = Coordinator.objects.get(user=request.user)
            if not coord.school:
                return Response({"detail": "Coordinator not assigned to a school."}, status=403)
            
            attendance_ids = request.data.get("attendance_ids", [])
            if not attendance_ids:
                return Response({"detail": "No attendance_ids provided"}, status=400)

            action = request.data.get("action", "approve") # Default to approve
            status_val = "APPROVED" if action == "approve" else "REJECTED"

            # Only allow updating attendance within the coordinator's school that is PENDING
            updated_count = StudentAttendance.objects.filter(
                id__in=attendance_ids,
                classroom__school=coord.school,
                approved="PENDING"
            ).update(
                approved=status_val,
                approved_by=str(request.user.id),
                approved_at=timezone.now(),
                notes=request.data.get("notes", "") # Optional notes
            )

            return Response({
                "message": f"Successfully {action}d {updated_count} student attendance records.",
                "updated_count": updated_count,
                "action": action
            })
        except Coordinator.DoesNotExist:
            return Response({"detail": "Coordinator profile not found."}, status=404)
