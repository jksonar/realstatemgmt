from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncYear, TruncDay
from apps.payments.models import Payment
from apps.properties.models import Property

class RevenueAnalyticsViewSet(viewsets.ViewSet):
    """
    A viewset for providing revenue analytics.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def total_revenue(self, request):
        """Get total revenue."""
        total = Payment.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        return Response({'total_revenue': total})

    @action(detail=False, methods=['get'])
    def revenue_by_property(self, request):
        """Get revenue breakdown by property."""
        data = Payment.objects.filter(status='paid') \
            .values('lease__property__address') \
            .annotate(total=Sum('amount')) \
            .order_by('-total')
        return Response(data)

    @action(detail=False, methods=['get'])
    def monthly_revenue_trend(self, request):
        """Get monthly revenue trend."""
        data = Payment.objects.filter(status='paid') \
            .annotate(month=TruncMonth('payment_date')) \
            .values('month') \
            .annotate(total=Sum('amount')) \
            .order_by('month')
        return Response(data)