from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Dietologist, Group, ClientRequest
from users.models import User
from meals.models import Meal

@admin.register(Dietologist)
class DietologistAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['phone_number', 'first_name', 'last_name']
    
    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            if form.cleaned_data.get('password'):
                obj.set_password(form.cleaned_data['password'])
        obj.save()
    
    def has_module_permission(self, request):
        # Only superusers can manage dietologists
        return request.user.is_superuser

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'dietologist', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'dietologist__first_name', 'dietologist__last_name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Dietologists only see their own groups
        if isinstance(request.user, Dietologist):
            return qs.filter(dietologist=request.user)
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        if not change and isinstance(request.user, Dietologist):
            obj.dietologist = request.user
        obj.save()

@admin.register(ClientRequest)
class ClientRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'group', 'status', 'requested_at', 'responded_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['user__email', 'user__phone_number', 'group__name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Dietologists only see requests for their groups
        if isinstance(request.user, Dietologist):
            return qs.filter(group__dietologist=request.user)
        return qs.none()

# Register User as read-only for dietologists
class UserReadOnlyAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number', 'first_name', 'last_name', 'profile_completed']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Dietologists see only their approved clients
        if isinstance(request.user, Dietologist):
            approved_requests = ClientRequest.objects.filter(
                group__dietologist=request.user,
                status='approved'
            ).values_list('user_id', flat=True)
            return qs.filter(id__in=approved_requests)
        return qs.none()
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Register Meal as read-only for dietologists
class MealReadOnlyAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'meal_date', 'meal_time', 'created_at']
    list_filter = ['meal_date', 'meal_time']
    search_fields = ['user__email', 'user__phone_number']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Dietologists see meals of their approved clients
        if isinstance(request.user, Dietologist):
            approved_requests = ClientRequest.objects.filter(
                group__dietologist=request.user,
                status='approved'
            ).values_list('user_id', flat=True)
            return qs.filter(user_id__in=approved_requests)
        return qs.none()
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Unregister and re-register User and Meal if already registered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Meal)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserReadOnlyAdmin)
admin.site.register(Meal, MealReadOnlyAdmin)