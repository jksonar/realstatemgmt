from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

class Property(models.Model):
    property_id = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    property_type = models.CharField(max_length=10)  # 1BHK, 2BHK, etc.
    size_sqft = models.IntegerField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # available, occupied, maintenance
    furnished_type = models.CharField(max_length=20)
    amenities = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tenant(models.Model):
    tenant_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    id_proof_type = models.CharField(max_length=20)
    id_proof_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Lease(models.Model):
    lease_id = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # active, expired, terminated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    payment_id = models.CharField(max_length=20, unique=True)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    due_date = models.DateField()
    payment_type = models.CharField(max_length=20)  # rent, deposit, maintenance
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20)  # paid, pending, overdue
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MaintenanceRequest(models.Model):
    request_id = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)
    issue_type = models.CharField(max_length=50)
    description = models.TextField()
    priority = models.CharField(max_length=20)  # low, medium, high, urgent
    status = models.CharField(max_length=20)  # reported, in_progress, completed
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    assigned_to = models.CharField(max_length=100, blank=True)
    reported_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)