from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WifiPackageViewSet

router = DefaultRouter()

# Register the endpoint
# URL becomes: /api/plans/packages/
router.register(r'packages', WifiPackageViewSet, basename='wifipackage')

urlpatterns = [
    path('', include(router.urls)),
]