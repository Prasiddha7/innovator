from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomeView, UserSyncView, CategoryViewSet, ProfileView,
    PostViewSet, CommentViewSet, ReactionViewSet, UserViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'reactions', ReactionViewSet, basename='reaction')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('internal/sync-user/', UserSyncView.as_view(), name='sync-user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
