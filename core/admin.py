
from django.contrib import admin
from .models import Property, Tenant, Lease, Payment, MaintenanceRequest, CustomUser

admin.site.register(CustomUser)
admin.site.register(Property)
admin.site.register(Tenant)
admin.site.register(Lease)
admin.site.register(Payment)
admin.site.register(MaintenanceRequest)
