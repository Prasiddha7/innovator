from rest_framework import viewsets, generics, views, status
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from elearning.models import (
    User, Category, Course, CourseContent,
    VendorProfile, Enrollment, Payment, PayoutRequest
)
from elearning.serializers import (
    UserSyncSerializer, CategorySerializer, CourseSerializer, CourseListSerializer,
    CourseContentSerializer, VendorProfileSerializer,
    EnrollmentSerializer, PaymentSerializer, PayoutRequestSerializer,
    StudentProfileSerializer
)
from elearning.permissions import IsElearningVendorUser, IsStudentUser

# --- USER SYNC ---

class UserSyncView(APIView):
    """
    Internal API to sync users from auth_service
    """
    permission_classes = [AllowAny]  # Later secure with service token
    serializer_class = UserSyncSerializer

    def post(self, request):
        serializer = UserSyncSerializer(data=request.data)

        if serializer.is_valid():
            user_data = serializer.validated_data

            # Create or update user
            user, created = User.objects.update_or_create(
                id=user_data["id"],  # UUID from auth_service
                defaults={
                    "username": user_data["username"],
                    "full_name": user_data.get("full_name"),
                    "email": user_data["email"],
                    "role": user_data.get("role"),
                    "gender": user_data.get("gender"),
                    "date_of_birth": user_data.get("date_of_birth"),
                    "address": user_data.get("address"),
                    "phone_number": user_data.get("phone_number"),
                }
            )

            # Sync to corresponding profile if applicable
            role = user_data.get("role")
            if role in ["elearning_vendor", "vendor"]:
                from elearning.models import VendorProfile
                VendorProfile.objects.get_or_create(user=user, defaults={'id': user.id})
            elif role == "student":
                from elearning.models import StudentProfile
                StudentProfile.objects.get_or_create(user=user, defaults={'id': user.id})

            return Response({
                "message": "User synced successfully",
                "created": created
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# --- VENDOR APIs ---
class VendorDashboardView(views.APIView):
    permission_classes = [IsElearningVendorUser]
    
    @extend_schema(responses={200: VendorProfileSerializer})
    def get(self, request):
        user = request.user
        
        # If admin/superuser, they might not have a vendor profile.
        # We'll provide a general overview or pick the first profile for context if needed.
        if (user.role == 'admin' or user.is_superuser) and not hasattr(user, 'vendor_profile'):
            courses = Course.objects.all()
            students_enrolled = Enrollment.objects.all().count()
            
            return Response({
                "vendor_profile": {
                    "id": None,
                    "is_approved": True,
                    "bio": "Administrator View",
                    "commission_rate": 0,
                    "commission_amount": 0,
                    "total_earnings": 0,
                    "created_at": None,
                },
                "dashboard_stats": {
                    "courses_count": courses.count(),
                    "students_enrolled": students_enrolled,
                    "total_earnings": 0
                }
            })

        vendor_profile = user.vendor_profile
        courses = vendor_profile.courses.all() # Changed from .course.all() after checking model's related_name

        students_enrolled = Enrollment.objects.filter(
            course__in=courses
        ).count()

        return Response({
            "vendor_profile": {
                "id": vendor_profile.id,
                "is_approved": vendor_profile.is_approved,
                "bio": vendor_profile.bio,
                "commission_rate": vendor_profile.commission_rate,
                "commission_amount": vendor_profile.commission_amount,
                "total_earnings": vendor_profile.total_earnings,
                "created_at": vendor_profile.created_at,
            },
            "dashboard_stats": {
                "courses_count": courses.count(),
                "students_enrolled": students_enrolled,
                "total_earnings": vendor_profile.total_earnings
            }
        })
    

class VendorCourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsElearningVendorUser]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if (user.role == 'admin' or user.is_superuser):
            return Course.objects.all()
        return Course.objects.filter(vendor=user.vendor_profile)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)

class VendorCourseContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsElearningVendorUser]
    serializer_class = CourseContentSerializer

    def get_queryset(self):
        user = self.request.user
        if (user.role == 'admin' or user.is_superuser):
            return CourseContent.objects.all()
        return CourseContent.objects.filter(course__vendor=user.vendor_profile)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_pk'], vendor=self.request.user.vendor_profile)
        serializer.save(course=course)

class VendorPayoutViewSet(viewsets.ModelViewSet):
    permission_classes = [IsElearningVendorUser]
    serializer_class = PayoutRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if (user.role == 'admin' or user.is_superuser):
            return PayoutRequest.objects.all()
        return PayoutRequest.objects.filter(vendor=user.vendor_profile)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)

# --- PUBLIC / STUDENT APIs ---
class PublicCourseListView(generics.ListAPIView):
    """Catalog: List all published courses, accessible to anyone."""
    permission_classes = [AllowAny]
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseListSerializer

class StudentCourseListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] # any authenticated can browse
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseListSerializer

class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        # Safely fetch or create the profile and update role
        from elearning.models import StudentProfile
        user = self.request.user
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user, defaults={'id': user.id}
        )
        if user.role != "student":
            user.role = "student"
            user.save(update_fields=['role'])
            
        return Enrollment.objects.filter(student=student_profile)

    def perform_create(self, serializer):
        from elearning.models import StudentProfile
        user = self.request.user
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user, defaults={'id': user.id}
        )
        if user.role != "student":
            user.role = "student"
            user.save(update_fields=['role'])
        course = serializer.validated_data.get('course')
        
        # Course validation and existing enrollment check
        if not course:
            raise ValidationError({"course": "This field is required."})
            
        if Enrollment.objects.filter(student=student_profile, course=course).exists():
            raise ValidationError({"detail": "You are already enrolled in this course."})
            
        # 1. Save Enrollment
        enrollment = serializer.save(student=student_profile)
        
        # 2. Process Payment Mock & Vendor Earnings
        price = course.price
        if price > 0:
            from elearning.models import Payment
            Payment.objects.create(
                student=student_profile,
                course=course,
                amount=price,
                status='completed',
                transaction_id=f"mock_txn_{enrollment.id}"
            )
            
            # Calculate Commission & Earnings
            from decimal import Decimal
            vendor_profile = course.vendor
            commission_rate = vendor_profile.commission_rate
            commission_cut = price * (commission_rate / Decimal('100.0'))
            vendor_earnings = price - commission_cut
            
            vendor_profile.commission_amount += commission_cut
            vendor_profile.total_earnings += vendor_earnings
            vendor_profile.save()

class StudentCourseContentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseContentSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_pk']
        user = self.request.user
        
        # Ensure student profile exists
        from elearning.models import StudentProfile
        try:
            student_profile = user.student_profile
        except StudentProfile.DoesNotExist:
            return CourseContent.objects.none()

        # Check if enrolled
        if not Enrollment.objects.filter(course_id=course_id, student=student_profile).exists():
            return CourseContent.objects.none()
        return CourseContent.objects.filter(course_id=course_id).order_by('order')


class VendorProfileView(APIView):
    permission_classes = [IsElearningVendorUser]
    serializer_class = VendorProfileSerializer

    def get(self, request):
        user = request.user
        if (user.role == 'admin' or user.is_superuser) and not hasattr(user, 'vendor_profile'):
            return Response({
                "id": None,
                "is_approved": True,
                "bio": "Administrator",
                "commission_rate": 0,
                "commission_amount": 0,
                "total_earnings": 0,
                "created_at": None,
            })
            
        vendor_profile = user.vendor_profile
        serializer = VendorProfileSerializer(vendor_profile)
        return Response(serializer.data)
    
class VendorCatagoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsElearningVendorUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses={200: StudentProfileSerializer})
    def get(self, request):
        from elearning.models import StudentProfile
        user = request.user
        
        # Auto-create profile if missing and update role
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user, defaults={'id': user.id}
        )
        if user.role != "student":
            user.role = "student"
            user.save(update_fields=['role'])
            
        serializer = StudentProfileSerializer(student_profile)
        return Response(serializer.data)