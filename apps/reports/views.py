from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, FloatField
from django.utils import timezone
from datetime import timedelta, datetime
import json
import calendar

from apps.properties.models import Property
from apps.tenants.models import Tenant
from apps.leases.models import Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest

@login_required
def report_list(request):
    """View for listing available reports"""
    return render(request, 'reports/report_list.html')

@login_required
def financial_report(request):
    """View for financial reports with filtering by period"""
    # Get date range based on period parameter
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    # Set default date range based on period
    if period == 'month':
        start_date = today.replace(day=1)
        end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        period_label = f"{start_date.strftime('%B %Y')}"
        
        # Previous period for comparison
        prev_start_date = (start_date - timedelta(days=1)).replace(day=1)
        prev_end_date = start_date - timedelta(days=1)
    elif period == 'quarter':
        current_quarter = (today.month - 1) // 3 + 1
        start_date = datetime(today.year, 3 * current_quarter - 2, 1).date()
        end_date = datetime(today.year, 3 * current_quarter + 1, 1).date() - timedelta(days=1)
        if 3 * current_quarter + 1 > 12:
            end_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
        period_label = f"Q{current_quarter} {today.year}"
        
        # Previous quarter for comparison
        prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
        prev_year = today.year if current_quarter > 1 else today.year - 1
        prev_start_date = datetime(prev_year, 3 * prev_quarter - 2, 1).date()
        prev_end_date = datetime(prev_year, 3 * prev_quarter + 1, 1).date() - timedelta(days=1)
        if 3 * prev_quarter + 1 > 12:
            prev_end_date = datetime(prev_year + 1, 1, 1).date() - timedelta(days=1)
    elif period == 'year':
        start_date = datetime(today.year, 1, 1).date()
        end_date = datetime(today.year, 12, 31).date()
        period_label = f"{today.year}"
        
        # Previous year for comparison
        prev_start_date = datetime(today.year - 1, 1, 1).date()
        prev_end_date = datetime(today.year - 1, 12, 31).date()
    elif period == 'custom':
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            period_label = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
            
            # Previous period with same duration
            duration = (end_date - start_date).days
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=duration)
        except (ValueError, TypeError):
            # Default to current month if dates are invalid
            start_date = today.replace(day=1)
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            period_label = f"{start_date.strftime('%B %Y')}"
            
            # Previous period for comparison
            prev_start_date = (start_date - timedelta(days=1)).replace(day=1)
            prev_end_date = start_date - timedelta(days=1)
    else:
        # Default to current month
        start_date = today.replace(day=1)
        end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        period_label = f"{start_date.strftime('%B %Y')}"
        
        # Previous period for comparison
        prev_start_date = (start_date - timedelta(days=1)).replace(day=1)
        prev_end_date = start_date - timedelta(days=1)
    
    # Calculate financial metrics for current period
    total_revenue = Payment.objects.filter(
        status='paid',
        payment_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = MaintenanceRequest.objects.filter(
        status='completed',
        updated_at__range=[start_date, end_date]
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    net_income = total_revenue - total_expenses
    
    outstanding_balance = Payment.objects.filter(
        Q(status='pending') | Q(status='overdue'),
        due_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate financial metrics for previous period for comparison
    prev_total_revenue = Payment.objects.filter(
        status='paid',
        payment_date__range=[prev_start_date, prev_end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    prev_total_expenses = MaintenanceRequest.objects.filter(
        status='completed',
        updated_at__range=[prev_start_date, prev_end_date]
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    prev_net_income = prev_total_revenue - prev_total_expenses
    
    prev_outstanding_balance = Payment.objects.filter(
        Q(status='pending') | Q(status='overdue'),
        due_date__range=[prev_start_date, prev_end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate percentage changes
    revenue_change = round(((total_revenue - prev_total_revenue) / prev_total_revenue * 100) if prev_total_revenue > 0 else 0)
    expense_change = round(((total_expenses - prev_total_expenses) / prev_total_expenses * 100) if prev_total_expenses > 0 else 0)
    income_change = round(((net_income - prev_net_income) / prev_net_income * 100) if prev_net_income > 0 else 0)
    outstanding_change = round(((outstanding_balance - prev_outstanding_balance) / prev_outstanding_balance * 100) if prev_outstanding_balance > 0 else 0)
    
    # Payment status breakdown
    paid_amount = Payment.objects.filter(
        status='paid',
        payment_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_amount = Payment.objects.filter(
        status='pending',
        due_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    overdue_amount = Payment.objects.filter(
        status='overdue',
        due_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    refunded_amount = Payment.objects.filter(
        status='refunded',
        payment_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_payment_amount = paid_amount + pending_amount + overdue_amount + refunded_amount
    
    # Calculate payment status percentages
    paid_percentage = round((paid_amount / total_payment_amount * 100) if total_payment_amount > 0 else 0)
    pending_percentage = round((pending_amount / total_payment_amount * 100) if total_payment_amount > 0 else 0)
    overdue_percentage = round((overdue_amount / total_payment_amount * 100) if total_payment_amount > 0 else 0)
    refunded_percentage = round((refunded_amount / total_payment_amount * 100) if total_payment_amount > 0 else 0)
    
    payment_status = {
        'paid': paid_amount,
        'pending': pending_amount,
        'overdue': overdue_amount,
        'refunded': refunded_amount,
        'paid_percentage': paid_percentage,
        'pending_percentage': pending_percentage,
        'overdue_percentage': overdue_percentage,
        'refunded_percentage': refunded_percentage
    }
    
    # Expense categories breakdown
    maintenance_categories = MaintenanceRequest.objects.filter(
        status='completed',
        updated_at__range=[start_date, end_date]
    ).values('category').annotate(total=Sum('cost')).order_by('-total')
    
    # Define colors for expense categories
    category_colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#5a5c69', '#858796', '#6f42c1', '#20c9a6', '#fd7e14'
    ]
    
    # Prepare expense categories data for charts
    expense_categories = []
    expense_categories_names = []
    expense_categories_values = []
    expense_categories_colors = []
    
    for i, category in enumerate(maintenance_categories):
        category_name = category['category'].replace('_', ' ').title() if category['category'] else 'Other'
        category_amount = category['total'] or 0
        category_percentage = round((category_amount / total_expenses * 100) if total_expenses > 0 else 0)
        category_color = category_colors[i % len(category_colors)]
        
        expense_categories.append({
            'name': category_name,
            'amount': category_amount,
            'percentage': category_percentage,
            'color': category_color
        })
        
        expense_categories_names.append(category_name)
        expense_categories_values.append(category_amount)
        expense_categories_colors.append(category_color)
    
    # Property performance data
    property_performance = []
    properties = Property.objects.all()
    
    for prop in properties:
        # Calculate revenue for this property
        property_revenue = Payment.objects.filter(
            lease__property=prop,
            status='paid',
            payment_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate expenses for this property
        property_expenses = MaintenanceRequest.objects.filter(
            property=prop,
            status='completed',
            updated_at__range=[start_date, end_date]
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        # Calculate net income
        property_net_income = property_revenue - property_expenses
        
        # Calculate ROI (Return on Investment)
        # Assuming property value is stored or can be derived
        property_value = prop.rent * 12 * 10  # Simple estimation: 10 years of annual rent
        property_roi = (property_net_income / property_value * 100) if property_value > 0 else 0
        
        # Calculate occupancy rate
        days_in_period = (end_date - start_date).days + 1
        occupied_days = Lease.objects.filter(
            property=prop,
            status='active',
            start_date__lte=end_date,
            end_date__gte=start_date
        ).count() * days_in_period  # Simplified calculation
        
        occupancy_rate = round((occupied_days / days_in_period * 100) if days_in_period > 0 else 0)
        
        property_performance.append({
            'property_id': prop.property_id,
            'address': prop.address,
            'image': prop.image,
            'revenue': property_revenue,
            'expenses': property_expenses,
            'net_income': property_net_income,
            'roi': property_roi,
            'occupancy_rate': occupancy_rate,
            'status': prop.status
        })
    
    # Sort properties by net income (descending)
    property_performance = sorted(property_performance, key=lambda x: x['net_income'], reverse=True)
    
    # Monthly data for charts
    months = []
    monthly_revenue = []
    monthly_expenses = []
    monthly_net_income = []
    
    # Determine the number of months to show based on the period
    if period == 'month':
        num_months = 12  # Show last 12 months
    elif period == 'quarter':
        num_months = 12  # Show last 12 months
    elif period == 'year':
        num_months = 12  # Show all months in the year
    else:
        num_months = min(12, (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1)
    
    # Generate monthly data
    for i in range(num_months - 1, -1, -1):
        if period == 'year':
            # For yearly report, show all months in the selected year
            month_date = datetime(today.year, 12 - i, 1).date()
        else:
            # For other periods, show the last num_months months
            month_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            month_date = month_date - timedelta(days=30 * i)
        
        month_end = (month_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Get month name
        month_name = month_date.strftime('%b %Y')
        months.append(month_name)
        
        # Get revenue for this month
        month_revenue = Payment.objects.filter(
            status='paid',
            payment_date__range=[month_date, month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue.append(month_revenue)
        
        # Get expenses for this month
        month_expenses = MaintenanceRequest.objects.filter(
            status='completed',
            updated_at__range=[month_date, month_end]
        ).aggregate(total=Sum('cost'))['total'] or 0
        monthly_expenses.append(month_expenses)
        
        # Calculate net income
        month_net_income = month_revenue - month_expenses
        monthly_net_income.append(month_net_income)
    
    context = {
        'period': period,
        'period_label': period_label,
        'start_date': start_date,
        'end_date': end_date,
        
        # Financial summary
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'outstanding_balance': outstanding_balance,
        
        # Percentage changes
        'revenue_change': revenue_change,
        'expense_change': expense_change,
        'income_change': income_change,
        'outstanding_change': outstanding_change,
        
        # Payment status
        'payment_status': payment_status,
        
        # Expense categories
        'expense_categories': expense_categories,
        'expense_categories_names': json.dumps(expense_categories_names),
        'expense_categories_values': json.dumps(expense_categories_values),
        'expense_categories_colors': json.dumps(expense_categories_colors),
        
        # Property performance
        'property_performance': property_performance,
        
        # Monthly data for charts
        'months': json.dumps(months),
        'monthly_revenue': json.dumps(monthly_revenue),
        'monthly_expenses': json.dumps(monthly_expenses),
        'monthly_net_income': json.dumps(monthly_net_income),
    }
    
    return render(request, 'reports/financial_report.html', context)

@login_required
def export_financial_report(request):
    """Export financial report in various formats"""
    export_format = request.GET.get('format', 'pdf')
    
    # This is a placeholder for actual export functionality
    # In a real implementation, you would generate the appropriate file format
    # and return it as a downloadable response
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="financial_report.{export_format}"'
    response.write(f'This is a placeholder for the financial report export in {export_format} format.')
    
    return response

@login_required
def custom_report_builder(request):
    """View for custom report builder"""
    return render(request, 'reports/custom_report_builder.html')