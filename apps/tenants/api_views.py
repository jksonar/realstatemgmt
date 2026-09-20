from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tenant
from .serializers import TenantSerializer, TenantDetailSerializer

class TenantViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tenants
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tenant_id', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TenantDetailSerializer
        return TenantSerializer
    
    @action(detail=True, methods=['get'])
    def leases(self, request, pk=None):
        """Return all leases for a tenant"""
        tenant = self.get_object()
        from apps.leases.models import Lease
        from apps.leases.serializers import LeaseSerializer
        
        leases = Lease.objects.filter(tenant=tenant)
        serializer = LeaseSerializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Return all payments associated with a tenant's leases"""
        tenant = self.get_object()
        from apps.leases.models import Lease
        from apps.payments.models import Payment
        from apps.payments.serializers import PaymentSerializer
        
        # Get all leases for this tenant
        leases = Lease.objects.filter(tenant=tenant)
        
        # Get all payments for these leases
        payments = Payment.objects.filter(lease__in=leases)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)