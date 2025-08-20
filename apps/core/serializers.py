from rest_framework import serializers
from apps.accounts.models import CustomUser
from apps.properties.models import Property, FavoriteProperty
from apps.tenants.models import Tenant
from apps.leases.models import Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest
from .models import SavedSearch, SearchHistory



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

class FavoritePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProperty
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'
