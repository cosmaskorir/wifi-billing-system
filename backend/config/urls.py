from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect # Import this

# Function to redirect root URL to dashboard
def root_redirect(request):
    return redirect('/api/dashboard/')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Add this line at the top to handle the homepage:
    path('', root_redirect, name='root'),

    # ... your existing API paths ...
    path('api/auth/', include('rest_framework.urls')), 
    # (Note: I'm assuming you have the other includes here from previous steps)
    path('api/users/', include('users.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/mpesa/', include('mpesa.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]