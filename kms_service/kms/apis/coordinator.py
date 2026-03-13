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
     Coordinator, Teacher, TeacherAttendance, TeacherSalary
)


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
            teacher__in=teachers
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
