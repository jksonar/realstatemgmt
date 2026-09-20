from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from apps.payments.models import Payment
from .serializers import PaymentSerializer

class OutstandingPaymentsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing and managing outstanding payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the outstanding payments
        for the currently authenticated user.
        """
        return Payment.objects.filter(Q(status='pending') | Q(status='overdue'))

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of outstanding payments."""
        queryset = self.get_queryset()
        total_outstanding = queryset.aggregate(total=Sum('amount'))['total'] or 0
        count = queryset.count()
        return Response({
            'total_outstanding': total_outstanding,
            'count': count
        })