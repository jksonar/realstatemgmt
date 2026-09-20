from django import forms
from .models import Tenant, TenantDocument

class TenantDocumentForm(forms.ModelForm):
    class Meta:
        model = TenantDocument
        fields = ['document_type', 'document', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description of the document'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }