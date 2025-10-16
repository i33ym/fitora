from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import Meal
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .serializers import (
    MealSerializer, MealCreateSerializer, MealListSerializer, 
    MealAnalyzeSerializer, VoiceAnalyzeSerializer
)
from django.utils.translation import gettext as _
from common.responses import success_response, error_response

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
        if not value_str:
            return 0.0
        try:
            value_str = str(value_str)
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

                nutritions = food.get('nutritions', {})
                if isinstance(nutritions, dict):
                    totals['calories'] += parse_value(nutritions.get('calories', '0'))
                    totals['carbs'] += parse_value(nutritions.get('carbs', '0'))
                    totals['fat'] += parse_value(nutritions.get('fat', '0'))
                    totals['protein'] += parse_value(nutritions.get('protein', '0'))

                minerals = food.get('minerals', {})
                if isinstance(minerals, dict):
                    totals['calcium'] += parse_value(minerals.get('calcium', '0'))
                    totals['iron'] += parse_value(minerals.get('iron', '0'))
                    totals['magnesium'] += parse_value(minerals.get('magnesium', '0'))
                    totals['potassium'] += parse_value(minerals.get('potassium', '0'))
                    totals['zinc'] += parse_value(minerals.get('zinc', '0'))

                vitamins = food.get('vitamins', {})
                if isinstance(vitamins, dict):
                    totals['vitamin_a'] += parse_value(vitamins.get('vitamin_a', '0'))
                    totals['vitamin_b12'] += parse_value(vitamins.get('vitamin_b12', '0'))
                    totals['vitamin_b9'] += parse_value(vitamins.get('vitamin_b9', '0'))
                    totals['vitamin_c'] += parse_value(vitamins.get('vitamin_c', '0'))
                    totals['vitamin_d'] += parse_value(vitamins.get('vitamin_d', '0'))

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_meal(request):
    serializer = MealAnalyzeSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    image = serializer.validated_data['image']
    meal_date = serializer.validated_data.get('meal_date', datetime.now().date())
    meal_time = serializer.validated_data.get('meal_time')

    filename = f"meals/{meal_date.year}/{meal_date.month:02d}/{meal_date.day:02d}/{image.name}"
    path = default_storage.save(filename, ContentFile(image.read()))
    image_url = request.build_absolute_uri(default_storage.url(path))

    image.seek(0)
    image_data = image.read()

    try:
        from .services import analyze_meal_image
        analysis_result = analyze_meal_image(image_data)
        
        return success_response(
            data={
                'image_url': image_url,
                'foods': analysis_result['foods']
            }
        )
    except Exception as e:
        default_storage.delete(path)
        return error_response(
            message=_('Analysis failed'),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_voice(request):
    from django.utils.translation import get_language_from_request
    
    serializer = VoiceAnalyzeSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            message=_('Validation error'),
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    audio = serializer.validated_data['audio']
    meal_date = serializer.validated_data.get('meal_date', datetime.now().date())
    meal_time = serializer.validated_data.get('meal_time')
    language = serializer.validated_data.get('language') or get_language_from_request(request)
    
    filename = f"meals/audio/{meal_date.year}/{meal_date.month:02d}/{meal_date.day:02d}/{audio.name}"
    path = default_storage.save(filename, ContentFile(audio.read()))
    audio_url = request.build_absolute_uri(default_storage.url(path))
    
    audio.seek(0)
    audio_data = audio.read()
    
    try:
        from .services import analyze_meal_voice
        analysis_result = analyze_meal_voice(audio_data, language)
        
        return success_response(
            data={
                'transcription': analysis_result.get('transcription', ''),
                'audio_url': audio_url,
                'foods': analysis_result['foods']
            }
        )
    except Exception as e:
        default_storage.delete(path)
        return error_response(
            message=_('Analysis failed: ') + str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
class MealPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def meals(request):
    if request.method == 'GET':
        meals_qs = Meal.objects.filter(user=request.user)
        
        paginator = MealPagination()
        paginated_meals = paginator.paginate_queryset(meals_qs, request)
        serializer = MealListSerializer(paginated_meals, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MealCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message=_('Validation error'),
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        meal = serializer.save(user=request.user)
        return success_response(
            data=MealSerializer(meal, context={'request': request}).data,
            status_code=status.HTTP_201_CREATED
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def meal_detail(request, pk):
    meal = get_object_or_404(Meal, pk=pk, user=request.user)
    
    if request.method == 'GET':
        serializer = MealSerializer(meal, context={'request': request})
        return success_response(data=serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = MealSerializer(meal, data=request.data, partial=(request.method == 'PATCH'), context={'request': request})
        
        if not serializer.is_valid():
            return error_response(
                message=_('Validation error'),
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return success_response(data=serializer.data)
    
    elif request.method == 'DELETE':
        meal.delete()
        return success_response(
            message=_('Meal deleted successfully'),
            status_code=status.HTTP_204_NO_CONTENT
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_summary(request):
    date_str = request.query_params.get('date')
    
    if not date_str:
        return error_response(
            message=_('Date parameter is required'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return error_response(
            message=_('Invalid date format. Use YYYY-MM-DD'),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    meals_qs = Meal.objects.filter(
        user=request.user,
        meal_date=date_obj
    )
    totals = calculate_daily_totals(meals_qs)
    serializer = MealSerializer(meals_qs, many=True, context={'request': request})
    
    return success_response(
        data={
            'date': date_str,
            'meals': serializer.data,
            'total_meals': meals_qs.count(),
            **totals
        }
    )