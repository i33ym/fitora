from django.http import JsonResponse

def handler404(request, exception=None):
    """
    Custom 404 handler
    """
    return JsonResponse({
        "success": False,
        "message": "Resource not found"
    }, status=404)

def handler405(request, exception=None):
    """
    Custom 405 handler
    """
    return JsonResponse({
        "success": False,
        "message": "Method not allowed"
    }, status=405)

def handler500(request):
    """
    Custom 500 handler
    """
    return JsonResponse({
        "success": False,
        "message": "Internal server error"
    }, status=500)
