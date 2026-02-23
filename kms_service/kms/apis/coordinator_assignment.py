import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.db import models

from kms.models import School, User, Coordinator
from kms.permissions import IsAdmin
from kms.authentication import CustomJWTAuthentication

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

def resolve_coordinator(value):
    if is_valid_uuid(value):
        coord = Coordinator.objects.filter(id=value).first()
        if coord: return coord
        coord = Coordinator.objects.filter(user__id=value).first()
        if coord: return coord
    return Coordinator.objects.filter(
        models.Q(name=value) | models.Q(user__username=value) | models.Q(user__email=value)
    ).first()

class CoordinatorSchoolAssignmentView(APIView):
    """Assign schools to coordinators"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        """Assign a coordinator to a school"""
        coordinator_input = request.data.get('coordinator')
        school_input = request.data.get('school')
        
        if not all([coordinator_input, school_input]):
            return Response(
                {"error": "coordinator and school are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        coordinator = resolve_coordinator(coordinator_input)
        if not coordinator:
            return Response(
                {"error": f"Coordinator '{coordinator_input}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Find school
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
        
        old_school = coordinator.school
        coordinator.school = school
        coordinator.save()
        
        return Response({
            'coordinator_id': str(coordinator.user.id),
            'coordinator_name': coordinator.name,
            'school_id': str(school.id),
            'school_name': school.name,
            'previous_school': old_school.name if old_school else None,
            'message': f"Coordinator assigned to school '{school.name}' successfully"
        }, status=status.HTTP_200_OK)

    def get(self, request):
        """Get coordinator school assignments"""
        coordinators = Coordinator.objects.all()
        
        coordinator_id = request.query_params.get('coordinator_id')
        if coordinator_id:
            coordinators = coordinators.filter(models.Q(id=coordinator_id) | models.Q(user__id=coordinator_id))
        
        school_id = request.query_params.get('school_id')
        if school_id:
            coordinators = coordinators.filter(school_id=school_id)
        
        data = []
        for coord in coordinators.select_related('school', 'user'):
            data.append({
                'coordinator_id': str(coord.user.id),
                'coordinator_profile_id': str(coord.id),
                'coordinator_name': coord.name,
                'coordinator_email': coord.user.email,
                'school_id': str(coord.school.id) if coord.school else None,
                'school_name': coord.school.name if coord.school else None,
                'assigned': coord.school is not None
            })
        
        return Response({
            'total': len(data),
            'unassigned': len([c for c in data if not c['assigned']]),
            'coordinators': data
        })

    def delete(self, request, coordinator_id):
        """Unassign coordinator from school"""
        coordinator = resolve_coordinator(coordinator_id)
        if not coordinator:
            return Response(
                {"error": f"Coordinator not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        old_school = coordinator.school
        coordinator.school = None
        coordinator.save()
        
        return Response({
            'message': f"Coordinator '{coordinator.name}' removed from school '{old_school.name if old_school else 'none'}'",
            'coordinator_name': coordinator.name
        }, status=status.HTTP_200_OK)
