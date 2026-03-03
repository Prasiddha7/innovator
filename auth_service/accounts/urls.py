from django.urls import path
from .views import RegisterView, SSOLoginView, UserDetailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("sso/login/", SSOLoginView.as_view(), name="sso-login"),
    path("user/me/", UserDetailView.as_view(), name="user-detail"),

]
