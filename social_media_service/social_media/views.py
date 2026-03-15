from rest_framework import viewsets, generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
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
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSyncSerializer # Reusing for list/detail for now
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
        request.user.following.add(user_to_follow)
        return Response({"message": f"Successfully followed {user_to_follow.username}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()
        request.user.following.remove(user_to_unfollow)
        return Response({"message": f"Successfully unfollowed {user_to_unfollow.username}"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def following(self, request):
        following = request.user.following.all()
        serializer = UserSyncSerializer(following, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        followers = request.user.followers.all()
        serializer = UserSyncSerializer(followers, many=True)
        return Response(serializer.data)
