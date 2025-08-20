from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('add/', views.PropertyCreateView.as_view(), name='property_add'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_edit'),
    path('bulk-update/', views.BulkUpdatePropertiesView.as_view(), name='property_bulk_update'),
    path('compare/', views.PropertyCompareView.as_view(), name='property_compare'),
    path('csv-import-export/', views.CSVImportExportView.as_view(), name='property_csv_import_export'),
]
