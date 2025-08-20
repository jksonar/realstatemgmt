from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from apps.payments.models import Payment

class PaymentMethodViewSet(viewsets.ViewSet):
    """
    A viewset for providing analytics on payment methods.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def usage_summary(self, request):
        """Get a summary of payment method usage."""
        data = Payment.objects.values('payment_method') \
            .annotate(count=Count('id')) \
            .order_by('-count')
        return Response(data)