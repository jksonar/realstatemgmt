from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lease, Property

@receiver(post_save, sender=Lease)
def update_property_status(sender, instance, created, **kwargs):
    if created:
        if instance.status == 'active':
            instance.property.status = 'occupied'
            instance.property.save()
