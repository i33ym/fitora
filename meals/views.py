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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
from .serializers import (
    MealSerializer, MealCreateSerializer, MealListSerializer, 
    MealAnalyzeSerializer, MealAnalysisResponseSerializer, 
    DailySummaryResponseSerializer
)

def calculate_daily_totals(meals):
    """Calculate total nutritional values from all meals"""
    totals = {
        'calories': 0.0,
        'carbs': 0.0,
        'fat': 0.0,
        'protein': 0.0,
        'calcium': 0.0,
        'iron': 0.0,
        'magnesium': 0.0,
        'potassium': 0.0,
        'zinc': 0.0,
        'vitamin_a': 0.0,
        'vitamin_b12': 0.0,
        'vitamin_b9': 0.0,
        'vitamin_c': 0.0,
        'vitamin_d': 0.0,
        'cholesterol': 0.0,
        'fiber': 0.0,
        'omega_3': 0.0,
        'saturated_fat': 0.0,
        'sodium': 0.0,
    }
    
    def parse_value(value_str):
        """Extract numeric value from string like '780 kcal' -> 780.0"""
        if not value_str:
            return 0.0
        try:
            # Convert to string if it's not already
            value_str = str(value_str)
            # Split by space and get first part (the number)
            return float(value_str.split()[0])
        except (ValueError, IndexError, AttributeError):
            return 0.0
    
    for meal in meals:
        try:
            foods_data = meal.foods_data
            if not foods_data or not isinstance(foods_data, dict):
                continue
            
            if 'foods' not in foods_data or not isinstance(foods_data['foods'], list):
                continue
            
            for food in foods_data['foods']:
                if not isinstance(food, dict):
                    continue
                
                # Parse nutritions
                nutritions = food.get('nutritions', {})
                if isinstance(nutritions, dict):
                    totals['calories'] += parse_value(nutritions.get('calories', '0'))
                    totals['carbs'] += parse_value(nutritions.get('carbs', '0'))
                    totals['fat'] += parse_value(nutritions.get('fat', '0'))
                    totals['protein'] += parse_value(nutritions.get('protein', '0'))
                
                # Parse minerals
                minerals = food.get('minerals', {})
                if isinstance(minerals, dict):
                    totals['calcium'] += parse_value(minerals.get('calcium', '0'))
                    totals['iron'] += parse_value(minerals.get('iron', '0'))
                    totals['magnesium'] += parse_value(minerals.get('magnesium', '0'))
                    totals['potassium'] += parse_value(minerals.get('potassium', '0'))
                    totals['zinc'] += parse_value(minerals.get('zinc', '0'))
                
                # Parse vitamins
                vitamins = food.get('vitamins', {})
                if isinstance(vitamins, dict):
                    totals['vitamin_a'] += parse_value(vitamins.get('vitamin_a', '0'))
                    totals['vitamin_b12'] += parse_value(vitamins.get('vitamin_b12', '0'))
                    totals['vitamin_b9'] += parse_value(vitamins.get('vitamin_b9', '0'))
                    totals['vitamin_c'] += parse_value(vitamins.get('vitamin_c', '0'))
                    totals['vitamin_d'] += parse_value(vitamins.get('vitamin_d', '0'))
                
                # Parse additional
                additional = food.get('additional', {})
                if isinstance(additional, dict):
                    totals['cholesterol'] += parse_value(additional.get('cholesterol', '0'))
                    totals['fiber'] += parse_value(additional.get('fiber', '0'))
                    totals['omega_3'] += parse_value(additional.get('omega_3', '0'))
                    totals['saturated_fat'] += parse_value(additional.get('saturated_fat', '0'))
                    totals['sodium'] += parse_value(additional.get('sodium', '0'))
        except Exception as e:
            print(f"Error processing meal {meal.id}: {str(e)}")
            continue
    
    # Format with units
    return {
        'total_calories': f"{totals['calories']:.1f} kcal",
        'total_carbs': f"{totals['carbs']:.1f} g",
        'total_fat': f"{totals['fat']:.1f} g",
        'total_protein': f"{totals['protein']:.1f} g",
        'total_calcium': f"{totals['calcium']:.1f} mg",
        'total_iron': f"{totals['iron']:.1f} mg",
        'total_magnesium': f"{totals['magnesium']:.1f} mg",
        'total_potassium': f"{totals['potassium']:.1f} mg",
        'total_zinc': f"{totals['zinc']:.1f} mg",
        'total_vitamin_a': f"{totals['vitamin_a']:.1f} mcg",
        'total_vitamin_b12': f"{totals['vitamin_b12']:.1f} mcg",
        'total_vitamin_b9': f"{totals['vitamin_b9']:.1f} mcg",
        'total_vitamin_c': f"{totals['vitamin_c']:.1f} mg",
        'total_vitamin_d': f"{totals['vitamin_d']:.1f} mcg",
        'total_cholesterol': f"{totals['cholesterol']:.1f} mg",
        'total_fiber': f"{totals['fiber']:.1f} g",
        'total_omega_3': f"{totals['omega_3']:.1f} g",
        'total_saturated_fat': f"{totals['saturated_fat']:.1f} g",
        'total_sodium': f"{totals['sodium']:.1f} mg",
    }

