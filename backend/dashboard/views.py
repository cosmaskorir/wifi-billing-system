from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Sum

# Import models safely (in case you haven't migrated yet)
try:
    from billing.models import Payment
    from users.models import User
except ImportError:
    pass

def dashboard_landing(request):
    """
    Serves the HTML Admin Dashboard.
    """
    return render(request, 'index.html')

@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """
    API Endpoint to fetch stats for the React/JS dashboard.
    """
    # Default values
    total_users = 0
    total_revenue = 0
    
    # Try to fetch real data
    try:
        total_users = User.objects.filter(role='CUSTOMER').count()
        revenue_data = Payment.objects.filter(status='COMPLETED').aggregate(Sum('amount'))
        total_revenue = revenue_data['amount__sum'] or 0
    except Exception:
        pass

    return Response({
        "total_users": total_users,
        "total_revenue": total_revenue,
        "status": "online"
    })