from rest_framework.views import exception_handler
from django.http import Http404
from rest_framework.exceptions import (
    ValidationError, 
    PermissionDenied, 
    NotAuthenticated,
    MethodNotAllowed,
    NotFound
)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            "success": False,
        }
        
        if isinstance(exc, ValidationError):
            error_data["message"] = "Validation error"
            error_data["errors"] = response.data
        elif isinstance(exc, NotAuthenticated):
            error_data["message"] = "Authentication credentials were not provided"
        elif isinstance(exc, PermissionDenied):
            error_data["message"] = "You do not have permission to perform this action"
        elif isinstance(exc, NotFound) or isinstance(exc, Http404):
            error_data["message"] = "Resource not found"
        elif isinstance(exc, MethodNotAllowed):
            error_data["message"] = f"Method not allowed"
        else:
            if isinstance(response.data, dict):
                error_data["message"] = response.data.get('detail', 'An error occurred')
                if len(response.data) > 1:
                    error_data["errors"] = {k: v for k, v in response.data.items() if k != 'detail'}
            else:
                error_data["message"] = str(response.data)
        
        response.data = error_data
    
    return response