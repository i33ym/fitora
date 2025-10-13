from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Dietologist, Group, ClientRequest
from .serializers import (
    DietologistLoginSerializer, GroupSerializer, GroupCreateSerializer,
    ClientRequestSerializer, ClientDetailSerializer, RequestDietologistSerializer
)
from .middleware import DietologistJWTAuthentication
from users.models import User
from users.serializers import UserProfileSerializer
from meals.models import Meal
from meals.serializers import MealSerializer

def get_tokens_for_dietologist(dietologist):
    refresh = RefreshToken()
    refresh['dietologist_id'] = dietologist.id
    refresh['type'] = 'dietologist'
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }

@extend_schema(
    request=DietologistLoginSerializer,
    responses={
        200: OpenApiResponse(description='Login successful'),
        401: OpenApiResponse(description='Invalid credentials')
    },
    tags=['Dietologist']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def dietologist_login(request):
    serializer = DietologistLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    password = serializer.validated_data['password']
    
    try:
        dietologist = Dietologist.objects.get(phone_number=phone_number, is_active=True)
    except Dietologist.DoesNotExist:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not dietologist.check_password(password):
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    tokens = get_tokens_for_dietologist(dietologist)
    return Response({
        **tokens,
        'dietologist': {
            'id': dietologist.id,
            'first_name': dietologist.first_name,
            'last_name': dietologist.last_name,
            'phone_number': dietologist.phone_number
        }
    })

@extend_schema(
    request=GroupCreateSerializer,
    responses={
        201: OpenApiResponse(response=GroupSerializer, description='Group created'),
        400: OpenApiResponse(description='Invalid data')
    },
    tags=['Dietologist']
)
@api_view(['POST'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def create_group(request):
    dietologist = request.user
    
    serializer = GroupCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    code = serializer.validated_data.get('code') or Group.generate_code()
    
    group = Group.objects.create(
        dietologist=dietologist,
        name=serializer.validated_data['name'],
        code=code
    )
    
    return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)

@extend_schema(
    responses={
        200: OpenApiResponse(response=GroupSerializer(many=True), description='List of groups')
    },
    tags=['Dietologist']
)
@api_view(['GET'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def list_groups(request):
    dietologist = request.user
    groups = Group.objects.filter(dietologist=dietologist)
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)

@extend_schema(
    request=GroupSerializer,
    responses={
        200: OpenApiResponse(response=GroupSerializer, description='Group updated'),
        400: OpenApiResponse(description='Invalid data'),
        404: OpenApiResponse(description='Group not found')
    },
    tags=['Dietologist']
)
@api_view(['PATCH'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def update_group(request, pk):
    dietologist = request.user
    group = get_object_or_404(Group, pk=pk, dietologist=dietologist)
    
    if 'code' in request.data:
        new_code = request.data['code']
        if Group.objects.filter(code=new_code).exclude(id=group.id).exists():
            return Response({'message': 'Code already in use'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = GroupSerializer(group, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response(serializer.data)

@extend_schema(
    responses={
        200: OpenApiResponse(response=ClientRequestSerializer(many=True), description='Pending requests')
    },
    tags=['Dietologist']
)
@api_view(['GET'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def pending_requests(request):
    dietologist = request.user
    
    requests_qs = ClientRequest.objects.filter(
        group__dietologist=dietologist,
        status='pending'
    ).select_related('user', 'group')
    
    serializer = ClientRequestSerializer(requests_qs, many=True)
    return Response(serializer.data)

@extend_schema(
    responses={
        200: OpenApiResponse(description='Request approved'),
        404: OpenApiResponse(description='Request not found')
    },
    tags=['Dietologist']
)
@api_view(['POST'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def approve_request(request, pk):
    dietologist = request.user
    
    client_request = get_object_or_404(
        ClientRequest,
        pk=pk,
        group__dietologist=dietologist,
        status='pending'
    )
    
    client_request.status = 'approved'
    client_request.responded_at = timezone.now()
    client_request.save()
    
    return Response({'message': 'Request approved'})

@extend_schema(
    responses={
        200: OpenApiResponse(description='Request rejected'),
        404: OpenApiResponse(description='Request not found')
    },
    tags=['Dietologist']
)
@api_view(['POST'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def reject_request(request, pk):
    dietologist = request.user
    
    client_request = get_object_or_404(
        ClientRequest,
        pk=pk,
        group__dietologist=dietologist,
        status='pending'
    )
    
    client_request.status = 'rejected'
    client_request.responded_at = timezone.now()
    client_request.save()
    
    return Response({'message': 'Request rejected'})

@extend_schema(
    responses={
        200: OpenApiResponse(response=UserProfileSerializer(many=True), description='List of clients')
    },
    tags=['Dietologist']
)
@api_view(['GET'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def list_clients(request):
    dietologist = request.user
    
    approved_requests = ClientRequest.objects.filter(
        group__dietologist=dietologist,
        status='approved'
    ).select_related('user')
    
    clients = [req.user for req in approved_requests]
    serializer = UserProfileSerializer(clients, many=True)
    return Response(serializer.data)

@extend_schema(
    responses={
        200: OpenApiResponse(response=ClientDetailSerializer, description='Client details with meals'),
        404: OpenApiResponse(description='Client not found')
    },
    tags=['Dietologist']
)
@api_view(['GET'])
@authentication_classes([DietologistJWTAuthentication])
@permission_classes([IsAuthenticated])
def client_detail(request, user_id):
    dietologist = request.user
    
    client_request = get_object_or_404(
        ClientRequest,
        user_id=user_id,
        group__dietologist=dietologist,
        status='approved'
    )
    
    user = client_request.user
    meals = Meal.objects.filter(user=user).order_by('-meal_date', '-created_at')
    
    return Response({
        'profile': UserProfileSerializer(user).data,
        'meals': MealSerializer(meals, many=True).data,
        'total_meals': meals.count()
    })

@extend_schema(
    request=RequestDietologistSerializer,
    responses={
        201: OpenApiResponse(description='Request sent successfully'),
        400: OpenApiResponse(description='Invalid group code or already requested'),
        404: OpenApiResponse(description='Group not found')
    },
    tags=['User']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_dietologist(request):
    user = request.user
    
    serializer = RequestDietologistSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    group_code = serializer.validated_data['group_code']
    
    try:
        group = Group.objects.get(code=group_code)
    except Group.DoesNotExist:
        return Response({'message': 'Invalid group code'}, status=status.HTTP_404_NOT_FOUND)
    
    existing_approved = ClientRequest.objects.filter(user=user, status='approved').first()
    if existing_approved:
        return Response({'message': 'You already have an approved dietologist'}, status=status.HTTP_400_BAD_REQUEST)
    
    if ClientRequest.objects.filter(user=user, group=group, status='pending').exists():
        return Response({'message': 'Request already pending'}, status=status.HTTP_400_BAD_REQUEST)
    
    ClientRequest.objects.create(user=user, group=group)
    
    return Response({'message': 'Request sent successfully'}, status=status.HTTP_201_CREATED)