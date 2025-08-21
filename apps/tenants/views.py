from django.views import generic as django_generic
from .models import Tenant
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy

class TenantListView(django_generic.ListView):
    model = Tenant
    template_name = 'tenants/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add filtering here if needed
        return queryset


class TenantDetailView(django_generic.DetailView):
    model = Tenant
    template_name = 'tenants/tenant_detail.html'
    context_object_name = 'tenant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add lease information
        tenant = self.get_object()
        from apps.leases.models import Lease
        context['leases'] = Lease.objects.filter(tenant=tenant)
        return context


class TenantCreateView(django_generic.CreateView):
    model = Tenant
    template_name = 'tenants/tenant_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'id_proof_type', 'id_proof_number']
    success_url = reverse_lazy('tenants:tenant_list')

    def form_valid(self, form):
        # Generate tenant_id automatically
        tenant = form.save(commit=False)
        # Format: T-YYYYMMDD-XXXX (where XXXX is a sequential number)
        import datetime
        today = datetime.date.today()
        count = Tenant.objects.filter(created_at__date=today).count() + 1
        tenant.tenant_id = f"T-{today.strftime('%Y%m%d')}-{count:04d}"
        return super().form_valid(form)


class TenantUpdateView(django_generic.UpdateView):
    model = Tenant
    template_name = 'tenants/tenant_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'id_proof_type', 'id_proof_number']
    success_url = reverse_lazy('tenants:tenant_list')