from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # --- Admin Panel ---
    path('admin/', admin.site.urls),

    # --- Authentication (Login/Refresh) ---
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- App URLs ---
    path('api/users/', include('users.urls')),      # Connects to the file above
    path('api/billing/', include('billing.urls')),  # Your billing app
    # path('api/routers/', include('routers.urls')), # Uncomment if you have this app
]

# Serve static files in development (WhiteNoise handles this in production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)