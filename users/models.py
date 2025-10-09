from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField

class UserManager(BaseUserManager):
    def create_user(self, **extra_fields):
        user = self.model(**extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('profile_completed', True)
        return self.create_user(email=email, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    ACTIVENESS_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extremely_active', 'Extremely Active'),
    ]
    
    GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('maintain_weight', 'Maintain Weight'),
    ]

    MOTIVATION_CHOICES = [
        ('vocation', 'Vocation'),
        ('wedding', 'Wedding'),
        ('competetion', 'Competetion'),
        ('other', 'Other'),
        ('no', 'No'),
    ]
    
    DIET_CHOICES = [
        ('artificial_intelligence', 'Artificial Intelligence'),
        ('balanced', 'Balanced'),
        ('low_carbs', 'Low Carbs'),
        ('keto', 'Keto'),
        ('high_protein', 'High Protein'),
        ('low_fat', 'Low Fat'),
    ]

    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    fcm_token = models.TextField(null=True, blank=True)
    
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    current_height = models.FloatField(null=True, blank=True)
    current_weight = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    
    activeness_level = models.CharField(max_length=50, choices=ACTIVENESS_CHOICES, null=True, blank=True)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, null=True, blank=True)
    motivation = models.CharField(max_length=50, choices=MOTIVATION_CHOICES, blank=True, null=True)
    preferred_diet = models.CharField(max_length=50, choices=DIET_CHOICES, null=True, blank=True)
    # diet_restrictions = models.TextField(null=True, blank=True)
    diet_restrictions = ArrayField(models.CharField(max_length=100), null=True, blank=True, default=list)
    
    profile_completed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    
    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email or self.phone_number or f"User {self.id}"
    

class OTPSession(models.Model):
    session = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'otp_sessions'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.phone_number} - {self.session}"
