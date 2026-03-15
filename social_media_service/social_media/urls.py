from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserSyncView, CategoryViewSet, ProfileView,
    PostViewSet, CommentViewSet, ReactionViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'reactions', ReactionViewSet, basename='reaction')

urlpatterns = [
    path('internal/sync-user/', UserSyncView.as_view(), name='sync-user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
