from rest_framework import serializers
from .models import Lease
from apps.properties.serializers import PropertySerializer
from apps.tenants.serializers import TenantSerializer

class LeaseSerializer(serializers.ModelSerializer):
    """Serializer for the Lease model"""
    class Meta:
        model = Lease
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """Validate that end date is after start date"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({'end_date': 'End date must be after start date'})
        return data

class LeaseDetailSerializer(LeaseSerializer):
    """Detailed serializer for the Lease model with additional information"""
    property_details = PropertySerializer(source='property', read_only=True)
    tenant_details = TenantSerializer(source='tenant', read_only=True)
    
    class Meta(LeaseSerializer.Meta):
        fields = '__all__'