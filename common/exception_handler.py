from rest_framework.views import exception_handler
from django.http import Http404
from rest_framework.exceptions import (
    ValidationError, 
    PermissionDenied, 
    NotAuthenticated,
    AuthenticationFailed,
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
        
        # Handle AuthenticationFailed with custom codes
        if isinstance(exc, AuthenticationFailed):
            if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
                error_data["message"] = exc.detail.get('message', 'Authentication failed')
                error_data["code"] = exc.detail.get('code', 'authentication_failed')
            else:
                error_data["message"] = str(exc.detail)
                error_data["code"] = "authentication_failed"
            
            # Set appropriate status code
            if error_data["code"] == "expired_access_token":
                response.status_code = 403
        
        elif isinstance(exc, ValidationError):
            error_data["message"] = "Validation error"
            error_data["code"] = "validation_error"
            error_data["errors"] = response.data
        
        elif isinstance(exc, NotAuthenticated):
            error_data["message"] = "Authentication credentials were not provided"
            error_data["code"] = "not_authenticated"
        
        elif isinstance(exc, PermissionDenied):
            error_data["message"] = "You do not have permission to perform this action"
            error_data["code"] = "permission_denied"
        
        elif isinstance(exc, NotFound) or isinstance(exc, Http404):
            error_data["message"] = "Resource not found"
            error_data["code"] = "not_found"
        
        elif isinstance(exc, MethodNotAllowed):
            error_data["message"] = "Method not allowed"
            error_data["code"] = "method_not_allowed"
        
        else:
            # Generic error
            if isinstance(response.data, dict):
                error_data["message"] = response.data.get('detail', 'An error occurred')
                error_data["code"] = "error"
            else:
                error_data["message"] = str(response.data)
                error_data["code"] = "error"
        
        response.data = error_data
    
    return response