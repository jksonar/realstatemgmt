from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from .models import Payment, Property, Tenant, Lease

class FinancialDashboardViewSet(viewsets.ViewSet):
    """
    A viewset for providing data to the financial dashboard.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of financial data."""
        total_revenue = Payment.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        outstanding_payments = Payment.objects.filter(Q(status='pending') | Q(status='overdue')).aggregate(total=Sum('amount'))['total'] or 0
        active_leases = Lease.objects.filter(status='active').count()
        occupied_properties = Property.objects.filter(status='occupied').count()

        return Response({
            'total_revenue': total_revenue,
            'outstanding_payments': outstanding_payments,
            'active_leases': active_leases,
            'occupied_properties': occupied_properties
        })