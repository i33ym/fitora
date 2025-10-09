from rest_framework import serializers
from .models import User
from datetime import date

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    session = serializers.UUIDField()
    otp = serializers.CharField(max_length=6)
    phone_number = serializers.CharField(max_length=15)
    fcm_token = serializers.CharField()

class GoogleAuthSerializer(serializers.Serializer):
    google_token = serializers.CharField()
    fcm_token = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'first_name', 'last_name', 
            'gender', 'date_of_birth', 'current_height', 'current_weight',
            'target_weight', 'target_date', 'activeness_level', 'goal', 'motivation',
            'preferred_diet', 'diet_restrictions', 'profile_completed'
        ]
        read_only_fields = ['id', 'email', 'phone_number', 'profile_completed']
    
    def validate_date_of_birth(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise serializers.ValidationError("User must be at least 13 years old.")
        return value
    
    def validate_target_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError("Target date must be in the future.")
        return value
    
    def validate(self, data):
        if data.get('current_weight') and data.get('target_weight'):
            if data['current_weight'] <= 0 or data['target_weight'] <= 0:
                raise serializers.ValidationError("Weight values must be positive.")
        if data.get('current_height') and data['current_height'] <= 0:
            raise serializers.ValidationError("Height must be positive.")
        return data

class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'current_height', 'current_weight', 'target_weight', 'target_date',
            'activeness_level', 'goal', 'motivation', 'preferred_diet', 'diet_restrictions'
        ]
    
    def validate_date_of_birth(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise serializers.ValidationError("User must be at least 13 years old.")
        return value
    
    def validate_target_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError("Target date must be in the future.")
        return value
    
    def validate(self, data):
        if data['current_weight'] <= 0 or data['target_weight'] <= 0:
            raise serializers.ValidationError("Weight values must be positive.")
        if data['current_height'] <= 0:
            raise serializers.ValidationError("Height must be positive.")
        return data