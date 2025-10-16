from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Dietologist, Group, ClientRequest
from .serializers import (
    DietologistLoginSerializer, GroupSerializer, GroupCreateSerializer,
    ClientRequestSerializer, RequestDietologistSerializer
)
from users.serializers import UserProfileSerializer
from meals.models import Meal
from meals.serializers import MealSerializer
from django.utils.translation import gettext as _
from common.responses import success_response, error_response

def get_dietologist_from_request(request):
    """Extract and validate dietologist from JWT token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token_string = auth_header.split(' ')[1]
    
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(token_string)
        if token.get('type') != 'dietologist':
            return None
        
        dietologist_id = token.get('dietologist_id')
        return Dietologist.objects.get(id=dietologist_id, is_active=True)
    except Exception:
        return None

def get_tokens_for_dietologist(dietologist):
    refresh = RefreshToken()
    refresh['dietologist_id'] = dietologist.id
    refresh['type'] = 'dietologist'
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def dietologist_login(request):
    serializer = DietologistLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    phone_number = serializer.validated_data['phone_number']
    password = serializer.validated_data['password']
    
    try:
        dietologist = Dietologist.objects.get(phone_number=phone_number, is_active=True)
    except Dietologist.DoesNotExist:
        return error_response(
            message=_('Invalid credentials'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    if not dietologist.check_password(password):
        return error_response(
            message=_('Invalid credentials'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    tokens = get_tokens_for_dietologist(dietologist)
    return success_response(
        data={
            **tokens,
            'dietologist': {
                'id': dietologist.id,
                'first_name': dietologist.first_name,
                'last_name': dietologist.last_name,
                'phone_number': dietologist.phone_number
            }
        }
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_group(request):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = GroupCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    code = serializer.validated_data.get('code') or Group.generate_code()
    
    group = Group.objects.create(
        dietologist=dietologist,
        name=serializer.validated_data['name'],
        code=code
    )
    
    return success_response(
        data=GroupSerializer(group).data,
        status_code=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def list_groups(request):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    groups = Group.objects.filter(dietologist=dietologist)
    serializer = GroupSerializer(groups, many=True)
    return success_response(data=serializer.data)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_group(request, pk):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    group = get_object_or_404(Group, pk=pk, dietologist=dietologist)
    
    if 'code' in request.data:
        new_code = request.data['code']
        if Group.objects.filter(code=new_code).exclude(id=group.id).exists():
            return error_response(
                message=_('Code already in use'),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    serializer = GroupSerializer(group, data=request.data, partial=True)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    serializer.save()
    return success_response(data=serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def pending_requests(request):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    requests_qs = ClientRequest.objects.filter(
        group__dietologist=dietologist,
        status='pending'
    ).select_related('user', 'group')
    
    serializer = ClientRequestSerializer(requests_qs, many=True)
    return success_response(data=serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def approve_request(request, pk):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    client_request = get_object_or_404(
        ClientRequest,
        pk=pk,
        group__dietologist=dietologist,
        status='pending'
    )
    
    client_request.status = 'approved'
    client_request.responded_at = timezone.now()
    client_request.save()
    
    return success_response(message=_('Request approved'))

@api_view(['POST'])
@permission_classes([AllowAny])
def reject_request(request, pk):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    client_request = get_object_or_404(
        ClientRequest,
        pk=pk,
        group__dietologist=dietologist,
        status='pending'
    )
    
    client_request.status = 'rejected'
    client_request.responded_at = timezone.now()
    client_request.save()
    
    return success_response(message=_('Request rejected'))

@api_view(['GET'])
@permission_classes([AllowAny])
def list_clients(request):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    approved_requests = ClientRequest.objects.filter(
        group__dietologist=dietologist,
        status='approved'
    ).select_related('user')
    
    clients = [req.user for req in approved_requests]
    serializer = UserProfileSerializer(clients, many=True)
    return success_response(data=serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def client_detail(request, user_id):
    dietologist = get_dietologist_from_request(request)
    if not dietologist:
        return error_response(
            message=_('Unauthorized'),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    client_request = get_object_or_404(
        ClientRequest,
        user_id=user_id,
        group__dietologist=dietologist,
        status='approved'
    )
    
    user = client_request.user
    meals = Meal.objects.filter(user=user).order_by('-meal_date', '-created_at')
    
    return success_response(
        data={
            'profile': UserProfileSerializer(user).data,
            'meals': MealSerializer(meals, many=True, context={'request': request}).data,
            'total_meals': meals.count()
        }
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_dietologist(request):
    user = request.user
    
    serializer = RequestDietologistSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    group_code = serializer.validated_data['group_code']
    
    try:
        group = Group.objects.get(code=group_code)
    except Group.DoesNotExist:
        return error_response(
            message=_('Invalid group code'),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    existing_approved = ClientRequest.objects.filter(user=user, status='approved').first()
    if existing_approved:
        return error_response(
            message=_('You already have an approved dietologist'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if ClientRequest.objects.filter(user=user, group=group, status='pending').exists():
        return error_response(
            message=_('Request already pending'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    ClientRequest.objects.create(user=user, group=group)
    
    return success_response(
        message=_('Request sent successfully'),
        status_code=status.HTTP_201_CREATED
    )