# @extend_schema(
#     request={
#         'multipart/form-data': {
#             'type': 'object',
#             'properties': {
#                 'image': {
#                     'type': 'string',
#                     'format': 'binary'
#                 },
#                 'meal_date': {
#                     'type': 'string',
#                     'format': 'date'
#                 },
#                 'meal_time': {
#                     'type': 'string',
#                     'enum': ['breakfast', 'lunch', 'dinner', 'snack']
#                 }
#             },
#             'required': ['image']
#         }
#     },
#     responses={
#         200: OpenApiResponse(description='Meal analysis complete'),
#         400: OpenApiResponse(description='Invalid data')
#     },
#     tags=['Meals']
# # )
# @extend_schema(
#     request=MealAnalyzeSerializer,
#     responses={
#         200: OpenApiResponse(response=MealAnalysisResponseSerializer, description='Meal analysis complete'),
#         400: OpenApiResponse(description='Invalid data'),
#         500: OpenApiResponse(description='Analysis failed')
#     },
#     tags=['Meals']
# )
@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Meal image file'
                },
                'meal_date': {
                    'type': 'string',
                    'format': 'date',
                    'description': 'Date of the meal (YYYY-MM-DD). Defaults to today if not provided.'
                },
                'meal_time': {
                    'type': 'string',
                    'enum': ['breakfast', 'lunch', 'dinner', 'snack'],
                    'description': 'Optional meal time'
                }
            },
            'required': ['image']
        }
    },
    responses={
        200: OpenApiResponse(response=MealAnalysisResponseSerializer, description='Meal analysis complete'),
        400: OpenApiResponse(description='Invalid data'),
        500: OpenApiResponse(description='Analysis failed')
    },
    tags=['Meals']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_meal(request):
    serializer = MealAnalyzeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    image = serializer.validated_data['image']
    meal_date = serializer.validated_data.get('meal_date', datetime.now().date())
    meal_time = serializer.validated_data.get('meal_time')
    
    # Save image to storage
    filename = f"meals/{meal_date.year}/{meal_date.month:02d}/{meal_date.day:02d}/{image.name}"
    path = default_storage.save(filename, ContentFile(image.read()))
    image_url = request.build_absolute_uri(default_storage.url(path))
    
    # Read image data for OpenAI
    image.seek(0)
    image_data = image.read()
    
    # Analyze with OpenAI
    try:
        from .services import analyze_meal_image
        analysis_result = analyze_meal_image(image_data)
        
        return Response({
            'image_url': image_url,
            'foods': analysis_result['foods']
        })
    except Exception as e:
        # If analysis fails, delete the uploaded image
        default_storage.delete(path)
        return Response(
            {'message': f'Analysis failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
class MealPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# @extend_schema(
#     request=MealCreateSerializer,
#     responses={
#         200: OpenApiResponse(response=MealListSerializer(many=True), description='List of meals'),
#         201: OpenApiResponse(response=MealSerializer, description='Meal created successfully'),
#         400: OpenApiResponse(description='Invalid data')
#     },
#     tags=['Meals']
# )
# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def meals(request):
#     if request.method == 'GET':
#         meals = Meal.objects.filter(user=request.user)
        
#         paginator = MealPagination()
#         paginated_meals = paginator.paginate_queryset(meals, request)
#         serializer = MealListSerializer(paginated_meals, many=True)
        
#         return paginator.get_paginated_response(serializer.data)
    
#     elif request.method == 'POST':
#         serializer = MealCreateSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         meal = serializer.save(user=request.user)
#         return Response(MealSerializer(meal).data, status=status.HTTP_201_CREATED)

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
@extend_schema(
    parameters=[
        OpenApiParameter(name='date', description='Date in YYYY-MM-DD format', required=True, type=str)
    ],
    responses={
        200: OpenApiResponse(response=DailySummaryResponseSerializer, description='Daily meal summary with totals'),
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
    totals = calculate_daily_totals(meals_qs)
    serializer = MealSerializer(meals_qs, many=True)
    
    return Response({
        'date': date_str,
        'meals': serializer.data,
        'total_meals': meals_qs.count(),
        **totals
    })