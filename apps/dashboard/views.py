from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.properties.models import Property
from apps.tenants.models import Tenant
from apps.leases.models import Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest

@login_required
def dashboard(request):
    # Get current date
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Property statistics
    property_count = Property.objects.count()
    occupied_count = Property.objects.filter(status='occupied').count()
    vacant_count = Property.objects.filter(status='vacant').count()
    maintenance_count = Property.objects.filter(status='maintenance').count()
    
    # Calculate percentages
    occupied_percentage = round((occupied_count / property_count) * 100) if property_count > 0 else 0
    vacant_percentage = round((vacant_count / property_count) * 100) if property_count > 0 else 0
    maintenance_property_percentage = round((maintenance_count / property_count) * 100) if property_count > 0 else 0
    
    # Tenant statistics
    tenant_count = Tenant.objects.count()
    
    # Lease statistics
    active_lease_count = Lease.objects.filter(status='active').count()
    
    # Get leases expiring in the next 90 days
    expiring_date = today + timedelta(days=90)
    expiring_leases = Lease.objects.filter(
        status='active',
        end_date__range=[today, expiring_date]
    ).select_related('property', 'tenant').order_by('end_date')[:5]
    
    # Add days remaining to each lease
    for lease in expiring_leases:
        lease.days_remaining = (lease.end_date - today).days
    
    # Maintenance statistics
    open_maintenance_count = MaintenanceRequest.objects.filter(
        Q(status='open') | Q(status='in_progress')
    ).count()
    
    recent_maintenance = MaintenanceRequest.objects.select_related('property')\
        .order_by('-reported_date')[:5]
    
    # Payment statistics
    total_revenue = Payment.objects.filter(
        status='paid',
        payment_date__range=[first_day_of_month, last_day_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_payments = Payment.objects.filter(
        status='pending',
        due_date__range=[first_day_of_month, last_day_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    overdue_payments = Payment.objects.filter(
        status='overdue',
        due_date__lt=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    maintenance_expenses = MaintenanceRequest.objects.filter(
        status='completed',
        completed_date__range=[first_day_of_month, last_day_of_month]
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    # Calculate percentages for financial summary
    total_expected = total_revenue + pending_payments + overdue_payments
    pending_percentage = round((pending_payments / total_expected) * 100) if total_expected > 0 else 0
    overdue_percentage = round((overdue_payments / total_expected) * 100) if total_expected > 0 else 0
    expense_percentage = round((maintenance_expenses / total_revenue) * 100) if total_revenue > 0 else 0
    
    # Recent payments
    recent_payments = Payment.objects.select_related(
        'lease', 'lease__property', 'lease__tenant'
    ).order_by('-payment_date', '-created_at')[:5]
    
    context = {
        # Property statistics
        'property_count': property_count,
        'occupied_count': occupied_count,
        'vacant_count': vacant_count,
        'maintenance_count': maintenance_count,
        'occupied_percentage': occupied_percentage,
        'vacant_percentage': vacant_percentage,
        'maintenance_property_percentage': maintenance_property_percentage,
        
        # Tenant statistics
        'tenant_count': tenant_count,
        
        # Lease statistics
        'active_lease_count': active_lease_count,
        'expiring_leases': expiring_leases,
        
        # Maintenance statistics
        'open_maintenance_count': open_maintenance_count,
        'recent_maintenance': recent_maintenance,
        
        # Payment statistics
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'overdue_payments': overdue_payments,
        'maintenance_expenses': maintenance_expenses,
        'pending_percentage': pending_percentage,
        'overdue_percentage': overdue_percentage,
        'expense_percentage': expense_percentage,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'dashboard/dashboard.html', context)