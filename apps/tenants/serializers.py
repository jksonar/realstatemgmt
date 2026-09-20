from rest_framework import serializers
from .models import Tenant

class TenantSerializer(serializers.ModelSerializer):
    """Serializer for the Tenant model"""
    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_phone(self, value):
        """Validate phone number format"""
        # Simple validation for demonstration purposes
        if not value.isdigit():
            raise serializers.ValidationError("Phone number should contain only digits")
        return value

    def validate_email(self, value):
        """Validate email is unique"""
        # The unique constraint is already enforced by the model,
        # but we can add additional validation if needed
        return value

class TenantDetailSerializer(TenantSerializer):
    """Detailed serializer for the Tenant model with additional information"""
    # We could add additional fields here like lease information
    # lease_info = serializers.SerializerMethodField()
    
    class Meta(TenantSerializer.Meta):
        fields = '__all__'

    # def get_lease_info(self, obj):
    #     from apps.leases.serializers import LeaseSerializer
    #     leases = obj.lease_set.all()
    #     return LeaseSerializer(leases, many=True).data