from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.views.generic import RedirectView 
from django.conf import settings # Needed for static/media files in development

# Import all necessary ViewSets for the router
from billing.views import SubscriptionViewSet, PaymentViewSet, DataUsageViewSet, PlanActionViewSet
from plans.views import WiFiPackageViewSet # <-- Ensure this ViewSet is imported
from support.views import TicketViewSet

# Create the router instance
router = routers.DefaultRouter()

# --- 1. BILLING APP REGISTRATIONS ---
router.register(r'subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register(r'payments', PaymentViewSet, basename='payments')
# Using 'usage' instead of 'usages' to match the specific frontend request: /api/billing/usage/current/
router.register(r'usage', DataUsageViewSet, basename='usage') 
router.register(r'plan-actions', PlanActionViewSet, basename='plan-actions') 

# --- 2. SUPPORT APP REGISTRATIONS ---
router.register(r'tickets', TicketViewSet, basename='tickets')

# --- 3. PLANS APP REGISTRATIONS ---
# This registers the endpoint to fetch the list of available plans
router.register(r'wifipackages', WiFiPackageViewSet, basename='wifipackages')


# --- MAIN URL PATTERNS ---
urlpatterns = [
    # 1. ROOT PATH REDIRECT: Redirects 127.0.0.1:8000/ to the Admin login
    path('', RedirectView.as_view(url='admin/', permanent=True), name='index-redirect'), 
    
    # 2. ADMIN INTERFACE
    path('admin/', admin.site.urls),
    
    # 3. AUTHENTICATION (Users, Login, Register, Password Reset)
    path('api/auth/', include('users.urls')),
    
    # 4. API ENDPOINTS served by the DefaultRouter (Billing, Support, Plans)
    # Note: These are split for organizational clarity:
    path('api/billing/', include(router.urls)), 
    path('api/support/', include(router.urls)),
    path('api/plans/', include(router.urls)),
    
    # 5. M-PESA
    path('api/mpesa/', include('mpesa.urls')),
]

# --- DEVELOPMENT STATIC/MEDIA FILE SERVING ---
# This block is only for development and helps serve static/media files
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)