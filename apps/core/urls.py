from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet,
    TenantViewSet,
    LeaseViewSet,
    PaymentViewSet,
    MaintenanceRequestViewSet,
    FinancialReportingViewSet,
    BulkUpdatePropertiesView,
    AutocompleteView,
    PropertyListView,
    PropertyDetailView,
    PropertyCreateView,
    PropertyUpdateView,
    TenantCreateView,
    LeaseCreateView,
    PaymentCreateView,
    SearchInterfaceView,
    DashboardView
)
from .outstanding_payments_views import OutstandingPaymentsViewSet
from .analytics_views import RevenueAnalyticsViewSet
from .payment_history_views import PaymentHistoryViewSet
from .payment_method_views import PaymentMethodViewSet
from .dashboard_views import FinancialDashboardViewSet
from .payment_import_export_views import PaymentImportExportViewSet, PropertyImportExportViewSet
from .property_search_views import PropertySearchViewSet
from .saved_search_views import SavedSearchViewSet, FavoritePropertyViewSet, SearchHistoryViewSet
from .reporting_views import FinancialReportView, CustomReportBuilderView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'maintenance', MaintenanceRequestViewSet, basename='maintenance')
router.register(r'reports', FinancialReportingViewSet, basename='reports')
router.register(r'outstanding-payments', OutstandingPaymentsViewSet, basename='outstanding-payment')
router.register(r'analytics/revenue', RevenueAnalyticsViewSet, basename='revenue-analytics')
router.register(r'payment-history', PaymentHistoryViewSet, basename='payment-history')
router.register(r'analytics/payment-methods', PaymentMethodViewSet, basename='payment-method-analytics')
router.register(r'dashboard/financial', FinancialDashboardViewSet, basename='financial-dashboard')
router.register(r'payments/import-export', PaymentImportExportViewSet, basename='payment-import-export')
router.register(r'properties/import-export', PropertyImportExportViewSet, basename='property-import-export')
router.register(r'properties/search', PropertySearchViewSet, basename='property-search')
router.register(r'saved-searches', SavedSearchViewSet, basename='saved-search')
router.register(r'favorite-properties', FavoritePropertyViewSet, basename='favorite-property')
router.register(r'search-history', SearchHistoryViewSet, basename='search-history')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('properties/list/', PropertyListView.as_view(), name='property-list'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('properties/new/', PropertyCreateView.as_view(), name='property-create'),
    path('properties/<int:pk>/edit/', PropertyUpdateView.as_view(), name='property-update'),
    path('tenants/new/', TenantCreateView.as_view(), name='tenant-create'),
    path('leases/new/', LeaseCreateView.as_view(), name='lease-create'),
    path('payments/new/', PaymentCreateView.as_view(), name='payment-create'),
    path('search/', SearchInterfaceView.as_view(), name='search-interface'),
    path('reports/financial/', FinancialReportView.as_view(), name='financial-report'),
    path('reports/custom-builder/', CustomReportBuilderView.as_view(), name='custom-report-builder'),
    
    path('properties/bulk-update/', BulkUpdatePropertiesView.as_view(), name='bulk-update-properties'),
    path('search/autocomplete/', AutocompleteView.as_view(), name='search-autocomplete'),
    path('', include(router.urls)),
]
