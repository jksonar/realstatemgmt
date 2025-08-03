from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, UserProfileView, PropertyViewSet, TenantViewSet, 
    LeaseViewSet, PaymentViewSet, MaintenanceRequestViewSet
)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'maintenance', MaintenanceRequestViewSet, basename='maintenance')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
