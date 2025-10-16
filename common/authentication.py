from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from jwt.exceptions import ExpiredSignatureError

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except ExpiredSignatureError:
            raise AuthenticationFailed(
                detail={'code': 'expired_access_token', 'message': 'Access token has expired'},
                code='expired_access_token'
            )
        except (InvalidToken, TokenError):
            raise AuthenticationFailed(
                detail={'code': 'invalid_token', 'message': 'Invalid or malformed token'},
                code='invalid_token'
            )