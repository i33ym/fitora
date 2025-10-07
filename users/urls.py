from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('sms/send-otp', views.send_otp, name='send-otp'),
    path('sms/verify-otp', views.verify_otp, name='verify-otp'),
    path('auth/google', views.google_auth, name='google-auth'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('user/profile', views.profile, name='profile'),
]