from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView  # <--- Import this
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # --- 1. Redirect Root URL ('') to Admin Panel ---
    path('', RedirectView.as_view(url='/admin/')), 

    # --- Admin Panel ---
    path('admin/', admin.site.urls),

    # --- Authentication (Login/Refresh) ---
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- App URLs ---
    path('api/users/', include('users.urls')),
    path('api/billing/', include('billing.urls')),
    # path('api/routers/', include('routers.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)