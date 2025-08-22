from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import MaintenanceRequestViewSet

# Register DRF viewsets
router = DefaultRouter()
router.register(r'api/maintenance', MaintenanceRequestViewSet)

app_name = 'maintenance'

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Template-based views
    path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenance/<int:pk>/', views.MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('maintenance/add/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.MaintenanceUpdateView.as_view(), name='maintenance_edit'),
]