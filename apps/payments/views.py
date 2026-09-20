from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
import uuid
import datetime

from .models import Payment
from apps.leases.models import Lease

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by lease if provided
        lease_id = self.request.GET.get('lease')
        if lease_id:
            queryset = queryset.filter(lease_id=lease_id)
            
        # Filter by date range if provided
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
            
        return queryset.order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paid_count'] = Payment.objects.filter(status='paid').count()
        context['pending_count'] = Payment.objects.filter(status='pending').count()
        context['overdue_count'] = Payment.objects.filter(status='overdue').count()
        
        # Calculate total amounts
        context['paid_amount'] = Payment.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        context['pending_amount'] = Payment.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        context['overdue_amount'] = Payment.objects.filter(status='overdue').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return context

class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payment_detail.html'
    context_object_name = 'payment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        
        # Get lease details
        context['lease'] = payment.lease
        context['property'] = payment.lease.property
        context['tenant'] = payment.lease.tenant
        
        # Get related payments for the same lease
        context['related_payments'] = Payment.objects.filter(
            lease=payment.lease
        ).exclude(id=payment.id).order_by('-payment_date')[:5]
        
        return context

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    template_name = 'payment_form.html'
    fields = ['lease', 'amount', 'payment_date', 'due_date', 'payment_type', 'payment_method', 'status']
    success_url = reverse_lazy('payments:payment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leases'] = Lease.objects.filter(status='active')
        context['title'] = 'Record New Payment'
        
        # Pre-fill lease if provided in URL
        lease_id = self.request.GET.get('lease')
        if lease_id:
            context['selected_lease'] = get_object_or_404(Lease, id=lease_id)
            
        return context
    
    def form_valid(self, form):
        # Generate a unique payment ID
        form.instance.payment_id = f"P-{uuid.uuid4().hex[:8].upper()}"
        messages.success(self.request, 'Payment recorded successfully!')
        return super().form_valid(form)

class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    template_name = 'payment_form.html'
    fields = ['amount', 'payment_date', 'due_date', 'payment_type', 'payment_method', 'status']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Payment'
        return context
    
    def get_success_url(self):
        return reverse_lazy('payments:payment_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Payment updated successfully!')
        return super().form_valid(form)

class PaymentReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/financial_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request or default to current month
        today = timezone.now().date()
        start_date = self.request.GET.get('start_date', today.replace(day=1).isoformat())
        end_date = self.request.GET.get('end_date', today.isoformat())
        
        # Convert string dates to date objects
        if isinstance(start_date, str):
            start_date = datetime.date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.date.fromisoformat(end_date)
            
        # Filter payments by date range
        payments = Payment.objects.filter(
            payment_date__gte=start_date,
            payment_date__lte=end_date
        )
        
        # Calculate summary statistics
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['total_payments'] = payments.count()
        context['total_amount'] = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Payment status breakdown
        status_summary = payments.values('status').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        context['status_summary'] = status_summary
        
        # Payment method breakdown
        method_summary = payments.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        context['method_summary'] = method_summary
        
        # Payment type breakdown
        type_summary = payments.values('payment_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        context['type_summary'] = type_summary
        
        # Monthly trend data for chart
        months = []
        amounts = []
        
        # Generate monthly data for the past 12 months
        for i in range(11, -1, -1):
            month_start = today.replace(day=1) - datetime.timedelta(days=i*30)
            month_end = (month_start.replace(month=month_start.month+1, day=1) - datetime.timedelta(days=1)) \
                if month_start.month < 12 else month_start.replace(year=month_start.year+1, month=1, day=1) - datetime.timedelta(days=1)
            
            month_total = Payment.objects.filter(
                payment_date__gte=month_start,
                payment_date__lte=month_end,
                status='paid'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            months.append(month_start.strftime('%b %Y'))
            amounts.append(float(month_total))
        
        context['chart_labels'] = months
        context['chart_data'] = amounts
        
        return context