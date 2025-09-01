from django import forms
from django.utils import timezone
from .models import Lead, LeadSource, LeadActivity

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'source', 'status', 'score', 'priority', 'budget_range',
            'preferred_contact_method', 'referral_source', 'campaign',
            'related_property', 'assigned_to', 'inquiry_date', 
            'next_follow_up', 'notes', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'budget_range': forms.Select(attrs={'class': 'form-control'}),
            'preferred_contact_method': forms.Select(attrs={'class': 'form-control'}),
            'referral_source': forms.TextInput(attrs={'class': 'form-control'}),
            'campaign': forms.TextInput(attrs={'class': 'form-control'}),
            'related_property': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'inquiry_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'next_follow_up': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for new leads
        if not self.instance.pk:
            self.fields['inquiry_date'].initial = timezone.now().date()
            self.fields['status'].initial = 'new'
            self.fields['is_active'].initial = True
            self.fields['score'].initial = 0
        
        # Make some fields optional
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['related_property'].required = False
        self.fields['assigned_to'].required = False
        self.fields['next_follow_up'].required = False
        self.fields['notes'].required = False
        self.fields['budget_range'].required = False
        self.fields['referral_source'].required = False
        self.fields['campaign'].required = False

class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }

class LeadActivityForm(forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ['activity_type', 'description', 'activity_date']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'activity_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default value for activity date
        if not self.instance.pk:
            self.fields['activity_date'].initial = timezone.now()