# backend/config/views.py
from django.http import JsonResponse

def api_root_view(request):
    """
    Returns a simple JSON response confirming the API is running.
    """
    return JsonResponse({
        "message": "ISP Customer Portal API is running.",
        "version": "1.0",
        "endpoints": [
            "/admin/",
            "/api/auth/",
            "/api/billing/",
            "/api/support/",
            "/api/mpesa/",
        ]
    })