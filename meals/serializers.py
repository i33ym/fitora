from rest_framework import serializers
from .models import Meal

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'image', 'foods_data', 'meal_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_foods_data(self, value):
        if not isinstance(value, dict) or 'foods' not in value:
            raise serializers.ValidationError("foods_data must contain a 'foods' array")
        if not isinstance(value['foods'], list):
            raise serializers.ValidationError("'foods' must be an array")
        return value

class MealCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Meal
        fields = ['image', 'foods_data', 'meal_time']
    
    def validate_foods_data(self, value):
        if not isinstance(value, dict) or 'foods' not in value:
            raise serializers.ValidationError("foods_data must contain a 'foods' array")
        if not isinstance(value['foods'], list):
            raise serializers.ValidationError("'foods' must be an array")
        return value

class MealListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'image', 'meal_time', 'created_at']