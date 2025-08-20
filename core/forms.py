from django import forms
from .models import Property, Tenant, Payment, Lease, MaintenanceRequest

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

class BulkUpdatePropertiesForm(forms.Form):
    properties = forms.ModelMultipleChoiceField(
        queryset=Property.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    status = forms.ChoiceField(choices=Property.STATUS_CHOICES, required=False, label='Status')

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'