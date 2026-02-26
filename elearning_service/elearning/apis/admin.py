# --- ADMIN APIs ---
from elearning.models import Category, VendorProfile, Course, CourseContent
from elearning.permissions import IsAdminUser
from elearning.serializers import CategorySerializer, VendorProfileSerializer, AdminCourseSerializer, CourseContentSerializer
from rest_framework import viewsets, generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


class AdminCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AdminVendorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminUser]
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer

class AdminCourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Course.objects.all()
    serializer_class = AdminCourseSerializer

class AdminCourseContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = CourseContentSerializer

    def get_queryset(self):
        return CourseContent.objects.filter(course_id=self.kwargs['course_pk'])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_pk'])
        serializer.save(course=course)