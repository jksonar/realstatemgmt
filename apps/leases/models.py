from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class Lease(models.Model):
    lease_id = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, db_index=True)  # active, expired, terminated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")

    class Meta:
        indexes = [
            models.Index(fields=['property', 'tenant']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return self.lease_id
