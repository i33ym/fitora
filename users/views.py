from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .models import User, OTPSession
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, GoogleAuthSerializer,
    UserProfileSerializer, ProfileCreateSerializer
)
from .utils import generate_otp, send_sms, verify_google_token

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User, OTPSession
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, GoogleAuthSerializer,
    UserProfileSerializer, ProfileCreateSerializer
)
from .utils import generate_otp, send_sms, verify_google_token

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }

@extend_schema(
    request=SendOTPSerializer,
    responses={
        200: OpenApiResponse(description='OTP sent successfully'),
        400: OpenApiResponse(description='Invalid request'),
        500: OpenApiResponse(description='Failed to send OTP')
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = generate_otp()
    
    otp_session = OTPSession.objects.create(
        phone_number=phone_number,
        otp_code=otp_code
    )
    
    sms_sent = send_sms(phone_number, otp_code)
    
    if not sms_sent:
        return Response(
            {'message': 'Failed to send OTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    expiry_seconds = int((otp_session.expires_at - timezone.now()).total_seconds())
    
    return Response({
        'session': str(otp_session.session),
        'message': 'OTP sent successfully',
        'expiry': expiry_seconds
    })

@extend_schema(
    request=VerifyOTPSerializer,
    responses={
        200: OpenApiResponse(description='OTP verified successfully'),
        400: OpenApiResponse(description='Invalid session, expired OTP, or invalid OTP')
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        return Response(
            {'message': 'Invalid session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if otp_session.is_expired():
        return Response(
            {'message': 'OTP expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if otp_session.otp_code != otp_code:
        return Response(
            {'message': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    otp_session.is_verified = True
    otp_session.save()
    
    user, created = User.objects.get_or_create(phone_number=phone_number)
    user.fcm_token = fcm_token
    user.save()
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        **tokens,
        'new_user': created
    })

@extend_schema(
    request=GoogleAuthSerializer,
    responses={
        200: OpenApiResponse(description='Google authentication successful'),
        400: OpenApiResponse(description='Invalid Google token')
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    google_token = serializer.validated_data['google_token']
    fcm_token = serializer.validated_data['fcm_token']
    
    google_data = verify_google_token(google_token)
    
    if not google_data:
        return Response(
            {'message': 'Invalid Google token'},
            status=status.HTTP_400_BAD_REQUEST
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
    
    return Response({
        **tokens,
        'new_user': created
    })

@extend_schema(
    request=ProfileCreateSerializer,
    responses={
        200: OpenApiResponse(response=UserProfileSerializer, description='Profile operation successful'),
        400: OpenApiResponse(description='Invalid data')
    },
    tags=['User Profile']
)
@api_view(['GET', 'POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if user.profile_completed:
            return Response(
                {'message': 'Profile already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProfileCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        for field, value in serializer.validated_data.items():
            setattr(user, field, value)
        
        user.profile_completed = True
        user.save()
        
        return Response(UserProfileSerializer(user).data)
    
    else:  # PUT or PATCH
        serializer = UserProfileSerializer(user, data=request.data, partial=(request.method == 'PATCH'))
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data)