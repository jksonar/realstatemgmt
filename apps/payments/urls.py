from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import PaymentViewSet

# Register DRF viewsets
router = DefaultRouter()
router.register(r'api/payments', PaymentViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Template-based views
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    path('payments/report/', views.PaymentReportView.as_view(), name='payment_report'),
]