from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import LeaseViewSet

# Register DRF viewsets
router = DefaultRouter()
router.register(r'api/leases', LeaseViewSet)

app_name = 'leases'

urlpatterns = [
    # Template-based views
    path('', views.LeaseListView.as_view(), name='lease_list'),
    path('<int:pk>/', views.LeaseDetailView.as_view(), name='lease_detail'),
    path('add/', views.LeaseCreateView.as_view(), name='lease_add'),
    path('<int:pk>/edit/', views.LeaseUpdateView.as_view(), name='lease_edit'),
    
    # API endpoints - moved to the end to prioritize template views
    path('api/', include(router.urls)),
]