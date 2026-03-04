import uuid
from rest_framework import serializers
from .models import (
    User, AdminProfile, VendorProfile, StudentProfile,
    Category, Course, CourseContent, Enrollment, Payment, PayoutRequest
)

class UserSyncSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "role", "gender", "date_of_birth", "address", "phone_number"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = '__all__'
        read_only_fields = ['course']

class CourseSerializer(serializers.ModelSerializer):
    contents = CourseContentSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.user.username', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'vendor', 'vendor_name', 'category', 'category_name', 
            'title', 'description', 'price', 'is_published', 'created_at', 'contents'
        ]
        read_only_fields = ['vendor']

class CourseListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.user.username', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'vendor', 'vendor_name', 'category', 'category_name', 
            'title', 'description', 'price', 'is_published', 'created_at'
        ]
        read_only_fields = ['vendor', 'is_published']

class AdminCourseSerializer(CourseSerializer):
    """Admin serializer for Course allowing vendor to be manually assigned during creation."""
    class Meta:
        model = Course
        fields = [
            'id', 'category', 'category_name', 
            'title', 'description', 'price', 'is_published', 'created_at'
        ]
        
    def create(self, validated_data):
        from elearning.models import VendorProfile
        request = self.context.get("request")
        user = request.user
        # Admins act as a vendor for courses they create directly
        vendor_profile, _ = VendorProfile.objects.get_or_create(
            user=user, 
            defaults={'id': user.id, 'is_approved': True}
        )
        validated_data["vendor"] = vendor_profile
        return super().create(validated_data)


class VendorProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.full_name', required=False)
    email = serializers.EmailField(source='user.email', read_only=True)
    courses_count = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = VendorProfile
        fields = [
            "id", "user", "username", "full_name", "email",
            "is_approved", "bio", "commission_rate",
            "commission_amount", "total_earnings", "created_at",
            "courses_count", "courses"
        ]
        read_only_fields = ['user', 'commission_amount', 'total_earnings']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data and 'full_name' in user_data:
            user = instance.user
            user.full_name = user_data['full_name']
            user.save(update_fields=['full_name'])
        
        return super().update(instance, validated_data)

    def get_courses_count(self, obj):
        return obj.course.count()

    def get_courses(self, obj):
        return [
            {
                "id": course.id,
                "title": course.title,
                "price": course.price,
                "is_published": course.is_published
            }
            for course in obj.course.all()
        ]

class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = '__all__'
        read_only_fields = ['vendor', 'status', 'processed_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'enrolled_at']
        read_only_fields = ['student']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['student', 'timestamp']