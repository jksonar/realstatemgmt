from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import MaintenanceRequestViewSet

# Register DRF viewsets
router = DefaultRouter()
router.register(r'api/maintenance', MaintenanceRequestViewSet)

app_name = 'maintenance'

urlpatterns = [
    # Template-based views
    path('', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('<int:pk>/', views.MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('add/', views.MaintenanceCreateView.as_view(), name='maintenance_add'),
    path('<int:pk>/edit/', views.MaintenanceUpdateView.as_view(), name='maintenance_edit'),
    
    # API endpoints
    path('api/', include(router.urls)),
]