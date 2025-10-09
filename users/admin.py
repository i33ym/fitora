from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPSession

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'email', 'phone_number', 'profile_completed', 'is_active', 'created_at']
    list_filter = ['profile_completed', 'is_active', 'gender', 'motivation']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Authentication', {'fields': ('email', 'phone_number', 'google_id', 'password', 'fcm_token')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'date_of_birth')}),
        ('Physical Info', {'fields': ('current_height', 'current_weight', 'target_weight', 'target_date')}),
        ('Goals & Preferences', {'fields': ('activeness_level', 'goal', 'motivation', 'preferred_diet', 'diet_restrictions')}),
        ('Status', {'fields': ('profile_completed', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = []

@admin.register(OTPSession)
class OTPSessionAdmin(admin.ModelAdmin):
    list_display = ['session', 'phone_number', 'otp_code', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['phone_number', 'session']
    readonly_fields = ['session', 'created_at']
