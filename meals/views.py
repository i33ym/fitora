# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.pagination import PageNumberPagination
# from django.shortcuts import get_object_or_404
# from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
# from datetime import datetime
# from .models import Meal
# from .serializers import MealSerializer, MealCreateSerializer, MealListSerializer

# class MealPagination(PageNumberPagination):
#     page_size = 20
#     page_size_query_param = 'page_size'
#     max_page_size = 100

# @extend_schema(
#     request=MealCreateSerializer,
#     responses={
#         201: OpenApiResponse(response=MealSerializer, description='Meal created successfully'),
#         400: OpenApiResponse(description='Invalid data')
#     },
#     tags=['Meals']
# )
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_meal(request):
#     serializer = MealCreateSerializer(data=request.data)
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     meal = serializer.save(user=request.user)
#     return Response(MealSerializer(meal).data, status=status.HTTP_201_CREATED)

# @extend_schema(
#     responses={
#         200: OpenApiResponse(response=MealListSerializer(many=True), description='List of meals')
#     },
#     tags=['Meals']
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_meals(request):
#     meals = Meal.objects.filter(user=request.user)
    
#     paginator = MealPagination()
#     paginated_meals = paginator.paginate_queryset(meals, request)
#     serializer = MealListSerializer(paginated_meals, many=True)
    
#     return paginator.get_paginated_response(serializer.data)

# @extend_schema(
#     responses={
#         200: OpenApiResponse(response=MealSerializer, description='Meal details'),
#         404: OpenApiResponse(description='Meal not found')
#     },
#     tags=['Meals']
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_meal(request, pk):
#     meal = get_object_or_404(Meal, pk=pk, user=request.user)
#     serializer = MealSerializer(meal)
#     return Response(serializer.data)

# @extend_schema(
#     request=MealSerializer,
#     responses={
#         200: OpenApiResponse(response=MealSerializer, description='Meal updated successfully'),
#         400: OpenApiResponse(description='Invalid data'),
#         404: OpenApiResponse(description='Meal not found')
#     },
#     tags=['Meals']
# )
# @api_view(['PUT', 'PATCH'])
# @permission_classes([IsAuthenticated])
# def update_meal(request, pk):
#     meal = get_object_or_404(Meal, pk=pk, user=request.user)
#     serializer = MealSerializer(meal, data=request.data, partial=(request.method == 'PATCH'))
    
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     serializer.save()
#     return Response(serializer.data)

# @extend_schema(
#     responses={
#         204: OpenApiResponse(description='Meal deleted successfully'),
#         404: OpenApiResponse(description='Meal not found')
#     },
#     tags=['Meals']
# )
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_meal(request, pk):
#     meal = get_object_or_404(Meal, pk=pk, user=request.user)
#     meal.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

# @extend_schema(
#     parameters=[
#         OpenApiParameter(name='date', description='Date in YYYY-MM-DD format', required=True, type=str)
#     ],
#     responses={
#         200: OpenApiResponse(description='Daily meal summary'),
#         400: OpenApiResponse(description='Invalid date format')
#     },
#     tags=['Meals']
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def daily_summary(request):
#     date_str = request.query_params.get('date')
    
#     if not date_str:
#         return Response({'message': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return Response({'message': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
#     meals = Meal.objects.filter(
#         user=request.user,
#         created_at__date=date_obj
#     )
    
#     serializer = MealSerializer(meals, many=True)
    
#     return Response({
#         'date': date_str,
#         'meals': serializer.data,
#         'total_meals': meals.count()
#     })


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from datetime import datetime
from .models import Meal
from .serializers import MealSerializer, MealCreateSerializer, MealListSerializer

class MealPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema(
    request=MealCreateSerializer,
    responses={
        200: OpenApiResponse(response=MealListSerializer(many=True), description='List of meals'),
        201: OpenApiResponse(response=MealSerializer, description='Meal created successfully'),
        400: OpenApiResponse(description='Invalid data')
    },
    tags=['Meals']
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def meals(request):
    if request.method == 'GET':
        meals = Meal.objects.filter(user=request.user)
        
        paginator = MealPagination()
        paginated_meals = paginator.paginate_queryset(meals, request)
        serializer = MealListSerializer(paginated_meals, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MealCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        meal = serializer.save(user=request.user)
        return Response(MealSerializer(meal).data, status=status.HTTP_201_CREATED)

@extend_schema(
    request=MealSerializer,
    responses={
        200: OpenApiResponse(response=MealSerializer, description='Meal operation successful'),
        204: OpenApiResponse(description='Meal deleted successfully'),
        400: OpenApiResponse(description='Invalid data'),
        404: OpenApiResponse(description='Meal not found')
    },
    tags=['Meals']
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def meal_detail(request, pk):
    meal = get_object_or_404(Meal, pk=pk, user=request.user)
    
    if request.method == 'GET':
        serializer = MealSerializer(meal)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = MealSerializer(meal, data=request.data, partial=(request.method == 'PATCH'))
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        meal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    parameters=[
        OpenApiParameter(name='date', description='Date in YYYY-MM-DD format', required=True, type=str)
    ],
    responses={
        200: OpenApiResponse(description='Daily meal summary'),
        400: OpenApiResponse(description='Invalid date format')
    },
    tags=['Meals']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_summary(request):
    date_str = request.query_params.get('date')
    
    if not date_str:
        return Response({'message': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'message': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    meals_qs = Meal.objects.filter(
        user=request.user,
        created_at__date=date_obj
    )
    
    serializer = MealSerializer(meals_qs, many=True)
    
    return Response({
        'date': date_str,
        'meals': serializer.data,
        'total_meals': meals_qs.count()
    })