from django.contrib import admin
from .models import Property, FavoriteProperty

admin.site.register(Property)
admin.site.register(FavoriteProperty)
