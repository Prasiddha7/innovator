from django.urls import path
from .views import RegisterView, SSOLoginView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("sso/login/", SSOLoginView.as_view(), name="sso-login"),

]
