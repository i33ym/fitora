from django.db import models
from users.models import User
from django.utils import timezone

class Meal(models.Model):
    MEAL_TIME_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    image_url = models.ImageField(upload_to='meals/%Y/%m/%d/')
    meal_date = models.DateField(default=timezone.now)
    foods_data = models.JSONField()
    meal_time = models.CharField(max_length=20, choices=MEAL_TIME_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meals'
        ordering = ['-meal_date', '-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
