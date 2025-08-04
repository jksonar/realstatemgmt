from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, UserProfileView, PropertyViewSet, TenantViewSet, 
    LeaseViewSet, PaymentViewSet, MaintenanceRequestViewSet, FinancialReportingView
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
    path('reports/revenue-summary/', FinancialReportingView.as_view({'get': 'revenue_summary'}), name='revenue-summary'),
    path('reports/monthly-revenue/', FinancialReportingView.as_view({'get': 'monthly_revenue'}), name='monthly-revenue'),
    path('reports/yearly-revenue/', FinancialReportingView.as_view({'get': 'yearly_revenue'}), name='yearly-revenue'),
    path('reports/payment-type-breakdown/', FinancialReportingView.as_view({'get': 'payment_type_breakdown'}), name='payment-type-breakdown'),
    path('reports/outstanding-amounts/', FinancialReportingView.as_view({'get': 'outstanding_amounts'}), name='outstanding-amounts'),
    path('reports/property-revenue/', FinancialReportingView.as_view({'get': 'property_revenue'}), name='property-revenue'),
    path('reports/dashboard/', FinancialReportingView.as_view({'get': 'financial_dashboard'}), name='financial-dashboard'),
    path('', include(router.urls)),
]
