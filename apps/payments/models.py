from django.db import models
from django.core.validators import MinValueValidator

class Payment(models.Model):
    payment_id = models.CharField(max_length=20, unique=True)
    lease = models.ForeignKey('leases.Lease', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    payment_type = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, db_index=True)  # paid, pending, overdue
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['lease', 'due_date']),
        ]

    def __str__(self):
        return self.payment_id
