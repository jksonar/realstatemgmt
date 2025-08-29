from rest_framework import serializers
from apps.accounts.models import CustomUser
from apps.properties.models import Property, FavoriteProperty
from apps.tenants.models import Tenant
from apps.leases.models import Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest
from .models import SavedSearch, SearchHistory, AdvancedSearchFilter



class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class LeaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lease
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'

class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add a formatted date for display purposes
        if instance.last_used:
            representation['last_used_formatted'] = instance.last_used.strftime('%Y-%m-%d %H:%M')
        return representation

class FavoritePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProperty
        fields = '__all__'

class AdvancedSearchFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedSearchFilter
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'
