from django.db import models
from django.conf import settings

class AdvancedSearchFilter(models.Model):
    name = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    filter_type = models.CharField(max_length=50)  # range, exact, contains, etc.
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.field_name})"

class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    query_params = models.JSONField()
    is_advanced = models.BooleanField(default=False)
    advanced_filters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
