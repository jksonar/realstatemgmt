from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = 'tenants'

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'api', api_views.TenantViewSet)

urlpatterns = [
    # Template-based views
    path('', views.TenantListView.as_view(), name='tenant_list'),
    path('<int:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    path('add/', views.TenantCreateView.as_view(), name='tenant_add'),
    path('<int:pk>/edit/', views.TenantUpdateView.as_view(), name='tenant_edit'),
    path('<int:pk>/documents/', views.TenantDocumentUploadView.as_view(), name='tenant_documents'),
    path('<int:pk>/documents/<int:document_pk>/delete/', views.TenantDocumentDeleteView.as_view(), name='tenant_document_delete'),
    
    # API endpoints
    path('', include(router.urls)),
]