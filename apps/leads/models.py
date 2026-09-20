from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.properties.models import Property

class LeadSource(models.Model):
    """Model to track where leads are coming from"""
    name = models.CharField(_('Source Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Lead Source')
        verbose_name_plural = _('Lead Sources')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Lead(models.Model):
    """Model to track property inquiries and leads"""
    LEAD_STATUS_CHOICES = [
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('qualified', _('Qualified')),
        ('unqualified', _('Unqualified')),
        ('converted', _('Converted')),
        ('lost', _('Lost')),
    ]
    
    LEAD_PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    BUDGET_RANGE_CHOICES = [
        ('under_100k', _('Under $100,000')),
        ('100k_250k', _('$100,000 - $250,000')),
        ('250k_500k', _('$250,000 - $500,000')),
        ('500k_750k', _('$500,000 - $750,000')),
        ('750k_1m', _('$750,000 - $1,000,000')),
        ('over_1m', _('Over $1,000,000')),
    ]
    
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    email = models.EmailField(_('Email Address'))
    phone = models.CharField(_('Phone Number'), max_length=20, blank=True)
    related_property = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL, 
        related_name='leads',
        verbose_name=_('Property'),
        null=True,
        blank=True
    )
    source = models.ForeignKey(
        LeadSource,
        on_delete=models.SET_NULL,
        related_name='leads',
        verbose_name=_('Lead Source'),
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_leads',
        verbose_name=_('Assigned To'),
        null=True,
        blank=True
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=LEAD_STATUS_CHOICES,
        default='new'
    )
    score = models.IntegerField(
        _('Lead Score'),
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=50,
        help_text=_('Score from 1-100 indicating lead quality')
    )
    priority = models.CharField(
        _('Priority'),
        max_length=20,
        choices=LEAD_PRIORITY_CHOICES,
        default='medium',
        help_text=_('Priority level for follow-up')
    )
    budget_range = models.CharField(
        _('Budget Range'),
        max_length=20,
        choices=BUDGET_RANGE_CHOICES,
        blank=True,
        null=True,
        help_text=_('Estimated budget range of the lead')
    )
    preferred_contact_method = models.CharField(
        _('Preferred Contact Method'),
        max_length=20,
        choices=[('email', _('Email')), ('phone', _('Phone')), ('sms', _('SMS'))],
        default='email',
        help_text=_('Preferred method of contact')
    )
    referral_source = models.CharField(
        _('Referral Source'),
        max_length=100,
        blank=True,
        help_text=_('Name of person who referred this lead')
    )
    campaign = models.CharField(
        _('Marketing Campaign'),
        max_length=100,
        blank=True,
        help_text=_('Marketing campaign that generated this lead')
    )
    notes = models.TextField(_('Notes'), blank=True)
    inquiry_date = models.DateTimeField(_('Inquiry Date'), default=timezone.now)
    last_contact_date = models.DateTimeField(_('Last Contact Date'), null=True, blank=True)
    next_follow_up = models.DateTimeField(_('Next Follow Up'), null=True, blank=True)
    converted_date = models.DateTimeField(_('Conversion Date'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')
        ordering = ['-inquiry_date']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    def get_status_badge_class(self):
        """Return the appropriate Bootstrap badge class for the lead status"""
        status_classes = {
            'new': 'info',
            'contacted': 'primary',
            'qualified': 'success',
            'unqualified': 'warning',
            'converted': 'success',
            'lost': 'danger'
        }
        return status_classes.get(self.status, 'secondary')
        
    def get_priority_badge_class(self):
        """Return the appropriate Bootstrap badge class for the lead priority"""
        priority_classes = {
            'low': 'secondary',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'dark'
        }
        return priority_classes.get(self.priority, 'secondary')

class LeadActivity(models.Model):
    """Model to track activities and interactions with leads"""
    ACTIVITY_TYPE_CHOICES = [
        ('note', _('Note')),
        ('call', _('Phone Call')),
        ('email', _('Email')),
        ('meeting', _('Meeting')),
        ('task', _('Task')),
    ]
    
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('Lead')
    )
    activity_type = models.CharField(
        _('Activity Type'),
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES
    )
    description = models.TextField(_('Description'))
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='lead_activities',
        verbose_name=_('Performed By'),
        null=True
    )
    activity_date = models.DateTimeField(_('Activity Date'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Lead Activity')
        verbose_name_plural = _('Lead Activities')
        ordering = ['-activity_date']
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.lead}"
