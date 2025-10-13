from django.urls import path
from . import views

urlpatterns = [
    path('dietologist/auth/login', views.dietologist_login, name='dietologist-login'),
    path('dietologist/groups', views.create_group, name='create-group'),
    path('dietologist/groups', views.list_groups, name='list-groups'),
    path('dietologist/groups/<int:pk>', views.update_group, name='update-group'),
    path('dietologist/requests', views.pending_requests, name='pending-requests'),
    path('dietologist/requests/<int:pk>/approve', views.approve_request, name='approve-request'),
    path('dietologist/requests/<int:pk>/reject', views.reject_request, name='reject-request'),
    path('dietologist/clients', views.list_clients, name='list-clients'),
    path('dietologist/clients/<int:user_id>', views.client_detail, name='client-detail'),
    path('user/request-dietologist', views.request_dietologist, name='request-dietologist'),
]