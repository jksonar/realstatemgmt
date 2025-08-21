from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import Payment
from .serializers import PaymentSerializer, PaymentDetailSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing payments
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lease', 'payment_type', 'payment_method', 'status', 'payment_date', 'due_date']
    search_fields = ['payment_id', 'lease__lease_id']
    ordering_fields = ['payment_date', 'due_date', 'amount', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return PaymentDetailSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        # Generate a unique payment ID if not provided
        if not serializer.validated_data.get('payment_id'):
            payment_id = f"P-{uuid.uuid4().hex[:8].upper()}"
            serializer.save(payment_id=payment_id)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Return overdue payments
        """
        today = timezone.now().date()
        overdue_payments = self.get_queryset().filter(
            status__in=['pending', 'overdue'],
            due_date__lt=today
        )
        page = self.paginate_queryset(overdue_payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Return upcoming payments due in the next 30 days
        """
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        upcoming_payments = self.get_queryset().filter(
            status='pending',
            due_date__gte=today,
            due_date__lte=thirty_days_later
        )
        page = self.paginate_queryset(upcoming_payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(upcoming_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark a payment as paid
        """
        payment = self.get_object()
        
        if payment.status == 'paid':
            return Response(
                {'error': 'Payment is already marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update payment status
        payment.status = 'paid'
        payment.payment_date = request.data.get('payment_date', timezone.now().date())
        payment.payment_method = request.data.get('payment_method', payment.payment_method)
        payment.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Return payment summary statistics
        """
        from django.db.models import Sum, Count
        
        # Get query parameters for filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Base queryset
        queryset = self.get_queryset()
        
        # Apply date filters if provided
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        # Calculate summary statistics
        summary = {
            'total_payments': queryset.filter(status='paid').count(),
            'total_amount_paid': queryset.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0,
            'pending_payments': queryset.filter(status='pending').count(),
            'pending_amount': queryset.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0,
            'overdue_payments': queryset.filter(status='overdue').count(),
            'overdue_amount': queryset.filter(status='overdue').aggregate(Sum('amount'))['amount__sum'] or 0,
        }
        
        # Add payment method breakdown
        payment_methods = queryset.filter(status='paid').values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        summary['payment_methods'] = payment_methods
        
        return Response(summary)