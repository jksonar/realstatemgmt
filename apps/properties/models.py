from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

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

class FavoriteProperty(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.address}"
