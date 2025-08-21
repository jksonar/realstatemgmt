from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
import uuid

from .models import Lease
from apps.properties.models import Property
from apps.tenants.models import Tenant
from apps.payments.models import Payment

class LeaseListView(LoginRequiredMixin, ListView):
    model = Lease
    template_name = 'lease_list.html'
    context_object_name = 'leases'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by property if provided
        property_id = self.request.GET.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
            
        # Filter by tenant if provided
        tenant_id = self.request.GET.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_count'] = Lease.objects.filter(status='active').count()
        context['expired_count'] = Lease.objects.filter(status='expired').count()
        context['terminated_count'] = Lease.objects.filter(status='terminated').count()
        return context

class LeaseDetailView(LoginRequiredMixin, DetailView):
    model = Lease
    template_name = 'lease_detail.html'
    context_object_name = 'lease'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lease = self.get_object()
        
        # Get related payments
        context['payments'] = Payment.objects.filter(lease=lease).order_by('-payment_date')
        
        # Calculate lease financial summary
        total_paid = sum(payment.amount for payment in context['payments'])
        total_expected = lease.monthly_rent * ((lease.end_date.year - lease.start_date.year) * 12 + 
                                             lease.end_date.month - lease.start_date.month)
        
        context['total_paid'] = total_paid
        context['total_expected'] = total_expected
        context['balance'] = total_expected - total_paid
        
        return context

class LeaseCreateView(LoginRequiredMixin, CreateView):
    model = Lease
    template_name = 'lease_form.html'
    fields = ['property', 'tenant', 'start_date', 'end_date', 'monthly_rent', 'security_deposit', 'status']
    success_url = reverse_lazy('lease_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.all()
        context['tenants'] = Tenant.objects.all()
        context['title'] = 'Add New Lease'
        return context
    
    def form_valid(self, form):
        # Generate a unique lease ID
        form.instance.lease_id = f"L-{uuid.uuid4().hex[:8].upper()}"
        messages.success(self.request, 'Lease created successfully!')
        return super().form_valid(form)

class LeaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Lease
    template_name = 'lease_form.html'
    fields = ['start_date', 'end_date', 'monthly_rent', 'security_deposit', 'status']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Lease'
        return context
    
    def get_success_url(self):
        return reverse_lazy('lease_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Lease updated successfully!')
        return super().form_valid(form)