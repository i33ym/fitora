from rest_framework import serializers
from .models import Meal
from datetime import date
from django.utils.translation import gettext_lazy as _

class MealAnalyzeSerializer(serializers.Serializer):
    image = serializers.ImageField()
    meal_date = serializers.DateField(required=False, default=date.today)
    meal_time = serializers.ChoiceField(
        choices=['breakfast', 'lunch', 'dinner', 'snack'],
        required=False,
        allow_null=True
    )

class VoiceAnalyzeSerializer(serializers.Serializer):
    audio = serializers.FileField()
    meal_date = serializers.DateField(required=False, default=date.today)
    meal_time = serializers.ChoiceField(
        choices=['breakfast', 'lunch', 'dinner', 'snack'],
        required=False,
        allow_null=True
    )
    language = serializers.ChoiceField(
        choices=['en', 'uz', 'uz-cyrl', 'ru'],
        required=False,
        default='uz'
    )
    
    def validate_audio(self, value):
        # Check file extension
        if not value.name.endswith('.wav'):
            raise serializers.ValidationError(_("Only WAV audio files are supported"))
        
        # Check file size (25MB limit for Whisper, but we limit to 10MB for 45 seconds)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(_("Audio file too large. Maximum 10MB allowed"))
        
        return value

class MealSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Meal
        fields = ['id', 'image_url', 'meal_date', 'foods_data', 'meal_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if not obj.image_url:
            return None
        
        url = str(obj.image_url)

        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image_url)
        
        return url
    
    def validate_foods_data(self, value):
        if not isinstance(value, dict) or 'foods' not in value:
            raise serializers.ValidationError(_("foods_data must contain a 'foods' array"))
        if not isinstance(value['foods'], list):
            raise serializers.ValidationError(_("'foods' must be an array"))
        return value

class MealCreateSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(required=True)
    
    class Meta:
        model = Meal
        fields = ['image_url', 'meal_date', 'foods_data', 'meal_time']
    
    def validate_foods_data(self, value):
        if not isinstance(value, dict) or 'foods' not in value:
            raise serializers.ValidationError(_("foods_data must contain a 'foods' array"))
        if not isinstance(value['foods'], list):
            raise serializers.ValidationError(_("'foods' must be an array"))
        return value

class MealListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Meal
        fields = ['id', 'image_url', 'meal_date', 'meal_time', 'created_at']
    
    def get_image_url(self, obj):
        if not obj.image_url:
            return None
        
        url = str(obj.image_url)
        
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image_url)
        
        return url

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

class VoiceAnalysisResponseSerializer(serializers.Serializer):
    transcription = serializers.CharField()
    audio_url = serializers.URLField()
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