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
     Coordinator, Teacher, ClassRoom, TeacherClassAssignment, TeacherCourseAssignment,
    StudentAttendance, TeacherAttendance, School, TeacherSalary
)
from decimal import Decimal


# class CoordinatorAssignmentView(APIView):
#     authentication_classes = [CustomJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsCoordinatorUser]

#     def get_coordinator(self, request):
#         auth_id = request.auth.get('user_id') or request.auth.get('auth_user_id')
#         try:
#             return Coordinator.objects.get(auth_user_id=str(auth_id))
#         except Coordinator.DoesNotExist:
#             return None

#     def post(self, request):
#         """Assign teacher to multiple classrooms/courses within coordinator's school.
        
#         Request body:
#         {
#             "teacher": "teacher_name or uuid",
#             "classrooms": ["Class 1", "Class 2"],  # optional
#             "courses": ["Course 1", "Course 2"]    # optional
#         }
        
#         Returns list of created/existing assignments.
#         """
#         serializer = CoordinatorAssignmentSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         coord = self.get_coordinator(request)
#         if isinstance(coord, dict):
#             return Response({'detail': coord['error']}, status=status.HTTP_403_FORBIDDEN)

#         teacher = serializer.validated_data['teacher']
#         classrooms = serializer.validated_data.get('classrooms', [])
#         courses = serializer.validated_data.get('courses', [])
#         school = coord.school
        
#         results = {
#             "classroom_assignments": [],
#             "course_assignments": []
#         }
        
#         # Validate and create classroom assignments
#         for classroom in classrooms:
#             if classroom.school_id != school.id:
#                 return Response(
#                     {'detail': f'Classroom "{classroom.name}" is outside your school'},
#                     status=status.HTTP_403_FORBIDDEN
#                 )
            
#             assignment, created = TeacherClassAssignment.objects.get_or_create(
#                 teacher=teacher,
#                 classroom=classroom
#             )
#             results["classroom_assignments"].append({
#                 "id": str(assignment.id),
#                 "teacher": assignment.teacher.name,
#                 "classroom": assignment.classroom.name,
#                 "created": created,
#                 "assigned_at": assignment.assigned_at.isoformat()
#             })
        
#         # Validate and create course assignments
#         for course in courses:
#             if course.school_id != school.id:
#                 return Response(
#                     {'detail': f'Course "{course.title}" is outside your school'},
#                     status=status.HTTP_403_FORBIDDEN
#                 )
            
#             assignment, created = TeacherCourseAssignment.objects.get_or_create(
#                 teacher=teacher,
#                 course=course
#             )
#             results["course_assignments"].append({
#                 "id": str(assignment.id),
#                 "teacher": assignment.teacher.name,
#                 "course": assignment.course.title,
#                 "created": created,
#                 "assigned_at": assignment.assigned_at.isoformat()
#             })
        
#         return Response(results, status=status.HTTP_201_CREATED)

#     def get(self, request):
#         coord = self.get_coordinator(request)
#         if not coord:
#             return Response({'detail': 'Coordinator profile not found'}, status=status.HTTP_403_FORBIDDEN)

#         teacher_id = request.query_params.get('teacher_id')
#         classroom_id = request.query_params.get('classroom_id')
#         course_id = request.query_params.get('course_id')

#         data = {'classroom_assignments': [], 'course_assignments': []}

#         classroom_qs = TeacherClassAssignment.objects.filter(classroom__school=coord.school)
#         if teacher_id:
#             classroom_qs = classroom_qs.filter(teacher_id=teacher_id)
#         if classroom_id:
#             classroom_qs = classroom_qs.filter(classroom_id=classroom_id)

#         for a in classroom_qs.select_related('teacher', 'classroom'):
#             data['classroom_assignments'].append({
#                 'id': str(a.id),
#                 'teacher_id': str(a.teacher.id),
#                 'teacher_name': a.teacher.name,
#                 'classroom_id': str(a.classroom.id),
#                 'classroom_name': a.classroom.name,
#                 'assigned_at': a.assigned_at.isoformat()
#             })

#         course_qs = TeacherCourseAssignment.objects.filter(course__school=coord.school)
#         if teacher_id:
#             course_qs = course_qs.filter(teacher_id=teacher_id)
#         if course_id:
#             course_qs = course_qs.filter(course_id=course_id)

