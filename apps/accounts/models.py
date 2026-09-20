from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
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
    
    class Meta:
        permissions = [
            ("view_dashboard", "Can view dashboard"),
            ("manage_properties", "Can manage properties"),
            ("manage_tenants", "Can manage tenants"),
            ("manage_leases", "Can manage leases"),
            ("manage_payments", "Can manage payments"),
            ("manage_maintenance", "Can manage maintenance"),
            ("view_reports", "Can view reports"),
            ("manage_users", "Can manage users"),
        ]
