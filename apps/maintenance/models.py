from django.db import models
from django.core.validators import MinValueValidator

class MaintenanceRequest(models.Model):
    request_id = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.SET_NULL, null=True, blank=True)
    issue_type = models.CharField(max_length=50)
    description = models.TextField()
    priority = models.CharField(max_length=20)  # low, medium, high, urgent
    status = models.CharField(max_length=20, db_index=True)  # reported, in_progress, completed
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    assigned_to = models.CharField(max_length=100, blank=True)
    reported_date = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['property', 'status']),
            models.Index(fields=['reported_date']),
        ]

    def __str__(self):
        return self.request_id