#         for a in course_qs.select_related('teacher', 'course'):
#             data['course_assignments'].append({
#                 'id': str(a.id),
#                 'teacher_id': str(a.teacher.id),
#                 'teacher_name': a.teacher.name,
#                 'course_id': str(a.course.id),
#                 'course_title': a.course.title,
#                 'assigned_at': a.assigned_at.isoformat()
#             })

#         return Response(data)

#     def delete(self, request, assignment_id):
#         coord = self.get_coordinator(request)
#         if isinstance(coord, dict):
#             return Response({'detail': coord['error']}, status=status.HTTP_403_FORBIDDEN)

#         # Try classroom assignment
#         try:
#             a = TeacherClassAssignment.objects.get(id=assignment_id)
#             if a.classroom.school_id != coord.school.id:
#                 return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
#             a.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except TeacherClassAssignment.DoesNotExist:
#             pass

#         try:
#             a = TeacherCourseAssignment.objects.get(id=assignment_id)
#             if a.course.school_id != coord.school.id:
#                 return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
#             a.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except TeacherCourseAssignment.DoesNotExist:
#             pass

#         return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)


# class CoordinatorPendingAttendanceView(APIView):
#     authentication_classes = [CustomJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsCoordinatorUser]

#     def get_coordinator(self, request):
#         auth_id = request.auth.get('user_id') or request.auth.get('auth_user_id')
#         try:
#             coord = Coordinator.objects.get(auth_user_id=str(auth_id))
#             if not coord.school:
#                 return {'error': 'Coordinator not yet assigned to a school. Please contact your administrator.', 'code': 'NO_SCHOOL_ASSIGNED'}
#             return coord
#         except Coordinator.DoesNotExist:
#             return {'error': 'Coordinator profile not found. Please contact your administrator.', 'code': 'PROFILE_NOT_FOUND'}

#     def get(self, request):
#         coord = self.get_coordinator(request)
#         if isinstance(coord, dict):
#             return Response({'detail': coord['error']}, status=status.HTTP_403_FORBIDDEN)

#         date = request.query_params.get('date')
#         classroom_id = request.query_params.get('classroom_id')
#         teacher_id = request.query_params.get('teacher_id')

#         qs = StudentAttendance.objects.filter(classroom__school=coord.school, approved= 'PENDING')
#         if date:
#             qs = qs.filter(date=date)
#         if classroom_id:
#             qs = qs.filter(classroom_id=classroom_id)
#         if teacher_id:
#             qs = qs.filter(teacher_id=teacher_id)

#         results = []
#         for r in qs.select_related('student', 'classroom', 'teacher'):
#             results.append({
#                 'id': r.id,
#                 'student_id': r.student.id,
#                 'student_name': r.student.name,
#                 'classroom_id': r.classroom.id,
#                 'classroom_name': r.classroom.name,
#                 'teacher_id': r.teacher.id,
#                 'teacher_name': r.teacher.name,
#                 'date': r.date,
#                 'status': r.status,
#                 'marked_at': r.marked_at,
#                 'notes': r.notes
#             })

#         return Response(results)


# class CoordinatorApproveAttendanceView(APIView):
#     authentication_classes = [CustomJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsCoordinatorUser]

#     def get_coordinator(self, request):
#         auth_id = request.auth.get('user_id') or request.auth.get('auth_user_id')
#         try:
#             coord = Coordinator.objects.get(auth_user_id=str(auth_id))
#             if not coord.school:
#                 return {'error': 'Coordinator not yet assigned to a school. Please contact your administrator.', 'code': 'NO_SCHOOL_ASSIGNED'}
#             return coord
#         except Coordinator.DoesNotExist:
#             return {'error': 'Coordinator profile not found. Please contact your administrator.', 'code': 'PROFILE_NOT_FOUND'}

#     def put(self, request, attendance_id):
#         coord = self.get_coordinator(request)
#         if isinstance(coord, dict):
#             return Response({'detail': coord['error']}, status=status.HTTP_403_FORBIDDEN)

#         try:
#             rec = StudentAttendance.objects.get(id=attendance_id)
#         except StudentAttendance.DoesNotExist:
#             return Response({'detail': 'Attendance not found'}, status=status.HTTP_404_NOT_FOUND)

#         if rec.classroom.school_id != coord.school.id:
#             return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

#         serializer = AttendanceApprovalSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         action = serializer.validated_data['action']
#         notes = serializer.validated_data.get('notes')

#         rec.approved = 'Approve' if action == 'approve' else 'Reject'
#         rec.approved_by = coord.auth_user_id
#         rec.approved_at = timezone.now()
#         if notes:
#             rec.notes = (rec.notes or '') + '\n[Coordinator] ' + notes
#         rec.save()

