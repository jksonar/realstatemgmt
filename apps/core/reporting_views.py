from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.payments.models import Payment
from apps.properties.models import Property
from apps.tenants.models import Tenant
from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from .forms import ReportBuilderForm, REPORTABLE_MODELS

class FinancialReportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        payments = Payment.objects.all()
        properties = Property.objects.all()
        tenants = Tenant.objects.all()

        paid_payments_count = payments.filter(status='paid').count()
        pending_payments_count = payments.filter(status='pending').count()
        overdue_payments_count = payments.filter(status='overdue').count()

        context = {
            'payments': payments,
            'properties': properties,
            'tenants': tenants,
            'total_revenue': sum(p.amount for p in payments if p.status == 'paid'),
            'outstanding_payments': sum(p.amount for p in payments if p.status in ['pending', 'overdue']),
            'active_leases': sum(1 for t in tenants if t.lease_set.filter(status='active').exists()),
            'paid_payments_count': paid_payments_count,
            'pending_payments_count': pending_payments_count,
            'overdue_payments_count': overdue_payments_count,
        }
        return render(request, 'reports/financial_report.html', context)

class CustomReportBuilderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ReportBuilderForm()
        return render(request, 'reports/custom_report_builder.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ReportBuilderForm(request.POST)
        if form.is_valid():
            model_name = form.cleaned_data['model_choice']
            fields = form.cleaned_data['fields']
            model = REPORTABLE_MODELS[model_name]
            queryset = model.objects.all()
            
            if not fields:
                fields = [field.name for field in model._meta.fields]

            context = {
                'form': form,
                'queryset': queryset,
                'fields': fields,
                'model_name': model_name.replace('_', ' ').title(),
            }
            return render(request, 'reports/custom_report_builder.html', context)
        
        return render(request, 'reports/custom_report_builder.html', {'form': form})