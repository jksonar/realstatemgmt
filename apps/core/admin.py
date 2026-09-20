from django.contrib import admin
from .models import SavedSearch, SearchHistory

admin.site.register(SavedSearch)
admin.site.register(SearchHistory)