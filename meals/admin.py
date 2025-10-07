from django.contrib import admin
from .models import Meal

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'meal_time', 'created_at']
    list_filter = ['meal_time', 'created_at']
    search_fields = ['user__email', 'user__phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Meal Info', {'fields': ('user', 'image', 'meal_time')}),
        ('Nutritional Data', {'fields': ('foods_data',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
