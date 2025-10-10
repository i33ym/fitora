# from rest_framework import serializers
# from .models import Meal

# class MealSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Meal
#         fields = ['id', 'image', 'foods_data', 'meal_time', 'created_at', 'updated_at']
#         read_only_fields = ['id', 'created_at', 'updated_at']
    
#     def validate_foods_data(self, value):
#         if not isinstance(value, dict) or 'foods' not in value:
#             raise serializers.ValidationError("foods_data must contain a 'foods' array")
#         if not isinstance(value['foods'], list):
#             raise serializers.ValidationError("'foods' must be an array")
#         return value

# class MealCreateSerializer(serializers.ModelSerializer):
#     image = serializers.ImageField(required=False)
#     class Meta:
#         model = Meal
#         fields = ['image', 'foods_data', 'meal_time']
    
#     def validate_foods_data(self, value):
#         if not isinstance(value, dict) or 'foods' not in value:
#             raise serializers.ValidationError("foods_data must contain a 'foods' array")
#         if not isinstance(value['foods'], list):
#             raise serializers.ValidationError("'foods' must be an array")
#         return value

# class MealListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Meal
#         fields = ['id', 'image', 'meal_time', 'created_at']

from rest_framework import serializers
from .models import Meal
from datetime import date

class MealAnalyzeSerializer(serializers.Serializer):
    image = serializers.ImageField()
    meal_date = serializers.DateField(required=False, default=date.today)
    meal_time = serializers.ChoiceField(
        choices=['breakfast', 'lunch', 'dinner', 'snack'],
        required=False,
        allow_null=True
    )

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'image_url', 'meal_date', 'foods_data', 'meal_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_foods_data(self, value):
        if not isinstance(value, dict) or 'foods' not in value:
            raise serializers.ValidationError("foods_data must contain a 'foods' array")
        if not isinstance(value['foods'], list):
            raise serializers.ValidationError("'foods' must be an array")
        return value

class MealCreateSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField(max_length=500)
    class Meta:
        model = Meal
        fields = ['image_url', 'meal_date', 'foods_data', 'meal_time']
    
    def validate_foods_data(self, value):
        if not isinstance(value, dict) or 'foods' not in value:
            raise serializers.ValidationError("foods_data must contain a 'foods' array")
        if not isinstance(value['foods'], list):
            raise serializers.ValidationError("'foods' must be an array")
        return value

class MealListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'image_url', 'meal_date', 'meal_time', 'created_at']

class FoodAnalysisSerializer(serializers.Serializer):
    name = serializers.CharField()
    portion_size = serializers.CharField()
    nutritions = serializers.DictField()
    minerals = serializers.DictField()
    vitamins = serializers.DictField()
    additional = serializers.DictField()

class MealAnalysisResponseSerializer(serializers.Serializer):
    image_url = serializers.URLField()
    foods = FoodAnalysisSerializer(many=True)

class DailySummaryResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    meals = MealSerializer(many=True)
    total_meals = serializers.IntegerField()
    total_calories = serializers.CharField()
    total_carbs = serializers.CharField()
    total_fat = serializers.CharField()
    total_protein = serializers.CharField()
    total_calcium = serializers.CharField()
    total_iron = serializers.CharField()
    total_magnesium = serializers.CharField()
    total_potassium = serializers.CharField()
    total_zinc = serializers.CharField()
    total_vitamin_a = serializers.CharField()
    total_vitamin_b12 = serializers.CharField()
    total_vitamin_b9 = serializers.CharField()
    total_vitamin_c = serializers.CharField()
    total_vitamin_d = serializers.CharField()
    total_cholesterol = serializers.CharField()
    total_fiber = serializers.CharField()
    total_omega_3 = serializers.CharField()
    total_saturated_fat = serializers.CharField()
    total_sodium = serializers.CharField()