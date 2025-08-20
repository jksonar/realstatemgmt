import django_filters
from .models import Property

class PropertyFilter(django_filters.FilterSet):
    class Meta:
        model = Property
        fields = {
            'city': ['icontains'],
            'area': ['icontains'],
            'property_type': ['exact'],
            'status': ['exact'],
        }
