from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
from apps.payments.models import Payment
from apps.leases.models import Lease
from apps.tenants.models import Tenant
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_payment_reminders():
    """
    Send payment reminders for upcoming and overdue payments
    """
    try:
        # Get payments due in the next 3 days
        upcoming_due_date = timezone.now().date() + timedelta(days=3)
        upcoming_payments = Payment.objects.filter(
            due_date__lte=upcoming_due_date,
            status='pending'
        ).select_related('lease__tenant')
        
        reminder_count = 0
        
        for payment in upcoming_payments:
            tenant = payment.lease.tenant
            days_until_due = (payment.due_date - timezone.now().date()).days
            
            if days_until_due <= 0:
                subject = f"URGENT: Payment Overdue - {payment.payment_type}"
                message_type = "overdue"
            else:
                subject = f"Payment Reminder - Due in {days_until_due} days"
                message_type = "upcoming"
            
            message = f"""
            Dear {tenant.first_name} {tenant.last_name},
            
            This is a {'payment overdue notice' if message_type == 'overdue' else 'friendly reminder'} regarding your upcoming payment:
            
            Payment Details:
            - Amount: ${payment.amount}
            - Type: {payment.payment_type}
            - Due Date: {payment.due_date}
            - Property: {payment.lease.property.address}
            
            {'Please make this payment immediately to avoid late fees.' if message_type == 'overdue' else 'Please ensure payment is made by the due date.'}
            
            If you have already made this payment, please disregard this message.
            
            Thank you,
            Property Management Team
            """
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[tenant.email],
                    fail_silently=False,
                )
                reminder_count += 1
                logger.info(f"Payment reminder sent to {tenant.email} for payment {payment.id}")
            except Exception as e:
                logger.error(f"Failed to send reminder to {tenant.email}: {str(e)}")
        
        logger.info(f"Sent {reminder_count} payment reminders")
        return f"Successfully sent {reminder_count} payment reminders"
        
    except Exception as e:
        logger.error(f"Error in send_payment_reminders task: {str(e)}")
        raise

@shared_task
def mark_overdue_payments():
    """
    Mark payments as overdue if they are past due date
    """
    try:
        today = timezone.now().date()
        overdue_payments = Payment.objects.filter(
            due_date__lt=today,
            status='pending'
        )
        
        updated_count = overdue_payments.update(status='overdue')
        logger.info(f"Marked {updated_count} payments as overdue")
        
        return f"Marked {updated_count} payments as overdue"
        
    except Exception as e:
        logger.error(f"Error in mark_overdue_payments task: {str(e)}")
        raise

@shared_task
def send_individual_payment_reminder(payment_id):
    """
    Send a payment reminder for a specific payment
    """
    try:
        payment = Payment.objects.select_related('lease__tenant', 'lease__property').get(id=payment_id)
        tenant = payment.lease.tenant
        
        subject = f"Payment Reminder - {payment.payment_type}"
        message = f"""
        Dear {tenant.first_name} {tenant.last_name},
        
        This is a reminder regarding your payment:
        
        Payment Details:
        - Amount: ${payment.amount}
        - Type: {payment.payment_type}
        - Due Date: {payment.due_date}
        - Property: {payment.lease.property.address}
        
        Please ensure payment is made by the due date.
        
        Thank you,
        Property Management Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[tenant.email],
            fail_silently=False,
        )
        
        logger.info(f"Individual payment reminder sent to {tenant.email} for payment {payment_id}")
        return f"Payment reminder sent to {tenant.email}"
        
    except Payment.DoesNotExist:
        logger.error(f"Payment with ID {payment_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error sending individual payment reminder: {str(e)}")
        raise

@shared_task
def send_bulk_payment_reminders(payment_ids):
    """
    Send payment reminders for multiple payments
    """
    try:
        payments = Payment.objects.filter(
            id__in=payment_ids
        ).select_related('lease__tenant', 'lease__property')
        
        sent_count = 0
        for payment in payments:
            try:
                send_individual_payment_reminder.delay(payment.id)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to queue reminder for payment {payment.id}: {str(e)}")
        
        return f"Queued {sent_count} payment reminders"
        
    except Exception as e:
        logger.error(f"Error in send_bulk_payment_reminders task: {str(e)}")
        raise

@shared_task
def generate_monthly_payment_report():
    """
    Generate monthly payment report and send to administrators
    """
    try:
        from django.db.models import Sum, Count
        from datetime import date
        
        # Get current month data
        current_month = date.today().replace(day=1)
        
        monthly_stats = Payment.objects.filter(
            payment_date__gte=current_month
        ).aggregate(
            total_collected=Sum('amount', filter=Q(status='paid')),
            total_pending=Sum('amount', filter=Q(status='pending')),
            total_overdue=Sum('amount', filter=Q(status='overdue')),
            paid_count=Count('id', filter=Q(status='paid')),
            pending_count=Count('id', filter=Q(status='pending')),
            overdue_count=Count('id', filter=Q(status='overdue'))
        )
        
        report = f"""
        Monthly Payment Report - {current_month.strftime('%B %Y')}
        
        Summary:
        - Total Collected: ${monthly_stats['total_collected'] or 0}
        - Total Pending: ${monthly_stats['total_pending'] or 0}
        - Total Overdue: ${monthly_stats['total_overdue'] or 0}
        
        Payment Counts:
        - Paid: {monthly_stats['paid_count']}
        - Pending: {monthly_stats['pending_count']}
        - Overdue: {monthly_stats['overdue_count']}
        """
        
        # Send to administrators (you can customize this)
        admin_emails = ['admin@example.com']  # Replace with actual admin emails
        
        send_mail(
            subject=f"Monthly Payment Report - {current_month.strftime('%B %Y')}",
            message=report,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False,
        )
        
        logger.info("Monthly payment report sent to administrators")
        return "Monthly payment report generated and sent"
        
    except Exception as e:
        logger.error(f"Error generating monthly payment report: {str(e)}")
        raise

@shared_task
def email_financial_report():
    """Generate and email the financial report."""
    payments = Payment.objects.all()
    context = {
        'payments': payments,
        'total_revenue': sum(p.amount for p in payments if p.status == 'paid'),
        'outstanding_payments': sum(p.amount for p in payments if p.status in ['pending', 'overdue']),
    }
    html_content = render_to_string('reports/financial_report.html', context)
    email = EmailMessage(
        'Monthly Financial Report',
        html_content,
        'from@example.com',
        ['to@example.com'],
    )
    email.content_subtype = 'html'
    email.send()