#         return Response({'id': rec.id, 'approved': rec.approved, 'approved_by': rec.approved_by, 'approved_at': rec.approved_at})


# class CoordinatorBulkApproveAttendanceView(APIView):
#     authentication_classes = [CustomJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsCoordinatorUser]

#     def put(self, request):
#         auth_id = request.auth.get('user_id') or request.auth.get('auth_user_id')
#         coord = Coordinator.objects.filter(auth_user_id=str(auth_id)).first()
#         if not coord or not coord.school:
#             error_msg = 'Coordinator not yet assigned to a school' if coord and not coord.school else 'Coordinator profile not found'
#             return Response({'detail': f'{error_msg}. Please contact your administrator.'}, status=status.HTTP_403_FORBIDDEN)

#         serializer = BulkAttendanceApprovalSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         ids = serializer.validated_data['attendance_ids']
#         action = serializer.validated_data['action']
#         notes = serializer.validated_data.get('notes')

#         updated = []
#         qs = StudentAttendance.objects.filter(id__in=ids, classroom__school=coord.school)
#         for rec in qs:
#             rec.approved = 'Approve' if action == 'approve' else 'Reject'
#             rec.approved_by = coord.auth_user_id
#             rec.approved_at = timezone.now()
#             if notes:
#                 rec.notes = (rec.notes or '') + '\n[Coordinator] ' + notes
#             rec.save()
#             updated.append(rec.id)

#         return Response({'updated_ids': updated, 'action': action})


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

        try:
            attendance = TeacherAttendance.objects.get(id=attendance_id)
        except TeacherAttendance.DoesNotExist:
            return Response({"detail": "Attendance not found"}, status=404)

        if not TeacherSalary.objects.filter(
            teacher=attendance.teacher,
            school=coord.school,
        ).exists():
            return Response({"detail": "Not authorized"}, status=403)

        action = request.data.get("action")

        if action not in ["approve", "reject"]:
            return Response(
                {"detail": 'Action must be "approve" or "reject"'},
                status=400,
            )

        attendance.status = "Approve" if action == "approve" else "Reject"
        attendance.supervised_at = timezone.now()
        attendance.supervised_by = str(coord.user.id)
        attendance.save()

        return Response(
            {
                "id": str(attendance.id),
                "status": attendance.status,
                "message": f"Attendance {action}d successfully",
            }
        )


# class TeacherInvoiceView(APIView):
#     """Generate invoices for classes taught by teachers"""
#     authentication_classes = [CustomJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsCoordinatorUser]

#     def get_coordinator(self, request):
#         auth_id = request.auth.get('user_id') or request.auth.get('auth_user_id')
#         try:
#             coord = Coordinator.objects.get(auth_user_id=str(auth_id))
#             if not coord.school:
#                 return {'error': 'Coordinator not yet assigned to a school. Please contact your administrator.', 'code': 'NO_SCHOOL_ASSIGNED'}
#             return coord
#         except Coordinator.DoesNotExist:
#             return {'error': 'Coordinator profile not found. Please contact your administrator.', 'code': 'PROFILE_NOT_FOUND'}

#     def get(self, request):
#         """Generate teacher invoices for classes/attendance in a period
        
#         Query params:
#         - teacher_id: Specific teacher UUID (optional, shows all if not provided)
#         - start_date: Period start (YYYY-MM-DD)
#         - end_date: Period end (YYYY-MM-DD)
#         """
#         coord = self.get_coordinator(request)
#         if isinstance(coord, dict):
#             return Response({'detail': coord['error']}, status=status.HTTP_403_FORBIDDEN)
        
#         # Get teachers in coordinator's school
#         teachers = Teacher.objects.filter(teachersalary__school=coord.school).distinct()
        
#         teacher_id = request.query_params.get('teacher_id')
#         if teacher_id:
#             teachers = teachers.filter(id=teacher_id)
#             if not teachers.exists():
#                 return Response({'detail': 'Teacher not found in your school'}, status=status.HTTP_404_NOT_FOUND)
        
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
        
#         if not start_date or not end_date:
#             return Response(
#                 {'detail': 'start_date and end_date are required (format: YYYY-MM-DD)'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         try:
#             start = datetime.strptime(start_date, '%Y-%m-%d').date()
#             end = datetime.strptime(end_date, '%Y-%m-%d').date()
#         except ValueError:
#             return Response({'detail': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
#         invoices = []
#         total_all = Decimal('0')
        
