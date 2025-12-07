from django.urls import path
from .views import dashboard_landing

urlpatterns = [
    # GET /api/dashboard/ -> Shows the HTML Admin Page
    path('', dashboard_landing, name='dashboard_landing'),
]