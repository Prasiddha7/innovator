from rest_framework import viewsets, generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import User, Category, Profile, Post, Comment, Reaction, ChatMessage
from .serializers import (
    UserSyncSerializer, CategorySerializer, ProfileSerializer, 
    PostSerializer, CommentSerializer, ReactionSerializer, ChatMessageSerializer
)

class HomeView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "Social Media API is running"}, status=status.HTTP_200_OK)

class UserSyncView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSyncSerializer

    def post(self, request):
        serializer = UserSyncSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            user, created = User.objects.update_or_create(
                id=user_data["id"],
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
            # Auto-create profile
            Profile.objects.get_or_create(user=user)
            
            return Response({"message": "User synced", "created": created}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        
        # Feed implementation: if user has interests, show those first?
        # For now, just basic filtering and ordering
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.request.query_params.get('post'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReactionViewSet(viewsets.ModelViewSet):
    serializer_class = ReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reaction.objects.filter(post_id=self.request.query_params.get('post'))

    def perform_create(self, serializer):
        post = serializer.validated_data['post']
        Reaction.objects.filter(user=self.request.user, post=post).delete()
        serializer.save(user=self.request.user)
