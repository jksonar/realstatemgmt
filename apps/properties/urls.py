from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = 'properties'

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'api/properties', api_views.PropertyViewSet)
router.register(r'api/favorites', api_views.FavoritePropertyViewSet, basename='favorite')

urlpatterns = [
    # Template-based views
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('add/', views.PropertyCreateView.as_view(), name='property_add'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_edit'),
    path('bulk-update/', views.BulkUpdatePropertiesView.as_view(), name='property_bulk_update'),
    path('compare/', views.PropertyCompareView.as_view(), name='property_compare'),
    path('csv-import-export/', views.CSVImportExportView.as_view(), name='property_csv_import_export'),
    path('advanced-search/', views.AdvancedSearchView.as_view(), name='advanced_search'),
    path('saved-searches/', views.SavedSearchesView.as_view(), name='saved_searches'),
    
    # API endpoints
    path('', include(router.urls)),
]