#         for teacher in teachers:
#             # Count classes taught (approved attendance)
#             approved_attendances = TeacherAttendance.objects.filter(
#                 teacher=teacher,
#                 status='approved',
#                 date__gte=start,
#                 date__lte=end
#             ).count()
            
#             # Get teacher salary for school
#             salary_obj = TeacherSalary.objects.filter(
#                 teacher=teacher,
#                 school=coord.school
#             ).first()
            
#             monthly_salary = salary_obj.monthly_salary if salary_obj else Decimal('0')
            
#             # Calculate per-class amount (monthly salary / 22 working days)
#             per_class_amount = monthly_salary / Decimal('22') if monthly_salary > 0 else Decimal('0')
#             total_amount = per_class_amount * Decimal(str(approved_attendances))
            
#             invoice = {
#                 'teacher_id': str(teacher.id),
#                 'teacher_name': teacher.name,
#                 'teacher_email': teacher.email,
#                 'school_id': str(coord.school.id),
#                 'school_name': coord.school.name,
#                 'period_start': start.isoformat(),
#                 'period_end': end.isoformat(),
#                 'days_count': (end - start).days + 1,
#                 'classes_attended': approved_attendances,
#                 'monthly_salary': float(monthly_salary),
#                 'per_class_rate': float(per_class_amount),
#                 'total_amount': float(total_amount),
#                 'invoice_date': timezone.now().isoformat(),
#                 'generated_by': 'Coordinator',
#             }
            
#             invoices.append(invoice)
#             total_all += total_amount
        
#         return Response({
#             'period': {
#                 'start': start.isoformat(),
#                 'end': end.isoformat(),
#             },
#             'coordinator': {
#                 'id': str(coord.id),
#                 'school': coord.school.name,
#             },
#             'total_invoices': len(invoices),
#             'total_payable': float(total_all),
#             'invoices': invoices
#         }, status=status.HTTP_200_OK)

#     def post(self, request):
#         """Mark teacher as present for a class
        
#         Request body:
#         {
#             "teacher_id": "teacher_uuid",
#             "classroom_id": "classroom_uuid",
#             "date": "2026-02-20",
#             "notes": "optional notes"
#         }
#         """
#         coord = self.get_coordinator(request)
#         if isinstance(coord, dict):
#             return Response({'detail': coord['error']}, status=status.HTTP_403_FORBIDDEN)
        
#         teacher_id = request.data.get('teacher_id')
#         classroom_id = request.data.get('classroom_id')
#         date_str = request.data.get('date')
#         notes = request.data.get('notes', '')
        
#         if not all([teacher_id, classroom_id, date_str]):
#             return Response(
#                 {'detail': 'teacher_id, classroom_id, and date are required'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Verify teacher is in coordinator's school
#         try:
#             teacher = Teacher.objects.get(id=teacher_id)
#             if not TeacherSalary.objects.filter(teacher=teacher, school=coord.school).exists():
#                 return Response({'detail': 'Teacher not in your school'}, status=status.HTTP_403_FORBIDDEN)
#         except Teacher.DoesNotExist:
#             return Response({'detail': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         # Verify classroom is in coordinator's school
#         try:
#             classroom = ClassRoom.objects.get(id=classroom_id)
#             if classroom.school_id != coord.school.id:
#                 return Response({'detail': 'Classroom not in your school'}, status=status.HTTP_403_FORBIDDEN)
#         except ClassRoom.DoesNotExist:
#             return Response({'detail': 'Classroom not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         # Parse date
#         try:
#             att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#         except ValueError:
#             return Response({'detail': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Create or update attendance
#         attendance, created = TeacherAttendance.objects.get_or_create(
#             teacher=teacher,
#             classroom=classroom,
#             date=att_date,
#             defaults={
#                 'status': 'approved',  # Coordinator marking directly approves
#                 'approved_at': timezone.now(),
#                 'notes': notes or 'Marked present by coordinator'
#             }
#         )
        
#         if not created:
#             attendance.status = 'approved'
#             attendance.approved_at = timezone.now()
#             if notes:
#                 attendance.notes = notes
#             attendance.save()
        
#         return Response({
#             'id': str(attendance.id),
#             'teacher_name': teacher.name,
#             'classroom_name': classroom.name,
#             'date': att_date.isoformat(),
#             'status': attendance.status,
#             'message': 'Teacher marked present' if created else 'Teacher attendance updated',
#             'created': created
#         }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

