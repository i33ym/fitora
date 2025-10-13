from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from .models import Dietologist

class DietologistJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = AccessToken(raw_token)
        except Exception:
            return None
        
        # Check if this is a dietologist token
        if validated_token.get('type') != 'dietologist':
            return None
        
        dietologist_id = validated_token.get('dietologist_id')
        if not dietologist_id:
            return None
        
        try:
            dietologist = Dietologist.objects.get(id=dietologist_id, is_active=True)
        except Dietologist.DoesNotExist:
            raise AuthenticationFailed('Dietologist not found')
        
        return (dietologist, validated_token)