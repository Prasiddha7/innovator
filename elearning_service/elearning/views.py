from rest_framework import viewsets, generics, views, status
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
    EnrollmentSerializer, PaymentSerializer, PayoutRequestSerializer
)
from elearning.permissions import IsElearningVendorUser, IsStudentUser

# --- USER SYNC ---

class UserSyncView(APIView):
    """
    Internal API to sync users from auth_service
    """
    permission_classes = [AllowAny]  # Later secure with service token

    def post(self, request):
        serializer = UserSyncSerializer(data=request.data)

        if serializer.is_valid():
            user_data = serializer.validated_data

            # Create or update user
            user, created = User.objects.update_or_create(
                id=user_data["id"],  # UUID from auth_service
                defaults={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "role": user_data["role"],
                }
            )

            # Sync to corresponding profile if applicable
            role = user_data.get("role")
            if role == "elearning_vendor":
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

    def get(self, request):
        vendor_profile = request.user.vendor_profile

        courses = vendor_profile.course.all()

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
        return Course.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)

class VendorCourseContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsElearningVendorUser]
    serializer_class = CourseContentSerializer

    def get_queryset(self):
        return CourseContent.objects.filter(course__vendor=self.request.user.vendor_profile)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_pk'], vendor=self.request.user.vendor_profile)
        serializer.save(course=course)

class VendorPayoutViewSet(viewsets.ModelViewSet):
    permission_classes = [IsElearningVendorUser]
    serializer_class = PayoutRequestSerializer

    def get_queryset(self):
        return PayoutRequest.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)

# --- PUBLIC / STUDENT APIs ---
class PublicCourseListView(generics.ListAPIView):
    """Catalog: List all published courses, accessible to anyone."""
    permission_classes = [AllowAny]
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseListSerializer

class StudentCourseListView(generics.ListAPIView):
    # Backward compatible if needed, but PublicCourseListView is better
    permission_classes = [IsAuthenticated] # any authenticated can browse
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseListSerializer

class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStudentUser]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        # Safely fetch or create the profile just in case it's missing from sync
        from elearning.models import StudentProfile
        student_profile, _ = StudentProfile.objects.get_or_create(
            user=self.request.user, defaults={'id': self.request.user.id}
        )
        return Enrollment.objects.filter(student=student_profile)

    def perform_create(self, serializer):
        from elearning.models import StudentProfile
        student_profile, _ = StudentProfile.objects.get_or_create(
            user=self.request.user, defaults={'id': self.request.user.id}
        )
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
    permission_classes = [IsStudentUser]
    serializer_class = CourseContentSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_pk']
        # Check if enrolled
        if not Enrollment.objects.filter(course_id=course_id, student=self.request.user.student_profile).exists():
            return CourseContent.objects.none()
        return CourseContent.objects.filter(course_id=course_id).order_by('order')


class VendorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendor_profile = request.user.vendor_profile
        serializer = VendorProfileSerializer(vendor_profile)
        return Response(serializer.data)
    
class VendorCatagoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsElearningVendorUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer