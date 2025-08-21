from rest_framework import serializers
from .models import MaintenanceRequest
from apps.properties.serializers import PropertySerializer
from apps.tenants.serializers import TenantSerializer

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Serializer for the MaintenanceRequest model"""
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
        read_only_fields = ('reported_date', 'request_id')
    
    def validate(self, data):
        """Validate maintenance request data"""
        # Ensure cost is positive if provided
        if data.get('cost') and data['cost'] < 0:
            raise serializers.ValidationError({'cost': 'Cost cannot be negative'})
        
        # Ensure completed_date is not before reported_date
        if data.get('completed_date') and data['completed_date'] < data.get('reported_date', self.instance.reported_date if self.instance else None):
            raise serializers.ValidationError({'completed_date': 'Completion date cannot be before reported date'})
        
        return data

class MaintenanceRequestDetailSerializer(MaintenanceRequestSerializer):
    """Detailed serializer for the MaintenanceRequest model with additional information"""
    property_details = PropertySerializer(source='property', read_only=True)
    tenant_details = TenantSerializer(source='tenant', read_only=True)
    
    class Meta(MaintenanceRequestSerializer.Meta):
        fields = '__all__'