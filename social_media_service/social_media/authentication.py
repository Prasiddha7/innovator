from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from .models import User

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if not user_id:
            return None
        
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
