from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
import uuid

from .models import MaintenanceRequest
from apps.properties.models import Property
from apps.tenants.models import Tenant

class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceRequest
    template_name = 'maintenance_list.html'
    context_object_name = 'maintenance_requests'
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
            
        # Filter by priority if provided
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        return queryset.order_by('-priority', '-reported_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reported_count'] = MaintenanceRequest.objects.filter(status='reported').count()
        context['in_progress_count'] = MaintenanceRequest.objects.filter(status='in_progress').count()
        context['completed_count'] = MaintenanceRequest.objects.filter(status='completed').count()
        context['urgent_count'] = MaintenanceRequest.objects.filter(priority='urgent', status__in=['reported', 'in_progress']).count()
        return context

class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRequest
    template_name = 'maintenance_detail.html'
    context_object_name = 'maintenance_request'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        maintenance_request = self.get_object()
        
        # Get property and tenant details
        context['property'] = maintenance_request.property
        if maintenance_request.tenant:
            context['tenant'] = maintenance_request.tenant
        
        # Get related maintenance requests for the same property
        context['related_requests'] = MaintenanceRequest.objects.filter(
            property=maintenance_request.property
        ).exclude(id=maintenance_request.id).order_by('-reported_date')[:5]
        
        return context

class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRequest
    template_name = 'maintenance_form.html'
    fields = ['property', 'tenant', 'issue_type', 'description', 'priority', 'status', 'assigned_to']
    success_url = reverse_lazy('maintenance_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.all()
        context['tenants'] = Tenant.objects.all()
        context['title'] = 'Create Maintenance Request'
        
        # Pre-fill property and tenant if provided in URL
        property_id = self.request.GET.get('property')
        if property_id:
            context['selected_property'] = get_object_or_404(Property, id=property_id)
            
        tenant_id = self.request.GET.get('tenant')
        if tenant_id:
            context['selected_tenant'] = get_object_or_404(Tenant, id=tenant_id)
            
        return context
    
    def form_valid(self, form):
        # Generate a unique request ID
        form.instance.request_id = f"MR-{uuid.uuid4().hex[:8].upper()}"
        
        # Set reported_date to current time
        form.instance.reported_date = timezone.now()
        
        messages.success(self.request, 'Maintenance request created successfully!')
        return super().form_valid(form)

class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRequest
    template_name = 'maintenance_form.html'
    fields = ['issue_type', 'description', 'priority', 'status', 'assigned_to', 'cost', 'completed_date']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Maintenance Request'
        return context
    
    def get_success_url(self):
        return reverse_lazy('maintenance_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # If status is changed to completed and completed_date is not set, set it to now
        if form.instance.status == 'completed' and not form.instance.completed_date:
            form.instance.completed_date = timezone.now()
            
        messages.success(self.request, 'Maintenance request updated successfully!')
        return super().form_valid(form)