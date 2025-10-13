from django.contrib.auth.backends import BaseBackend
from .models import Dietologist

class DietologistBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            dietologist = Dietologist.objects.get(phone_number=username, is_active=True)
            if dietologist.check_password(password):
                return dietologist
        except Dietologist.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return Dietologist.objects.get(pk=user_id, is_active=True)
        except Dietologist.DoesNotExist:
            return None