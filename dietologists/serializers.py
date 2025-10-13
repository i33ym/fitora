from rest_framework import serializers
from .models import Dietologist, Group, ClientRequest
from users.serializers import UserProfileSerializer
from meals.serializers import MealSerializer

class DietologistLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class GroupCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=False)
    
    class Meta:
        model = Group
        fields = ['name', 'code']
    
    def validate_code(self, value):
        if value and Group.objects.filter(code=value).exists():
            raise serializers.ValidationError("This code is already in use")
        return value

class UserBasicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.CharField()
    date_of_birth = serializers.DateField()

class ClientRequestSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = ClientRequest
        fields = ['id', 'user', 'group_name', 'status', 'requested_at', 'responded_at']

class ClientDetailSerializer(serializers.Serializer):
    profile = UserProfileSerializer()
    meals = MealSerializer(many=True)
    total_meals = serializers.IntegerField()

class RequestDietologistSerializer(serializers.Serializer):
    group_code = serializers.CharField()