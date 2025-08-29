from django.db import models
from django.conf import settings
import os

def tenant_document_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/tenants/documents/tenant_<id>/<filename>
    return f'tenants/documents/tenant_{instance.tenant_id}/{filename}'

class TenantDocument(models.Model):
    DOCUMENT_TYPES = (
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('income_proof', 'Income Proof'),
        ('reference', 'Reference Letter'),
        ('employment', 'Employment Verification'),
        ('other', 'Other Document'),
    )
    
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document = models.FileField(upload_to=tenant_document_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tenant.tenant_id} - {self.get_document_type_display()}"
    
    def filename(self):
        return os.path.basename(self.document.name)

class Tenant(models.Model):
    tenant_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    id_proof_type = models.CharField(max_length=20)
    id_proof_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return self.tenant_id
