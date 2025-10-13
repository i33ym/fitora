from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from users.models import User
import secrets
import string

class Dietologist(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'phone_number'
    
    class Meta:
        db_table = 'dietologists'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_superuser(self):
        return False
    
    def has_perm(self, perm, obj=None):
        return perm in [
            'dietologists.view_group',
            'dietologists.add_group',
            'dietologists.change_group',
            'dietologists.view_clientrequest',
            'dietologists.change_clientrequest',
            'users.view_user',
            'meals.view_meal',
        ]
    
    def has_module_perms(self, app_label):
        return app_label in ['dietologists', 'users', 'meals']
    
    def get_username(self):
        return self.phone_number
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

class Group(models.Model):
    dietologist = models.ForeignKey(Dietologist, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dietologist_groups'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @staticmethod
    def generate_code():
        """Generate a random 8-character code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(8))

class ClientRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dietologist_requests')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='client_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'client_requests'
        unique_together = ['user', 'group']
    
    def __str__(self):
        return f"{self.user} -> {self.group.name} ({self.status})"
