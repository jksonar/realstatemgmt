from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncYear
from .tasks import send_individual_payment_reminder, send_bulk_payment_reminders
from .models import (
    CustomUser, Property, Tenant, Lease, Payment, MaintenanceRequest
)
from .serializers import (
    UserSerializer, PropertySerializer, TenantSerializer, LeaseSerializer,
    PaymentSerializer, MaintenanceRequestSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = CustomUser.objects.filter(username=username).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a payment as paid"""
        payment = self.get_object()
        payment.status = 'paid'
        payment.payment_date = timezone.now().date()
        payment.save()
        return Response({'status': 'Payment marked as paid'})

    @action(detail=True, methods=['post'])
    def mark_overdue(self, request, pk=None):
        """Mark a payment as overdue"""
        payment = self.get_object()
        payment.status = 'overdue'
        payment.save()
        return Response({'status': 'Payment marked as overdue'})

    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Get all pending payments"""
        pending = self.queryset.filter(status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue_payments(self, request):
        """Get all overdue payments"""
        overdue = self.queryset.filter(status='overdue')
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def payments_by_status(self, request):
        """Get payment counts by status"""
        from django.db.models import Count
        status_counts = self.queryset.values('status').annotate(count=Count('id'))
        return Response(status_counts)

    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        """Bulk update payment status"""
        payment_ids = request.data.get('payment_ids', [])
        new_status = request.data.get('status')
        
        if not payment_ids or not new_status:
            return Response({'error': 'payment_ids and status are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = self.queryset.filter(id__in=payment_ids).update(status=new_status)
        return Response({'updated_count': updated_count})
    
    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send payment reminder for a specific payment"""
        payment = self.get_object()
        
        # Queue the reminder task
        task = send_individual_payment_reminder.delay(payment.id)
        
        return Response({
            'message': 'Payment reminder queued successfully',
            'task_id': task.id,
            'payment_id': payment.id
        })
    
    @action(detail=False, methods=['post'])
    def send_bulk_reminders(self, request):
        """Send payment reminders for multiple payments"""
        payment_ids = request.data.get('payment_ids', [])
        
        if not payment_ids:
            return Response(
                {'error': 'payment_ids list is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate that all payment IDs exist
        existing_payments = self.queryset.filter(id__in=payment_ids)
        if existing_payments.count() != len(payment_ids):
            return Response(
                {'error': 'Some payment IDs do not exist'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue the bulk reminder task
        task = send_bulk_payment_reminders.delay(payment_ids)
        
        return Response({
            'message': f'Bulk payment reminders queued for {len(payment_ids)} payments',
            'task_id': task.id,
            'payment_count': len(payment_ids)
        })
    
    @action(detail=False, methods=['get'])
    def reminder_candidates(self, request):
        """Get payments that are candidates for reminders"""
        # Payments due in next 7 days or overdue
        from datetime import timedelta
        upcoming_due_date = timezone.now().date() + timedelta(days=7)
        
        candidates = self.queryset.filter(
            Q(due_date__lte=upcoming_due_date) & 
            Q(status__in=['pending', 'overdue'])
        ).select_related('lease__tenant', 'lease__property')
        
        serializer = self.get_serializer(candidates, many=True)
        return Response({
            'count': candidates.count(),
            'payments': serializer.data
        })

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer


class FinancialReportingView(generics.GenericAPIView):
    """Financial reporting with Django aggregation"""
    
    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """Get revenue summary with aggregations"""
        total_revenue = Payment.objects.filter(status='paid').aggregate(
            total=Sum('amount'),
            count=Count('id'),
            average=Avg('amount')
        )
        return Response(total_revenue)
    
    @action(detail=False, methods=['get'])
    def monthly_revenue(self, request):
        """Get monthly revenue breakdown"""
        monthly_data = Payment.objects.filter(status='paid').annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            total_revenue=Sum('amount'),
            payment_count=Count('id')
        ).order_by('month')
        return Response(monthly_data)
    
    @action(detail=False, methods=['get'])
    def yearly_revenue(self, request):
        """Get yearly revenue breakdown"""
        yearly_data = Payment.objects.filter(status='paid').annotate(
            year=TruncYear('payment_date')
        ).values('year').annotate(
            total_revenue=Sum('amount'),
            payment_count=Count('id')
        ).order_by('year')
        return Response(yearly_data)
    
    @action(detail=False, methods=['get'])
    def payment_type_breakdown(self, request):
        """Get revenue breakdown by payment type"""
        type_breakdown = Payment.objects.filter(status='paid').values(
            'payment_type'
        ).annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('-total_amount')
        return Response(type_breakdown)
    
    @action(detail=False, methods=['get'])
    def outstanding_amounts(self, request):
        """Get outstanding payment amounts"""
        outstanding = Payment.objects.filter(
            Q(status='pending') | Q(status='overdue')
        ).aggregate(
            total_outstanding=Sum('amount'),
            pending_count=Count('id', filter=Q(status='pending')),
            overdue_count=Count('id', filter=Q(status='overdue'))
        )
        return Response(outstanding)
    
    @action(detail=False, methods=['get'])
    def property_revenue(self, request):
        """Get revenue breakdown by property"""
        property_revenue = Payment.objects.filter(status='paid').values(
            'lease__property__property_id',
            'lease__property__address'
        ).annotate(
            total_revenue=Sum('amount'),
            payment_count=Count('id')
        ).order_by('-total_revenue')
        return Response(property_revenue)
    
    @action(detail=False, methods=['get'])
    def financial_dashboard(self, request):
        """Comprehensive financial dashboard data"""
        # Total revenue
        total_revenue = Payment.objects.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Outstanding amounts
        outstanding = Payment.objects.filter(
            Q(status='pending') | Q(status='overdue')
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # This month's revenue
        from datetime import date
        current_month = date.today().replace(day=1)
        monthly_revenue = Payment.objects.filter(
            status='paid',
            payment_date__gte=current_month
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Payment status counts
        status_counts = Payment.objects.values('status').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_revenue': total_revenue,
            'outstanding_amount': outstanding,
            'monthly_revenue': monthly_revenue,
            'payment_status_counts': status_counts
        })
