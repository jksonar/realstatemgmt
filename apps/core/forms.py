from django import forms
from apps.properties.models import Property
from apps.tenants.models import Tenant
from apps.payments.models import Payment
from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from apps.accounts.models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm



REPORTABLE_MODELS = {
    'property': Property,
    'tenant': Tenant,
    'payment': Payment,
    'lease': Lease,
    'maintenance_request': MaintenanceRequest,
}

class ReportBuilderForm(forms.Form):
    model_choice = forms.ChoiceField(
        choices=[(name, name.replace('_', ' ').title()) for name in REPORTABLE_MODELS.keys()],
        label="Select a report type"
    )
    fields = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        label="Select fields to include",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'model_choice' in self.data:
            model_name = self.data.get('model_choice')
            model = REPORTABLE_MODELS.get(model_name)
            if model:
                self.fields['fields'].choices = [(field.name, field.verbose_name) for field in model._meta.fields]



class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'

class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = '__all__'

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'