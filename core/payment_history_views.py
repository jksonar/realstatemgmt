from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer

class PaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing payment history.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all payments, filterable by tenant and property.
        """
        queryset = Payment.objects.all().order_by('-payment_date')
        tenant_id = self.request.query_params.get('tenant_id', None)
        property_id = self.request.query_params.get('property_id', None)

        if tenant_id:
            queryset = queryset.filter(lease__tenant__id=tenant_id)
        
        if property_id:
            queryset = queryset.filter(lease__property__id=property_id)
            
        return queryset