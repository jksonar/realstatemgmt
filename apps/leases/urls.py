from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import LeaseViewSet

# Register DRF viewsets
router = DefaultRouter()
router.register(r'api/leases', LeaseViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Template-based views
    path('leases/', views.LeaseListView.as_view(), name='lease_list'),
    path('leases/<int:pk>/', views.LeaseDetailView.as_view(), name='lease_detail'),
    path('leases/add/', views.LeaseCreateView.as_view(), name='lease_add'),
    path('leases/<int:pk>/edit/', views.LeaseUpdateView.as_view(), name='lease_edit'),
]