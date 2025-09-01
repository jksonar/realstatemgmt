from django.contrib import admin
from .models import Lead, LeadSource, LeadActivity

@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'related_property', 'source', 'status', 'score', 'inquiry_date', 'next_follow_up')
    list_filter = ('status', 'source', 'is_active', 'inquiry_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    date_hierarchy = 'inquiry_date'
    readonly_fields = ('inquiry_date', 'created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Lead Details', {
            'fields': ('related_property', 'source', 'assigned_to', 'status', 'score', 'notes')
        }),
        ('Dates', {
            'fields': ('inquiry_date', 'last_contact_date', 'next_follow_up', 'converted_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ('lead', 'activity_type', 'activity_date', 'performed_by')
    list_filter = ('activity_type', 'activity_date')
    search_fields = ('lead__first_name', 'lead__last_name', 'description')
    date_hierarchy = 'activity_date'
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('lead', 'performed_by')
