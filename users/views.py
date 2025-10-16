from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User, OTPSession
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, GoogleAuthSerializer,
    UserProfileSerializer, ProfileCreateSerializer
)
from .utils import generate_otp, send_sms, verify_google_token
from django.utils.translation import gettext as _
from common.responses import success_response, error_response

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = generate_otp()
    
    otp_session = OTPSession.objects.create(
        phone_number=phone_number,
        otp_code=otp_code
    )
    
    sms_sent = send_sms(phone_number, otp_code)
    
    if not sms_sent:
        return error_response(
            message=_('Failed to send OTP'),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    expiry_seconds = int((otp_session.expires_at - timezone.now()).total_seconds())
    
    return success_response(
        data={
            'session': str(otp_session.session),
            'expiry': expiry_seconds
        },
        message=_('OTP sent successfully')
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    session_id = serializer.validated_data['session']
    otp_code = serializer.validated_data['otp']
    phone_number = serializer.validated_data['phone_number']
    fcm_token = serializer.validated_data['fcm_token']
    
    try:
        otp_session = OTPSession.objects.get(
            session=session_id,
            phone_number=phone_number,
            is_verified=False
        )
    except OTPSession.DoesNotExist:
        return error_response(
            message=_('Invalid session'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if otp_session.is_expired():
        return error_response(
            message=_('OTP expired'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if otp_session.otp_code != otp_code:
        return error_response(
            message=_('Invalid OTP'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    otp_session.is_verified = True
    otp_session.save()
    
    user, created = User.objects.get_or_create(phone_number=phone_number)
    user.fcm_token = fcm_token
    user.save()
    
    tokens = get_tokens_for_user(user)
    
    return success_response(
        data={
            **tokens,
            'new_user': not user.profile_completed
        }
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    google_token = serializer.validated_data['google_token']
    fcm_token = serializer.validated_data['fcm_token']
    
    google_data = verify_google_token(google_token)
    
    if not google_data:
        return error_response(
            message=_('Invalid Google token'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    user, created = User.objects.get_or_create(
        google_id=google_data['google_id'],
        defaults={
            'email': google_data['email'],
            'first_name': google_data['first_name'],
            'last_name': google_data['last_name']
        }
    )
    
    user.fcm_token = fcm_token
    if not user.email:
        user.email = google_data['email']
    user.save()
    
    tokens = get_tokens_for_user(user)
    
    return success_response(
        data={
            **tokens,
            'new_user': not user.profile_completed
        }
    )

@api_view(['GET', 'POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return success_response(data=serializer.data)
    
    elif request.method == 'POST':
        if user.profile_completed:
            return error_response(
                message=_('Profile already completed'),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProfileCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message=_('Validation error'),
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        for field, value in serializer.validated_data.items():
            setattr(user, field, value)
        
        user.profile_completed = True
        user.save()
        
        return success_response(
            data=UserProfileSerializer(user).data,
            message=_('Profile created successfully')
        )
    
    else:  # PUT or PATCH
        serializer = UserProfileSerializer(user, data=request.data, partial=(request.method == 'PATCH'))
        
        if not serializer.is_valid():
            return error_response(
                message=_('Validation error'),
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return success_response(
            data=serializer.data,
            message=_('Profile updated successfully')
        )
    
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt.exceptions import ExpiredSignatureError

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    from rest_framework_simplejwt.serializers import TokenRefreshSerializer
    
    serializer = TokenRefreshSerializer(data=request.data)
    
    try:
        serializer.is_valid(raise_exception=True)
        return success_response(data=serializer.validated_data)
    except ExpiredSignatureError:
        return error_response(
            message=_('Refresh token has expired'),
            code='expired_refresh_token',
            status_code=status.HTTP_403_FORBIDDEN
        )
    except (InvalidToken, TokenError):
        return error_response(
            message=_('Invalid refresh token'),
            code='invalid_refresh_token',
            status_code=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        return error_response(
            message=_('Token refresh failed'),
            code='token_refresh_failed',
            status_code=status.HTTP_400_BAD_REQUEST
        )