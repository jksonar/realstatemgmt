from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'

class BulkUpdatePropertiesForm(forms.Form):
    properties = forms.ModelMultipleChoiceField(
        queryset=Property.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    status = forms.ChoiceField(choices=Property.STATUS_CHOICES, required=False, label='Status')
