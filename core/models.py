from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

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
    city = models.CharField(max_length=100, db_index=True)
    area = models.CharField(max_length=100, db_index=True)
    property_type = models.CharField(max_length=10)  # 1BHK, 2BHK, etc.
    size_sqft = models.IntegerField(validators=[MinValueValidator(1)])
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    furnished_type = models.CharField(max_length=20)
    amenities = models.JSONField(default=list)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.property_id

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

class Lease(models.Model):
    lease_id = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
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

class Payment(models.Model):
    payment_id = models.CharField(max_length=20, unique=True)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
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

class MaintenanceRequest(models.Model):
    request_id = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)
    issue_type = models.CharField(max_length=50)
    description = models.TextField()
    priority = models.CharField(max_length=20)  # low, medium, high, urgent
    status = models.CharField(max_length=20, db_index=True)  # reported, in_progress, completed
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, validators=[MinValueValidator(0)])
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

class SavedSearch(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    query_params = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class FavoriteProperty(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.address}"